import dash
import dash_html_components as html
import altair as alt


app = dash.Dash()
app.layout = html.Div("First Dash App")


if __name__ == "__main__":
    app.run_server(debug=True)