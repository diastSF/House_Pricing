import os
import base64
import datetime
import io
import dash_table

import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt
from dash.dependencies import Input, Output, State
from plotly import tools
import plotly.graph_objs as go
import pickle

loadModel = pickle.load(open('XGBRegressor_HousePricing.sav', 'rb'))
encoderKitchen = pickle.load(open('le_KitchenQual.sav', 'rb'))
encoderExterior = pickle.load(open('le_ExterQual.sav', 'rb'))
encoderBasement = pickle.load(open('le_BsmtQual.sav', 'rb'))
encoderHeating = pickle.load(open('le_HeatingQC.sav', 'rb'))

df = pd.read_csv('dataDashboard.csv')
dfTable = pd.read_csv('dataDashboard.csv')

app = dash.Dash(__name__)

server = app.server

app.title = 'House Price'

def generate_table(dataframe, pagesize=10) :
    return dt.DataTable(
        id = 'table-multicol-sorting',
        columns = [
            {'name': val, 'id': val} for val in dataframe.columns
        ],
        pagination_settings = {
            'current_page' : 0,
            'page_size' : pagesize
        },
        pagination_mode = 'be',
        style_table = {'overflowX' : 'scroll'},
        sorting = 'be',
        sorting_type = 'multi',
        sorting_settings = []
    )

