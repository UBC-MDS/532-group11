# Dash components
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_table

# Core data science libraries
import altair as alt
import pandas as pd

# Data loading functions
from data import read_data


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.MINTY], title="Movey Money")

server = app.server
data = read_data()

alt.themes.enable("fivethirtyeight")


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
    chart = (alt.Chart(filtered_data).mark_point().add_selection(click)).properties(
        width=600, height=350
    )

    first_chart = (
        chart.encode(
            alt.X(
                "release_year",
                title="Release Year",
                axis=alt.Axis(format="y", grid=False),
            ),
            alt.Y(
                "budget_adj",
                title="Budget (in million $)",
                axis=alt.Axis(grid=False),
            ),
            color=alt.Color(
                "genres", title="Genre", legend=alt.Legend(labelFontSize=17)
            ),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        )
        .transform_loess(
            loess="budget_adj",
            on="release_year",
            groupby=["genres"],
            bandwidth=0.35,
        )
        .mark_line()
    )

    second_chart = (
        chart.encode(
            x=alt.X(
                "release_month",
                title="Release Month",
                axis=alt.Axis(grid=False),
            ),
            y=alt.Y(
                "profit",
                title="Profit (in million $)",
                axis=alt.Axis(grid=False),
            ),
            color=alt.Color("genres", title="Genre"),
            opacity=alt.condition(click, alt.value(0.9), alt.value(0.05)),
        )
        .transform_loess("release_month", "profit", groupby=["genres"], bandwidth=0.35)
        .mark_line()
    )
    return (
        alt.hconcat(first_chart, second_chart).configure_view(strokeOpacity=0).to_html()
    )


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
        alt.Chart(filtered_data)
        .mark_rect()
        .encode(
            x=alt.X("vote_average", bin=alt.Bin(maxbins=11), title="Vote Average"),
            y=alt.Y("genres", title=""),
            color=alt.Color("count()", title="Count"),
            tooltip="count()",
        )
    ).properties(width=450, height=350)
    return chart.to_html()


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
                "selectable": False,
            },
            {
                "name": "Count",
                "id": "count",
                "selectable": False,
            },
        ],
        cell_selectable=False,
        data=top_actors.to_dict("records"),
        page_size=5,
        style_header={
            "backgroundColor": "rgb(230, 230, 230)",
            "fontWeight": "bold",
            "class": "table",
            "color": "#343a40",
        },
        style_data_conditional=[
            {
                "if": {"row_index": "odd"},
                "backgroundColor": "#78c2ad",
                "color": "#343a40",
            }
        ],
        style_cell={
            "padding": "7px",
            "color": "white",
            "backgroundColor": "#454d55",
        },
    )
    return table


def generate_button(id, text, width="50px", type="dark"):
    button = dbc.Button(
        text,
        id=f"button-{id}",
        className="btn btn-info" if type == "dark" else "btn btn-light",
        outline=False,
        style={
            "width": width,
            "display": "inline",
            "float": "right",
            "font-weight": "800",
        },
    )
    return button


def generate_modal():
    modal = dbc.Modal(
        [
            dbc.ModalHeader("Movey Money"),
            dbc.ModalBody(
                dcc.Markdown(
                    """
            This data visualization app aims at helping movie producers plan their next release. 
            The app contains key visualizations showing the financial trends, popularity metrics, as well as an actor selection widgets in order to help decision-makers identify factors that contribute to these key aspects. For more information please see the [detailed project proposal](https://github.com/UBC-MDS/532-group11/blob/main/proposal.md).
            """
                )
            ),
            dbc.ModalFooter(
                dbc.Button("Close", id="close-button-0", className="ml-auto")
            ),
        ],
        id="modal",
    )
    return modal


