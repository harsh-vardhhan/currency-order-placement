# NOTE: Not a SEBI research analyst. I am not responsibly for your profit or loss.
#TODO: dynamically save secret variable of replit
#TODO: break down actions into functions
#TODO: save max profit and loss in replit DB
#TODO: exit position if profit hits max profit

import tkinter as tk
import requests
import os
import time
from datetime import datetime, timedelta
import webbrowser
import json
import math

expiry = '24APR'

url = 'https://api.upstox.com/v2/login/authorization/token'
headers = {
  'accept': 'application/json',
  'Content-Type': 'application/x-www-form-urlencoded',
}

data = {
  'code': os.environ['CODE'],
  'client_id': os.environ['CLIENT_ID'],
  'client_secret': os.environ['API_SECRET'],
  'redirect_uri': os.environ['REDIRECT_URL'],
  'grant_type': 'authorization_code',
}

authorizeUrl = "https://api.upstox.com/v2/login/authorization/dialog/"

params = {
  'client_id': os.environ['CLIENT_ID'],
  'redirect_uri': os.environ['REDIRECT_URL'],
}

usdinr_lotsize = 1000
liquid_spread = 0.25

max_profit = ''
max_loss = ''
sell_strike = ''


def authorize():
  url = authorizeUrl + '?client_id=' + os.environ[
    'CLIENT_ID'] + '&redirect_uri=' + os.environ['REDIRECT_URL']
  webbrowser.open(url, new=0, autoraise=True)


def login():
  response = requests.post(url, headers=headers, data=data)
  response_data = response.json()
  access_token = 'access_token'
  if access_token in response_data:
    print(response_data[access_token])
  else:
    print('reauthorize')


def call_credit_spread():
  url = 'https://api.upstox.com/v2/market-quote/ltp?instrument_key=NCD_FO|9063'
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN']
  }
  response = requests.get(url, headers=headers)
  response_data = response.json()
  future_price = response_data\
  .get('data')\
  .get('NCD_FO:USDINR' + expiry +'FUT')\
  .get('last_price')
  # get options data by strike
  NSE = open('NSE.json')
  data = json.load(NSE)

  date_time = datetime(2024, 4, 26, 23, 59, 59) - timedelta(hours=5,
                                                            minutes=30)
  unix_time = math.trunc(time.mktime(date_time.timetuple()) * 1000)
  # filter OTM call options
  OTM_call_options = []
  for i in data:
    if i['instrument_type'] == 'CE'\
    and i['segment'] == 'NCD_FO'\
    and i['name'] == 'USDINR'\
    and i['expiry'] == unix_time\
    and i['weekly'] == False\
    and i['strike_price'] > future_price:
      OTM_call_options.append(i)
  NSE.close()
  # sell strike
  smallest_difference = 100
  sell_strike = None
  for i in OTM_call_options:
    difference = i['strike_price'] - future_price
    if difference < smallest_difference:
      smallest_difference = difference
      sell_strike = i
  # buy strike
  buy_strike = None
  buy_strike_price = sell_strike['strike_price'] + 0.25
  for i in OTM_call_options:
    if i['strike_price'] == buy_strike_price:
      buy_strike = i
  # sell call price
  sell_price, sell_strike_price = sell_call_price(sell_strike)
  # buy call price
  buy_price, buy_strike_price = buy_call_price(buy_strike)
  # call credit spread - max profit & max loss
  spread = (buy_strike_price - sell_strike_price) * usdinr_lotsize
  net_credit = sell_price - buy_price

  max_profit = net_credit
  max_loss = spread - net_credit

  max_profit_label['text'] = 'Max Profit: ₹' + str(max_profit)
  max_loss_label['text'] = 'Max Loss: ₹' + str(max_loss)

  sell_strike_label.config(text=str(sell_strike['strike_price']) +
                           sell_strike['instrument_type'],
                           bg="red",
                           fg='white',
                           font='-weight bold')

  buy_strike_label.config(text=str(buy_strike['strike_price']) +
                          buy_strike['instrument_type'],
                          bg="green",
                          fg='white',
                          font='-weight bold')

  # place buy order
  place_order_url = "https://api.upstox.com/v2/order/place"
  order_payload = {
    "quantity": 1,
    "product": "D",
    "validity": "DAY",
    "price": (buy_price / usdinr_lotsize),
    "instrument_token": buy_strike['instrument_key'],
    "order_type": "LIMIT",
    "transaction_type": "BUY",
    "disclosed_quantity": 0,
    "trigger_price": 0,
    "is_amo": False
  }

  order_headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN'],
    'Content-Type': 'application/json',
  }
  response = requests.request(
    "POST",
    url=place_order_url,
    json=order_payload,
    headers=order_headers,
  )
  # place sell order
  place_order_url = "https://api.upstox.com/v2/order/place"
  order_payload = {
    "quantity": 1,
    "product": "D",
    "validity": "DAY",
    "price": (sell_price / usdinr_lotsize),
    "instrument_token": sell_strike['instrument_key'],
    "order_type": "LIMIT",
    "transaction_type": "SELL",
    "disclosed_quantity": 0,
    "trigger_price": 0,
    "is_amo": False
  }

  order_headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN'],
    'Content-Type': 'application/json',
  }
  response = requests.request(
    "POST",
    url=place_order_url,
    json=order_payload,
    headers=order_headers,
  )


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
  return sell_price, sell_strike_price


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
  .get('buy')
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


window = tk.Tk()
window.title("USDINR trading tool")
window.geometry("300x300")

button = tk.Button(text="Authorize", command=authorize)
button.pack()

button = tk.Button(text="Login", command=login)
button.pack()

bearish_strategy = tk.Label(text="Bearish")
bearish_strategy.config(font=("Courier", 14))
bearish_strategy.pack()

CallCreditSpread = tk.Button(text="Call Credit Spread",
                             command=call_credit_spread)

CallCreditSpread.pack()

buy_strike_label = tk.Label()
buy_strike_label.pack()

sell_strike_label = tk.Label()
sell_strike_label.pack()

max_profit_label = tk.Label()
max_profit_label.config(text=max_profit)
max_profit_label.pack()

max_loss_label = tk.Label()
max_loss_label.config(text=max_loss)
max_loss_label.pack()

tk.mainloop()
