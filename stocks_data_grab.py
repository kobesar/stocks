import yfinance as yf
import seaborn as sns
import math
import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import datetime as dt
import numpy as np
import pandas_datareader.data as pdr
from scipy import stats
import matplotlib.dates as mdates
import matplotlib.collections as collections
from fredapi import Fred
from pandas import DataFrame
from functools import reduce
from mpl_toolkits.mplot3d import Axes3D

delta = 1
fred = Fred(api_key='665dd852aaab13eab30b3dc4eb70fa02')
plt.style.use('seaborn')
yf.pdr_override()

def charts_basics(input):
    ticker = stock_info(input, delta)
    norm_chart(ticker, 'Close')
    vol_and_spread(ticker)

def symbol_lists(list):
    """Will return a list of the symbols given with their corresponding dfs."""
    result = []
    for symbol in list:
        result.append(stock_info(symbol, delta))
    return result

def sum(list):
    """Returns the sum of the numbers in a list"""
    sum = 0
    list = list[np.logical_not(np.isnan(list))]
    for num in list:
        sum += num
    return sum

def FRED_graph(symbols, graph):
    """Enter in the list of symbols and a boolean (to have the chart on or not)."""
    color = 'steelblue'

    FRED_symbols = []
    for sym in symbols:
        tempsym = fred.get_series(sym)
        tempsym.dropna(inplace=True)
        FRED_symbols.append(tempsym)
    symbols_con = pd.concat(FRED_symbols, axis=1, sort=False)
    index = 0
    for col in symbols_con.columns:
        symbols_con.rename(columns={col: symbols[index]}, inplace=True)
        index += 1
    index = 0
    if graph:
        for symbol in FRED_symbols:
            fig1, ax1 = plt.subplots(figsize=(30,15))
            ax1.plot(symbol, color=color)
            ax1.set_title(symbols[index])
            ax1.set_xlabel('Date')
            ax1.set_ylabel('$/%')
            fig1.show()
            index += 1

    return symbols_con

def ticker_to_yf(ticker):
    return yf.Ticker(ticker)

def stock_info(ticker):
    """Enter the ticker symbol and the time period (years) you want the data to be between."""
    today = dt.date.today()
    delta_year = dt.date.today() - dt.timedelta(days=delta * 365)

    return [pdr.get_data_yahoo(ticker, delta_year, today), ticker]

def options_vol(ticker, chart):
    """Enter the ticker  that you want the options volume of"""
    sym = ticker
    ticker = ticker_to_yf(ticker)
    dates = ticker.options
    dates_calls = {}
    dates_puts = {}

    for date in dates:
        opt = ticker.option_chain(date)
        opt_calls = opt.calls
        opt_puts = opt.puts
        calls_strikes = opt_calls['strike']
        calls_volume = opt_calls['volume']
        calls_dates_strike_vol = {}
        puts_strikes = opt_puts['strike']
        puts_volume = opt_puts['volume']
        puts_dates_strike_vol = {}

        for i in range(len(calls_strikes)):
            calls_dates_strike_vol[calls_strikes[i]] = calls_volume[i]

        for i in range(len(puts_strikes)):
            puts_dates_strike_vol[puts_strikes[i]] = puts_volume[i]

        dates_calls[date] = calls_dates_strike_vol
        dates_puts[date] = puts_dates_strike_vol

    totals = [sum(calls_volume),sum(puts_volume)]

    plt.figure(figsize=(10,10))
    plt.bar(['Calls', 'Puts'], totals, color='burlywood', edgecolor='darkslategrey', width=0.5)
    plt.title(sym + ' Calls vs Puts')
    plt.ylabel('Volume')
    plt.show()

    opt = {'Calls': dates_calls, 'Puts': dates_puts}

    if chart == 'c' or 'p':
        fig = plt.figure(figsize=(15,10))
        if chart == 'c':
            opt = opt['Calls']
            fig.suptitle(sym + 'calls')
        else:
            opt = opt['Puts']

            fig.suptitle(sym + 'puts')
        index = 1

        for date in opt.keys():
            strikes = list(opt[date].keys())
            vols = list(opt[date].values())
            ax = fig.add_subplot(4,3,index)
            ax.bar(strikes,vols,color='burlywood', edgecolor='darkslategrey',width=0.3)
            ax.set_xlabel('Strikes')
            ax.set_ylabel('Volume')
            ax.set_title(date)
            index += 1
        plt.tight_layout()
        plt.show()

    else:
        return opt

def vol_and_spread(ticker):
    """Enter the list that contains the ticker df and ticker name. Will output a chart of the
    spread of each day and a chart of the volume """
    color = 'steelblue'
    day_spread_vol = {}

    ticker_basic = stock_info(ticker)

    ticker_df = ticker_basic[0]
    ticker = ticker_basic[1]

    pchange = []
    previous_close = 0

    for row, col in ticker_df.iterrows():
        spread_day = col['High'] / col['Low'] * 100
        date = row.strftime('%m/%d/%Y')
        day_spread_vol[date] = [spread_day, col['Volume']]
        if previous_close == 0:
            pchange.append(0)
        else:
            pchange.append((col['Close']-previous_close)/previous_close * 100)
        previous_close = col['Close']

    pchange = DataFrame(pchange)
    pchange_pos = pchange <= 0
    pchange_neg = pchange < 0

    spread, vol = zip(*day_spread_vol.values())
    x = ticker_df.index.strftime('%m/%d/%Y').tolist()
    new_x = [dt.datetime.strptime(d, '%m/%d/%Y').date() for d in x]

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m/%d/%Y'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator())
    plt.gcf().autofmt_xdate()

    fig, (ax1,ax2,ax3) = plt.subplots(3, sharex=True, figsize=(30,15))
    fig.suptitle(ticker, fontsize=15)
    ax1.plot(new_x, spread, color=color)
    ax1.set_ylabel('Spread %')
    ax2.plot(new_x, pchange, color=color)
    ax2.set_ylabel('% change')
    ax3.bar(new_x, vol, color=color)
    ax3.set_ylabel('Volume')
    plt.yticks(fontsize=15)
    # collection = collections.BrokenBarHCollection.span_where(
    #     new_x, ymin=0, ymax=max(pchange_pos), where=pchange_pos, facecolor='green', alpha=0.5)
    # ax2.add_collection(collection)
    #
    # collection = collections.BrokenBarHCollection.span_where(
    #     new_x, ymax=0, where=min(pchange_neg), facecolor='red', alpha=0.5)
    # ax2.add_collection(collection)
    fig.show()

def norm_chart(ticker, type):
    ticker_basic = stock_info(ticker)
    ticker_df = ticker_basic[0]
    ticker = ticker_basic[1]

    plt.figure(figsize=(30,15))
    plt.title(ticker + '(' + type + ')')
    plt.plot(ticker_df[type], color='steelblue')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()

if __name__ == "__main__":
    # fig = plt.figure()
    # ax1 = fig.add_subplot(111, projection='3d')
    #
    # xpos = [1,2,3,4,5,6,7,8,9,10]
    # ypos = [3,2,5,5,7,2,9,5,3,2]
    # zpos = [0,0,0,0,0,0,0,0,0,0]
    #
    # dx = np.ones(10)
    # dy = np.ones(10)
    # dz = [1,2,3,4,5,6,7,8,9,10]
    #
    # ax1.bar3d(xpos, ypos, zpos, dx, dy, dz, color='#00ceaa')
    # ax1.set_xlabel('x')
    # ax1.set_ylabel('y')
    # ax1.set_zlabel('z')
    # plt.show()
    options_vol('NOK','c')