@app.callback(
    Output("modal", "is_open"),
    Output("collapse-1", "is_open"),
    Output("collapse-2", "is_open"),
    Output("collapse-3", "is_open"),
    [Input("button-0", "n_clicks")],
    [Input("close-button-0", "n_clicks")],
    [Input("button-1", "n_clicks")],
    [Input("button-2", "n_clicks")],
    [Input("button-3", "n_clicks")],
    [State("modal", "is_open")],
    [State("collapse-1", "is_open")],
    [State("collapse-2", "is_open")],
    [State("collapse-3", "is_open")],
)
def toggle_collapse(n0, n0c, n1, n2, n3, is_open0, is_open1, is_open2, is_open3):
    changed_id = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "button-0" in changed_id:
        return (not is_open0, is_open1, is_open2, is_open3)
    elif "close-button-0" in changed_id:
        return (not is_open0, is_open1, is_open2, is_open3)
    elif "button-1" in changed_id:
        return (is_open0, not is_open1, is_open2, is_open3)
    elif "button-2" in changed_id:
        return (is_open0, is_open1, not is_open2, is_open3)
    elif "button-3" in changed_id:
        return (is_open0, is_open1, is_open2, not is_open3)
    else:
        return (is_open0, is_open1, is_open2, is_open3)


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
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "Movey Money",
                                ),
                                html.H5("A Movie Production Planning Dashboard"),
                            ],
                        )
                    ],
                ),
                dbc.Col(
                    [
                        generate_button(
                            "0", text="LEARN MORE", width="150px", type="Main"
                        ),
                        generate_modal(),
                    ]
                ),
            ],
            style={
                "backgroundColor": "#78c2ad",
                "padding": 20,
                "margin-top": 0,
                "margin-bottom": 10,
                "text-align": "left",
                "font-size": "48px",
                "border-radius": 5,
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
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    [
                                                        html.Label(
                                                            "Discover historical and recent financial trends".upper(),
                                                            style={"font-size": 17},
                                                        ),
                                                        generate_button("1", text="?"),
                                                        dbc.Collapse(
                                                            html.P(
                                                                """This section depicts trends for two very important financial indicators in the movie making business - namely budget and profit. 
                                                                The plot on the left shows how budgets have changed over the years while the plot on the right can be used 
                                                                to explore how release month might be related to the success of a movie based on profits. Lines are estimated using LOESS regression.""",
                                                                style={
                                                                    "font-size": "13px"
                                                                },
                                                            ),
                                                            id="collapse-1",
                                                        ),
                                                    ]
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        html.Iframe(
                                                            id="linechart",
                                                            style={
                                                                "display": "block",
                                                                "overflow": " hidden",
                                                                "margin": "auto",
                                                                "border-width": "0",
                                                                "width": "1550px",
                                                                "height": "500px",
                                                            },
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            style={
                                                "height": "100%",
                                                "margin-left": "15px",
                                                "background": "#f0f0f0",
                                            },
                                        )
                                    ]
                                ),
                            ]
                        ),
                        # Second Row of Plots
                        dbc.Row(
                            [
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    [
                                                        html.Label(
                                                            "Identify most-liked genres".upper(),
                                                            style={"font-size": 17},
                                                        ),
                                                        generate_button("2", text="?"),
                                                        dbc.Collapse(
                                                            html.P(
                                                                """
                                                                This plot can help identify which type of movies are well-received by viewers 
                                                                based on user-submitted ratings.
                                                                """,
                                                                style={
                                                                    "font-size": "13px"
                                                                },
                                                            ),
                                                            id="collapse-2",
                                                        ),
                                                    ],
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        html.Iframe(
                                                            id="heatmap",
                                                            style={
                                                                "display": "block",
                                                                "overflow": " hidden",
                                                                "margin": "auto",
                                                                "height": "110%",
                                                                "width": "690px",
                                                                "border-width": "0",
                                                            },
                                                        ),
                                                    ]
                                                ),
                                            ],
                                            style={
                                                "height": "100%",
                                                "margin": "15px 15px 15px 15px",
                                                "background": "#f0f0f0",
                                            },
                                        )
                                    ]
                                ),
                                dbc.Col(
                                    [
                                        dbc.Card(
                                            [
                                                dbc.CardHeader(
                                                    [
                                                        html.Label(
                                                            "Find some potential actors".upper(),
                                                            style={"font-size": 17},
                                                        ),
                                                        generate_button("3", text="?"),
                                                        dbc.Collapse(
                                                            html.P(
                                                                """
                                                                This widget can help identify suitable actors for a potential movie in a given genre with a specific budget range in mind. 
                                                                The table suggests potential actors ranked based on the actor's experience in movies matching the specified criteria. 
                                                                Specifically, "Count" represents the number of matching movies in the database that the given actor has starred in.
                                                                """,
                                                                style={
                                                                    "font-size": "13px"
                                                                },
                                                            ),
                                                            id="collapse-3",
                                                        ),
                                                    ],
                                                ),
                                                dbc.CardBody(
                                                    [
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    html.Label(
                                                                        [
                                                                            "Drill down on a specific genre",
                                                                            dcc.Dropdown(
                                                                                id="genres_drill",
                                                                                multi=False,
                                                                                style={
                                                                                    "width": "200px"
                                                                                },
                                                                            ),
                                                                        ],
                                                                        style={
                                                                            "font-size": 13
                                                                        },
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
                                                                                "Narrow down your budget"
                                                                            ],
                                                                            style={
                                                                                "font-size": 13
                                                                            },
                                                                        ),
                                                                        dcc.RangeSlider(
                                                                            id="budget",
                                                                            count=1,
                                                                            step=5000000,
                                                                            min=data[
                                                                                "budget_adj"
                                                                            ].min(),
                                                                            max=data[
                                                                                "budget_adj"
                                                                            ].max(),
                                                                            value=[
                                                                                0,
                                                                                425000000,
                                                                            ],
                                                                            marks={
                                                                                0.99: "$0",
                                                                                425000000: "$425 million",
                                                                            },
                                                                            tooltip={
                                                                                "always_visible": False,
                                                                                "placement": "top",
                                                                            },
                                                                        ),
                                                                    ],
                                                                    md=5,
                                                                    style={
                                                                        "width": "100px"
                                                                    },
                                                                )
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    [
                                                                        html.Label(
                                                                            [
                                                                                "Discover some potentially suitable actors"
                                                                            ],
                                                                            style={
                                                                                "font-size": 13
                                                                            },
                                                                        )
                                                                    ]
                                                                )
                                                            ]
                                                        ),
                                                        dbc.Row(
                                                            [
                                                                dbc.Col(
                                                                    id="actor_col", md=5
                                                                )
                                                            ]
                                                        ),
                                                    ],
                                                ),
                                            ],
                                            style={
                                                "height": "100%",
                                                "margin-top": "15px",
                                                "background": "#f0f0f0",
                                            },
                                        )
                                    ],
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
        html.Br(),
        html.Hr(),
        dcc.Markdown(
            "This dashboard was created by Yazan Saleh, Rahul Kuriyedath, and Yanhua Chen. You can find the source code on [GitHub](https://github.com/UBC-MDS/532-group11). The data was provided by [The Movie Database (TMDB)](https://www.themoviedb.org/?language=en-CA) and was sourced from [Kaggle](https://www.kaggle.com/juzershakir/tmdb-movies-dataset). This project is released under the [MIT License](https://github.com/UBC-MDS/532-group11/blob/main/LICENSE)"
        ),
    ],
    fluid=True,
    style={"background": "#f0f0f0"},
)


if __name__ == "__main__":
    app.run_server(debug=False)
