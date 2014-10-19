'''
python marketsim.py 1000000 orders.csv values.csv
'''

import sys
import csv
import datetime as dt
import QSTK.qstkutil.qsdateutil as du
import QSTK.qstkutil.DataAccess as da
import pandas as pd


def getMarketData(startTime, endTime, ls_symbols):
    ldt_timestamps = du.getNYSEdays(startTime, endTime, dt.timedelta(hours=16))

    dataobj = da.DataAccess('Yahoo')
    ls_keys = ['open', 'high', 'low', 'close', 'volume', 'actual_close']
    ldf_data = dataobj.get_data(ldt_timestamps, ls_symbols, ls_keys)
    marketData = dict(zip(ls_keys, ldf_data))

    for s_key in ls_keys:
        marketData[s_key] = marketData[s_key].fillna(method='ffill')
        marketData[s_key] = marketData[s_key].fillna(method='bfill')
        marketData[s_key] = marketData[s_key].fillna(1.0)
    
    return marketData


def loadOrders(orderCsv):
    reader = csv.reader(open(orderCsv, 'rU'), delimiter=',')
    orders = []
    for row in reader:
        orders.append(row)
    return orders


def parseOrder(order):
    d = dt.datetime(int(order[0]), int(order[1]), int(order[2])) + dt.timedelta(hours=16) # normalise to marke data date index
    symbol = order[3]
    share = int(order[5]) if order[4] == 'Buy' else -int(order[5])
    return d, symbol, share


def getDateRangeAndSymbols(orders):
    dates = []
    symbols = []
    for row in orders:
        d, symbol, _ = parseOrder(row)
        dates.append(d)
        symbols.append(symbol)
    startDate = dates[0]
    endDate = dates[-1]
    symbols = list(set(symbols))
    return startDate, endDate, symbols


def getTradeMatrix(orders, dateIndex, symbols):
    tradeMatrix = pd.DataFrame(index=dateIndex, columns=symbols)
    tradeMatrix = tradeMatrix.fillna(0)
    for row in orders:
        d, symbol, share = parseOrder(row)
        tradeMatrix.loc[d, symbol] += share
    return tradeMatrix


def addCashValueToTradeMatrix(orders, closePrice, tradeMatrix):
    cashSeries = pd.Series(index=tradeMatrix.index)
    cashSeries = cashSeries.fillna(0)
    for row in orders:
        d, symbol, share = parseOrder(row)
        cp = closePrice.loc[d, symbol]
        # print(d, symbol, share, cp, share*cp)
        cashSeries.loc[d] += -1 * share * cp 
    tradeMatrix['_CASH'] = cashSeries
    return tradeMatrix


def getHoldingMatrix(tradeMatrix, initCash):
    tradeMatrix['_CASH'].ix[0] += initCash
    holdingMatrix = tradeMatrix.cumsum()
    return holdingMatrix


def getPortforlioValue(holdingMatrix, closePrice):
    closePrice['_CASH'] = 1.0
    portfolioValue = pd.Series(index=closePrice.index)
    for d in holdingMatrix.index:
        hold = holdingMatrix.loc[d, :]
        cp = closePrice.loc[d, :]
        portfolioValue.loc[d] = hold.dot(cp)
    return portfolioValue


def savePortfolioValue(portfolioValue, valueCsv):
    writer = csv.writer(open(valueCsv, 'wb'), delimiter=',')
    for d in portfolioValue.index[:-1]:
        row_to_enter = [d.year, d.month, d.day, int(portfolioValue.loc[d])]
        writer.writerow(row_to_enter)


def main():
    if len(sys.argv) == 4:
        initCash = int(sys.argv[1])
        orderCsv = sys.argv[2]
        valueCsv = sys.argv[3]
    else:
        initCash = 1000000
        orderCsv = 'orders/orders2.csv' 
        valueCsv = 'values.csv'
    print(initCash, orderCsv, valueCsv)

    orders = loadOrders(orderCsv)
    startDate, endDate, symbols = getDateRangeAndSymbols(orders)
    marketData = getMarketData(startDate, endDate+dt.timedelta(days=1), symbols)
    print('='*25, 'Adjusted close price')
    print(marketData['close'])
    tradeMatrix = getTradeMatrix(orders, marketData['close'].index, symbols)
    tradeMatrix = addCashValueToTradeMatrix(orders, marketData['close'], tradeMatrix)
    print('='*25, 'Trade Matrix')
    print(tradeMatrix)
    holdingMatrix = getHoldingMatrix(tradeMatrix, initCash)
    print('='*25, 'Holding Matrix')
    print(holdingMatrix)
    portfolioValue = getPortforlioValue(holdingMatrix, marketData['close'])
    print('='*25, 'Portfolio Value')
    print(portfolioValue)
    savePortfolioValue(portfolioValue, valueCsv)

    print(portfolioValue.loc[dt.datetime(2011, 7, 21)+dt.timedelta(hours=16)])


if __name__ == '__main__':
    main()
