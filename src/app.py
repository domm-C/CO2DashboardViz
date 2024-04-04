import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load data
df = pd.read_csv('owid-co2-data.csv')
df = df.fillna(0)
df['gdp_per_capita'] = np.where(df['population'] != 0, df['gdp'] / df['population'], 0)

# Define continents
continents = ['World', 'Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']
continents_excl_world = ['Asia', 'Oceania', 'Europe', 'Africa', 'North America', 'South America', 'Antarctica']

app = dash.Dash(__name__)
server = app.server

# CSS styles for graphs
graph_style = {'width': '100%', 'height': '500px', 'margin': 'auto'}  # Adjusted width to 80% and added margin auto

# Layout
app.layout = html.Div([
    #html.H1("World CO2 Emission Dashboard", style={'text-align': 'center'}),  # Centered the main title
    
    html.Div([
        html.H1("World CO2 Emissions Dashboard", style={'text-align': 'center'}),  # Centered the subtitle
        html.P("Carbon dioxide emissions are the primary driver of global climate change. It’s widely recognised that to avoid the worst impacts of climate change, the world needs to urgently reduce emissions. But, how this responsibility is shared between regions, countries, and individuals has been an endless point of contention in international discussions.", style={'text-align': 'center'}),  # Centered the paragraph
    ]),
    
    html.Div([
        html.H3("Timeline", style={'text-align': 'center'}),  # Centered the settings title
        dcc.Slider(
            id='year-slider',
            min=1750,
            max=2020,
            step=5,
            value=1850,
            marks={str(year): str(year) for year in range(1750, 2021, 25)}
        )
    ]),
    
    html.Div([
        html.Div([
            dcc.Graph(id='co2-plot', style=graph_style),
        ], className="row3_child1"),
        
        html.Div([
            dcc.Graph(id='co2-gdp-plot', style=graph_style),
            html.Label('Checklist'),
            dcc.Checklist(
                id='co2-range-checklist',
                options=[
                    {'label': 'Min CO2', 'value': 'min'},
                    {'label': 'Max CO2', 'value': 'max'}
                ],
                value=[]
            ),
            html.Div(id='co2-range-output')
        ], className="row3_child1")
    ], id="row3"),
    
    html.Div([
        html.Div([
            dcc.RadioItems(
                id='yaxis-co2-source',
                options=[{'label': 'Coal', 'value': 'coal_co2'},
                         {'label': 'Gas', 'value': 'gas_co2'},
                         {'label': 'Oil', 'value': 'oil_co2'}],
                value='coal_co2',
                labelStyle={'display': 'inline-block'}
            ),
            dcc.Graph(id='co2-source-bar-plot', style=graph_style),
        ], className="row3_child2"),
        
        html.Div([
            dcc.Graph(id='co2-per-capita-pie-chart', style=graph_style),
        ], className="row3_child2")
    ], id="row3")
])

# Callbacks
@app.callback(
    [Output('co2-plot', 'figure'),
     Output('co2-gdp-plot', 'figure'),
     Output('co2-source-bar-plot', 'figure'),
     Output('co2-per-capita-pie-chart', 'figure'),
     Output('co2-range-output', 'children')],
    [Input('year-slider', 'value'),
     Input('yaxis-co2-source', 'value'),
     Input('co2-range-checklist', 'value')]
)
def update_plots(year, co2_source, checklist_values):
    # Filter data based on selected year and continents
    co2_data = df[(df['year'] <= year) & (df['country'].isin(continents))].groupby(['country', 'year'])['co2'].mean().reset_index()
    
    co2_vs_gdp_data = df[(df['year'] == year) & (~df['country'].isin(continents)) & (df['gdp_per_capita'] != 0)].groupby(['country', 'year', 'gdp_per_capita'])['co2'].mean().reset_index()
    
    co2_source_data = df[(df['year'] == year) & (df['country'].isin(continents_excl_world))].groupby(['year', 'country'])[co2_source].sum().reset_index()
    
    # CO2 emissions per capita data for pie chart
    co2_per_capita_data = df[(df['year'] == year) & (df['country'].isin(continents)) & (df['country'] != 'World')][['country', 'co2_per_capita']].groupby('country').sum()
    
    # Create figures
    co2_plot = px.line(co2_data, x='year', y='co2', color='country', title="CO2 Emission by Continent")
    co2_plot.update_layout(title={'x':0.5}, plot_bgcolor='white')  # Centered the title
    
    co2_gdp_plot = px.scatter(co2_vs_gdp_data, x='gdp_per_capita', y='co2', color='country', title="CO2 vs GDP per capita")
    co2_gdp_plot.update_layout(title={'x':0.5}, plot_bgcolor='rgb(240, 240, 240)')  # Centered the title
    co2_gdp_plot.update_yaxes(gridcolor='white')
    
    for trace in co2_gdp_plot.data:
        trace.update(showlegend=False)  # Hide legend for each trace in the scatter plot
    
    co2_source_bar_plot = px.bar(co2_source_data, x='country', y=co2_source, title='CO2 source by Country')
    co2_source_bar_plot.update_layout(title={'x':0.5}, plot_bgcolor='white')  # Centered the title
    co2_source_bar_plot.update_yaxes(gridcolor='black')  # Set y-axis grid color
    
    # Pie chart for CO2 emissions per capita
    co2_per_capita_pie_chart = px.pie(co2_per_capita_data, names=co2_per_capita_data.index, title='CO2 Emissions per Capita')
    co2_per_capita_pie_chart.update_layout(title={'x':0.5})  # Centered the title
    
    # Output for the checklist
    output = ''
    if 'min' in checklist_values:
        min_co2 = df[df['co2'] > 0]['co2'].min()
        output += f"The Min CO2 is: {min_co2}. "
    if 'max' in checklist_values:
        max_co2 = df[df['co2'] > 0]['co2'].max()
        output += f"The Max CO2 is: {max_co2}. "
    
    return co2_plot, co2_gdp_plot, co2_source_bar_plot, co2_per_capita_pie_chart, output

if __name__ == '__main__':
    app.run_server(debug=True)
