'''
python analyze.py values.csv \$SPX 
'''
import sys
import csv
import copy
import pandas as pd
import numpy as np
import math
import copy
import QSTK.qstkutil.qsdateutil as du
import datetime as dt
import QSTK.qstkutil.DataAccess as da
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkstudy.EventProfiler as ep

NUM_TRADING_DAYS = 252

def loadValues(valuesCsv):
    reader = csv.reader(open(valuesCsv, 'rU'), delimiter=',')
    values = []
    for row in reader:
        values.append(row)
    return values

def parseValue(value):
    d = dt.datetime(int(value[0]), int(value[1]), int(value[2])) + dt.timedelta(hours=16)
    v = float(value[3])
    return d, v

def parseValues(values):
    portfolioValues = pd.Series()
    for row in values:
        d, v = parseValue(row)
        portfolioValues.set_value(d, v)
    return portfolioValues

def analyse(portfolioValues):
    portfolioValues = portfolioValues / portfolioValues[0]  # normalisation
    portforlioRet = copy.copy(portfolioValues)
    tsu.returnize0(portforlioRet)  # daily return of portforlio value
    std = np.std(portforlioRet)
    avg = np.mean(portforlioRet)
    sharpeRatio = np.sqrt(NUM_TRADING_DAYS) * avg / std
    cum_rets = portfolioValues[-1] / portfolioValues[0]
    # print(portfolioValues)
    return std, avg, sharpeRatio, cum_rets

def printResult(portfolioValues, std, avg, sharpeRatio, cum_rets):
    print('Date Range: {s} to {e}'.format(s=portfolioValues.index[0], e=portfolioValues.index[-1]))
    print('Sharpe Ratio: {s}'.format(s=sharpeRatio))
    print('Total Return: {r}'.format(r=cum_rets))
    print('Standard Deviation: {std}'.format(std=std))
    print('Average Daily Return: {avg}'.format(avg=avg))

def loadBenchmarkValues(benchmarkSymbol, dateRange):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(dateRange[0], dateRange[-1], dt_timeofday)
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    c_dataobj = da.DataAccess('Yahoo')
    ldf_data = c_dataobj.get_data(ldt_timestamps, [benchmarkSymbol], ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)
    return df_rets

def main():
    if len(sys.argv) == 3:
        valuesCsv = sys.argv[1]
        benchmarkSymbol = sys.argv[2]
    else:
        valuesCsv = 'values.csv' 
        benchmarkSymbol = '$SPX'
    print(valuesCsv, benchmarkSymbol)

    values = loadValues(valuesCsv)
    portfolioValues = parseValues(values)
    # print(portfolioValues)
    std, avg, sharpeRatio, cum_rets = analyse(portfolioValues.values)
    print('='*25, 'portforlio')
    printResult(portfolioValues, std, avg, sharpeRatio, cum_rets)

    benchmarkValues = loadBenchmarkValues(benchmarkSymbol, portfolioValues.index)
    # print(benchmarkValues)
    std, avg, sharpeRatio, cum_rets = analyse(benchmarkValues[benchmarkSymbol].values)
    print('='*25, 'benchmark')
    printResult(benchmarkValues, std, avg, sharpeRatio, cum_rets)


if __name__ == '__main__':
    main()