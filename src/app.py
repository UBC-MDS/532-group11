# Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table

# Core data science libraries
import altair as alt
import pandas as pd
import random

# Data loading functions
from data import read_data


app = dash.Dash(external_stylesheets=[dbc.themes.MINTY])

server = app.server
data = read_data()

alt.themes.enable("latimes")


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
    filtered_data.loc[:, "budget_adj"] = filtered_data.loc[:, "budget_adj"] / 1000000
    filtered_data.loc[:, "profit"] = filtered_data.loc[:, "profit"] / 1000000
    click = alt.selection_multi(fields=["genres"], bind="legend")
    chart = (
        alt.Chart(filtered_data).mark_line(point=True).add_selection(click)
    ).properties(width=600, height=350)

    return alt.hconcat(
        chart.encode(
            alt.X("release_year", title="Release Year", axis=alt.Axis(format="y")),
            alt.Y("mean(budget_adj)", title="Adjusted Mean Budget (in million $)"),
            tooltip=["release_year", "mean(budget_adj)"],
            color=alt.Color("genres", title="Genre"),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        ),
        chart.encode(
            x=alt.X("month(release_date):O", title="Release Month"),
            y=alt.Y("median(profit):Q", title="Adjusted Profit (in million $)"),
            color=alt.Color("genres", title="Genre"),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        ),
    ).to_html()


@app.callback(
    Output("actor_col", "children"),
    Input("genres_drill", "value"),
    Input("years", "value"),
    Input("budget", "value"),
)
def generate_dash_table(selected_genre, years, budget):
    filtered_data = data.query(
        "release_date >= @years[0] & release_date <= @years[1] & genres == @selected_genre & budget_adj >= @budget[0] & budget_adj <= @budget[1]"
    )
    top_actors = pd.DataFrame(
        pd.Series(filtered_data["cast"].str.cat(sep="|").split("|")).value_counts(),
        columns=["count"],
    )
    top_actors.index.names = ["actor"]
    top_actors.reset_index(inplace=True)
    table = dash_table.DataTable(
        id="actorDataTable",
        columns=[
            {
                "name": "Actor Name",
                "id": "actor",
                "selectable": True,
            },
            {
                "name": "Count",
                "id": "count",
                "selectable": True,
            },
        ],
        data=top_actors.to_dict("records"),
        page_size=5,
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
            "class": "table",
        },
        style_data_conditional=[
            {"if": {"row_index": "odd"}, "backgroundColor": "rgb(240, 240, 230)"}
        ],
        style_cell={"padding": "7px"},
    )
    return table


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
        html.H1(
            "Movie Production Planner",
            style={
                "backgroundColor": "#78c2ad",
                "padding": 20,
                "color": "white",
                "margin-top": 20,
                "margin-bottom": 20,
                "text-align": "left",
                "font-size": "48px",
                "border-radius": 3,
            },
        ),
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
                            className="slider_class",
                            id="years",
                            count=1,
                            step=1,
                            min=data["release_year"].min(),
                            max=data["release_year"].max(),
                            value=[2000, 2016],
                            marks={
                                1960: {
                                    "label": "1960",
                                },
                                2015: {"label": "2015"},
                            },
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
                                    value=[
                                        "Action",
                                        "Drama",
                                        "Adventure",
                                        "Family",
                                        "Animation",
                                    ],
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
                                            "Discover historical and recent budget trends",
                                            style={"font-size": 20},
                                        ),
                                        html.Iframe(
                                            id="linechart",
                                            style={
                                                "display": "block",
                                                "overflow": " hidden",
                                                "margin": "auto",
                                                "border-width": "0",
                                                "width": "1500px",
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
                                        dbc.Row([dbc.Col(id="actor_col")]),
                                    ]
                                ),
                            ]
                        ),
                    ],
                    md=12,
                    style={
                        "width": "100%",
                        "height": "100%",
                    },
                )
            ]
        ),
    ],
    fluid=True,
)


if __name__ == "__main__":
    app.run_server(debug=True)