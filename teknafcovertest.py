import dash
from dash import dcc, html, Input, Output, State
import geemap.plotlymap as geemap
import ee

cloud_project = 'ee-adinak934'

try:
    ee.Initialize(project=cloud_project)
except:
    ee.Authenticate()
    ee.Initialize(project=cloud_project)

#colors for land cover visuals
landvisPalette = ['#1a6f2b', '#e9c889', '#365dcb', '#aeec49']

#colors for change detection visuals
transitionPalette = [
  '#428023', #// No change: mangroves to mangroves (00 -> 00)
  '#e06666', #// Change: mangroves to bare (0 -> 1)
  '#b60535', #// Change: mangroves to water (0 -> 2)
  '#ff4100', #// Change: mangroves to other vegetation (0 -> 3)
  '#428023', #// Change: bare to mangroves (1 -> 10)
  '#f9cb9c', #// No change: bare to bare (1 -> 11)
  '#cfe2f3', #// Change: bare to water (1 -> 12)
  '#cdee5d', #// Change: bare to other vegetation (1 -> 13)
  '#5b9686', #// Change: water to mangroves (2 -> 20)
  '#fff2cc', #// Change: water to bare (2 -> 21)
  '#16537e', #// No change: water to water (2 -> 22)
  '#8fce00', #// Change: water to other vegetation (2 -> 23)
  '#7d9150', #// Change: other vegetation to mangroves (3 -> 30)
  '#d9ef8b', #// Change: other vegetation to bare (3 -> 31)
  '#3288bd', #// Change: other vegetation to water (3 -> 32)
  '#d9ead3', #// No change: other vegetation to other vegetation (3 -> 33)
]

#assets for each year for land cover, in a dict
land_cover_assets = {
    2014: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2014',
    2015: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2015',
    2016: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2016',
    2017: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2017',
    2018: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2018',
    2019: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2019',
    2020: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2020',
    2021: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2021',
    2022: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2022',
    2023: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2023',
    2024: 'projects/ee-neelsimpson112/assets/ClassifiedTeknafImages/Classified_2024',
}

#assets for each change detection timeframe, in a dict
change_detection_assets = {
    "2013_2014": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2013_2014',
    "2014_2015": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2014_2015',
    "2015_2016": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2015_2016',
    "2016_2017": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2016_2017',
    "2017_2018": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2017_2018',
    "2018_2019": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2018_2019',
    "2019_2020": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2019_2020',
    "2020_2021": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2020_2021',
    "2021_2022": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2021_2022',
    "2022_2023": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2022_2023',
    "2023_2024": 'projects/ee-neelsimpson112/assets/ChangeDetection/Change_2023_2024',
}

#dictionary of categories and colors for the legend
legends = {
    "land_cover": {
        "title": "Land Cover Classes",
        "categories": ['Mangroves', 'Bare', 'Water', 'Other Vegetation'],
        "colors": landvisPalette
    },
    "change_detection": {
        "title": "Change Detection Transitions",
        "categories": [
            'No change (Mangroves)',
            'Deforestation: Mangroves to Bare',
            'Deforestation: Mangroves to Water',
            'Deforestation: Mangroves to Other Vegetation',
            'Afforestation: Bare to Mangroves',
            'No change (Bare)',
            'Bare to Water',
            'Bare to Other Vegetation',
            'Land Reclamation: Water to Mangroves',
            'Water to Bare',
            'No change (Water)',
            'Water to Other Vegetation',
            'Afforestation:Other Vegetation to Mangroves',
            'Other Vegetation to Bare',
            'Other Vegetation to Water',
            'No change (Other Vegetation)'],
        "colors": transitionPalette
    }
}

#visualization parameters for each layer 
land_vis_params = {
    'min': 0,
    'max': 3,
    'palette': landvisPalette
}

change_vis_params = {
    'min': 0,
    'max': 33,
    'palette': transitionPalette
}

#load app and external css stylesheet
app = dash.Dash(__name__, external_stylesheets=["https://cdnjs.cloudflare.com/ajax/libs/bootswatch/5.3.3/cerulean/bootstrap.min.css"])

