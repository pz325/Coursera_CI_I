import copy
import numpy as np
import csv

import datetime as dt
import pandas as pd
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

def getData(startTime, endTime, stockList):
    timestamps = du.getNYSEdays(startTime, endTime, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    symbols = dataobj.get_symbols_from_list(stockList)
    symbols.append('SPY')
    print(symbols)

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(timestamps, symbols, ls_keys)
    marketData = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        marketData[s_key] = marketData[s_key].fillna(method='ffill')
        marketData[s_key] = marketData[s_key].fillna(method='bfill')
        marketData[s_key] = marketData[s_key].fillna(1.0)
    
    return symbols, marketData

def bollingerBand(marketData, lookbackPeriod):
    price = marketData['close']
    rolling_mean = pd.stats.moments.rolling_mean(price, lookbackPeriod)
    rolling_std = pd.stats.moments.rolling_std(price, lookbackPeriod)
    bollingerValue = (price - rolling_mean) / rolling_std
    return bollingerValue

def eventAnalyser(symbols, bollingerValue, lookbackPeriod, t1, t2, t3, tradingStrategy):
    ''' 
    Finding the event dataframe 
    Apply trading strategy
    @param t1 threshold for bollinger value for the equity today
    @param t2 threshold for bollinger value for the equity yesterday
    @param t3 threshold for bollinger value for SPY today

    @param tradingStrategy ('dateDelta', 'action', 'share')
    @param orders a list of trading record ('date', 'symbol', 'action', 'share')
    '''
    print('eventAnalyser')
    orders = []

    # Creating an empty dataframe
    df_events = copy.deepcopy(bollingerValue)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    timestamps = bollingerValue.index
    totalEvent = 0
    for sym in symbols:
        for i in range(lookbackPeriod, len(timestamps)):
            bollingerToday = bollingerValue[sym].ix[timestamps[i]]
            bollingerYesterday = bollingerValue[sym].ix[timestamps[i-1]]
            bollingerSPYToday = bollingerValue['SPY'].ix[timestamps[i]]
            if bollingerToday <= t1 and bollingerYesterday >= t2 and bollingerSPYToday >= t3:   
                # print('event found at ', timestamps[i])
                for s in tradingStrategy:
                    # print('strategy', s)
                    timestampIndex = i + s[0]
                    if timestampIndex >= len(timestamps): timestampIndex = len(timestamps) - 1 
                    action = s[1]
                    share = s[2]
                    d = timestamps[timestampIndex]
                    # print('trade:', d, sym, action, share)
                    orders.append((d, sym, action, share))
                totalEvent += 1
    #sort orders
    orders.sort(key=lambda tup: tup[0])
    return orders, totalEvent

def saveOrders(orders, ordersCsv):
    writer = csv.writer(open(ordersCsv, 'wb'), delimiter=',')
    for o in orders:
        d = o[0]
        symbol = o[1]
        action = o[2]
        share = o[3]
        row_to_enter = [d.year, d.month, d.day, symbol, action, share]
        writer.writerow(row_to_enter)


def main():
    startTime = dt.datetime(2008, 1, 1)
    endTime = dt.datetime(2009, 12, 31)
    lookbackPeriod = 20
    symbolList = 'SP5002012'
    t1, t2, t3 = -2.0, -2.0, 1.4
    tradingStrategy = []
    tradingStrategy.append((0, 'Buy', 100))
    tradingStrategy.append((5, 'Sell', 100))

    symbols, marketData = getData(startTime, endTime, symbolList)
    bollingerValue = bollingerBand(marketData, lookbackPeriod)
    orders, _ = eventAnalyser(symbols, bollingerValue, lookbackPeriod, t1, t2, t3, tradingStrategy)

    print(orders)
    ordersCsv = '../hw3/hw7.csv'    
    saveOrders(orders, ordersCsv)


if __name__ == '__main__':
    main()
