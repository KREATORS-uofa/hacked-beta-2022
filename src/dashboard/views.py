from django.shortcuts import render
import folium, geocoder
from folium import plugins
from .models import Data
from django.http import Http404


def sum(request):
    print("im sum")
    data_list = Data.objects.values_list('latitude','longitude','sum')
    map = folium.Map(location=[53.544389,-113.4909],zoom_start=6)
    plugins.HeatMap(data_list).add_to(map)
    plugins.Fullscreen(position = 'topright').add_to(map)
    map = map._repr_html_()
    context ={
    'map':map
    }
    return render(request, "dashboard/index.html", context)

# -*- coding: utf-8 -*-
"""
Team Name: KANDY
Date: November 06, 2022
Project: Analyzing Information on Car Collision in Canada
Competition: HACKED(beata) 2022 at the University of Alberta
Author: Min Joh
Team Members: Min Joh, Jamie Lee, Taekwan Yoon, Yongbin Kim, Dohyun Kim

Description of file:
This Python File predicts of the number of collisions in Canada from 2020 to 2022. Data is referenced from National
Collision Database Online, and used to train Facebook Prophet model. The Facebook Prophet model "works best with time
series that have strong seasonal effects and several seasons of historical data." Hence, this model is selected. This
Python file is referred to the Jupyter Notebook in the same folder with this file. This file renders an interactive plot
on a webpage.
"""

import os                               # data load module
import pandas as pd                     # dataframe module
from fbprophet import Prophet           # prediction model
import plotly.graph_objects as go       # plot module
from plotly.offline import plot         # rendering module
from django.shortcuts import render     # rendering module


def load_data(folder_path, filename):
    """ load data """
    data = os.path.join(folder_path, filename)
    dataframe = pd.read_csv(data)
    return dataframe


def make_prophet_dataframe(dataframe, column_name):
    """ create dataframe for Prophet prediction model """
    df = pd.DataFrame()
    df['ds'] = dataframe['Date']
    df['y'] = dataframe[column_name]
    return df


def forecast(dataframe):
    """ train model """
    model = Prophet(growth='linear',
                    changepoint_prior_scale=0.05,  # flexibility
                    changepoint_range=0.80,  # percentage of size of training set
                    daily_seasonality=False,
                    weekly_seasonality=False, )
    model.fit(dataframe)

    ''' create forecast dataframe '''
    future = model.make_future_dataframe(periods=36, freq='MS')  # predict 36 months
    forecast = model.predict(future)
    return model, forecast


def index(request):
    """ loading data """
    data_path = '../datasets/'
    collision_df = load_data(data_path, 'alberta_collision_statistics.csv')
    print("Raw data has successfully been imported.")

    """ data frame modification """
    # collision_df.insert(0, "Date", pd.to_datetime(collision_df['Year'].astype(str) + collision_df['Month'].astype(str), format='%Y%B'))
    print("Collision data frame has successfully been created.")

    """ prediction """
    df = make_prophet_dataframe(collision_df, 'Total Collsions')
    [model, forecast] = forecast(df)
    print("Prediction has successfully been completed.")

    """ plot data """
    fig = go.Figure()

    # Actual Data
    fig.add_trace(go.Scatter(
        x=collision_df['Date'], y=collision_df['Total Collsions'],
        mode='lines',
        name="actual",
        line=dict(color='#2B616D'),  # dark teal
        hovertemplate=""
    ))

    # Predicted Data
    fig.add_trace(go.Scatter(
        x=forecast['ds'], y=forecast['yhat'],
        mode='lines',
        name="predicted",
        line=dict(color='#FFB52E'),  # bright orange
        hovertemplate=""
    ))

    # plot style
    fig.update_layout(
        # title
        title=dict(
            text="Number of Collisions in Alberta",
        ),
        # x-axis
        xaxis=dict(
            title="Time",
            showline=True,
            linewidth=1,
            linecolor='black',
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(count=5, label="5y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            ),
        ),
        # y-axis
        yaxis=dict(
            title="Number of Collisions",
            showline=True,
            fixedrange=False,
            linewidth=1,
            linecolor='black',
            exponentformat='none'
        ),
        # plot background
        plot_bgcolor='white',
        # label mode
        hovermode='x',
        showlegend=True
    )

    print("Figure has been created.")
    #fig.show()
    plot_div = plot({'data': fig}, output_type='div')
    return render(request, 'templates/partials/base.html', context={'plot_div': plot_div})
