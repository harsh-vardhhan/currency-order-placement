import requests
import os

usdinr_lotsize = 1000


# place buy order
def place_buy_order(buy_price, buy_strike):
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


def place_sell_order(sell_price, sell_strike):
  # place sell order
  place_order_url = "https://api.upstox.com/v2/order/place"
  order_payload = {
    "quantity": 1,
    "product": "D",
    "validity": "DAY",
    "price": sell_price,
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
  return response


def modify_sell_order(sell_price, order_id):
  # place sell order
  modify_order_url = "https://api.upstox.com/v2/order/modify"
  order_payload = {
    "validity": "DAY",
    "price": sell_price,
    "order_id": order_id,
    "order_type": "LIMIT",
    "disclosed_quantity": 0,
    "trigger_price": 0
  }
  print(order_payload)
  order_headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN'],
    'Content-Type': 'application/json',
  }
  response = requests.request(
    "PUT",
    url=modify_order_url,
    json=order_payload,
    headers=order_headers,
  )
  return response
