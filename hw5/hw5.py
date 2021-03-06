import datetime as dt
import pandas as pd
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da

def getData(startTime, endTime, stockList):
    ldt_timestamps = du.getNYSEdays(startTime, endTime, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_symbols = dataobj.get_symbols_from_list(stockList)
    ls_symbols.append('SPY')
    print(ls_symbols)

    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        d_data[s_key] = d_data[s_key].fillna(method='ffill')
        d_data[s_key] = d_data[s_key].fillna(method='bfill')
        d_data[s_key] = d_data[s_key].fillna(1.0)
    
    return ls_symbols, d_data


def bollingerBand(price, lookbackPeriod):
    rolling_mean = pd.stats.moments.rolling_mean(price, lookbackPeriod)
    rolling_mean.columns = ['rolling_mean']
    rolling_std = pd.stats.moments.rolling_std(price, lookbackPeriod)
    rolling_std.columns = ['rolling_std']
    bollingerValue = (price.ix[:, 0] - rolling_mean.ix[:, 0]) / rolling_std.ix[:, 0]
    return bollingerValue

def main():
    startTime = dt.datetime(2010, 1, 1)
    endTime = dt.datetime(2010, 12, 31)
    symbol = ['MSFT']
    marketData = getMarketData(startTime, endTime, symbol)
    lookbackPeriod = 20
    bollingerValue = bollingerBand(marketData['actual_close'], lookbackPeriod)
    
    indexDate = dt.datetime(2010, 6, 14)+dt.timedelta(hours=16)
    print(bollingerValue.loc[indexDate])



if __name__ == '__main__':
    main()