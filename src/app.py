# Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output

# Core data science libraries
import altair as alt
import pandas as pd
import random

# Data loading functions
from data import read_data


app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server
data = read_data_2()


@app.callback(
    Output("heatmap", "srcDoc"),
    Input("genres", "value"),
    Input("years", "value"),
)
def plot_heatmap(genres, years):
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres in @genres"
    )
    alt.data_transformers.disable_max_rows()
    chart = (
        alt.Chart(filtered_data, title="Vote Average by Genre")
        .mark_rect()
        .encode(
            x=alt.X("vote_average", bin=alt.Bin(maxbins=40), title="Vote Average"),
            y=alt.Y("genres", title=""),
            color=alt.Color("count()", title="Count"),
            tooltip="count()",
        )
    ).properties(width=350, height=300)
    return chart.to_html()


@app.callback(
    Output("linechart", "srcDoc"),
    Input("genres", "value"),
    Input("years", "value"),
)
def plot_linechart(genres, years):
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres in @genres"
    )
    click = alt.selection_multi(fields=["genres"], bind="legend")
    chart = (
        alt.Chart(filtered_data, title="Mean Budget by Release Year")
        .mark_line(point=True)
        .encode(
            alt.X("release_year", title="Release Year"),
            alt.Y("mean(budget_adj)", title="Adjusted Mean Budget ($)"),
            tooltip=["release_year", "mean(budget_adj)"],
            color=alt.Color("genres", title="Genre"),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        )
        .add_selection(click)
    ).properties(width=280, height=350)
    return chart.to_html()


@app.callback(
    Output("actor_table", "children"),
    Input("genres_drill", "value"),
    Input("years", "value"),
    Input("budget", "value"),
)
def generate_actor_table(selected_genre, years, budget):
    print(budget)
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres == @selected_genre & budget_adj >= @budget[0] & budget_adj <= @budget[1]"
    )
    top_actors = pd.DataFrame(
        pd.Series(filtered_data["cast"].str.cat(sep="|").split("|")).value_counts(),
        columns=["count"],
    )
    top_actors.index.names = ["actor"]
    top_actors.reset_index(inplace=True)
    return (
        html.Thead(
            html.Tr(
                children=[
                    html.Th("Actor"),
                    html.Th("# of matching movies they starred in"),
                ]
            )
        ),
        html.Tbody(
            [
                html.Tr(
                    children=[html.Td(data[0]), html.Td(html.Br()), html.Td(data[1])]
                )
                for data in top_actors[["actor", "count"]][1:6].values
            ]
        ),
    )


@app.callback(
    Output("profit_year", "srcDoc"),
    Input("genres", "value"),
    Input("years", "value"),
)
def plot_profit_vs_year(genres, years):
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres in @genres"
    )
    click = alt.selection_multi(fields=["genres"], bind="legend")
    chart = (
        alt.Chart(filtered_data, title="Median Profit by Release Month")
        .mark_line(point=True)
        .encode(
            x=alt.X("month(release_date):O", title="Release Month"),
            y=alt.Y("median(profit):Q", title="Adjusted Profit ($)"),
            color=alt.Color("genres", title="Genre"),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        )
        .add_selection(click)
    ).properties(width=280, height=350)
    return chart.to_html()


def init_genres():
    return random.sample(list(data["genres"].unique()), 6)


@app.callback(
    Output("genres_drill", "options"),
    Output("genres_drill", "value"),
    Input("genres", "value"),
)
def update_genres(genres):
    options_list = []
    for item in genres:
        options_list.append({"label": item, "value": item})
    return (options_list, options_list[0]["label"])


app.layout = dbc.Container(
    [
        html.H1("Movie Production Planner"),
        html.Br(),
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Label(
                            [
                                "Years",
                            ]
                        ),
                        dcc.RangeSlider(
                            id="years",
                            count=1,
                            step=1,
                            min=data["release_year"].min(),
                            max=data["release_year"].max(),
                            value=[2000, 2016],
                            marks={1960: "1960", 2015: "2015"},
                            tooltip={"always_visible": False, "placement": "top"},
                        ),
                    ],
                    md=6,
                    style={
                        "border": "0px",
                        "border-radius": "10px",
                    },
                ),
                dbc.Col(
                    [
                        html.Label(
                            [
                                "Genres",
                                dcc.Dropdown(
                                    id="genres",
                                    options=[
                                        {"label": col, "value": col}
                                        for col in data["genres"].unique()
                                    ],
                                    value=init_genres(),
                                    multi=True,
                                ),
                            ]
                        ),
                    ],
                    md=6,
                    style={
                        "border": "0px",
                        "border-radius": "10px",
                    },
                ),
            ],
        ),
        html.Br(),
        ## Main Plots Area
        dbc.Row(
            [
                dbc.Col(
                    [
                        # First Row of Plots
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Br(),
                                        html.Label(
                                            "Identify most-liked genres",
                                            style={"font-size": 20},
                                        ),
                                        html.Iframe(
                                            id="heatmap",
                                            style={
                                                "border-width": "0",
                                                "width": "100%",
                                                "height": "100%",
                                            },
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Br(),
                                        html.Label(
                                            "Discover historical and recent budget trends",
                                            style={"font-size": 20},
                                        ),
                                        html.Iframe(
                                            id="linechart",
                                            style={
                                                "border-width": "0",
                                                "width": "100%",
                                                "height": "500px",
                                            },
                                        ),
                                    ]
                                ),
                            ]
                        ),
                        # Second Row of Plots
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        html.Br(),
                                        html.Label(
                                            "Find some potential actors",
                                            style={"font-size": 20},
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    html.Label(
                                                        [
                                                            "1. Drill down on a specific genre",
                                                            dcc.Dropdown(
                                                                id="genres_drill",
                                                                multi=False,
                                                                style={
                                                                    "width": "200px"
                                                                },
                                                            ),
                                                        ]
                                                    ),
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            [
                                                                "2. Narrow down your budget"
                                                            ]
                                                        ),
                                                        dcc.RangeSlider(
                                                            id="budget",
                                                            count=1,
                                                            step=1,
                                                            min=data[
                                                                "budget_adj"
                                                            ].min(),
                                                            max=data[
                                                                "budget_adj"
                                                            ].max(),
                                                            value=[0, 425000000],
                                                            marks={
                                                                0.99: "0",
                                                                425000000: "425,000,000",
                                                            },
                                                            tooltip={
                                                                "always_visible": False,
                                                                "placement": "top",
                                                            },
                                                        ),
                                                    ],
                                                    style={"width": "100px"},
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Label(
                                                            ["3. Select an actor!"]
                                                        )
                                                    ]
                                                )
                                            ]
                                        ),
                                        dbc.Row(
                                            [
                                                dbc.Col(
                                                    [
                                                        html.Table(id="actor_table"),
                                                        html.Br(),
                                                    ]
                                                )
                                            ]
                                        ),
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        html.Br(),
                                        html.Label(
                                            "Plan your release month",
                                            style={"font-size": 20},
                                        ),
                                        html.Iframe(
                                            id="profit_year",
                                            style={
                                                "border-width": "0",
                                                "width": "100%",
                                                "height": "450px",
                                            },
                                        ),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    md=12,
                    style={
                        "width": "100%",
                        "height": "100%",
                        "border": "1px solid #d3d3d3",
                        "border-radius": "10px",
                    },
                )
            ]
        ),
    ],
)


if __name__ == "__main__":
    app.run_server(debug=True)