import itertools
import pandas as pd
from . import utils
from datetime import date


def financial_ratio(symbol):
    """Retrieves the financial ratio for the given symbol

    Args:
      symbol (str): Stock Market symbol for the relevant company

    Returns:
      Dict of Pandas DataFrame with the relevant information
    """
    url = utils.build_url("financial-ratios", symbol)
    data = utils.fetch(url)

    # convert all items
    ratios = data["ratios"]
    items = {}
    dates = []
    for rat in ratios:
        if "date" in rat:
            dates.append(rat.pop("date"))
        else:
            dates.append(date(date.today().year - 1, 12, 31).strftime("%Y/%m/%d"))

        for key in rat:
            if key in items:
                items[key].append(rat[key])
            else:
                items[key] = [rat[key]]

    for key in items:
        items[key] = pd.DataFrame(items[key]).assign(date=dates).set_index("date")

    return items


def enterprise_value(symbol, period="annual"):
    """Retrieves the enterprise value for the given symbol.

    Args:
      symbol (str): Stock Market symbol for the relevant company
      period (str): Interval for the market data (options: 'annual', 'quarter')

    Returns:
      DataFrame with the relevant enterprise values
    """
    meta = {}
    if period == "quarter":
        meta["period"] = period
    url = utils.build_url("enterprise-value", symbol, meta)
    data = utils.fetch(url)

    return pd.DataFrame(data["enterpriseValue"])


def rating(symbol):
    """Retrieves the rating for the given company.

    Args:
      symbol (str): Symbol for COmpany to retrieve rating for

    Returns:
      rating (dict): Dictionary that contains the rating
      details (DataFrame): Dataframe with the details for the individual ratings
    """
    url = utils.build_url("company/rating", symbol)
    data = utils.fetch(url)

    return data["rating"], pd.DataFrame(data["ratingDetails"]).transpose()


def key_metrics(symbol, period="annual", limit=40):
    """Retrieves the key metrics for the given company.

    Args:
      symbol (str): Stock Market symbol for the relevant company
      period (str): Interval for the market data (options: 'annual', 'quarter')

    Returns:
      DataFrame
    """
    meta = { "period": period, "limit": limit }
    url = utils.build_url("key-metrics", symbol, meta=meta)
    data = utils.fetch(url)

    items = {}
    dates = []
    for rat in data:
        # This if is only necessary because of a bug in financialprep, they don't send date for the last year report.
        if "date" in rat:
            dates.append(rat.pop("date"))
        else:
            dates.append(date(date.today().year - 1, 12, 31).strftime("%Y/%m/%d"))
        for key in rat:
            if key in items:
                items[key].append(rat[key])
            else:
                items[key] = [rat[key]]

    return pd.DataFrame(items).assign(date=dates)
