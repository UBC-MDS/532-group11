import dash
import dash_core_components as dcc
import dash_html_components as html
import altair as alt
from data import read_data
from dash.dependencies import Input, Output


app = dash.Dash()
data = read_data()


app.layout =
    html.Div(
        [
            html.Label(
                [
                    "Genre Selector",
                    dcc.Dropdown(
                        id="genres",
                        options=[
                            {"label": col, "value": col}
                            for col in data["primary_genre"].unique()
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
        ]
    )


@app.callback(
    Output("profit_year", "srcDoc"),
    Input("genres", "value"),
    Input("years", "value"),
)
def plot_profit_vs_year(genres, year):
    filtered_data = data.query(
        "release_date >= @year[0] & release_date <= @year[1] & primary_genre in @genres"
    )
    chart = (
        alt.Chart(filtered_data)
        .mark_line(opacity=0.5)
        .encode(
            x=alt.X("month(release_date):O"),
            y=alt.Y("median(profit):Q"),
            color="primary_genre",
        )
    )
    return chart.to_html()


if __name__ == "__main__":
    app.run_server(debug=True)