####### PLOTS ########

# import plotly
import plotly.graph_objs as go
import pandas as pd
import numpy as np

# import data
SKU = pd.read_csv('SKU_year.csv')
# change timestamp datatype to datetime
SKU['date'] = pd.to_datetime(SKU['date'])


# function to profit per quarter
def quarter_profit(dataframe):
    df = dataframe
    profit_year = str(int(sum(df['profit_day_sum']) / 10000))
    df.index = df['date']
    df1 = df['profit_day_sum'].resample('Q').sum().to_frame()
    df2 = df1.pct_change()

    data = [go.Scatter(
        x=['一', '二', '三', '四'],
        y=df1['profit_day_sum'],
        name='利润',
        marker=dict(color='#4ea1d3')
    ),
        go.Bar(
            x=['一', '二', '三', '四'],
            y=df2['profit_day_sum'],
            yaxis='y2',
            name='环比增长',
            marker=dict(color='#d8e9ef'),
            opacity=0.6
        )]
    layout = go.Layout(
        title='2018各季度利润，年度总和=' + profit_year + '万元',
        yaxis=dict(
            title='利润'
        ),
        yaxis2=dict(
            title='环比增长',
            tickformat=".1%",
            overlaying='y',
            side='right'
        ),
        legend=dict(orientation="h"),
        font=dict(family='微软雅黑')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# function to plot number of transactions per month
def month_transaction(dataframe):
    df = dataframe
    transaction_year = str(int(sum(df['transaction_num'])))
    df.index = df['date']
    df1 = df['transaction_num'].resample('M', label='left').sum().to_frame()
    df2 = df1.pct_change()

    data = [go.Scatter(
        x=df1.index,
        y=df1['transaction_num'],
        name='销量',
        marker=dict(color='#4ea1d3')
    ),
        go.Bar(
            x=df2.index,
            y=df2['transaction_num'],
            yaxis='y2',
            opacity=0.6,
            name='环比增长',
            marker=dict(color='#d8e9ef')
        )]

    layout = go.Layout(
        title='2018月销量，年度总和=' + transaction_year + '笔',
        yaxis=dict(
            title='销量'
        ),
        yaxis2=dict(
            title='环比增长',
            tickformat=".1%",
            overlaying='y',
            side='right'
        ),
        legend=dict(orientation="h"),
        font=dict(family='微软雅黑')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# function to plot profit per SKU unit
def sku_unit_profit(dataframe):
    df = dataframe['unit_profit'].groupby(dataframe['SKU']).mean().to_frame().sort_values(by=['unit_profit'], ascending=False)
    data = [go.Bar(
        x=df.index,
        y=df['unit_profit'],
        marker=dict(color='#4ea1d3')
    )]
    layout = go.Layout(
        title='单件平均利润（元）',
        font=dict(family='微软雅黑')
    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# function to plot transactions per SKU unit
def sku_transaction(dataframe):
    df = dataframe['transaction_num'].groupby(dataframe['SKU']).sum().to_frame().sort_values(by=['transaction_num'],
                                                                                 ascending=False)
    data = [go.Bar(
        x=df.index,
        y=df['transaction_num'],
        marker=dict(color='#4ea1d3')
    )]
    layout = go.Layout(
        title='床垫年销量（件）',
        font=dict(family='微软雅黑')
    )

    fig = go.Figure(data=data, layout=layout)

    return fig


# function to plot try vs transaction
def sku_try_transaction(dataframe):
    df = dataframe[['try_num', 'transaction_num']].groupby(dataframe['SKU']).mean().sort_values(by=['try_num'],
                                                                                    ascending=False).round(1)
    df['conversion'] = df['transaction_num'] / df['try_num']

    trace1 = go.Bar(
        x=df.index,
        y=df['try_num'],
        name='试睡次数',
        marker=dict(color='#4ea1d3')
    )
    trace2 = go.Bar(
        x=df.index,
        y=df['transaction_num'],
        name='交易量',
        marker=dict(color='#e85a71')
    )
    trace3 = go.Scatter(
        x=df.index,
        y=df['conversion'],
        name='转化率',
        yaxis='y2',
        marker=dict(color='#454552')
    )

    data = [trace1, trace2, trace3]
    layout = go.Layout(
        barmode='group',
        title='日均试睡次数vs交易量',
        yaxis=dict(
            title='试睡次数、交易量'
        ),
        yaxis2=dict(
            title='转化率',
            tickformat=".0%",
            overlaying='y',
            side='right'
        ),
        legend=dict(orientation="h"),
        font=dict(family='微软雅黑')

    )

    fig = go.Figure(data=data, layout=layout)
    return fig


# function to plot profit per zone
def zone_perform(dataframe):
    df = dataframe[['transaction_num']].groupby(dataframe['zoneID']).mean()
    df['ppl'] = [1200, 1100, 2000, 800]
    df['ppl_per_trans'] = df['ppl'] / df['transaction_num']
    colors = ['#e85a71', '#4ea1d3', '#4ea1d3', '#4ea1d3']
    p1 = go.Scatter(x=df['transaction_num'],
                    y=df['ppl'],
                    text=df.index,
                    mode='markers+text',
                    hoverinfo='text',
                    marker=dict(
                        size=df['ppl_per_trans'] / 3,
                        color=colors))

    layout = go.Layout(title='各区域日均人流量vs销量（圆圈大小=人流量/销量）',
                       yaxis=dict(title='人流量'),
                       xaxis=dict(title='销量'),
                       font=dict(family='微软雅黑'))

    fig = go.Figure(data=[p1], layout=layout)
    return fig


######## Dashboard #######
import dash
from dash.dependencies import Input, Output
import dash_core_components as dcc
import dash_html_components as html

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H1(children='单店年度报告',
            style={
                'textAlign': 'center'
            }),
    html.Div(children='Dashboard Demo by Ariel Li, May 28 2019',
             style={
                 'textAlign': 'center'
             }),
    dcc.Tabs(id="tabs", value='tab-2', children=[
        dcc.Tab(label='时间分析', value='tab-1'),
        dcc.Tab(label='产品分析', value='tab-2'),
        dcc.Tab(label='区域分析', value='tab-3')
    ]),
    html.Div(id='tabs-content')
])


@app.callback(Output('tabs-content', 'children'),
              [Input('tabs', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H5('示例小结：销量稳定增长，第四季度销量最优，利润最高，三四季度增速较快。'),

            html.Div([
                html.Div([
                    dcc.Graph(id='fig1', figure=quarter_profit(SKU))
                ], className="six columns"),

                html.Div([
                    dcc.Graph(id='fig2', figure=month_transaction(SKU))
                ], className="six columns")
            ], className="row")
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H5('示例小结：4D磁悬浮销量最高，舒缦利润率最高，4D磁悬浮和月光宝盒摆在进门区，试睡次数最多，但就转化率而言，4D磁悬浮、云朗、诺蓝、畅眠表现出众，可以考虑挪换展示位置。'),

            html.Div([
                html.Div([
                    dcc.Graph(id='fig3', figure=sku_unit_profit(SKU))
                ], className="six columns"),

                html.Div([
                    dcc.Graph(id='fig4', figure=sku_transaction(SKU))
                ], className="six columns"),
            ], className="row"),

            dcc.Graph(
                id='fig5',
                figure=sku_try_transaction(SKU)
            )
        ])
    elif tab == 'tab-3':
        return html.Div([
            html.H5('小结：人流量大的区域交易量较大，如进门区。但中区1人流量大，交易量却小，需要反思中区1的布置。'),

            dcc.Graph(
                id='fig6',
                figure=zone_perform(SKU)
            )
        ])


if __name__ == '__main__':
    app.run_server(debug=True)
