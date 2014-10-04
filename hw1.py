# QSTK Imports
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.tsutil as tsu
import QSTK.qstkutil.DataAccess as da

# Third Party Imports
import datetime as dt
import numpy
import itertools


c_dataobj = da.DataAccess('Yahoo')
ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
NUM_TRADING_DAYS = 252

def simulate(startDate, endDate, symbols, allocations):
    dt_timeofday = dt.timedelta(hours=16)
    ldt_timestamps = du.getNYSEdays(startDate, endDate, dt_timeofday)
    ldf_data = c_dataobj.get_data(ldt_timestamps, symbols, ls_keys)
    d_data = dict(zip(ls_keys, ldf_data))
    df_rets = d_data['close'].copy()
    # Filling the data.
    df_rets = df_rets.fillna(method='ffill')
    df_rets = df_rets.fillna(method='bfill')
    df_rets = df_rets.fillna(1.0)

    price = df_rets.values
    price = price / price[0, :]  # normalisation
    port_value = numpy.sum(price * allocations, axis=1)  # get portforlio value
    port_ret = port_value.copy()
    tsu.returnize0(port_ret)  # daily return of portforlio value

    std = numpy.std(port_ret)
    avg = numpy.mean(port_ret)
    sharpeRatio = numpy.sqrt(NUM_TRADING_DAYS) * avg / std
    cum_rets = port_value[-1] / port_value[0]
    # cum_rets = numpy.cumprod(port_daily_rets + 1, axis=0)[-1]

    return std, avg, sharpeRatio, cum_rets


def optimise(startDate, endDate, symbols):
    maxShapeRatio = 0
    bestAllocation = []
    for allocations in itertools.product(numpy.arange(0.0, 1.1, 0.1), repeat=len(symbols)):
        if sum(allocations) != 1: continue
        _, _, sharpeRatio, _ = simulate(startDate, endDate, symbols, allocations)
        if sharpeRatio > maxShapeRatio:
            maxShapeRatio = sharpeRatio
            bestAllocation = allocations
    return maxShapeRatio, bestAllocation


def example1():
    startDate = dt.datetime(2011, 1, 1)
    endDate = dt.datetime(2011, 12, 31) 
    symbols = ["AAPL", "GLD", "GOOG", "XOM"]
    maxShapeRatio, bestAllocation = optimise(startDate, endDate, symbols)
    print('start date', startDate)
    print('end date', endDate)
    print('symbols', symbols)
    print('shape ratio', maxShapeRatio)
    print('optimal allocation', bestAllocation)

    # bestAllocation = [0.4, 0.4, 0.0, 0.2]
    std, avg, sharpeRatio, cum = simulate(startDate, endDate, symbols, bestAllocation)
    print('volatility', std)
    print('average', avg)
    print('cumulative', cum)


def example2():
    startDate = dt.datetime(2010, 1, 1)
    endDate = dt.datetime(2010, 12, 31) 
    symbols = ["AXP", "HPQ", "IBM", "HNZ"]
    maxShapeRatio, bestAllocation = optimise(startDate, endDate, symbols)
    print('start date', startDate)
    print('end date', endDate)
    print('symbols', symbols)
    print('shape ratio', maxShapeRatio)
    print('optimal allocation', bestAllocation)

    # bestAllocation = [0.0, 0.0, 0.0, 1.0]
    std, avg, sharpeRatio, cum = simulate(startDate, endDate, symbols, bestAllocation)
    print('volatility', std)
    print('average', avg)
    print('cumulative', cum)


def main():
    print('example1')
    example1()
    print('example2')
    example2()

    print('quiz')
    startDate = dt.datetime(2011, 1, 1)
    endDate = dt.datetime(2011, 12, 31)
    symbols = ['BRCM', 'ADBE', 'AMD', 'ADI']
    maxShapeRatio, bestAllocation = optimise(startDate, endDate, symbols)   
    print('best shape ratio:', maxShapeRatio)
    print('best allocations:', bestAllocation)


if __name__ == '__main__':
    main()
