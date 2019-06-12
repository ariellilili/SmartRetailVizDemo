####### PLOTS ########

# import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# import data
face = pd.read_csv('face_camera.csv')
# change timestamp datatype to datetime
face['timestamp'] = pd.to_datetime(face['timestamp'])


# function to plot visits per hour
def visits_per_hour(dataframe):
    # indoor rate
    df = dataframe
    in_rate = "{:.0%}".format(df[df['zoneID'] == 'in'].shape[0] / df[df['zoneID'] == 'outdoor'].shape[0])
    # calculate per hour visits
    df.index = df['timestamp']
    df = df['faceID'].groupby(df['zoneID']).resample('H').count().to_frame()

    data = [go.Scatter(
        x=df.loc['outdoor'].index,
        y=df.loc['outdoor']['faceID'],
        mode='lines+markers',
        name='门口人流量',
        marker=dict(color='#454552')
    ),
        go.Scatter(
            x=df.loc['in'].index,
            y=df.loc['in']['faceID'],
            mode='lines+markers',
            name='进门数',
            marker=dict(color='#e85a71')
        )
    ]
    layout = go.Layout(
        title='每小时访客，总进门率：' + in_rate,
        font=dict(family='微软雅黑')
    )

    fig1 = go.Figure(data=data, layout=layout)
    return fig1


# function to plot age/gender pyramid
def age_gender_pyramid(dataframe):
    # get data
    df = dataframe[dataframe['zoneID'] == 'in']
    women_bins, bins = np.histogram(df[df['gender'] == 'Female']['age'], bins=list(range(10, 80, 10)))
    men_bins, bins = np.histogram(df[df['gender'] == 'Male']['age'], bins=list(range(10, 80, 10)))
    women_bins = -women_bins
    y = bins

    # plot
    layout = go.Layout(title="年龄与性别",
                       yaxis=go.layout.YAxis(title='年龄'),
                       xaxis=go.layout.XAxis(
                           showticklabels=False,
                           showgrid=False,
                           title='访客数'),
                       barmode='overlay',
                       bargap=0.1,
                       font=dict(family='微软雅黑'))

    data = [go.Bar(y=y,
                   x=men_bins,
                   orientation='h',
                   name='男',
                   hoverinfo='x',
                   text=men_bins,
                   textposition='auto',
                   marker=dict(color='#4ea1d3'),
                   opacity=0.8
                   ),
            go.Bar(y=y,
                   x=women_bins,
                   orientation='h',
                   name='女',
                   text=-1 * women_bins.astype('int'),
                   hoverinfo='text',
                   textposition='auto',
                   marker=dict(color='#e85a71'),
                   opacity=0.8
                   )]

    fig2 = go.Figure(data=data, layout=layout)
    return fig2


# function to plot donut plots for customer type, mood, and accompany
def multi_donuts(dataframe):
    # prepare data
    df = dataframe[dataframe['zoneID'] == 'in']
    df1 = df['customerType'].value_counts().to_frame()
    df2 = df['mood'].value_counts().to_frame()
    df3 = df['accompany'].value_counts().to_frame()

    fig3 = {
        "data": [
            {
                "values": df1['customerType'],
                "labels": df1.index,
                "domain": {"column": 0},
                "name": "Customer Type",
                'textinfo': 'label+percent',
                'showlegend': False,
                "hoverinfo": "value",
                "hole": .5,
                "type": "pie",
                'marker': {'colors': ['#d8e9ef',
                                      '#4ea1d3']}
            },
            {
                "values": df2['mood'],
                "labels": df2.index,
                'textinfo': 'label+percent',
                'showlegend': False,
                "hoverinfo": "value",
                "domain": {"column": 1},
                "name": "Mood",
                "hole": .5,
                "type": "pie",
                'marker': {'colors': ['#d8e9ef',
                                      '#4ea1d3']}
            },
            {
                "values": df3['accompany'],
                "labels": df3.index,
                'textinfo': 'label+percent',
                'showlegend': False,
                "hoverinfo": "value",
                "domain": {"column": 2},
                "name": "Mood",
                "hole": .5,
                "type": "pie",
                'marker': {'colors': ['#d8e9ef',
                                      '#4ea1d3']}
            }
        ],

        "layout": {
            "grid": {"rows": 1, "columns": 3},
            "font": {'family': '微软雅黑'},
            "annotations": [
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "回头客",
                    "x": 0.12,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "情绪",
                    "x": 0.5,
                    "y": 0.5
                },
                {
                    "font": {
                        "size": 20
                    },
                    "showarrow": False,
                    "text": "有伴与否",
                    "x": 0.9,
                    "y": 0.5
                }
            ]
        }
    }
    return fig3


