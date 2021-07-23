from typing import Text
import dash
import dash_bootstrap_components as dbc
from dash_bootstrap_components._components import Label, Row
from dash_bootstrap_components._components.Col import Col
from dash_bootstrap_components._components.PopoverBody import PopoverBody
from dash_bootstrap_components._components.PopoverHeader import PopoverHeader
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Output,Input
from dash_html_components import Hr
from dash_html_components.Br import Br
import plotly.express as px
import pandas as pd
import sqlite3
from datetime import date


con = sqlite3.connect('data.sqlite')

def select(sql):
    return pd.read_sql(sql,con)

sql = '''
    select distinct order_date as date
    from 'public.orders' o 
    order by date  
'''
df_interval = select(sql)
df_interval['number'] = range(1,len(df_interval)+1)

sql = '''
    select order_date,round(sum(unit_price*quantity)) as sum , count(o.order_id) as cnt
    from 'public.order_details' od 
    join 'public.orders' o on o.order_id=od.order_id
    group by order_date
    order by order_date 
'''
df_daily_sales = select(sql)


app = dash.Dash(__name__,external_stylesheets=[dbc.themes.DARKLY])

alert = dbc.Alert('Input Correct Date', color='warning', dismissable=True)

app.layout = dbc.Container([
    html.Div(id='my_alert',children=[]),
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card(dbc.CardBody([
                    html.H6('Select an interval',style={'textAlign':'center'},className='mb-4'),
                    dcc.DatePickerSingle(id='start-date',
                                        date=date(1996,7,4),
                                        min_date_allowed=date(1996,7,4),
                                        max_date_allowed=date(1998,5,6),
                                        initial_visible_month=date(1996,7,4),
                                        # display_format='MMMM Y, DD',
                                        placeholder='Select a date',
                                        ),
                    dcc.DatePickerSingle(id='end-date',
                                        date=date(1998,5,6),
                                        min_date_allowed=date(1996,7,4),
                                        max_date_allowed=date(1998,5,6),
                                        initial_visible_month=date(1998,5,6),
                                        # display_format='MMMM Y, DD',
                                        placeholder='Select a date',
                                        className='ml-5'
                                        ),
                    html.Hr(),
                    dcc.RangeSlider(id='slider-date', min=1,max=480,step=1, value=[1, 480],allowCross=False,className='mt-4'),
                ])),width=6,className='mt-2'),
                dbc.Col([
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6('Sum of Sales',style={'textAlign':'center'}),
                            html.H5(id='sum-sales', children='', style={'fontWeight':'bold','textAlign':'center'})
                        ])),width=12,className='mt-2')
                    ]),
                    dbc.Row([
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6('Number of orders',style={'textAlign':'center','font-size':'13px'}),
                            html.H5(id='number-orders', children='', style={'fontWeight':'bold','textAlign':'center'})
                        ])),width=6,className='mt-3'),
                        dbc.Col(dbc.Card(dbc.CardBody([
                            html.H6('Unique customers',style={'textAlign':'center','font-size':'13px'}),
                            html.H5(id='number-customers', children='', style={'fontWeight':'bold','textAlign':'center'})
                        ])),width=6,className='mt-3')
                    ])
                ],width=6),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Col(dbc.Card(dbc.CardImg(src='/assets/northwind.jpg',alt='DB Northwind'),id='hover-target',style={"width": "20rem"}),width=4,className='mt-2'),
                    dbc.Popover([
                        dbc.PopoverHeader('DB Northwind'),
                        dbc.PopoverBody('This App is effort to show the main metrics and charts based on database NORTHWIND'),
                        dbc.PopoverHeader('Created by Sapr*')],
                        id='hover',
                        target='hover-target',
                        trigger='hover'
                    ),
                ],width=12)
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.RadioItems(id='radio-manager-customer',
                                options=[
                                    {'label': 'Report by Managers', 'value': 'managers'},
                                    {'label': 'TOP 4 Customers', 'value': 'customers'}
                                ],
                                value='managers'),
                            dbc.Spinner([dcc.Graph(id='sales-managers',figure={})],size='lg',color='primary',type='border')
                        ])
                    ])
                ],width=6,className='mt-2'),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dbc.RadioItems(id='radio-top-product',
                                options=[
                                    {'label': 'TOP 8 Best Sales Products', 'value': 'best_sales'},
                                    {'label': 'Sum of Sales Products by Category', 'value': 'sale_category'}
                                ],
                                value='best_sales'),
                            dbc.Spinner([dcc.Graph(id='top-product',figure={})],size='lg',color='primary',type='border')
                        ])
                    ])
                ],width=6,className='mt-2')
            ])

        ],xl=6,lg=6,md=12,sm=12,xs=12,className='mt-2'),

        dbc.Col([
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Label('Daily Sales, $',style={'textAlign':'center'}),
                        dbc.Spinner([dcc.Graph(id='sales-by-days',figure={})],size='lg',color='primary',type='border')
                    ])
                ]),width=12,className='mt-2')
            ]),
            dbc.Row([
                dbc.Col(dbc.Card([
                    dbc.CardBody([
                        html.Label('Share of Shippers by Region',style={'textAlign':'center'}),
                        dbc.Spinner([dcc.Graph(id='icicle',figure={})],size='lg',color='primary',type='border') 
                    ])
                ]),width=12,className='mt-2')
            ])

        ],xl=6,lg=6,md=12,sm=12,xs=12,className='mt-2 mb-2')
    ],justify='center')
],fluid=True)


