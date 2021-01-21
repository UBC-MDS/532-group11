import pandas as pd
import altair as alt
import numpy as np


def read_data():
    raw = pd.read_csv("data/raw/tmdb_movies_data.csv", parse_dates=True)
    columns_to_keep = [
        "popularity",
        "original_title",
        "cast",
        "director",
        "runtime",
        "genres",
        "production_companies",
        "release_date",
        "vote_count",
        "vote_average",
        "release_year",
        "budget_adj",
        "revenue_adj",
    ]

    # Only keep cols of interest
    processed = raw[columns_to_keep]

    # Get rid of na
    processed = raw.dropna(subset=set(raw.columns) - set(["production_companies"]))

    # Get rid of movies without revenue and budget data as that is useless for our purposes
    processed = processed.query("revenue_adj != 0 & budget_adj != 0")

    # Parse dates, Pd did not do it correctly
    processed["release_date"] = processed["release_date"].astype("datetime64")
    processed["year"] = processed["release_date"].astype("datetime64")

    # Create primary genre column
    processed["primary_genre"] = processed["genres"].str.split("|").str[0]

    # Create profit column
    processed["profit"] = processed["revenue_adj"] - processed["budget_adj"]

    return processed


if __name__ == "__main__":
    read_data()