# import data
track = pd.read_csv('track_camera.csv')
# change timestamp datatype to datetime
track['timestamp'] = pd.to_datetime(track['timestamp'])

# function to plot stay minutes in each zone
def stay_minutes(dataframe):
    df = dataframe['stay'].groupby(dataframe['from']).mean().to_frame().sort_values(by=['stay'], ascending=False)
    # seconds to minutes
    df = df / 60
    df['stay'] = df['stay'].round(1)

    data = [go.Bar(
        x=df.index,
        y=df['stay'],
        text=df['stay'],
        textposition='inside',
        marker=dict(color='#4ea1d3'),
        opacity=0.8
    )]
    layout = dict(
        title="各区域停留时间(分钟)",
        yaxis=dict(
            showticklabels=False,
            showgrid=False
        ),
        font=dict(family='微软雅黑')
    )

    fig = dict(data=data, layout=layout)
    return fig


# function to plot sankey diagram
def sankey_flow(dataframe):
    df = dataframe.groupby(['from', 'to'], as_index=False)['timestamp'].count()
    df = df[:8]
    df['source_index'] = [1, 1, 1, 2, 2, 2, 0, 0]
    df['target_index'] = [4, 3, 6, 5, 3, 6, 1, 2]

    data = dict(
        type='sankey',
        node=dict(
            pad=15,
            thickness=20,
            label=['进门区', '中区1', '中区2', '进门区', '中区2', '中区1', '里间'],
            color=['#454552'] * 3 + ['#e85a71'] + ['#454552'] * 3
        ),
        link=dict(
            source=df['source_index'],
            target=df['target_index'],
            value=df['timestamp'],
            color=['#d8e9ef'] * 8
        ))

    # Setting up the layout settings in the "layout" argument
    layout = dict(
        title="人流路线（数字为在前一区停留的分钟数）",
        font=dict(family='微软雅黑'),
        xaxis=dict(
            range=[0, 3],
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        yaxis=dict(
            range=[0, 4],
            showgrid=False,
            zeroline=False,
            showline=False,
            ticks='',
            showticklabels=False
        ),
        annotations=[
            dict(
                x=2,
                y=3.2,
                xref='x',
                yref='y',
                text='5',
                showarrow=False
            ),
            dict(
                x=2,
                y=2.3,
                xref='x',
                yref='y',
                text='8',
                showarrow=False
            ),
            dict(
                x=2,
                y=2.3,
                xref='x',
                yref='y',
                text='8',
                showarrow=False
            ),
            dict(
                x=1.7,
                y=1.8,
                xref='x',
                yref='y',
                text='12',
                showarrow=False
            ),
            dict(
                x=1.7,
                y=1.4,
                xref='x',
                yref='y',
                text='3',
                showarrow=False
            ),
            dict(
                x=2,
                y=1,
                xref='x',
                yref='y',
                text='7',
                showarrow=False
            ),
            dict(
                x=2,
                y=0.3,
                xref='x',
                yref='y',
                text='5',
                showarrow=False
            )
        ]
    )

    fig = dict(data=[data], layout=layout)
    return fig


# function to plot number of people in each zone in each hour
def ppl_zone(dataframe):
    # Set the datetime column as the index
    dataframe['timestamp'] = pd.to_datetime(dataframe['timestamp'])
    dataframe.index = dataframe['timestamp']
    # Group the data by month, and take the mean for each group (i.e. each month)
    df = dataframe['stay'].groupby(dataframe['from']).resample('H').count()
    df = df.reset_index()
    df.rename(columns={'stay': 'count'}, inplace=True)

    trace1 = go.Scatter(
        x=df[df['from'] == '进门区']['timestamp'],
        y=df[df['from'] == '进门区']['count'],
        name='进门区',
        mode='lines',
        marker=dict(color='#e85a71')
    )
    trace2 = go.Scatter(
        x=df[df['from'] == '中区1']['timestamp'],
        y=df[df['from'] == '中区1']['count'],
        name='中区1',
        mode='lines',
        marker=dict(color='#4ea1d3')
    )
    trace3 = go.Scatter(
        x=df[df['from'] == '中区2']['timestamp'],
        y=df[df['from'] == '中区2']['count'],
        name='中区2',
        mode='lines',
        marker=dict(color='#ffc952')
    )
    trace4 = go.Scatter(
        x=df[df['from'] == '里间']['timestamp'],
        y=df[df['from'] == '里间']['count'],
        name='里间',
        mode='lines',
        marker=dict(color='#454552')
    )

    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title="每小时在各区域人数",
        font=dict(family='微软雅黑')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# import data
IEQ = pd.read_csv('IEQ.csv')
# change timestamp datatype to datetime
IEQ['timestamp'] = pd.to_datetime(IEQ['timestamp'])
IEQ.index = IEQ['timestamp']


def temp(dataframe):
    df = dataframe[['temp']].groupby(dataframe['zoneID']).resample('0.1H').mean()
    day_mean = dataframe['temp'].mean()

    trace1 = go.Scatter(
        x=df.loc['进门区', :].index,
        y=df.loc['进门区', 'temp'],
        mode='lines',
        name='进门区',
        marker=dict(color='#e85a71')
    )
    trace2 = go.Scatter(
        x=df.loc['中区1', :].index,
        y=df.loc['中区1', 'temp'],
        mode='lines',
        name='中区1',
        marker=dict(color='#4ea1d3')
    )
    trace3 = go.Scatter(
        x=df.loc['中区2', :].index,
        y=df.loc['中区2', 'temp'],
        mode='lines',
        name='中区2',
        marker=dict(color='#ffc952')
    )
    trace4 = go.Scatter(
        x=df.loc['里间', :].index,
        y=df.loc['里间', 'temp'],
        mode='lines',
        name='里间',
        marker=dict(color='#454552')
    )
    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title='温度(°C)，日均：' + str(round(day_mean, 1)),
        font=dict(family='微软雅黑')
    )

    fig1 = go.Figure(data=data, layout=layout)
    return fig1


