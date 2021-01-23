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
    ).properties(width=280, height=300)
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
        alt.Chart(filtered_data, title="Mean budget by Release Year")
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
        alt.Chart(filtered_data, title="Median Profit by Release Month")
        .mark_line(point=True)
        .encode(
            x=alt.X("month(release_date):O", title="Release Month"),
            y=alt.Y("median(profit):Q", title="Adjusted Profit ($)"),
            color=alt.Color("genres", title="Genre"),
        )
    ).properties(width=280, height=350)
    return chart.to_html()


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
                            value=[2000, 2010],
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
                                    value=data["genres"].unique(),
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
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Iframe(
                                        id="heatmap",
                                        style={
                                            "border-width": "0",
                                            "width": "100%",
                                            "height": "100%",
                                        },
                                    )
                                ),
                                dbc.Col(
                                    html.Iframe(
                                        id="linechart",
                                        style={
                                            "border-width": "0",
                                            "width": "100%",
                                            "height": "500px",
                                        },
                                    )
                                ),
                            ]
                        ),
                        dbc.Row(
                            [
                                dbc.Col(
                                    html.Table(id="actor_table"),
                                ),
                                dbc.Col(
                                    html.Iframe(
                                        id="profit_year",
                                        style={
                                            "border-width": "0",
                                            "width": "100%",
                                            "height": "450px",
                                        },
                                    ),
                                ),
                            ]
                        ),
                    ],
                    md=12,
                    style={
                        "width": "100%",
                        "height": "100vh",
                        "border": "1px solid #d3d3d3",
                        "border-radius": "10px",
                    },
                )
            ]
        ),
    ],
)

# app.layout = html.Div(
#     [
#         html.Label(
#             [
#                 "Genre Selector",
#                 dcc.Dropdown(
#                     id="genres",
#                     options=[
#                         {"label": col, "value": col} for col in data["genres"].unique()
#                     ],
#                     value=["Action", "Drama", "Comedy"],
#                     multi=True,
#                 ),
#             ]
#         ),
#         html.Label(
#             [
#                 "Year",
#                 dcc.RangeSlider(
#                     id="years",
#                     count=1,
#                     min=1960,
#                     max=2015,
#                     step=1,
#                     value=[2011, 2014],
#                 ),
#             ]
#         ),
#         html.Iframe(
#             id="profit_year",
#             style={"border-width": "0", "width": "100%", "height": "400px"},
#         ),
#         html.Br(),
#         html.Table(id="actor_table"),
#     ]
# )


if __name__ == "__main__":
    app.run_server(debug=True)