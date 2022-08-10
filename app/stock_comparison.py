# app/stock_comparison.py

import requests
import json
import os
import pandas
from getpass import getpass
from pandas import read_csv
from pprint import pprint
from dotenv import load_dotenv
from app import APP_ENV


# use professor code to format numbers and percentages
def to_usd(my_price):
    return f"${my_price:,.4f}" # dollar sign and 4 decimal places

def to_pct(my_number):
    return f"{(my_number * 100):.4f}%" # % and 4 decimal places

load_dotenv()

STOCK_1 = os.getenv("1st Stock Symbol")
STOCK_2 = os.getenv("2nd Stock Symbol")
alphavantage_API_KEY = os.getenv("alphavantage_API_KEY")

def select_stocks():
    if APP_ENV == "development":
        symbol_1 = input("Please input the 1st stcok symbol: ")
        symbol_2 = input("Please input the 2nd stcok symbol: ")
    else:
        symbol_1 = STOCK_1
        symbol_2 = STOCK_2
    return symbol_1, symbol_2


def stock_information(symbol):

    # fetch the data for the stock
    # print some basic information from json data
    # get time series daily adjusted price: cvs format, using "full" to get all historical data
    # using pandas to read csv
    # define the earliest and latest trade date
    overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={symbol}&apikey={alphavantage_API_KEY}"
    overview = requests.get(overview_url)
    info = overview.json()
    csv_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={alphavantage_API_KEY}&datatype=csv"
    df = read_csv(csv_url)
    latest_day = df["timestamp"].max()
    earliest_day = df["timestamp"].min()

    print(f"---------------- Basic Information:{symbol}","----------------")
    print("Symbol:", info["Symbol"])
    print("Name:", info["Name"])
    print("Description:", info["Description"])
    print("Sector:",info["Sector"])
    print("Industry:",info["Industry"])
    print("Market Capitalization:", to_usd(float(info["MarketCapitalization"])/1000000000),"billion")
    print("PE Ratio: ",info["PERatio"])
    print("Earnings Per Share: ",to_usd(float(info["EPS"])))
    print("Diluted EPS: ",to_usd(float(info["DilutedEPSTTM"])))
    print("---------------------------------------------------------")

    # loop through the dataframe to look up the adjusted closing price on the earliest and latest trade date

    for index, row in df.iterrows():
        if row["timestamp"] == earliest_day:
            earliest_price = row["adjusted_close"]
            print("Earliest trade day and adjusted closing price:",earliest_day, to_usd(earliest_price)),
        elif row["timestamp"] == latest_day:
            latest_price = row["adjusted_close"]
            print("Latest trade day and adjusted closing price:",latest_day, to_usd(latest_price))

    # calculate the inception accumulated gain/loss by holding the stock
    Accu_gain = latest_price/earliest_price-1
    print("Accumulated gain/loss since IPO: ",to_pct(Accu_gain))




   
print(f"GETTING THE DATA IN {APP_ENV.upper()} MODE...")

# capture inputs
symbol_1, symbol_2=select_stocks()
print("1st Stock:", symbol_1)
print("2nd Stock:", symbol_2)

# display results

stock_information(symbol=symbol_1)
stock_information(symbol=symbol_2)
