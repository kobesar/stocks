import pandas as pd
from pandas_datareader import data as pdr
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import date

def option_chain_by_ticker(ticker, type, expdate):
    ticker = yf.Ticker(ticker)
    if type == 'calls':
        return ticker.option_chain(expdate).calls
    if type == 'puts':
        return ticker.option_chain(expdate).puts
    else:
        print("Option type not entered right.")


def bullish(tickers_dict):
    list = []
    for ticker in tickers_dict:
        if tickers_dict.get(ticker) > 2.0:
            list.append(ticker)
    return list

def last_year_date(today):
    last_year = ''
    for i in range(len(today)):
        if today[3] == '0':
            if i == 2:
                last_year += str(int(today[2]) - 1)
            if i == 3:
                last_year += '9'
            if i != 2 and i != 3:
                last_year += today[i]
        else:
            #print('ths somehow ran')
            if i == 3:
                last_year += str(today[i - 1] - 1)
            else:
                last_year += today[i]
    return last_year

def ticker_info(tick):
    yf.pdr_override()

    today = str(date.today())
    last_year = last_year_date(today)
    data = pdr.get_data_yahoo(tick, start=last_year, end=today)
    totPriceVol = 0
    totVol = 0

    for i,j in data.iterrows():
        totPriceVol += j[3]*j[4]
        totVol += j[4]

    VWAP = totPriceVol / totVol

    return VWAP


def CP(s):
    if s == 'Call':
        return 1.1
    else:
        return 0.9

data = pd.read_csv('USO1.csv', usecols=['Symbol', 'Type', 'Vol/OI'])

symbols_freq = {}
symbols_CP_ratio = {}
symbols_info = {}

for i, j in data.iterrows():
    ticker = j[0]
    op = j[1]
    if ticker in symbols_freq:
        symbols_freq[ticker] += 1
        symbols_CP_ratio[ticker] *= CP(op)
    else:
        symbols_freq[ticker] = 1
        symbols_CP_ratio[ticker] = 1

# list = sorted(symbols_CP_ratio.items(), key=lambda item: item[1])

# bullish_list = bullish(symbols_CP_ratio)
#
# print(bullish_list)
#
# bullish_VWAP = {}
#
# for ticker in bullish_list:
#     bullish_VWAP[ticker] = ticker_info(ticker)
#
# print(bullish_VWAP)
#
# most_active_list = {}
#
# for ticker in symbols_freq:
#     if symbols_freq.get(ticker) >= 20:
#         most_active_list[ticker] = symbols_freq.get(ticker)
#
# print(most_active_list)
#
# print(symbols_CP_ratio.get('TSLA'))
# print(symbols_CP_ratio)

# print(sorted(symbols_CP_ratio.items(), key=lambda item: item[1]))
#
# print(symbols_freq)
#
# symbols_freq.popitem()
#
# print(symbols_freq)
#
# print(sorted(symbols_freq.items(), key=lambda item: item[1]))
#
# plt.bar(symbols_CP_ratio.keys(), symbols_CP_ratio.values())
# plt.show()

tsla_option_chain = option_chain_by_ticker('TSLA','calls','2020-05-14')

for col in tsla_option_chain.columns:
    print(col,end=", ", flush=True)
