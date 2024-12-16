import argparse

parser = argparse.ArgumentParser("Content-based recommender")
parser.add_argument(
    "--tickers",
    nargs="*",
    type=str,
    help="User's portfolio company tickers",
    default=[],
)
args = parser.parse_args()
import sys

sys.path.insert(1, "..")
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import QuantileTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.compose import ColumnTransformer


class ContentBasedRecommender:
    def __init__(self):
        self.companies_df = (
            pd.read_csv(
                "../data/nasdaq_companies_metadata.csv",
                dtype={
                    "Symbol": "string",
                    "Name": "string",
                    "IPO Year": "string",
                    "Market Cap": "float32",
                    "Country": "string",
                    "Sector": "string",
                    "Industry": "string",
                },
                usecols=[
                    "Symbol",
                    "Name",
                    "IPO Year",
                    "Market Cap",
                    "Country",
                    "Sector",
                    "Industry",
                ],
                low_memory=False,
                engine="c",
                na_values=["", " ", "NULL"],
                memory_map=True,
            )
            .dropna()
            .drop_duplicates(["Symbol"])
        )
        self.companies_df = self.companies_df.reset_index(drop=True)
        ct = ColumnTransformer(
            [
                ("Country", TfidfVectorizer(stop_words="english"), "Country"),
                ("Sector", TfidfVectorizer(stop_words="english"), "Sector"),
                ("Industry", TfidfVectorizer(stop_words="english"), "Industry"),
                (
                    "IPO Year",
                    QuantileTransformer(n_quantiles=3),
                    ["IPO Year"],
                ),
                (
                    "Market Cap",
                    QuantileTransformer(n_quantiles=10),
                    ["Market Cap"],
                ),
            ],
        )
        tfidf_matrix = ct.fit_transform(
            self.companies_df[
                ["Country", "Sector", "Industry", "IPO Year", "Market Cap"]
            ]
        )
        tfidf_matrix = tfidf_matrix.astype(np.float32)
        self.similarities = cosine_similarity(tfidf_matrix)

    def recommend(
        self,
        target_user_portfolio=[],
        companies_to_recommend=[],
        number_of_recommendations=5,
    ):
        target_user_rated_companies_idx = self.companies_df[
            self.companies_df["Symbol"].isin(target_user_portfolio)
        ].index
        recommendations = []

        # If target user portfolio is empty, this is probably a cold-start scenario
        if len(target_user_rated_companies_idx) == 0:
            for company_to_recommend in companies_to_recommend[:5]:
                recommendations.append(
                    {"company": company_to_recommend, "similarity": 1.0}
                )
        else:
            # If no specific list of movies is passed, try to predict for all movies that user didn't rate
            if len(companies_to_recommend) == 0:
                companies_to_recommend = self.companies_df.index.difference(
                    target_user_rated_companies_idx
                )
            else:
                companies_to_recommend = self.companies_df[
                    self.companies_df["Symbol"].isin(companies_to_recommend)
                ].index

            for company_idx in target_user_rated_companies_idx:
                company_similarities = self.similarities[company_idx]
                for company_to_recommend_idx in companies_to_recommend:
                    company_ticker = self.companies_df.loc[company_to_recommend_idx][
                        "Symbol"
                    ]
                    similarity = company_similarities[company_to_recommend_idx]
                    recommendations.append(
                        {"company": company_ticker, "similarity": similarity}
                    )

        return sorted(
            recommendations,
            key=lambda x: (x["similarity"], x["company"]),
            reverse=True,
        )[:number_of_recommendations]


user_tickers = args.tickers

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

# Selecting the top 30 companies that the user does not have in his portfolio
companies_to_recommend = (
    existing_summarized_df[~(existing_summarized_df["company"].isin(user_tickers))]
    .head(15)[["company"]]["company"]
    .values
)

recommender = ContentBasedRecommender()
recommended_companies = recommender.recommend(
    target_user_portfolio=user_tickers,
    companies_to_recommend=companies_to_recommend,
    number_of_recommendations=5,
)

print("AÇÕES RECOMENDADAS")
for i in recommended_companies:
    print(i["company"])