#app and containers (Title, Dropdown for choosing layer, Dropdown for selecting the year, legend, map)
app.layout = html.Div([
    html.H1("Mangrove Forest Visualization Dashboard", style={"textAlign": "center", "fontWeight": "bold"}),

   html.Div([
        # Dropdown for selecting the map type (Land Cover or Change Detection)
        dcc.Dropdown(
            id="map-type-dropdown",
            options=[
                {"label": "Land Cover", "value": "land_cover"},
                {"label": "Change Detection", "value": "change_detection"},
            ],
            value="land_cover",  # Default value
            style={"width": "50%", "margin": "auto"}
        ),
    ], style={'textAlign': 'center', 'padding': '5px'}),  # Center the dropdown and add space

    html.Div([
     # Dropdown for selecting the year
        dcc.Dropdown(
            id="year-dropdown",
            options=[],  # Options will be updated based on map type
            value=2017,  # Default value
            style={"width": "50%", "margin": "auto"}
        ),
    ], style={'textAlign': 'center', 'padding': '5px'}),  # Center the dropdown

    html.Div(id="map-container", style={"textAlign": "center", "marginTop": "10px"}),

    # Legend container
    html.Div(id="legend"),
    dcc.Store(id="map-state", data={"center": [20.791193, 92.317565], "zoom": 8})
])

#input: what is the map type. Output: get the options dor the year dropdown, and the default value
@app.callback(
    Output("year-dropdown", "options"),
    Output('year-dropdown', 'value'),
    Input("map-type-dropdown", "value"),
)

def update_year_dropdown(map_type):
    if map_type == "land_cover":
        # Land Cover maps: Years 2017-2024
        year_options = [{"label": f"Year {year}", "value": year} for year in range(2014, 2025)]
        year_value = 2017
    else:
        # Change Detection maps: Pairs of years
        year_options = [{"label": f"Change {year} to {year+1}", "value": f"{year}_{year+1}"} for year in range(2013, 2024)]
        year_value = "2017_2018"
    return year_options, year_value

#update map function: change the dictionary of assets to pull from depending on the map type, access image and create map
#based on visual parameters.
def update_map(map_type, selected_year):
    if map_type == "land_cover":
        # Load the land cover asset for the selected year
        asset_path = land_cover_assets[selected_year]
        vis_params = land_vis_params
    else:
        # Load the change detection asset for the selected pair of years
        asset_path = change_detection_assets[selected_year]
        vis_params = change_vis_params

    image = ee.Image(asset_path)

    # Get the bounds and center of the image

    # Create a geemap Map object
    Map = geemap.Map(center=[20.791193, 92.317565], zoom = 12)
    Map.add_basemap('SATELLITE')
    Map.addLayer(image, vis_params, f'{map_type} {selected_year}')

    # Save map to an HTML string
    map_html = Map.to_html()

    return map_html

#input map type and year selected. Output: updated map in html format in an iframe.
@app.callback(
    Output("map-container", "children"),
    [Input("map-type-dropdown", "value"),
     Input("year-dropdown", "value")],

)

def render_map(map_type, selected_year):
    # Generate the map HTML based on the selected map type and year
    map_html= update_map(map_type, selected_year)
    
    # Return the map as an iframe to display it in Dash
    return html.Iframe(
        srcDoc=map_html,
        style={"width": "100%", "height": "600px", "border": "none"}
    )


#input: map-type Output: legend to display
@app.callback(
    Output("legend", "children"),
    Input("map-type-dropdown", "value")
)

def update_legend(map_type):
    legend = legends.get(map_type, {})
    if not legend:
        return html.Div()

    legend_items = [
        html.Div(
            style={
                "display": "flex",
                "alignItems": "center",
                "marginBottom": "5px"
            },
            children=[
                html.Div(
                    style={
                        "backgroundColor": color,
                        "width": "20px",
                        "height": "20px",
                        "marginRight": "10px",
                        "border": "1px solid black"
                    }
                ),
                html.Span(category)
            ]
        )
        for category, color in zip(legend["categories"], legend["colors"])
    ]
    return html.Div(
        children=[
            html.H5(legend["title"], style={"marginBottom": "10px", "textAlign": "center"}),
            *legend_items
        ],
        style={
            "border": "1px solid black",
            "padding": "10px",
            "maxWidth": "200px",
            "backgroundColor": "white",
            "position": "absolute",
            "top": "10px",
            "left": "10px",
            "zIndex": "1000"
        }
    )

if __name__ == "__main__":
    app.run_server(debug=True)