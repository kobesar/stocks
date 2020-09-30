import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
import datetime as dt
import requests
from mpl_toolkits.mplot3d import Axes3D
from bs4 import BeautifulSoup

plt.style.use('seaborn')


class stocks:
    global ticker_df
    global ticker

    def __init__(self, ticker, delta):
        delta_year = dt.date.today() - dt.timedelta(days=delta * 365)
        self.ticker = ticker
        self.ticker_df = pdr.DataReader(ticker, data_source='yahoo', start=delta_year,
                                        end=dt.date.today())

    def chart(self):
        fig, ax = plt.subplots(figsize=(30, 15))
        fig.suptitle('Close of ' + self.ticker)
        ax.plot(self.ticker_df['Volume'], color='lightsteelblue')
        ax.set_xlabel('Date')
        ax.set_ylim([0, 5000000000])
        ax.set_ylabel('Price($)')

        ax2 = ax.twinx()
        ax2.plot(self.ticker_df['Close'], color='slategray')
        ax2.set_ylabel('Volume')
        plt.show()

    def revenue(self):
        ticker_bs = yf.Ticker(self.ticker)
        print(ticker_bs.info['zip'])

    def options_chain(self, opttype):
        ticker = yf.Ticker(self.ticker)
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

        totals = [sum(calls_volume), sum(puts_volume)]

        plt.figure(figsize=(10, 10))
        plt.bar(['Calls', 'Puts'], totals, color='cadetblue', edgecolor='darkslategrey',
                width=0.5)
        plt.title(self.ticker + ' Calls vs Puts')
        plt.ylabel('Volume')
        plt.show()

        opt = {'Calls': dates_calls, 'Puts': dates_puts}

        if opttype == 'c' or 'p':
            fig = plt.figure(figsize=(15, 10))
            if opttype == 'c':
                opt = opt['Calls']
                fig.suptitle(self.ticker + 'calls')
            else:
                opt = opt['Puts']
                fig.suptitle(self.ticker + 'puts')
            index = 1

            for date in opt.keys():
                strikes = list(opt[date].keys())
                vols = list(opt[date].values())
                ax = fig.add_subplot(4, 3, index)
                ax.bar(strikes, vols, color='cadetblue', edgecolor='darkslategrey', width=0.3)
                ax.set_xlabel('Strikes')
                ax.set_ylabel('Volume')
                ax.set_title(date)
                index += 1
            plt.tight_layout()
            plt.show()
        else:
            return opt

    def iv_chart(self, date):
        if date not in yf.Ticker(self.ticker).options:
            raise Exception('Date not in option chain')
        else:
            calls = yf.Ticker(self.ticker).option_chain(date).calls
            puts = yf.Ticker(self.ticker).option_chain(date).puts

            call_str = calls['strike'].to_frame()
            call_iv = calls['impliedVolatility'].to_frame()
            calls_ = pd.DataFrame(call_str)
            calls_['iv'] = call_iv * 100

            put_str = puts['strike'].to_frame()
            put_iv = puts['impliedVolatility'].to_frame()
            puts_ = pd.DataFrame(put_str)
            puts_['iv'] = put_iv * 100

            print(calls_)

            fig, ax = plt.subplots(2, 1, figsize=(30, 15))
            fig.suptitle('Strike and IV of ' + self.ticker, fontsize=16)
            ax[0].plot(calls_['strike'], calls_['iv'], '--')
            ax[0].set_title('Calls')
            ax[1].plot(puts_['strike'], puts_['iv'], '--')
            ax[1].set_title('Puts')
            plt.show()

    def vol_oi(self):
        ticker = yf.Ticker(self.ticker)
        dates = ticker.options
        strikes_calls = []
        strikes_puts = []
        calls = {}
        puts = {}
        for date in dates:
            calls_ = ticker.option_chain(date).calls
            puts_ = ticker.option_chain(date).puts
            strike = calls_['strike']
            vol = calls_['volume']
            oi = calls_['openInterest']

            strikes_calls = strike
            vol_oi_list = []

            for i in range(len(strike)):
                vol_oi_list.append(divide(vol[i], oi[i]))

            calls[date] = vol_oi_list

            strike = puts_['strike']
            vol = puts_['volume']
            oi = puts_['openInterest']

            strikes_puts = strike
            vol_oi_list = []

            for i in range(len(strike)):
                vol_oi_list.append(divide(vol[i], oi[i]))

            puts[date] = vol_oi_list

        print(calls)

def divide(x, y):
    if x or y == 0:
        return 0
    else:
        return x / y


def sp_analysis():
    table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies', )[0]
    symbols = table['Symbol']
    sym_dic = {}
    print(symbols)
    # for sym in symbols:
    #     tickerdf = yf.Ticker(sym)
    #     print(sym)
    #     print(tickerdf.cashflow)
    #     sym_dic[sym] = [tickerdf.info['heldPercentInstitutions'], tickerdf.info['forwardPE']]
    # print(sym_dic)


if __name__ == "__main__":
    # stocks('NOK', 5).revenue()
    """heldPercentInstitutions & forwardPE"""
    # stocks('NOK',5).chart()
    stocks('SPY', 1).vol_oi()