app.layout = html.Div([
    html.H1('Dashboard House Price'),
    html.H3('By : Diast SF.'),
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='House Price Data', value='tab-1', children=[
            html.Div([
                html.Div([
                    html.P('Overall Quality : '),
                    dcc.Dropdown(
                        id='filterOverallQual',
                        options=[i for i in [{ 'label': 'All Quality', 'value': '' },
                                            { 'label': 'Very Poor', 'value': 'Very Poor' },
                                            { 'label': 'Poor', 'value': 'Poor' },
                                            { 'label': 'Fair', 'value': 'Fair' },
                                            { 'label': 'Below Average', 'value': 'Below Average' },
                                            { 'label': 'Average', 'value': 'Average' },
                                            { 'label': 'Above Average', 'value': 'Above Average' },
                                            { 'label': 'Good', 'value': 'Good' },
                                            { 'label': 'Very Good', 'value': 'Very Good' },
                                            { 'label': 'Excellent', 'value': 'Excellent' },
                                            { 'label': 'Very Excellent', 'value': 'Very Excellent' }]],
                        value=''
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Kitchen Quality : '),
                    dcc.Dropdown(
                        id='filterKitchenQual',
                        options=[i for i in [{ 'label': 'All Quality', 'value': '' },
                                            { 'label': 'Excellent', 'value': 'Excellent' },
                                            { 'label': 'Good', 'value': 'Good' },
                                            { 'label': 'Average', 'value': 'Average' },
                                            { 'label': 'Fair', 'value': 'Fair' }]],
                        value=''
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Exterior Quality : '),
                    dcc.Dropdown(
                        id='filterExterQual',
                        options=[i for i in [{ 'label': 'All Quality', 'value': '' },
                                            { 'label': 'Excellent', 'value': 'Excellent' },
                                            { 'label': 'Good', 'value': 'Good' },
                                            { 'label': 'Average', 'value': 'Average' },
                                            { 'label': 'Fair', 'value': 'Fair' }]],
                        value=''
                    )
                ], className='col-4')
            ], className='row'),
            html.Br(),
            html.Div([
                html.Div([
                    html.P('Basement Quality : '),
                    dcc.Dropdown(
                        id='filterBasementQual',
                        options=[i for i in [{ 'label': 'All Quality', 'value': '' },
                                            { 'label': 'Excellent', 'value': 'Excellent' },
                                            { 'label': 'Good', 'value': 'Good' },
                                            { 'label': 'Average', 'value': 'Average' },
                                            { 'label': 'Fair', 'value': 'Fair' },
                                            { 'label': 'None', 'value': 'None' }]],
                        value=''
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Heating Quality & Condition: '),
                    dcc.Dropdown(
                        id='filterHeatingQC',
                        options=[i for i in [{ 'label': 'All Quality', 'value': '' },
                                            { 'label': 'Excellent', 'value': 'Excellent' },
                                            { 'label': 'Good', 'value': 'Good' },
                                            { 'label': 'Average', 'value': 'Average' },
                                            { 'label': 'Fair', 'value': 'Fair' },
                                            { 'label': 'Poor', 'value': 'Fair' }]],
                        value=''
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Garage Cars Capacity: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(df['GarageCars'].min(), df['GarageCars'].max()+1)},
                        min = df['GarageCars'].min(),
                        max = df['GarageCars'].max(),
                        value =[df['GarageCars'].min(), df['GarageCars'].max()],
                        className = 'rangeslider',
                        id = 'filterGarageCars'
                    )
                ], className='col-4')
            ], className='row'),
            html.Br(),
            html.Div([
                html.Div([
                    html.P('Bathrooms Above Ground: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(df['FullBath'].min(), df['FullBath'].max()+1)},
                        min = df['FullBath'].min(),
                        max = df['FullBath'].max(),
                        value =[df['FullBath'].min(), df['FullBath'].max()],
                        className = 'rangeslider',
                        id = 'filterBathroom'
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Rooms Above Ground: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(df['TotRmsAbvGrd'].min(), df['TotRmsAbvGrd'].max()+1, 2)},
                        min = df['TotRmsAbvGrd'].min(),
                        max = df['TotRmsAbvGrd'].max(),
                        value =[df['TotRmsAbvGrd'].min(), df['TotRmsAbvGrd'].max()],
                        className = 'rangeslider',
                        id = 'filterRooms'
                    )
                ], className='col-4'),
                html.Div([
                    html.P('Fireplaces Quantity: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(df['Fireplaces'].min(), df['Fireplaces'].max()+1)},
                        min = df['Fireplaces'].min(),
                        max = df['Fireplaces'].max(),
                        value =[df['Fireplaces'].min(), df['Fireplaces'].max()],
                        className = 'rangeslider',
                        id = 'filterFireplaces'
                    )
                ], className='col-4')
            ], className='row'),
            html.Br(),html.Br(),
            html.Div([
                html.Div([
                    html.P('Above Grade Area (square feet): '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(400,3601, 200)},
                        min = df['GrLivArea'].min(),
                        max = df['GrLivArea'].max(),
                        value =[df['GrLivArea'].min(), df['GrLivArea'].max()],
                        className = 'rangeslider',
                        id = 'filterGradeArea'
                    )
                ], className='col-12'),
            ], className='row'),
            html.Br(),html.Br(),
            html.Div([
                html.Div([
                    html.P('Year Built: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(1880, 2011, 10)},
                        min = df['YearBuilt'].min(),
                        max = df['YearBuilt'].max(),
                        value =[df['YearBuilt'].min(), df['YearBuilt'].max()],
                        className = 'rangeslider',
                        id = 'filterYearBuilt'
                    )
                ], className='col-12'),
            ], className='row'),
            html.Br(),html.Br(),
            html.Div([
                html.Div([
                    html.P('Price: '),
                    dcc.RangeSlider(
                        marks = {i: str(i) for i in range(50000,625001, 50000)},
                        min = df['SalePrice'].min(),
                        max = df['SalePrice'].max(),
                        value =[df['SalePrice'].min(), df['SalePrice'].max()],
                        className = 'rangeslider',
                        id = 'filterPrice'
                    )
                ], className='col-12'),
            ], className='row'),
            html.Br(),html.Br(),
            html.Div([
                html.Div([
                    
                ], className='col-4'),
                html.Div([
                    html.Button('Filter', id='buttonsearch', style=dict(width='100%'))
                ], className='col-4'),
                html.Div([
                    
                ], className='col-4')
            ], className='row'),
            html.Br(),html.Br(),html.Br(),
            html.Div([
                html.Div([
                    html.P('Max Rows : '),
                    dcc.Input(
                        id='filterrowstable',
                        type='number',
                        value=10,
                        style=dict(width='100%')
                    )
                ], className='col-3')
            ], className='row'),
            html.Center([
                html.H2('House Price Data', className='title'),
                html.Div(id='tablediv', children=generate_table(dfTable))
            ])
        ]),
        dcc.Tab(label='Categorical Plots', value='tab-2', children=[
            html.Div([
                html.Div([
                    html.P('X : '),
                    dcc.Dropdown(
                        id='xplotcategory',
                        options=[i for i in [{ 'label': 'Overall Quality', 'value': 'OverallQual' },
                                            { 'label': 'Kitchen Quality', 'value': 'KitchenQual' },
                                            { 'label': 'Exterior Quality', 'value': 'ExterQual' },
                                            { 'label': 'Basement Quality', 'value': 'BsmtQual' },
                                            { 'label': 'Heating Quality', 'value': 'HeatingQC' }]],
                        value='OverallQual'
                    )
                ], className='col-4'),
            ], className='row'),
            html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
            dcc.Graph(
                id='categorygraph'
            )
        ]),
        dcc.Tab(label='Scatter Plot', value='tab-3', children=[
            html.Div([
                html.Div([
                    html.P('X : '),
                    dcc.Dropdown(
                        id='xplotscatter',
                        options=[i for i in [{ 'label': 'Above Grade Area', 'value': 'GrLivArea' },
                                            { 'label': 'Garage Area', 'value': 'GarageArea' },
                                            { 'label': 'Basesment Area', 'value': 'TotalBsmtSF' },
                                            { 'label': 'Year Built', 'value': 'YearBuilt' },
                                            { 'label': 'Year Remodeling', 'value': 'YearRemodAdd' }]],
                        value='GrLivArea'
                    )
                ], className='col-4'),
            ], className='row'),
            html.Br(),html.Br(),html.Br(),html.Br(),html.Br(),
            dcc.Graph(
                id='scattergraph'
            )
        ]),
        dcc.Tab(label='Test Predict', value='tab-4', children=[
            html.Center([
                html.H3('Predict Your House Price',className='title')
            ]),
            # html.Div([
            #     html.Div([
            #         dcc.Upload(
            #             id='upload-data',
            #             children=html.Div([
            #                 'Drag and Drop or ',
            #                 html.A('Select Files')
            #             ]),
            #             style={
            #                 'width': '100%',
            #                 'height': '60px',
            #                 'lineHeight': '60px',
            #                 'borderWidth': '1px',
            #                 'borderStyle': 'dashed',
            #                 'borderRadius': '5px',
            #                 'textAlign': 'center',
            #                 'margin': '10px'
            #             },
            #             # Allow multiple files to be uploaded
            #             multiple=True
            #         )
            #     ], className='col-12'),
            # ], className='row'),
            html.Div([
                html.Div(id='output-data-upload')
            ], className='row'),
            html.Div([
                html.Div([
                    html.P('Overall Quality : '),
                    dcc.Dropdown(
                        id='predictOverall',
                        options=[i for i in [{ 'label': 'Very Poor', 'value': '1' },
                                            { 'label': 'Poor', 'value': '2' },
                                            { 'label': 'Fair', 'value': '3' },
                                            { 'label': 'Below Average', 'value': '4' },
                                            { 'label': 'Average', 'value': '5' },
                                            { 'label': 'Above Average', 'value': '6' },
                                            { 'label': 'Good', 'value': '7' },
                                            { 'label': 'Very Good', 'value': '8' },
                                            { 'label': 'Excellent', 'value': '8' },
                                            { 'label': 'Very Excellent', 'value': '10' }]],
                        value=''
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Kitchen Quality : '),
                    dcc.Dropdown(
                        id='predictKitchen',
                        options=[i for i in [{ 'label': 'Excellent', 'value': '0' },
                                            { 'label': 'Good', 'value': '2' },
                                            { 'label': 'Average', 'value': '3' },
                                            { 'label': 'Fair', 'value': '1' }]],
                        value=''
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Exterior Quality : '),
                    dcc.Dropdown(
                        id='predictExterior',
                        options=[i for i in [{ 'label': 'Excellent', 'value': '0' },
                                            { 'label': 'Good', 'value': '2' },
                                            { 'label': 'Average', 'value': '3' },
                                            { 'label': 'Fair', 'value': '1' }]],
                        value=''
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Basement Quality : '),
                    dcc.Dropdown(
                        id='predictBasement',
                        options=[i for i in [{ 'label': 'Excellent', 'value': '0' },
                                            { 'label': 'Good', 'value': '2' },
                                            { 'label': 'Average', 'value': '4' },
                                            { 'label': 'Fair', 'value': '1' },
                                            { 'label': 'None', 'value': '3' }]],
                        value=''
                    )
                ], className='col-3'),
            ], className='row paddingtop'),
            html.Div([
                html.Div([
                    html.P('Heating Quality : '),
                    dcc.Dropdown(
                        id='predictHeating',
                        options=[i for i in [{ 'label': 'Excellent', 'value': '0' },
                                            { 'label': 'Good', 'value': '2' },
                                            { 'label': 'Average', 'value': '4' },
                                            { 'label': 'Fair', 'value': '1' },
                                            { 'label': 'Poor', 'value': '3' }]],
                        value=''
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Above Grade Area : '),
                    dcc.Input(
                        id='predictAboveGrade',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Garage Cars Capacity : '),
                    dcc.Input(
                        id='predictGarageCars',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Garage Area : '),
                    dcc.Input(
                        id='predictGarageArea',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
            ], className='row paddingtop'),
            html.Div([
                html.Div([
                    html.P('Basement Area : '),
                    dcc.Input(
                        id='predictBasementArea',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('1st Floor Area : '),
                    dcc.Input(
                        id='predict1stFloor',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Number of Bathrooms : '),
                    dcc.Input(
                        id='predictBath',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Number of Rooms : '),
                    dcc.Input(
                        id='predictRooms',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
            ], className='row paddingtop'),
            html.Div([
                html.Div([
                    html.P('Year Built : '),
                    dcc.Input(
                        id='predictYearBuilt',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Year Remodeling : '),
                    dcc.Input(
                        id='predictYearRemod',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Masonry Veneer Area : '),
                    dcc.Input(
                        id='predictMasonry',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
                html.Div([
                    html.P('Number of Fireplaces : '),
                    dcc.Input(
                        id='predictFireplaces',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
            ], className='row paddingtop'),
            html.Div([
                html.Div([
                    html.P('Basement Finished Area : '),
                    dcc.Input(
                        id='predictBasementFinished',
                        type='number',
                        style=dict(width='100%')
                    )
                ], className='col-3'),
            ], className='row paddingtop'),
            html.Div([
                html.Div([
                    html.Button('Predict', id='buttonpredict', style=dict(width='100%',marginTop='32px'))
                ], className='col-3')
            ], className='row paddingtop'),
            html.Center([
            
            ], id='outputpredict', className='paddingtop')
        ])
    ],style={
        'fontFamily': 'system-ui'
    }, content_style={
        'fontFamily': 'Arial',
        'borderBottom': '1px solid #d6d6d6',
        'borderLeft': '1px solid #d6d6d6',
        'borderRight': '1px solid #d6d6d6',
        'padding': '44px'
    })
], style={
    'maxWidth': '1200px',
    'margin': '0 auto'
})


#----------------------------------------------------------------------#

###############         CALL BACK TAB 1         ###############

@app.callback(
    Output('table-multicol-sorting', "data"),
    [Input('table-multicol-sorting', "pagination_settings"),
     Input('table-multicol-sorting', "sorting_settings")])
def callbacksortingtable(pagination_setting, sorting_setting):
    if len(sorting_setting):
        dff = dfTable.sort_values(
            [col['column_id'] for col in sorting_setting],
            ascending = [
                col['direction'] == 'asc'
                for col in sorting_setting
            ],
            inplace = False
        )
    else:
        dff = dfTable

    return dff.iloc[
        pagination_setting['current_page'] * pagination_setting['page_size']:
        (pagination_setting['current_page'] + 1)*pagination_setting['page_size']
    ].to_dict('rows')

@app.callback(
    Output(component_id='tablediv', component_property='children'),
    [Input('buttonsearch', 'n_clicks'),
    Input('filterrowstable', 'value')],
    [State('filterOverallQual', 'value'),
    State('filterKitchenQual', 'value'),
    State('filterExterQual', 'value'),
    State('filterBasementQual', 'value'),
    State('filterHeatingQC', 'value'),
    State('filterGarageCars', 'value'),
    State('filterBathroom', 'value'),
    State('filterRooms', 'value'),
    State('filterFireplaces', 'value'),
    State('filterGradeArea', 'value'),
    State('filterYearBuilt', 'value'),
    State('filterPrice', 'value'),]
)
def callbackfiltertable(n_clicks,maxrows,overall,kitchen,exterior,basement,heating,
                        garage,bathroom,room,fireplace,area,year,price):
    global dfTable
    dfTable = df
    dfTable = df[((df['GarageCars'] >= int(garage[0])) & (df['GarageCars'] <= int(garage[1]))) &
            ((df['FullBath'] >= int(bathroom[0])) & (df['FullBath'] <= int(bathroom[1]))) &
            ((df['TotRmsAbvGrd'] >= int(room[0])) & (df['TotRmsAbvGrd'] <= int(room[1]))) &
            ((df['Fireplaces'] >= int(fireplace[0])) & (df['Fireplaces'] <= int(fireplace[1]))) &
            ((df['GrLivArea'] >= int(area[0])) & (df['GrLivArea'] <= int(area[1]))) &
            ((df['YearBuilt'] >= int(year[0])) & (df['YearBuilt'] <= int(year[1]))) &
            ((df['SalePrice'] >= int(price[0])) & (df['SalePrice'] <= int(price[1])))]
    
    if (overall != ''):
        dfTable = dfTable[dfTable['OverallQual'] == overall]

    if (kitchen != ''):
        dfTable = dfTable[dfTable['KitchenQual'] == kitchen]

    if (exterior != ''):
        dfTable = dfTable[dfTable['ExterQual'] == exterior]

    if (basement != ''):
        dfTable = dfTable[dfTable['BsmtQual'] == basement]

    if (heating != ''):
        dfTable = dfTable[dfTable['HeatingQC'] == heating]
    
    return generate_table(dfTable, pagesize=maxrows)


###############         CALL BACK TAB 2         ###############

index1 = {'OverallQual' : 'Overall Quality',
         'KitchenQual' : 'Kitchen Quality',
         'ExterQual' : 'Exterior Quality',
         'BsmtQual' : 'Basement Quality',
         'HeatingQC' : 'Heating Quality'
}

@app.callback(
    Output(component_id='categorygraph', component_property='figure'),
    [Input(component_id='xplotcategory', component_property='value')]
)
def callbackupdatecatgraph(x) :
    return dict(
        layout= go.Layout(
            title= 'House Price By {}'.format(index1[x]),
            xaxis= { 'title': index1[x] },
            yaxis= dict(title='Price'),
            
        ),
        data=[
            go.Box(
                x=df.sort_values('SalePrice')[x],
                y=df.sort_values('SalePrice')['SalePrice'],
                marker = dict(color='#c70039')
            )
        ]
    )


###############         CALL BACK TAB 3         ###############

index2 = {'GrLivArea' : 'Above Grade Area',
         'GarageArea' : 'Garage Area',
         'TotalBsmtSF' : 'Basesment Area',
         'YearBuilt' : 'Year Built',
         'YearRemodAdd' : 'Year Remodeling'
}

@app.callback(
    Output(component_id='scattergraph', component_property='figure'),
    [Input(component_id='xplotscatter', component_property='value')]
)
def callbackUpdateScatterGraph(x) :
    return dict(
                data=[
                    go.Scatter(
                        x=df[x],
                        y=df['SalePrice'],
                        mode='markers',
                        marker = dict(color='#159595')
                    )
                ],
                layout=go.Layout(
                    title= 'Price Distribution By {}'.format(index2[x]),
                    xaxis= { 'title': index2[x] },
                    yaxis= dict(title = 'Price'),
                    margin={ 'l': 40, 'b': 40, 't': 40, 'r': 10 },
                    hovermode='closest'
                )
            )


###############         CALL BACK TAB 4         ###############

# def parse_contents(contents, filename, date):
#     content_type, content_string = contents.split(',')

#     decoded = base64.b64decode(content_string)
#     try:
#         if 'csv' in filename:
#             # Assume that the user uploaded a CSV file
#             df = pd.read_csv(
#                 io.StringIO(decoded.decode('utf-8')))
#         elif 'xls' in filename:
#             # Assume that the user uploaded an excel file
#             df = pd.read_excel(io.BytesIO(decoded))
#     except Exception as e:
#         print(e)
#         return html.Div([
#             'There was an error processing this file.'
#         ])
    
#     df['KitchenQual'] = encoderKitchen.transform(df['KitchenQual'])
#     df['ExterQual'] = encoderExterior.transform(df['ExterQual'])
#     df['BsmtQual'] = encoderBasement.transform(df['BsmtQual'])
#     df['HeatingQC'] = encoderHeating.transform(df['HeatingQC'])
#     predictions = loadModel.predict(df.drop('SalePrice', axis=1))

#     df['prediction'] = predictions
#     df.drop(['SalePrice'], axis=1, inplace=True)
    
#     return html.Div([
#         html.H5(filename),
#         html.H6(datetime.datetime.fromtimestamp(date)),

#         dash_table.DataTable(
#             data=df.to_dict('records'),
#             columns=[{'name': i, 'id': i} for i in df.columns]
#         ),

#         html.Hr(),  # horizontal line

#         # For debugging, display the raw contents provided by the web browser
#         html.Div('Raw Content'),
#         html.Pre(contents[0:200] + '...', style={
#             'whiteSpace': 'pre-wrap',
#             'wordBreak': 'break-all'
#         })
#     ])

# @app.callback(Output('output-data-upload', 'children'),
#               [Input('upload-data', 'contents')],
#               [State('upload-data', 'filename'),
#                State('upload-data', 'last_modified')])
# def callback_table_prediction(list_of_contents, list_of_names, list_of_dates):
#     if list_of_contents is not None:
#         children = [
#             parse_contents(c, n, d) for c, n, d in
#             zip(list_of_contents, list_of_names, list_of_dates)]
#         return children

@app.callback(
    Output(component_id='outputpredict', component_property='children'),
    [Input('buttonpredict', 'n_clicks')],
    [State('predictOverall', 'value'),
    State('predictAboveGrade', 'value'),
    State('predictGarageCars', 'value'),
    State('predictGarageArea', 'value'),
    State('predictBasementArea', 'value'),
    State('predict1stFloor', 'value'),
    State('predictBath','value'),
    State('predictYearBuilt', 'value'),
    State('predictYearRemod', 'value'),
    State('predictRooms', 'value'),
    State('predictMasonry', 'value'),
    State('predictFireplaces', 'value'),
    State('predictBasementFinished', 'value'),
    State('predictKitchen', 'value'),
    State('predictExterior', 'value'),
    State('predictBasement', 'value'),
    State('predictHeating', 'value')]
)
def callbackpredict(n_clicks,overall,abvgrade,garagecars,garagearea,basementarea,
                    firstfloor,bath,yearbuilt,yearremod,rooms,masonry,fireplaces,
                    basementfinished,kitchen,exterior,basement,heating) :
    if(overall != '' and abvgrade != '' and garagecars != '' and garagearea != '' 
    and basementarea != '' and firstfloor != '' and bath != '' and yearbuilt != ''
    and yearremod != '' and rooms != '' and masonry != '' and fireplaces != ''
    and basementfinished != '' and kitchen != '' and exterior != ''
    and basement != '' and heating != '') :
        data=[[int(overall),int(abvgrade),int(garagecars),int(garagearea),
            int(basementarea),int(firstfloor),int(bath),int(yearbuilt),int(yearremod),
            int(rooms),int(masonry),int(fireplaces),int(basementfinished),int(kitchen),
            int(exterior),int(basement),int(heating)]]
        dfpredict = pd.DataFrame(data, columns=['OverallQual', 'GrLivArea', 'GarageCars', 
                                                'GarageArea', 'TotalBsmtSF', '1stFlrSF', 
                                                'FullBath', 'YearBuilt', 'YearRemodAdd', 
                                                'TotRmsAbvGrd', 'MasVnrArea', 'Fireplaces', 
                                                'BsmtFinSF1', 'KitchenQual', 'ExterQual', 
                                                'BsmtQual', 'HeatingQC'])
        predictions = loadModel.predict(dfpredict)
        return [
            html.H3('Prediction of Your House Price : $ {}'.format(int(predictions[0])))
        ]
    else :
        return html.H3('Please fill all inputs in the form above to Predict your House Price')

if __name__ == '__main__':
    app.run_server(debug=True)