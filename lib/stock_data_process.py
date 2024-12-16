# 1 - Get the list with all available stock's tickers  (Filter out those who have less than 5 years ??)
import sys

sys.path.insert(1, "..")
import pandas as pd
from datetime import date
from recommender.contrib.financialmodelingprep import statements as FMPStatements
import recommender.contrib.financialmodelingprep.indicators as Indicators
import time

currentYear = date.today().year

companies_df = (
    pd.read_csv(
        "../data/nasdaq_companies_metadata.csv",
        dtype={"Symbol": "string", "Name": "string", "IPO Year": "Int64"},
        usecols=["Symbol", "Name", "IPO Year"],
        low_memory=False,
        engine="c",
        na_values=["", " ", "NULL"],
        memory_map=True,
    )
    .dropna()
    .drop_duplicates(["Symbol"])
)

# Only companies with at least 5 years of IPO
companies_df = companies_df[companies_df["IPO Year"] <= (currentYear - 4)]

# 2 - For each one of them, get their statements for the last X years
dtype = {
    "company": "string",
    "net_income_last_five_years": "float32",
    "years_with_positive_net_income": "int64",
    "current_net_income": "float32",
    "ten_years_net_income_per_share_growth": "float32",
    "five_years_net_income_per_share_growth": "float32",
    "current_market_cap": "float32",
    "net_income_growth": "float32",
}

summary_columns = [
    "company",
    "current_net_income",
    "years_with_positive_net_income",
    "net_income_last_five_years",
    "ten_years_net_income_per_share_growth",
    "five_years_net_income_per_share_growth",
    "net_income_growth",
    "current_market_cap",
]

existing_summarized_df = pd.read_csv(
    "../data/nasdaq_companies_summarized_data.csv",
    dtype=dtype,
    usecols=summary_columns,
    low_memory=False,
    engine="c",
)

summarized_data = []

for company_ticker in companies_df["Symbol"]:
    data = existing_summarized_df.loc[
        existing_summarized_df["company"] == company_ticker
    ]
    try:
        if data.empty:
            time.sleep(2)
            key_metrics_df = Indicators.key_metrics(company_ticker)
            if key_metrics_df.empty == False:
                key_metrics_df["calendarYear"] = key_metrics_df["calendarYear"].astype(
                    "int64"
                )
                current_market_cap = key_metrics_df[
                    key_metrics_df["calendarYear"] == currentYear - 1
                ]["marketCap"]
                if current_market_cap.empty:
                    # This means there's not report for the current year
                    current_market_cap = 0.0
                else:
                    current_market_cap = current_market_cap.item()
            else:
                current_market_cap = 0.0

            financial_growth_df = FMPStatements.growth(company_ticker, period="annual")
            if financial_growth_df.empty == False:
                financial_growth_df["calendarYear"] = financial_growth_df[
                    "calendarYear"
                ].astype("int64")
                last_year_financial_growth = financial_growth_df[
                    financial_growth_df["calendarYear"] == currentYear - 1
                ]

                if last_year_financial_growth.empty == False:
                    net_income_growth = last_year_financial_growth[
                        "netIncomeGrowth"
                    ].item()
                    ten_years_net_income_per_share_growth = last_year_financial_growth[
                        "tenYNetIncomeGrowthPerShare"
                    ].item()
                    five_years_net_income_per_share_growth = last_year_financial_growth[
                        "fiveYNetIncomeGrowthPerShare"
                    ].item()
                else:
                    net_income_growth = 0.0
                    ten_years_net_income_per_share_growth = 0.0
                    five_years_net_income_per_share_growth = 0.0
            else:
                net_income_growth = 0.0
                ten_years_net_income_per_share_growth = 0.0
                five_years_net_income_per_share_growth = 0.0

            income_statement_df = FMPStatements.income(company_ticker, period="annual")
            if income_statement_df.empty == False:
                income_statement_df["calendarYear"] = income_statement_df[
                    "calendarYear"
                ].astype("int64")

                last_year_income_statement = income_statement_df[
                    income_statement_df["calendarYear"] == currentYear - 1
                ]

                if last_year_income_statement.empty:
                    current_net_income = 0.0
                else:
                    current_net_income = last_year_income_statement["netIncome"].item()

                net_income_last_five_years = (
                    income_statement_df[["netIncome"]].mean().item()
                )
                years_with_positive_net_income = len(
                    income_statement_df[income_statement_df["netIncome"] > 0].index
                )
            else:
                net_income_last_five_years = 0.0
                current_net_income = 0.0
                years_with_positive_net_income = 0.0
        else:
            current_net_income = data["current_net_income"].item()
            years_with_positive_net_income = data[
                "years_with_positive_net_income"
            ].item()
            net_income_last_five_years = data["net_income_last_five_years"].item()
            ten_years_net_income_per_share_growth = data[
                "ten_years_net_income_per_share_growth"
            ].item()
            five_years_net_income_per_share_growth = data[
                "five_years_net_income_per_share_growth"
            ].item()
            net_income_growth = data["net_income_growth"].item()
            current_market_cap = data["current_market_cap"].item()

        summarized_data.append(
            {
                "company": company_ticker,
                "current_net_income": current_net_income,
                "years_with_positive_net_income": years_with_positive_net_income,
                "net_income_last_five_years": net_income_last_five_years,
                "ten_years_net_income_per_share_growth": ten_years_net_income_per_share_growth,
                "five_years_net_income_per_share_growth": five_years_net_income_per_share_growth,
                "net_income_growth": net_income_growth,
                "current_market_cap": current_market_cap,
            }
        )
    except Exception as e:
        print(
            "=============================== ERRO ==================================="
        )
        print(e)
        break

summarized_df = pd.DataFrame(data=summarized_data, columns=summary_columns)
summarized_df = summarized_df.astype(dtype)
summarized_df.sort_values(
    [
        "net_income_last_five_years",
        "years_with_positive_net_income",
        "current_net_income",
        "ten_years_net_income_per_share_growth",
        "five_years_net_income_per_share_growth",
        "current_market_cap",
        "net_income_growth",
    ],
    ascending=False,
    inplace=True,
)
summarized_df.to_csv("../data/nasdaq_companies_summarized_data.csv")
# More than 40% is worrysome
# Sources:
# (https://www.investopedia.com/ask/answers/040715/what-are-some-strategies-companies-commonly-use-reduce-their-debt-capital-ratio.asp)
# company_debt_related_to_her_market_cap
