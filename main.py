import tkinter as tk
import requests
import os
import time
from datetime import datetime, timedelta
import webbrowser
import json
import math

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
  print('call_credit_spread')
  url = 'https://api.upstox.com/v2/market-quote/ltp?instrument_key=NCD_FO|1060'
  headers = {
    'Accept': 'application/json',
    'Authorization': 'Bearer ' + os.environ['ACCESS_TOKEN']
  }
  response = requests.get(url, headers=headers)
  response_data = response.json()
  ncd_fut_price = response_data.get('data').get('NCD_FO:USDINR24MARFUT').get(
    'last_price')
  # get options data by strike
  NSE = open('NSE.json')
  data = json.load(NSE)

  date_time = datetime(2024, 3, 26, 23, 59, 59) - timedelta(hours=5,
                                                            minutes=30)
  unix_time = math.trunc(time.mktime(date_time.timetuple()) * 1000)

  OTM_call_options = []
  for i in data:
    if i['instrument_type'] == 'CE'\
    and i['segment'] == 'NCD_FO'\
    and i['name'] == 'USDINR'\
    and i['expiry'] == unix_time\
    and i['weekly'] == False\
    and i['strike_price'] > ncd_fut_price:
      OTM_call_options.append(i)
  NSE.close()

  for i in OTM_call_options:
    print(i)


def put_credit_spread():
  print('call_credit_spread')


def iron_condor():
  print('iron_condor')


def short_strangle():
  print('short_strangle')


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

bullish_strategy = tk.Label(text="Bullish")
bullish_strategy.config(font=("Courier", 14))
bullish_strategy.pack()

PutCreditSpread = tk.Button(text="Put Credit Spread",
                            command=put_credit_spread)
PutCreditSpread.pack()

neutral_strategy = tk.Label(text="Neutral")
neutral_strategy.config(font=("Courier", 14))
neutral_strategy.pack()

ShortStrangle = tk.Button(text="Short Strangle", command=short_strangle)
ShortStrangle.pack()

IronCondor = tk.Button(text="Iron Condor", command=iron_condor)
IronCondor.pack()

tk.mainloop()
