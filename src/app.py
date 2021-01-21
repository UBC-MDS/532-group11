import dash
import dash_core_components as dcc
import dash_html_components as html
import altair as alt
from data import read_data
from dash.dependencies import Input, Output


app = dash.Dash()
data = read_data()


app.layout = html.Div(
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
                    id="years", count=1, min=1960, max=2015, step=1, value=[2011, 2014]
                ),
            ]
        ),
        html.Iframe(
            id="profit_genre",
            style={"border-width": "0", "width": "100%", "height": "400px"},
        ),
    ]
)


if __name__ == "__main__":
    app.run_server(debug=True)