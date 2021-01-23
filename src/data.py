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


def read_data_2():
    ## read data
    raw = pd.read_csv("data/raw/tmdb_movies_data.csv", parse_dates=True)

    ## data processing
    processed = raw[raw["revenue_adj"] != 0]
    processed = processed[processed["budget_adj"] != 0]

    ## motify release date column
    processed["release_date"] = pd.to_datetime(
        processed["release_date"], format="%m/%d/%Y"
    )
    processed["release_month"] = processed["release_date"].dt.month

    ## add profit column
    processed["profit"] = processed["revenue_adj"] - processed["budget_adj"]

    processed = explode(
        processed.assign(genres=processed.genres.str.split("|")), "genres"
    )
    ## get genres list
    genres_list = set(
        processed["genres"].str.split("|", expand=True).stack().values.tolist()
    )

    return processed


## Split genre column
def explode(df, lst_cols, fill_value="", preserve_index=False):
    # make sure `lst_cols` is list-alike
    if (
        lst_cols is not None
        and len(lst_cols) > 0
        and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))
    ):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)
    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()
    # preserve original index values
    idx = np.repeat(df.index.values, lens)
    # create "exploded" DF
    res = pd.DataFrame(
        {col: np.repeat(df[col].values, lens) for col in idx_cols}, index=idx
    ).assign(**{col: np.concatenate(df.loc[lens > 0, col].values) for col in lst_cols})
    # append those rows that have empty lists
    if (lens == 0).any():
        # at least one list in cells is empty
        res = res.append(df.loc[lens == 0, idx_cols], sort=False).fillna(fill_value)
    # revert the original index order
    res = res.sort_index()
    # reset index if requested
    if not preserve_index:
        res = res.reset_index(drop=True)
    return res


if __name__ == "__main__":
    read_data()