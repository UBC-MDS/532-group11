import pandas as pd
import altair as alt
import numpy as np


def read_data():
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

    processed.to_csv(r"data/processed/processed_movie_data.csv")
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