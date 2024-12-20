import sys

sys.path.insert(1, "..")
import pandas as pd
import numpy as np
from content_based_recommender import ContentBasedRecommender

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

companies_df = companies_df[companies_df["IPO Year"] < 2014]

# USER WITH A RANDOM PORTFOLIO
test_portfolio = companies_df.sample(n=5, random_state=1)["Symbol"].to_list()
print("========================= INITIAL PORTFOLIO =================================")
print(test_portfolio)

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

existing_summarized_df = existing_summarized_df[
    existing_summarized_df["company"].isin(companies_df["Symbol"])
]

companies_to_recommend = (
    existing_summarized_df[~(existing_summarized_df["company"].isin(test_portfolio))]
    .head(15)[["company"]]["company"]
    .values
)

recommender = ContentBasedRecommender()
recommended_companies = recommender.recommend(
    target_user_portfolio=test_portfolio,
    companies_to_recommend=companies_to_recommend,
    number_of_recommendations=8,
)

recommendations = []
for company, _similarity in recommended_companies:
    recommendations.append(company)

print(
    "========================= FINAL PORTFOLIO WITH RECOMMENDATION ================================="
)
print(test_portfolio + recommendations)

random_stocks = (
    companies_df[~(companies_df["Symbol"].isin(test_portfolio))]
    .sample(n=8, random_state=5)["Symbol"]
    .to_list()
)
print(
    "========================= FINAL PORTFOLIO WITH RANDONMIZATION ================================="
)
print(test_portfolio + random_stocks)

# ========================= INITIAL PORTFOLIO =================================
# ['SNOA', 'AUTL', 'EMKR', 'RVPHW', 'UCTT', 'VNOM', 'TSCO', 'ILMN']
# ========================= FINAL PORTFOLIO WITH RECOMMENDATION =================================
# ['SNOA', 'AUTL', 'EMKR', 'RVPHW', 'UCTT', 'VNOM', 'TSCO', 'ILMN', 'AMKR', 'AVGO', 'AMAT', 'DLTR', 'CPRT', 'CASY', 'AMGN', 'AMZN']
# ========================= FINAL PORTFOLIO WITH RANDONMIZATION =================================
# ['SNOA', 'AUTL', 'EMKR', 'RVPHW', 'UCTT', 'VNOM', 'TSCO', 'ILMN', 'IFRX', 'LSEAW', 'VRDN', 'EYEN', 'TCPC', 'VRNT', 'TACT', 'WYNN']
