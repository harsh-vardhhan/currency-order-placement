import requests
import os
import math
import time
from place_order import place_sell_order, modify_sell_order

expiry = '24APR'
usdinr_lotsize = 1000


def sell_call_price(sell_strike):
  quotes_price_url = "https://api.upstox.com/v2/market-quote/quotes?instrument_key=" + sell_strike[
    'instrument_key']
  payload = {}
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN']
  }
  response = requests.request("GET",
                              quotes_price_url,
                              headers=headers,
                              data=payload)
  response_data = response.json()

  sell_strike_price = sell_strike['strike_price']
  frac = math.modf(sell_strike_price)
  if frac[0] == 0.0:
    sell_strike_price = math.trunc(sell_strike_price)

  instrument_name = sell_strike['segment'] \
  + ':' + sell_strike['underlying_symbol'] \
  + expiry + str(sell_strike_price) \
  +sell_strike['instrument_type']

  sell_prices=response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('sell')
  sell_price = sell_prices[0]['price'] * usdinr_lotsize
  # TODO: smart pricing
  order_id = None
  for i, price in reversed(list(enumerate(sell_prices))):
    # Place order
    if i == (len(sell_prices) - 1):
      order_placed = place_sell_order(price['price'], sell_strike)
      order_id = order_placed.json().get('data').get('order_id')
    # Modify order
    else:
      order_status_api = "https://api.upstox.com/v2/order/details?order_id=" + str(
        order_id)
      response = requests.request("GET", order_status_api, headers=headers)
      pending_quantity = response.json().get('data').get('pending_quantity')
      if pending_quantity > 0:
        order_modified = modify_sell_order(price['price'], order_id)
        print(order_modified.json())
        order_id = order_modified.json().get('data').get('order_id')
    time.sleep(5)

  # check for spread width
  ask = response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('sell')[0]['price']
  bid = response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('buy')[0]['price']
  spread = ask - bid
  illiquid = False
  if spread > 0.25:
    illiquid = True
  return sell_price, sell_strike_price, illiquid


def buy_call_price(buy_strike):
  quotes_price_url = "https://api.upstox.com/v2/market-quote/quotes?instrument_key=" + buy_strike[
    'instrument_key']
  payload = {}
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN']
  }
  response = requests.request("GET",
                              quotes_price_url,
                              headers=headers,
                              data=payload)
  response_data = response.json()

  buy_strike_price = buy_strike['strike_price']
  frac = math.modf(buy_strike_price)
  if frac[0] == 0.0:
    buy_strike_price = math.trunc(buy_strike_price)

  instrument_name = buy_strike['segment'] \
  + ':' + buy_strike['underlying_symbol'] \
  + expiry + str(buy_strike_price) \
  +buy_strike['instrument_type']

  buy_prices=response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('sell')
  buy_price = buy_prices[0]['price'] * usdinr_lotsize
  # TODO: calculate bid ask spread
  ask = response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('sell')[0]['price']
  bid = response_data\
  .get('data')\
  .get(instrument_name)\
  .get('depth')\
  .get('buy')[0]['price']
  spread = ask - bid
  return buy_price, buy_strike_price
