# app/stock_comparison.py
# some packages/functions are not imported but not used. They are saved for furure-use,i.e. adding web_app.

import requests
import json
import os
import pandas
from getpass import getpass
from pandas import read_csv
from pprint import pprint
from dotenv import load_dotenv
from app import APP_ENV
from plotly.graph_objects import Figure, Scatter
import plotly
import plotly.graph_objects as go
from datetime import datetime
import sys


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
    
    # validate the stock symbol and exit the program if error.
    # reference: https://stackoverflow.com/questions/66652450/catch-systemexit-message-with-pytest
    # reference: https://medium.com/python-pandemonium/testing-sys-exit-with-pytest-10c6e5f7726f
    if len(info) == 0:
        sys.exit(f"{symbol.upper()} is not a valid stock symbol. Please re-enter.")
    
    csv_url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol={symbol}&outputsize=full&apikey={alphavantage_API_KEY}&datatype=csv"
    df = read_csv(csv_url)
    latest_day = df["timestamp"].max()
    earliest_day = df["timestamp"].min()

    print(f"---------------- Basic Information: {symbol.upper()}","----------------")
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
    print("")
    
# validate the input date format
# reference: https://stackoverflow.com/questions/16870663/how-do-i-validate-a-date-string-format-in-python   
def validate(date_text):
    try:
        if date_text != datetime.strptime(date_text, "%Y-%m-%d").strftime('%Y-%m-%d'):
            raise ValueError
        return True
    except ValueError:
        return False
    

# ask the user to select an input date
def get_custom_date():
    if APP_ENV == "development":
        input_date = input("Please select a date (YYYY-MM-DD): ")
    else:
        input_date = custom_date
    return input_date
    

def get_custom_data(input_date,symbol_1,symbol_2):
    
    # validate the date format
    if validate(input_date) == False:
        sys.exit("Your input date format is incorrect. Please use YYYY-MM-DD.")
       
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
    if input_date < max(earliest_day_1,earliest_day_2):
        sys.exit("Your input is invalid. Please enter a date that both stocks are listed.")
    elif input_date > max(latest_day_1,latest_day_2):
        sys.exit("Your input is invalid. Please enter a historical date.")
    else: # to get the adjusted closing price on the custom date for the two stocks and calculate the gain/loss
        for index, row in df_1.iterrows():
            if row["timestamp"] == input_date:
                stock_1_inputprice = row["adjusted_close"]
               
        for index, row in df_2.iterrows():
            if row["timestamp"] == input_date:
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

        print(f"Adjusted closing price of {symbol_1.upper()} on {input_date} is: ",to_usd(stock_1_inputprice))
        print(f"Adjusted closing price of {symbol_2.upper()} on {input_date} is: ",to_usd(stock_2_inputprice))
        print(f"If you invested $1,000 in {symbol_1.upper()} on {input_date}, your stock is worthing", to_usd(today_value_1),"today. Your holding period gain/(loss) is",to_pct(custom_gain_1))
        print(f"If you invested $1,000 in {symbol_2.upper()} on {input_date}, your stcok is worthing", to_usd(today_value_2),"today. Your holding period gain/(loss) is",to_pct(custom_gain_2))
        print(f"The winner is {winner.upper()}!")

def new_df():
    # get new_df for line chart
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
    
    # remove extra rows to get the same number of rows between the two stocks
    # use "copy" function to avoid SettingWithCopyWarning
    if earliest_day_1 < earliest_day_2:
        df_1 = df_1.loc[df_1.timestamp >= earliest_day_2]
        new_df_2 = df_2.copy()
        new_df_1 = df_1.copy()
    else:
        df_2 = df_2.loc[df_2.timestamp >= earliest_day_1]
        new_df_2 = df_2.copy()
        new_df_1 = df_1.copy()

    # add a column to both dataframes to calculate the holding gain/loss for each day
    new_df_1.loc[:, ('gain_loss_%')]=(latest_price_1/new_df_1["adjusted_close"]-1)*100
    new_df_2.loc[:, ('gain_loss_%')]=(latest_price_2/new_df_2["adjusted_close"]-1)*100

    line_1 = Scatter(x=new_df_1["timestamp"], y=new_df_1["gain_loss_%"], name=symbol_1)   
    line_2 = Scatter(x=new_df_2["timestamp"], y=new_df_2["gain_loss_%"], name=symbol_2)
    fig = Figure(data=[line_1,line_2]) 
    fig.update_layout(title=f"Holding Period Gain/Loss: {symbol_1.upper()} v.s. {symbol_2.upper()}",yaxis_ticksuffix = '%', yaxis_tickformat = ',.2f')
    
    chart = input("Print the performance chart? Y or N: ")
    if chart.upper() == "Y":
        fig.show()
    else:
        sys.exit("The program is ended.")
   

if __name__ == "__main__":

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

    get_custom_data(input_date, symbol_1, symbol_2)

    new_df()




