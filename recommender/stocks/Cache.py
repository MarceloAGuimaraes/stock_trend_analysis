'''Defines a cache function that loads data from disk.'''

import os
import glob
import pandas as pd
from .AlphaVantageTicker import AlphaVantageTicker

class Cache():
  '''Cache Function that stores stock and statement data on disk and loads it if required.

  Args:
    cache_folder (str): Folder to store the cache data into
  '''
  def __init__(self, cache_folder='../data'):
    self.path = cache_folder

  def list_data(self, type='stock'):
    '''Generates a list of available symbols for the given data type in cache.

    Args:
      type (str): type of data to retrieve (options: 'stock', 'etf', 'statement')
    '''
    # safty check
    if type not in ['stock', 'etf', 'statement']:
      raise ValueError("Given type is not recognized ({})".format(type))

    # set folder
    fldr = 'Stocks' if type == 'stock' else 'ETFs'
    path = os.path.join(self.path, fldr, '*.txt')
    # list all fiels in direcotry
    files = glob.glob(path)
    names = pd.Series(files).apply(lambda f: os.path.basename(f).split('.')[0])

    # create dict for search
    return dict(zip(names, files))

  def get_data(self, symbols, ticker=None, statement=None):
    '''Loads the relevant company data either from the Cache using the APIs.

    Args:
      symbols (list): List of symbols to load
      ticker (Ticker): Instance of a ticker to load data through (if None create AlphaVantage)
      statement (Statement): Instance of the statement to load data through (if None create FMP)

    Returns:
      DataFrame with the combined data for all given stocks.
    '''
    pass

  def load_stock_data(self, symbols, stocks=None, ticker=None, cache=True):
    '''Loads a dataframe with the given stock data.

    Args:
        symbols (list): List of symbol names to load
        stocks (dict): Stock name dictionary (if None, load with default vals)
        cache (bool): Defines if not found data that is loaded from API should be cached for later use (default=True)

    Returns:
        DataFrame in default stock format with additional symbol column
    '''
    # generate ticker data
    if stocks is None: stocks = self.list_data()
    if ticker is None: ticker = AlphaVantageTicker()

    # process data
    df_stocks = []
    for symbol in symbols:
        # load stock data
        if symbol in stocks:
            try:
                df_stock = pd.read_csv(stocks[symbol])
            except:
                continue
        else:
            try:
                df_stock = ticker.historic(symbol, start=None, resolution='daily').reset_index()
                # store it as filw
                df_stock.to_csv(os.path.join(self.path, 'Stocks', '{}.txt'.format(symbol)))
            except:
                print('Could not load {}'.format(symbol))
                continue

        # check if empty
        if df_stock is None or df_stock.empty == True:
            continue

        # post process data
        df_stock['symbol'] = symbol
        df_stock.columns = [col.lower() for col in df_stock.columns]
        df_stocks.append(df_stock)

    # combine and return
    return pd.concat(df_stocks, axis=0)