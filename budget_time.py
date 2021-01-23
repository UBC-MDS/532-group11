import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
#from vega_datasets import data
import altair as alt
import pandas as pd



processed = pd.read_csv('processed_movie_data.csv', parse_dates=True)
alt.data_transformers.disable_max_rows()

# Getting unique genres in the dataset
genre_list = set(processed['genres'].tolist())


def plot_altair(genres):
    #print(genres)
    if len(genres) >= 1:
        query = "genres == '"+genres[0]+"'"
        for i in range(1,len(genres)):
            query = query + " or genres == '"+genres[i]+"'"
        genres_4 = processed.query("genres == 'Drama' or genres == 'Action' or genres == 'Comedy' or genres == 'Animation'")
        print(query)
    else:
        genres_4 = processed

    click = alt.selection_multi(fields=['genres'], bind='legend')
    #genres_4 = processed.query("genres == 'Drama' or genres == 'Action' or genres == 'Comedy' or genres == 'Animation'")
    chart = (alt.Chart(genres_4).mark_line(point=True).encode(
        alt.X('release_year', title='Year of release'), 
        alt.Y('mean(budget_adj)',title='Mean budget (Adjusted)'), 
        tooltip=['release_year','mean(budget_adj)'], 
        color='genres',
        opacity=alt.condition(
            click, alt.value(0.9), alt.value(0.05))
            ).add_selection(click)).properties(title='Mean adjusted budget over time')
    return chart.to_html()
app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

app.layout = html.Div([
        html.Iframe(
            id='scatter',
            srcDoc=plot_altair('abc'),
            style={'border-width': '0', 'width': '100%', 'height': '400px'}),
        'Select the genres you want to look at',
        dcc.Dropdown(
            options=[{'label':i, 'value':i} for i in genre_list],
            id='genres', multi=True)])

@app.callback(
    Output('scatter', 'srcDoc'),
    Input('genres', 'value'))
def update_output(genres):
    return plot_altair(genres)


if __name__ == '__main__':
    app.run_server(debug=True)