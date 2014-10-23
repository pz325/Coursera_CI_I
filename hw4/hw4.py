import copy
import csv
import numpy as np
# import pandas as pd
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da


def getData(startTime, endTime, stockList):
    ldt_timestamps = du.getNYSEdays(startTime, endTime, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(stockList)
    # ls_symbols.append('SPY')
    print(ls_symbols)

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    return ls_symbols, d_data


def eventAnalyser(ls_symbols, d_data, priceThreshold, tradingStrategy):
    ''' 
    Finding the event dataframe 
    Apply trading strategy

    @param tradingStrategy ('dateDelta', 'action', 'share')
    @param orders a list of trading record ('date', 'symbol', 'action', 'share')
    '''
    print('eventAnalyser')
    orders = []

    df_close = d_data['actual_close']
    # Creating an empty dataframe
    df_events = copy.deepcopy(df_close)
    df_events = df_events * np.NAN

    # Time stamps for the event range
    ldt_timestamps = df_close.index
    totalEvent = 0
    for s_sym in ls_symbols:
        for i in range(1, len(ldt_timestamps)):
            # Calculating the returns for this timestamp
            f_symprice_today = df_close[s_sym].ix[ldt_timestamps[i]]
            f_symprice_yest = df_close[s_sym].ix[ldt_timestamps[i - 1]]
            if f_symprice_yest >= priceThreshold and f_symprice_today < priceThreshold:
                # print('event found at ', ldt_timestamps[i])
                for s in tradingStrategy:
                    # print('strategy', s)
                    timestampIndex = i + s[0]
                    if timestampIndex >= len(ldt_timestamps): timestampIndex = len(ldt_timestamps) - 1 
                    action = s[1]
                    share = s[2]
                    d = ldt_timestamps[timestampIndex]
                    # print('trade:', d, s_sym, action, share)
                    orders.append((d, s_sym, action, share))
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
    startDate = dt.datetime(2008, 1, 1)
    endDate = dt.datetime(2009, 12, 31)
    stockList = 'sp5002012'
    ls_symbols, d_data = getData(startDate, endDate, stockList)

    priceThreshold = 5
    tradingStrategy = []
    tradingStrategy.append((0, 'Buy', 100))
    tradingStrategy.append((5, 'Sell', 100))
    orders, _ = eventAnalyser(ls_symbols, d_data, priceThreshold, tradingStrategy)
    print(orders)
    ordersCsv = '../hw3/hw4.csv'    
    saveOrders(orders, ordersCsv)


if __name__ == '__main__':
    main()