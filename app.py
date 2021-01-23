import altair as alt
import pandas as pd
import numpy as np
from datetime import date

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc

## read data
raw = pd.read_csv('tmdb_movies_data.csv', parse_dates=True)

## data processing
processed = raw[raw['revenue_adj']!=0]
processed = processed[processed['budget_adj']!=0]

## motify release date column
processed["release_date"] = pd.to_datetime(processed["release_date"], format="%m/%d/%Y")
processed['release_month'] = processed['release_date'].dt.month

## add profit column
processed['profit'] = processed['revenue_adj'] - processed['budget_adj']

## Split genre column
def explode(df, lst_cols, fill_value='', preserve_index=False):
    # make sure `lst_cols` is list-alike
    if (lst_cols is not None
        and len(lst_cols) > 0
        and not isinstance(lst_cols, (list, tuple, np.ndarray, pd.Series))):
        lst_cols = [lst_cols]
    # all columns except `lst_cols`
    idx_cols = df.columns.difference(lst_cols)
    # calculate lengths of lists
    lens = df[lst_cols[0]].str.len()
    # preserve original index values    
    idx = np.repeat(df.index.values, lens)
    # create "exploded" DF
    res = (pd.DataFrame({
                col:np.repeat(df[col].values, lens)
                for col in idx_cols},
                index=idx)
             .assign(**{col:np.concatenate(df.loc[lens>0, col].values)
                            for col in lst_cols}))
    # append those rows that have empty lists
    if (lens == 0).any():
        # at least one list in cells is empty
        res = (res.append(df.loc[lens==0, idx_cols], sort=False)
                  .fillna(fill_value))
    # revert the original index order
    res = res.sort_index()
    # reset index if requested
    if not preserve_index:        
        res = res.reset_index(drop=True)
    return res

processed = explode(processed.assign(genres=processed.genres.str.split('|')), 'genres')
## get genres list
genres_list = set(processed['genres'].str.split('|',expand=True).stack().values.tolist())

def plot_heatmap(year):
    plot_data = processed[processed['release_year']>=year]
    alt.data_transformers.disable_max_rows()
    chart = (alt.Chart(plot_data, title='Genres Popularity Comparison').mark_rect().encode(
        x=alt.X('vote_average', bin=alt.Bin(maxbins=40)),
        y='genres',
        color='count()',
        tooltip='count()'))
    return chart.to_html()

def plot_release(year, genre_type):
    plot_data = processed[processed['release_year']>=year]
    plot_data = plot_data[plot_data['genres']==genre_type]
    chart = (alt.Chart(plot_data, title='Plan Your Movie Release').mark_point().encode(
        x=alt.X('release_month'),
        y=alt.Y('profit'),
        tooltip='original_title'))
    return chart.to_html()


## Setup app and Layout/frontend
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    html.H1('Movie Production Planner'),
    dbc.Row([
        dbc.Col([
            dcc.Slider(
                id='yearslider', 
                value=2005, #show the year range on the first page load
                min=1960, 
                max=2015),
            dcc.Dropdown(
                id='genreslist',
                value='Action',  # REQUIRED to show the plot on the first page load
                options=[{'label': genre, 'value': genre} for genre in genres_list])],
                md=20, style={'width':'20%', 'border': '1px solid #d3d3d3', 'border-radius': '10px'}),
        dbc.Col(
            html.Iframe(
                id='genre_rate',
                srcDoc=plot_heatmap(year=2005),
                style={'border-width': '0','width': '100%', 'height': '450px'})),
        dbc.Col(
            html.Iframe(
                id='release_time',
                srcDoc=plot_release(year=2005, genre_type="Action"),
                style={'border-width': '0','width': '100%', 'height': '450px'})
        )])])

@app.callback(
    Output('genre_rate', 'srcDoc'),
    Output('release_time', 'children'),
    Input('yearslider', 'value'),
    Input('genreslist', 'value'))

def update_output(year, genre_type):
    return plot_heatmap(year), plot_release(year, genre_type)


if __name__ == '__main__':
    app.run_server(debug=True) 