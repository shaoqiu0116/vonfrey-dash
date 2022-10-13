import base64
import datetime
import io
import plotly.graph_objs as go
import cufflinks as cf

import dash
from dash.dependencies import Input, Output, State
from dash import dcc
from dash import html
from dash import dash_table

import pandas as pd

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

colors = {
    "graphBackground": "#F5F5F5",
    "background": "#ffffff",
    "text": "#000000"
}

app.layout = html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div(['Drag and Drop or ',
                           html.A('Select Files')]),
        style={
            'width': '95%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True),
    html.Div(id='output-data-upload')
])

url = 'https://drive.google.com/uc?id=1GEkbOw68SgWtJrsT6oUMheCmdSaAV2Yk'
table_df = pd.read_csv(url, index_col='No.')


def parse_data(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV or TXT file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
        elif 'txt' or 'tsv' in filename:
            # Assume that the user upl, delimiter = r'\s+'oaded an excel file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')),
                             delimiter=r'\s+')
    except Exception as e:
        print(e)
        return html.Div(['There was an error processing this file.'])
    return df


@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents'),
     Input('upload-data', 'filename')])
def update_table(contents, filename):
    table = html.Div()
    if contents:
        contents = contents[0]
        filename = filename[0]
        test_df = parse_data(contents, filename)
        df = test_df.reset_index().merge(table_df, on='Response',
                                         how="left").set_index('No.')
        table = html.Div([
            html.H5(filename),
            dash_table.DataTable(id='table',
                                 style_header={
                                     'backgroundColor': 'rgb(30, 30, 30)',
                                     'color': 'white'
                                 },
                                 style_data={
                                     'backgroundColor': 'rgb(50, 50, 50)',
                                     'color': 'white'
                                 },
                                 export_format="csv",
                                 data=df.to_dict('rows'),
                                 columns=[{
                                     'name': i,
                                     'id': i
                                 } for i in df.columns]),
            html.Hr(),
            html.Div('Raw Content'),
            html.Pre(contents[0:200] + '...',
                     style={
                         'whiteSpace': 'pre-wrap',
                         'wordBreak': 'break-all'
                     })
        ])
    return table


if __name__ == '__main__':
    app.run_server(debug=True)
