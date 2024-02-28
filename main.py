import tkinter as tk
import requests
import os

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

authorizeUrl = "https://api.upstox.com/v2/login/authorization/dialog"

params = {
  'client_id': os.environ['CLIENT_ID'],
  'redirect_uri': os.environ['REDIRECT_URL'],
}


def authorize():
  response = requests.request("GET", authorizeUrl, params=params, data={})
  print(response.text)


def login():
  response = requests.post(url, headers=headers, data=data)
  print(response.status_code)
  print(response.json())


def call_credit_spread():
  print('call_credit_spread')


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