def CO2(dataframe):
    df = dataframe[['CO2']].groupby(dataframe['zoneID']).resample('0.5H').mean()
    day_mean = dataframe['CO2'].mean()

    trace1 = go.Scatter(
        x=df.loc['进门区', :].index,
        y=df.loc['进门区', 'CO2'],
        mode='lines',
        name='进门区',
        marker=dict(color='#e85a71')
    )
    trace2 = go.Scatter(
        x=df.loc['中区1', :].index,
        y=df.loc['中区1', 'CO2'],
        mode='lines',
        name='中区1',
        marker=dict(color='#4ea1d3')
    )
    trace3 = go.Scatter(
        x=df.loc['中区2', :].index,
        y=df.loc['中区2', 'CO2'],
        mode='lines',
        name='中区2',
        marker=dict(color='#ffc952')
    )
    trace4 = go.Scatter(
        x=df.loc['里间', :].index,
        y=df.loc['里间', 'CO2'],
        mode='lines',
        name='里间',
        marker=dict(color='#454552')
    )
    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title='二氧化碳(ppm)，日均：' + str(int(day_mean)),
        font=dict(family='微软雅黑')
    )

    fig1 = go.Figure(data=data, layout=layout)
    return fig1


def PM(dataframe):
    df = dataframe[['PM']].groupby(dataframe['zoneID']).resample('H').mean()
    day_mean = dataframe['PM'].mean()
    trace1 = go.Scatter(
        x=df.loc['进门区', :].index,
        y=df.loc['进门区', 'PM'],
        mode='lines',
        name='进门区',
        marker=dict(color='#e85a71')
    )
    trace2 = go.Scatter(
        x=df.loc['中区1', :].index,
        y=df.loc['中区1', 'PM'],
        mode='lines',
        name='中区1',
        marker=dict(color='#4ea1d3')
    )
    trace3 = go.Scatter(
        x=df.loc['中区2', :].index,
        y=df.loc['中区2', 'PM'],
        mode='lines',
        name='中区2',
        marker=dict(color='#ffc952')
    )
    trace4 = go.Scatter(
        x=df.loc['里间', :].index,
        y=df.loc['里间', 'PM'],
        mode='lines',
        name='里间',
        marker=dict(color='#454552')
    )
    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title='PM2.5(ug/m3)，日均：' + str(int(day_mean)),
        font=dict(family='微软雅黑')
    )

    fig1 = go.Figure(data=data, layout=layout)
    return fig1


