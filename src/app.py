# Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Core data science libraries
import altair as alt
import pandas as pd

# Data loading functions
from data import read_data
from data import read_data_2


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
data = read_data_2()


@app.callback(
    Output("profit_year", "srcDoc"),
    Input("genres", "value"),
    Input("years", "value"),
)
def plot_profit_vs_year(genres, years):
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres in @genres"
    )
    chart = (
        alt.Chart(filtered_data)
        .mark_line(opacity=0.5)
        .encode(
            x=alt.X("month(release_date):O"),
            y=alt.Y("median(profit):Q"),
            color="genres",
        )
    )
    return chart.to_html()


@app.callback(
    Output("actor_table", "children"), Input("genres", "value"), Input("years", "value")
)
def generate_actor_table(genres, years):
    # filtered_data = data.query(
    #     " budget_adj >= @b_q[0] & budget_adj <= @b_q[1] & genre in @g_q"
    # )
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres in @genres"
    )
    top_actors = pd.DataFrame(
        pd.Series(filtered_data["cast"].str.cat(sep="|").split("|")).value_counts(),
        columns=["count"],
    )
    top_actors.index.names = ["actor"]
    top_actors.reset_index(inplace=True)
    return (
        html.Thead(html.Tr(children=[html.Th("Actor"), html.Th("No. of Movies")])),
        html.Tbody(
            [
                html.Tr(children=[html.Td(data[0]), html.Td(data[1])])
                for data in top_actors[["actor", "count"]][1:6].values
            ]
        ),
    )


def plot_heatmap(year):
    plot_data = processed[processed["release_year"] >= year]
    alt.data_transformers.disable_max_rows()
    chart = (
        alt.Chart(plot_data, title="Genres Popularity Comparison")
        .mark_rect()
        .encode(
            x=alt.X("vote_average", bin=alt.Bin(maxbins=40)),
            y="genres",
            color="count()",
            tooltip="count()",
        )
    )
    return chart.to_html()


def plot_release(year, genre_type):
    plot_data = processed[processed["release_year"] >= year]
    plot_data = plot_data[plot_data["genres"] == genre_type]
    chart = (
        alt.Chart(plot_data, title="Plan Your Movie Release")
        .mark_point()
        .encode(x=alt.X("release_month"), y=alt.Y("profit"), tooltip="original_title")
    )
    return chart.to_html()


app.layout = html.Div(
    [
        html.Label(
            [
                "Genre Selector",
                dcc.Dropdown(
                    id="genres",
                    options=[
                        {"label": col, "value": col} for col in data["genres"].unique()
                    ],
                    value=["Action", "Drama", "Comedy"],
                    multi=True,
                ),
            ]
        ),
        html.Label(
            [
                "Year",
                dcc.RangeSlider(
                    id="years",
                    count=1,
                    min=1960,
                    max=2015,
                    step=1,
                    value=[2011, 2014],
                ),
            ]
        ),
        html.Iframe(
            id="profit_year",
            style={"border-width": "0", "width": "100%", "height": "400px"},
        ),
        html.Br(),
        html.Table(id="actor_table"),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)