# -------------------------------------------------------------
@app.callback(
    [Output(component_id='start-date',component_property='date'),
    Output(component_id='end-date',component_property='date'),
    Output(component_id='slider-date',component_property='value')],
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date'),
    Input(component_id='slider-date',component_property='value')]
)
def update_interval(start_date, end_date, slider_v):
    ctx = dash.callback_context
    component_triggered = ctx.triggered[0]["prop_id"].split(".")[0]

    if component_triggered == 'slider-date':
        start_date = df_interval[df_interval.number == slider_v[0]]['date'].values[0]
        end_date = df_interval[df_interval.number == slider_v[1]]['date'].values[0]

    elif component_triggered == 'start-date' or component_triggered == 'end-date':
        num_start = df_interval[df_interval.date==start_date]['number'].values[0]
        num_end = df_interval[df_interval.date==end_date]['number'].values[0]
        slider_v = [num_start, num_end]

    return start_date, end_date, slider_v

# -----------------------------------------------------------------
@app.callback(
    [Output(component_id='sum-sales',component_property='children'),
    Output(component_id='number-orders',component_property='children'),
    Output(component_id='number-customers',component_property='children'),
    Output(component_id='my_alert',component_property='children')],
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date')]
)
def update_metrics(start_date, end_date):
    if end_date < start_date:
        return [dash.no_update,dash.no_update,dash.no_update,alert]
    else:
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        cur.execute(
        '''
            select round(sum(unit_price*quantity),2), count(o.order_id), count(distinct c.customer_id)
            from 'public.order_details' od 
            join 'public.orders' o on o.order_id=od.order_id 
            join 'public.customers' c on c.customer_id=o.customer_id 
            where order_date between ? and ?
        ''',(start_date, end_date))

        result = cur.fetchall()
        sum_of_sales = f"${result[0][0]:,.2f}"
        number_orders = result[0][1]
        number_customers = result[0][2]
        return [sum_of_sales, number_orders, number_customers,dash.no_update]

# -----------------------------------------------------------------
@app.callback(
    Output(component_id='sales-by-days',component_property='figure'),
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date')]
)
def update_daily_chart(start_date, end_date):
    df = df_daily_sales.copy()
    df['colors'] = df.apply(lambda x:'orange' if x.order_date >= start_date and x.order_date <= end_date  else 'turquoise',axis=1)
    fig = px.bar(data_frame=df,x='order_date',y='sum',template='gridon',hover_data=['cnt'],
        labels={'order_date':'Order Date','sum':'Sum of Sales','cnt':'Number of Orders'})
    fig.update_traces(marker_color=df['colors'])
    return fig

# ----------------------------------------------------------------
@app.callback(
    Output(component_id='sales-managers',component_property='figure'),
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date'),
    Input(component_id='radio-manager-customer',component_property='value')]
)
def update_chart_managers(start_date, end_date, radio_value):
    if radio_value == 'managers':
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        cur.execute(
        '''
            ;with cte as (
            select order_date, employee_id,order_id 
            from 'public.orders' o
            where order_date between ? and ?
            )
            select last_name|| ' ' ||substr(first_name,1,1) as manager,round(sum(unit_price*quantity),2) as sum, count(cte.order_id)
            from 'public.employees' e 
            join cte on cte.employee_id=e.employee_id 
            join 'public.order_details' od on cte.order_id=od.order_id 
            group by e.employee_id 
            order by sum desc
        ''',(start_date, end_date))

        result = cur.fetchall()
        df = pd.DataFrame(result,columns=['Manager','Sum','Numbers'])
        df.sort_values(by='Sum',inplace=True)
        fig = px.bar(data_frame=df,x='Sum',y='Manager',orientation='h',template='gridon',text='Sum',
            labels={'Sum':'Sum of Sales','Numbers':'Number of Sales'},hover_data=['Numbers'])
        fig.update_traces(marker_color='turquoise',texttemplate='%{text:.2s}', textposition='inside')
        fig.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')
        return fig
    else:
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        cur.execute(
        '''
            ;with cte as (
            select customer_id,order_date,order_id  
            from 'public.orders' o
            where order_date between ? and ?
            )
            select company_name ,country, round(sum(unit_price*quantity),2),count(cte.order_id)
            from 'public.customers' c 
            join cte on cte.customer_id=c.customer_id 
            join 'public.order_details' od on cte.order_id=od.order_id 
            group by company_name ,country
            order by 3 desc
            limit 4
        ''',(start_date, end_date))

        result = cur.fetchall()
        df = pd.DataFrame(result,columns=['company_name','country','sum','count'])
        df['place'] = range(1,len(df)+1)
        fig = px.bar(data_frame=df,x='place',y='sum',text='company_name',
            hover_data=['count','country'],
            labels={'sum':'Purchase Amount','count':'number of orders','company_name':'Company Name','place':'the Best Customers'})
        fig.update_traces(marker_color='orange')
        fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide',plot_bgcolor = 'white')
        return fig