def formaldehyde(dataframe):
    df = dataframe[['formaldehyde']].groupby(dataframe['zoneID']).resample('H').mean()
    day_mean = dataframe['formaldehyde'].mean()
    trace1 = go.Scatter(
        x=df.loc['进门区', :].index,
        y=df.loc['进门区', 'formaldehyde'],
        mode='lines',
        name='进门区',
        marker=dict(color='#e85a71')
    )
    trace2 = go.Scatter(
        x=df.loc['中区1', :].index,
        y=df.loc['中区1', 'formaldehyde'],
        mode='lines',
        name='中区1',
        marker=dict(color='#4ea1d3')
    )
    trace3 = go.Scatter(
        x=df.loc['中区2', :].index,
        y=df.loc['中区2', 'formaldehyde'],
        mode='lines',
        name='中区2',
        marker=dict(color='#ffc952')
    )
    trace4 = go.Scatter(
        x=df.loc['里间', :].index,
        y=df.loc['里间', 'formaldehyde'],
        mode='lines',
        name='里间',
        marker=dict(color='#454552')
    )
    data = [trace1, trace2, trace3, trace4]
    layout = go.Layout(
        title='甲醛(mg/m3)，日均：' + str(round(day_mean, 3)),
        font=dict(family='微软雅黑')
    )

    fig1 = go.Figure(data=data, layout=layout)
    return fig1



######## Dashboard #######
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='单店单日客流分析',
            style={
                'textAlign': 'center'
            }),
    html.Div(children='Dashboard Demo by Ariel Li, June 10 2019',
             style={
                 'textAlign': 'center'
             }),
    dcc.Tabs(id="tabs", value='tab-1', children=[
        dcc.Tab(label='人脸识别', value='tab-1'),
        dcc.Tab(label='顾客轨迹', value='tab-2'),
        dcc.Tab(label='室内环境', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H5('小结：中午至下午人流量较大，顾客中年人居多，并无特别性别差异，近一半人结伴而行。需注意的是，回头客比例较小，开心情绪比例较低。'),

            html.Div([
                html.Div([
                    dcc.Graph(id='fig1', figure=visits_per_hour(face))
                ], className="six columns"),

                html.Div([
                    dcc.Graph(id='fig2', figure=age_gender_pyramid(face))
                ], className="six columns")
            ], className="row"),

            dcc.Graph(
                id='fig3',
                figure=multi_donuts(face)
            )
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H5(
                '小结：进门后中区1和2分流效果相当，顾客在中区1停留时间较长，但中区2比中区1留客效果好。那些选择从中区回到进门区进而离开的顾客，在中区停留时间较短。店家应想办法让顾客在中区停留5分钟以上，那么他们更有可能在店内继续体验。'),

            dcc.Graph(
                id='fig4',
                figure=sankey_flow(track)
            ),

            html.Div([
                html.Div([
                    dcc.Graph(id='fig5', figure=stay_minutes(track))
                ], className="six columns"),

                html.Div([
                    dcc.Graph(id='fig6', figure=ppl_zone(track))
                ], className="six columns"),
            ], className="row")
        ])
    elif tab == 'tab-3':
        return html.Div([
            dcc.Graph(id='fig7', figure=temp(IEQ)),
            dcc.Graph(id='fig8', figure=CO2(IEQ)),
            dcc.Graph(id='fig11', figure=PM(IEQ)),
            dcc.Graph(id='fig13', figure=formaldehyde(IEQ))
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
