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

STOCK_1 = os.getenv("1st_Stock")
STOCK_2 = os.getenv("2nd_Stock")
alphavantage_API_KEY = os.getenv("alphavantage_API_KEY")
custom_date = os.getenv("C_DATE")

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

    print(f"---------------- Basic Information: {symbol.upper()}","----------------")
    print("")
    print("Symbol:", info["Symbol"])
    print("Name:", info["Name"])
    print("Description:", info["Description"])
    print("Sector:",info["Sector"])
    print("Industry:",info["Industry"])
    print("Market Capitalization:", to_usd(float(info["MarketCapitalization"])/1000000000),"billion")
    print("PE Ratio: ",info["PERatio"])
    print("Earnings Per Share: ",to_usd(float(info["EPS"])))
    print("Diluted EPS: ",to_usd(float(info["DilutedEPSTTM"])))
    print("**************************************************************")


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
    


# ask the user to select an input date
def get_custom_date():
    if APP_ENV == "development":
        input_date = input("Please select a date (YYYY-MM-DD): ")
    else:
        input_date = custom_date
    return input_date
    

def get_custom_data(date):
    # pull data for stock 1
    csv_1_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol_1}&outputsize=full&apikey={alphavantage_API_KEY}&datatype=csv"
    df_1 = read_csv(csv_1_url)
    latest_day_1 = df_1["timestamp"].max()
    earliest_day_1 = df_1["timestamp"].min()

    for index, row in df_1.iterrows():
        if row["timestamp"] == latest_day_1:
            latest_price_1 = row["adjusted_close"]

    # pull data for stock 2
    csv_2_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol_2}&outputsize=full&apikey={alphavantage_API_KEY}&datatype=csv"
    df_2 = read_csv(csv_2_url)
    latest_day_2 = df_2["timestamp"].max()
    earliest_day_2 = df_2["timestamp"].min()

    for index, row in df_2.iterrows():
        if row["timestamp"] == latest_day_2:
            latest_price_2 = row["adjusted_close"]

    # pull stock price on the custom date
    # validate the custom date
    if date < max(earliest_day_1,earliest_day_2):
        print("Your input is invalid. Please enter a date that both stocks are listed.")
        exit()
    elif date > max(latest_day_1,latest_day_2):
        print("Your input is invalid. Please enter a historical date.")
        exit()
    else: # to get the adjusted closing price on the custom date for the two stocks and calculate the gain/loss
        for index, row in df_1.iterrows():
            if row["timestamp"] == date:
                stock_1_inputprice = row["adjusted_close"]
               
        for index, row in df_2.iterrows():
            if row["timestamp"] == date:
                stock_2_inputprice = row["adjusted_close"]
               
        today_value_1 = 1000/stock_1_inputprice*latest_price_1
        today_value_2 = 1000/stock_2_inputprice*latest_price_2
        custom_gain_1 = latest_price_1/stock_1_inputprice-1
        custom_gain_2 = latest_price_2/stock_2_inputprice-1

        if custom_gain_1 > custom_gain_2: 
            winner = symbol_1
            loser = symbol_2,
        else:
            winner = symbol_2
            loser = symbol_1

        print(f"Adjusted closing price of {symbol_1.upper()} on {date} is: ",to_usd(stock_1_inputprice))
        print(f"Adjusted closing price of {symbol_2.upper()} on {date} is: ",to_usd(stock_2_inputprice))
        print(f"If you invested $1,000 in {symbol_1.upper()} on {date}, your stock is worthing", to_usd(today_value_1),"today. Your accumulated gain/(loss) is",to_pct(custom_gain_1))
        print(f"If you invested $1,000 in {symbol_2.upper()} on {date}, your stcok is worthing", to_usd(today_value_2),"today. Your accumulated gain/(loss) is",to_pct(custom_gain_2))
        print(f"The winner is {winner.upper()}!")


   
print(f"GETTING THE DATA IN {APP_ENV.upper()} MODE...")

# part 1: get basic information
# capture inputs
symbol_1, symbol_2=select_stocks()
print("1st Stock: ", symbol_1.upper())
print("2nd Stock: ", symbol_2.upper())

# display results

stock_information(symbol=symbol_1)
stock_information(symbol=symbol_2)

# part 2: put custom date and compare
# capture input
input_date=get_custom_date()
print("Date selected: ", input_date)

# print out the results

get_custom_data(date=input_date)
