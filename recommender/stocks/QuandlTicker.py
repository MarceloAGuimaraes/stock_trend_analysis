'''
Ticker for the Quandl API.

Used mostly for historic data.
'''


import quandl
from .Ticker import Ticker, TickerResolution, TickerGranularity
from recommender import utils


class QuandlTicker(Ticker):
  '''Ticker implementation for the Quandl API.

  Note that Quandl does not provide real-time data and has a delay of at-least 1 day. It also provides rarely a resolution finer than daily.

  Args:
    key: `str` API key used for quandl access (if None try to load it through `utils.read_keys`)
  '''

  def __init__(self, key=None):
    # check if key is none
    if key is None:
      key = utils.read_keys()['quandl']
    # setup system
    self.__key = key
    # set the key to config
    quandl.ApiConfig.api_key = self.__key

  def _update_symbol(self, symbol):
    '''Updates the given symbol for the quandl API.'''
    # check if the symbol exists on the QUANDL
    # TODO: extent list
    for prefix in ["EOD", "CHRIS"]:
      symb = "{}/{}".format(prefix, symbol)
      # use try catch against 404 errors
      try:
        data = quandl.get(symb, rows=1)
      except:
        continue
      # final symbol
      return symb
    return symbol

  def price(self, symbol):
    '''Retrieves the current price of the given stock.

    Args:
      symbol: `str` of the symbol name

    Returns:
      `dict` that contains open, close, volume, high, low, timestamp
    '''
    # update the ticker symbol to relevant name
    symbol = self._update_symbol(symbol)

    # retrieve the relevant data
    try:
      data = quandl.get(symbol, rows=1)
    except:
      raise ValueError("The given stock symbol ({}) was not found in quandl".format(symbol))

    # extract current data
    return {'timestamp': utils.localize_datetime(data.index[0]),
            'open': data['Open'][0], 'close': data['Close'][0],
            'high': data['High'][0], 'low': data['Low'][0],
            'volume': data['Volume'][0]}

  def historic(self, symbol, start, end=None, resolution='daily'):
    '''Retrieves the historic prices from the quandl API.

    Args:
      symbol: `str` of the symbol name
      start: `datetime` or `long` of the starting point (`None` = from earliest)
      end: `datetime` or `long` of the ending point (`None` = up to current)
      resolution: `TickerResolution` or `str` on the resolution of the data. (strings can be `weekly`, `monthly`, `daily`,
        '<X>min', whereby X is replaced by a number)

    Returns:
      `pd.dataframe` with a `pd.DatetimeIndex` and columns `open`, `close`, `low`, `high`, `volume`.
    '''
    # update the ticker symbol to relevant name
    symbol = self._update_symbol(symbol)
    # safty: covnert input data
    start = utils.safe_datetime(start)
    end = utils.safe_datetime(end)

    # handle resolution
    if isinstance(resolution, str):
      resolution = TickerResolution.from_string(resolution)

    # TODO: check the relevant time frame & resolution
    data = quandl.get(symbol, start_date=utils.datetime.now(), end_date=utils.datetime.now())

    # TODO: update the pandas data
    if resolution.adjusted:
      pass
    else:
      pass

    # TODO: check if adjusted
    return data

    # TODO: use get_table function?
    # TODO: compnumber retrieval for stock symbol