# ----------------------------------------------------------------
@app.callback(
    Output(component_id='top-product',component_property='figure'),
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date'),
    Input(component_id='radio-top-product',component_property='value')]
)
def update_chart_managers(start_date, end_date, radio_value):
    if radio_value == 'best_sales':
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        cur.execute(
        '''
            ;with cte as (
            select order_id, order_date  
            from 'public.orders' o
            where order_date between ? and ?
            )
            select product_name,category_name,round(sum(od.unit_price*quantity),2) as sum,sum(quantity) as quantity
            from 'public.products' p
            join 'public.categories' c on p.category_id=c.category_id 
            join 'public.order_details' od on od.product_id=p.product_id
            join cte on cte.order_id=od.order_id
            group by product_name,category_name
            order by quantity desc
            limit 8
        ''',(start_date, end_date))

        result = cur.fetchall()
        df = pd.DataFrame(result,columns=['product_name','category_name','sum_of_sales','quantity_sold'])
        df['place'] = range(1,len(df)+1)
        fig = px.bar(data_frame=df,y='place',x='quantity_sold',orientation='h',template='gridon',text='product_name',
            hover_data=['category_name','sum_of_sales'],labels={'quantity_sold':'Quantity Sold','place':'TOP 8 Products'})
        fig.update_traces(marker_color='turquoise', textposition='inside')
        fig.update_layout(uniformtext_minsize=4, uniformtext_mode='hide')
        return fig
    else:
        con = sqlite3.connect('data.sqlite')
        cur = con.cursor()
        cur.execute(
        '''
            ;with cte as (
            select order_id, order_date  
            from 'public.orders' o
            where order_date between ? and ?
            )
            select category_name,round(sum(od.unit_price*quantity),2) as sum
            from 'public.categories' c
            join 'public.products' p on p.category_id=c.category_id 
            join 'public.order_details' od on od.product_id=p.product_id
            join cte on cte.order_id=od.order_id
            group by category_name
            order by sum desc
        ''',(start_date, end_date))
        result = cur.fetchall()
        df = pd.DataFrame(result,columns=['category_name','sum_of_sales'])
        fig = px.bar(data_frame=df,y='category_name',x='sum_of_sales',orientation='h',text='sum_of_sales',
            labels={'category_name':'Category Name','sum_of_sales':'Sum of Sales'})
        fig.update_traces(marker_color='orange',texttemplate='%{text:.2s}', textposition='inside')
        fig.update_layout(uniformtext_minsize=4, uniformtext_mode='hide',plot_bgcolor = 'white')
        return fig

# ----------------------------------------------------------------
@app.callback(
    Output(component_id='icicle',component_property='figure'),
    [Input(component_id='start-date',component_property='date'),
    Input(component_id='end-date',component_property='date')]
)
def update_icicle(start_date, end_date):
    con = sqlite3.connect('data.sqlite')
    cur = con.cursor()
    cur.execute(
    '''
        ;with cte as (
        select order_id, order_date  
        from 'public.orders' o
        where order_date between ? and ?
        )
        select company_name, ship_country, round(sum(freight),2) as freight
        from 'public.shippers' s
        join 'public.orders' o on o.ship_via=s.shipper_id 
        join cte on cte.order_id=o.order_id
        group by 1,2
    ''',(start_date, end_date))
    result = cur.fetchall()
    df = pd.DataFrame(result,columns=['company_name','ship_country','freight'])
    fig = px.icicle(data_frame=df,path=[px.Constant("All Shipper Companies"), 'company_name', 'ship_country'],values='freight',
        template='gridon',color_discrete_sequence=px.colors.qualitative.Pastel)
    fig.update_traces(textinfo='label+percent entry')
    fig.update_layout(margin={'t':0,'b':0,'l':0,'r':0})
    return fig

if __name__=='__main__':
    app.run_server(debug=True)