# -*- coding: utf-8 -*-
"""METRICS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1L78bqwUCI5fD90ZFudHX_ZooObj8rdMz
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
# %matplotlib inline
from scipy import stats
import pandas as pd 
import multiprocessing
import random

from matplotlib import rc
from sklearn.preprocessing import scale
from sklearn.preprocessing import OneHotEncoder
import timeit
import itertools
import seaborn as sns
from collections import Counter
import operator

import seaborn as sns
from __future__ import division

import plotly.offline as pyoff
import plotly.graph_objs as go

from google.colab import drive
drive.mount('/content/drive')

"""## LOAD EVENTOS"""

txt_event = '/content/drive/My Drive/TFM/03_DATASETS/eventos_2.rpt'
widths=[10,39,12,16,12,39,20,10,41,16,50,39,17,18,39,41,41,41,41,41,30,39] 

dfevent = pd.read_fwf(txt_event, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfevent.shape
dfevent=dfevent[0:(rowcl-3)]

new_header = ['TipoEvento','CodigoEvento','FechaEvento','UsuarioEvento','HoraEvento','ClienteEvento','CodigoPostalEvento','PaísEvento','RepresentanteEvento','TipoPortesEvento','FormaPagoEvento','PlazoPagoEvento','SkuArticuloEvento','TipoArticuloEvento','FamiliaArticuloEvento','SubfamiliaArticuloEvento','CantidadArticuloEvento','AlmacenArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento','MotivoEvento','CosteEvento']
dfevent.columns = new_header
dfevent

#vamos a utilizar solo los últimos dos años
dfevent = dfevent[(dfevent['FechaEvento'] >= '2009-01-07') &
          (dfevent['FechaEvento'] <= '2019-12-31')]

#eliminamos los eventos que sean una oferta
indexNames = dfevent[ dfevent['TipoEvento'] == 'OFERTA' ].index
# Delete these row indexes from dataFrame
dfevent.drop(indexNames , inplace=True)

events= dfevent.sort_values(by=['FechaEvento'])

events['ClienteEvento'] = events.ClienteEvento.map(lambda x: str(x)[:-2])

events = events[['ClienteEvento','FechaEvento','CodigoEvento','CantidadArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento']]

events.info()

# Load the dataset CLIENTES
txt_client = '/content/drive/My Drive/TFM/03_DATASETS/clientes.rpt'

widths = [40, 31, 16, 21, 12, 51, 17, 40, 40, 15, 50]

dfclient = pd.read_fwf(txt_client, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfclient.shape
dfclient=dfclient[0:(rowcl-3)]

new_header = ['CodigoCliente','NombreCliente','NIFCliente','CodigoPostalCliente','PaisCliente','SegmentoCliente','FechaAltaCliente','RepresentanteCliente','AreaCliente','MercadoCliente','GrupoDescuentoCliente']

dfclient.columns = new_header
clientes = dfclient

id_nombre = clientes[['CodigoCliente','NombreCliente','PaisCliente', 'SegmentoCliente']]

events = events.merge(id_nombre,left_on='ClienteEvento', right_on='CodigoCliente')

events

"""## KNOW EMUCA METRICS

### Yearly revenues
"""

#converting the type of Invoice Date Field from string to datetime.
events['FechaEvento'] = pd.to_datetime(events['FechaEvento'])

#creating YearMonth field for the ease of reporting and visualization
events['InvoiceYear'] = events['FechaEvento'].map(lambda date: date.year)

#calculate Revenue for each row and create a new dataframe with YearMonth - Revenue columns
events['Revenue'] = events["CantidadArticuloEvento"] * events["TarifaArticuloEvento"] * (100 - events["DescuentoArticuloEvento"])/100
tx_revenue = events.groupby(['InvoiceYear'])['Revenue'].sum().reset_index()
tx_revenue

#X and Y axis inputs for Plotly graph. We use Scatter for line graphs
plot_data = [
    go.Scatter(
        x=tx_revenue['InvoiceYear'],
        y=tx_revenue['Revenue'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Revenue'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### Yearly Revenue Growth Rate"""

#using pct_change() function to see monthly percentage change
tx_revenue['YearlyGrowth'] = tx_revenue['Revenue'].pct_change()

#showing first 5 rows
tx_revenue.head()

#visualization - line graph
plot_data = [
    go.Scatter(
        x=tx_revenue.query("InvoiceYear <= 2020")['InvoiceYear'],
        y=tx_revenue.query("InvoiceYear <= 2020")['YearlyGrowth'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Growth Rate'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### Yearly active customers"""

#creating a new dataframe with España customers only
#tx_es = tx_data.query("PaisEvento=='ES'").reset_index(drop=True)

#creating monthly active customers dataframe by counting unique Customer IDs
tx_yearly_active = events.groupby('InvoiceYear')['ClienteEvento'].nunique().reset_index()

#print the dataframe
tx_yearly_active

#plotting the output
plot_data = [
    go.Bar(
        x=tx_yearly_active['InvoiceYear'],
        y=tx_yearly_active['ClienteEvento'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Active Customers'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### Yearly orders count"""

#create a new dataframe for no. of order by using quantity field
tx_yearly_sales = events.groupby('InvoiceYear')['CantidadArticuloEvento'].sum().reset_index()

#print the dataframe
tx_yearly_sales

#plot
plot_data = [
    go.Bar(
        x=tx_yearly_sales['InvoiceYear'],
        y=tx_yearly_sales['CantidadArticuloEvento'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Total Number of Orders'
    )

fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### Average Revenue per Order"""

# create a new dataframe for average revenue by taking the mean of it
tx_yearly_order_avg = events.groupby('InvoiceYear')['Revenue'].mean().reset_index()

#print the dataframe
tx_yearly_order_avg

#plot the bar chart
plot_data = [
    go.Bar(
        x=tx_yearly_order_avg['InvoiceYear'],
        y=tx_yearly_order_avg['Revenue'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Order Average'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### New Customer ratio"""

#consideramos cliente nuevo cuando se realiza la primera compra en el periodo temporal establecido

#create a dataframe contaning ClienteEvento and first purchase date
tx_min_purchase = events.groupby('ClienteEvento').FechaEvento.min().reset_index()
tx_min_purchase.columns = ['ClienteEvento','MinPurchaseDate']
tx_min_purchase['MinPurchaseYear'] = tx_min_purchase['MinPurchaseDate'].map(lambda date: date.year)

#merge first purchase date column to our main dataframe (events)
events = pd.merge(events, tx_min_purchase, on='ClienteEvento')

events.head()

#create a column called User Type and assign Existing 
#if User's First Purchase Year Month before the selected Invoice Year Month
events['UserType'] = 'New'
events.loc[events['InvoiceYear']>events['MinPurchaseYear'],'UserType'] = 'Existing'

#calculate the Revenue per month for each user type
tx_user_type_revenue = events.groupby(['InvoiceYear','UserType'])['Revenue'].sum().reset_index()

#filtering the dates and plot the result
plot_data = [
    go.Scatter(
        x=tx_user_type_revenue.query("UserType == 'Existing'")['InvoiceYear'],
        y=tx_user_type_revenue.query("UserType == 'Existing'")['Revenue'],
        name = 'Existing'
    ),
    go.Scatter(
        x=tx_user_type_revenue.query("UserType == 'New'")['InvoiceYear'],
        y=tx_user_type_revenue.query("UserType == 'New'")['Revenue'],
        name = 'New'
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='New vs Existing'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#LET'S HAVE A BETTER VIEW TO OUR NEW CUSTOMER RATIO


#create a dataframe that shows new user ratio - we also need to drop NA values (first month new user ratio is 0)
tx_user_ratio = events.query("UserType == 'New'").groupby(['InvoiceYear'])['ClienteEvento'].nunique()/events.query("UserType == 'Existing'").groupby(['InvoiceYear'])['ClienteEvento'].nunique()
tx_user_ratio = tx_user_ratio.reset_index()
tx_user_ratio = tx_user_ratio.dropna()

#print the dafaframe
tx_user_ratio

#plot the result

plot_data = [
    go.Bar(
        x=tx_user_ratio.query("InvoiceYear>=2009 and InvoiceYear<=2020")['InvoiceYear'],
        y=tx_user_ratio.query("InvoiceYear>=2009 and InvoiceYear<=2020")['ClienteEvento'],
    )
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='New Customer Ratio'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""### Yearly retention rate

Yearly Retention Rate = Retained Customers From Prev. year/Active Customers Total
"""

#identify which users are active by looking at their revenue per month
tx_user_purchase = events.groupby(['ClienteEvento','InvoiceYear'])['Revenue'].sum().reset_index()

#create retention matrix with crosstab
tx_retention = pd.crosstab(tx_user_purchase['ClienteEvento'], tx_user_purchase['InvoiceYear']).reset_index()

tx_retention.head()

#create an array of dictionary which keeps Retained & Total User count for each month
months = tx_retention.columns[2:]
retention_array = []
for i in range(len(months)-1):
    retention_data = {}
    selected_month = months[i+1]
    prev_month = months[i]
    retention_data['InvoiceYear'] = int(selected_month)
    retention_data['TotalUserCount'] = tx_retention[selected_month].sum()
    retention_data['RetainedUserCount'] = tx_retention[(tx_retention[selected_month]>0) & (tx_retention[prev_month]>0)][selected_month].sum()
    retention_array.append(retention_data)
    
#convert the array to dataframe and calculate Retention Rate
tx_retention = pd.DataFrame(retention_array)
tx_retention['RetentionRate'] = tx_retention['RetainedUserCount']/tx_retention['TotalUserCount']

#plot the retention rate graph
plot_data = [
    go.Scatter(
        x=tx_retention.query("InvoiceYear<=2020")['InvoiceYear'],
        y=tx_retention.query("InvoiceYear<=2020")['RetentionRate'],
        name="organic"
    )
    
]

plot_layout = go.Layout(
        xaxis={"type": "category"},
        title='Yearly Retention Rate'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""## PREDICTING NEXT PURCHASE DAY"""

import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split

import xgboost as xgb
from sklearn.cluster import KMeans

events= dfevent.sort_values(by=['FechaEvento'])
events['ClienteEvento'] = events.ClienteEvento.map(lambda x: str(x)[:-2])

events = events.merge(id_nombre,left_on='ClienteEvento', right_on='CodigoCliente')
events = events[['ClienteEvento','FechaEvento','CodigoEvento','CantidadArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento']]
events['FechaEvento'] = pd.to_datetime(events['FechaEvento'])
events['ClienteEvento'] = events['ClienteEvento'].astype(int)
events

"""We use six months of behavioral data to predict customers’ first purchase date in the next three months. If there is no purchase, we will predict that too. Let’s assume our cut off date is 1st october 2019 and split the data:"""

tx_6m = events[(events.FechaEvento < '2019-10-01') & (events.FechaEvento >= '2019-04-01')].reset_index(drop=True)
tx_next = events[(events.FechaEvento >= '2019-10-01') & (events.FechaEvento < '2019-12-31')].reset_index(drop=True)

"""tx_6m represents the six months performance whereas we will use tx_next for the find out the days between the last purchase date in tx_6m and the first one in tx_next."""

#Also, we will create a dataframe called tx_user to possess a user-level feature set for the prediction model:
tx_user = pd.DataFrame(tx_6m['ClienteEvento'].unique())
tx_user.columns = ['ClienteEvento']

#create a dataframe with customer id and first purchase date in tx_next
tx_next_first_purchase = tx_next.groupby('ClienteEvento').FechaEvento.min().reset_index()
tx_next_first_purchase.columns = ['ClienteEvento','MinPurchaseDate']

#create a dataframe with customer id and last purchase date in tx_6m
tx_last_purchase = tx_6m.groupby('ClienteEvento').FechaEvento.max().reset_index()
tx_last_purchase.columns = ['ClienteEvento','MaxPurchaseDate']

#merge two dataframes
tx_purchase_dates = pd.merge(tx_last_purchase,tx_next_first_purchase,on='ClienteEvento',how='left')

#calculate the time difference in days:
tx_purchase_dates['NextPurchaseDay'] = (tx_purchase_dates['MinPurchaseDate'] - tx_purchase_dates['MaxPurchaseDate']).dt.days

#merge with tx_user 
tx_user = pd.merge(tx_user, tx_purchase_dates[['ClienteEvento','NextPurchaseDay']],on='ClienteEvento',how='left')

#print tx_user
tx_user.head()

#fill NA values with 999. we have NaN values because those customers haven’t made any purchase yet. We fill NaN with 999 to quickly identify them later.
tx_user = tx_user.fillna(999)

tx_user.head()

"""### Feature Engineering

For this project, we have selected our feature candidates like below:
- RFM scores & clusters
- Days between the last three purchases
- Mean & standard deviation of the difference between purchases in days
"""

#get max purchase date for Recency and create a dataframe
tx_max_purchase = tx_6m.groupby('ClienteEvento').FechaEvento.max().reset_index()
tx_max_purchase.columns = ['ClienteEvento','MaxPurchaseDate']

#find the recency in days and add it to tx_user
tx_max_purchase['Recency'] = (tx_max_purchase['MaxPurchaseDate'].max() - tx_max_purchase['MaxPurchaseDate']).dt.days
tx_user = pd.merge(tx_user, tx_max_purchase[['ClienteEvento','Recency']], on='ClienteEvento')

#plot recency
plot_data = [
    go.Histogram(
        x=tx_user['Recency']
    )
]

plot_layout = go.Layout(
        title='Recency'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#clustering for Recency
kmeans = KMeans(n_clusters=4)
kmeans.fit(tx_user[['Recency']])
tx_user['RecencyCluster'] = kmeans.predict(tx_user[['Recency']])

#order cluster method
def order_cluster(cluster_field_name, target_field_name,df,ascending):
    new_cluster_field_name = 'new_' + cluster_field_name
    df_new = df.groupby(cluster_field_name)[target_field_name].mean().reset_index()
    df_new = df_new.sort_values(by=target_field_name,ascending=ascending).reset_index(drop=True)
    df_new['index'] = df_new.index
    df_final = pd.merge(df,df_new[[cluster_field_name,'index']], on=cluster_field_name)
    df_final = df_final.drop([cluster_field_name],axis=1)
    df_final = df_final.rename(columns={"index":cluster_field_name})
    return df_final


#order recency clusters
tx_user = order_cluster('RecencyCluster', 'Recency',tx_user,False)

#print cluster characteristics
tx_user.groupby('RecencyCluster')['Recency'].describe()


#get total purchases for frequency scores
tx_frequency = tx_6m.groupby('ClienteEvento').FechaEvento.count().reset_index()
tx_frequency.columns = ['ClienteEvento','Frequency']

#add frequency column to tx_user
tx_user = pd.merge(tx_user, tx_frequency, on='ClienteEvento')

#plot frequency
plot_data = [
    go.Histogram(
        x=tx_user.query('Frequency < 10000')['Frequency']
    )
]

plot_layout = go.Layout(
        title='Frequency'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#clustering for frequency
kmeans = KMeans(n_clusters=4)
kmeans.fit(tx_user[['Frequency']])
tx_user['FrequencyCluster'] = kmeans.predict(tx_user[['Frequency']])

#order frequency clusters and show the characteristics
tx_user = order_cluster('FrequencyCluster', 'Frequency',tx_user,True)
tx_user.groupby('FrequencyCluster')['Frequency'].describe()


#calculate monetary value, create a dataframe with it
tx_6m['Revenue'] = tx_6m["CantidadArticuloEvento"] * tx_6m["TarifaArticuloEvento"] * (100 - tx_6m["DescuentoArticuloEvento"])/100
tx_revenue = tx_6m.groupby('ClienteEvento').Revenue.sum().reset_index()

#add Revenue column to tx_user
tx_user = pd.merge(tx_user, tx_revenue, on='ClienteEvento')

#plot Revenue
plot_data = [
    go.Histogram(
        x=tx_user.query('Revenue < 100000')['Revenue']
    )
]

plot_layout = go.Layout(
        title='Monetary Value'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#Revenue clusters 
kmeans = KMeans(n_clusters=4)
kmeans.fit(tx_user[['Revenue']])
tx_user['RevenueCluster'] = kmeans.predict(tx_user[['Revenue']])

#ordering clusters and who the characteristics
tx_user = order_cluster('RevenueCluster', 'Revenue',tx_user,True)
tx_user.groupby('RevenueCluster')['Revenue'].describe()


#building overall segmentation
tx_user['OverallScore'] = tx_user['RecencyCluster'] + tx_user['FrequencyCluster'] + tx_user['RevenueCluster']

#assign segment names
tx_user['Segment'] = 'Low-Value'
tx_user.loc[tx_user['OverallScore']>2,'Segment'] = 'Mid-Value' 
tx_user.loc[tx_user['OverallScore']>4,'Segment'] = 'High-Value' 

#plot revenue vs frequency
tx_graph = tx_user.query("Revenue < 500000 and Frequency < 20000")

plot_data = [
    go.Scatter(
        x=tx_graph.query("Segment == 'Low-Value'")['Frequency'],
        y=tx_graph.query("Segment == 'Low-Value'")['Revenue'],
        mode='markers',
        name='Low',
        marker= dict(size= 7,
            line= dict(width=1),
            color= 'blue',
            opacity= 0.8
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'Mid-Value'")['Frequency'],
        y=tx_graph.query("Segment == 'Mid-Value'")['Revenue'],
        mode='markers',
        name='Mid',
        marker= dict(size= 9,
            line= dict(width=1),
            color= 'green',
            opacity= 0.5
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'High-Value'")['Frequency'],
        y=tx_graph.query("Segment == 'High-Value'")['Revenue'],
        mode='markers',
        name='High',
        marker= dict(size= 11,
            line= dict(width=1),
            color= 'red',
            opacity= 0.9
           )
    ),
]

plot_layout = go.Layout(
        yaxis= {'title': "Revenue"},
        xaxis= {'title': "Frequency"},
        title='Segments'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#plot revenue vs recency
tx_graph = tx_user.query("Revenue < 500000 and Frequency < 20000")

plot_data = [
    go.Scatter(
        x=tx_graph.query("Segment == 'Low-Value'")['Recency'],
        y=tx_graph.query("Segment == 'Low-Value'")['Revenue'],
        mode='markers',
        name='Low',
        marker= dict(size= 7,
            line= dict(width=1),
            color= 'blue',
            opacity= 0.8
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'Mid-Value'")['Recency'],
        y=tx_graph.query("Segment == 'Mid-Value'")['Revenue'],
        mode='markers',
        name='Mid',
        marker= dict(size= 9,
            line= dict(width=1),
            color= 'green',
            opacity= 0.5
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'High-Value'")['Recency'],
        y=tx_graph.query("Segment == 'High-Value'")['Revenue'],
        mode='markers',
        name='High',
        marker= dict(size= 11,
            line= dict(width=1),
            color= 'red',
            opacity= 0.9
           )
    ),
]

plot_layout = go.Layout(
        yaxis= {'title': "Revenue"},
        xaxis= {'title': "Recency"},
        title='Segments'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#plot frequency vs recency
tx_graph = tx_user.query("Revenue < 500000 and Frequency < 20000")

plot_data = [
    go.Scatter(
        x=tx_graph.query("Segment == 'Low-Value'")['Recency'],
        y=tx_graph.query("Segment == 'Low-Value'")['Frequency'],
        mode='markers',
        name='Low',
        marker= dict(size= 7,
            line= dict(width=1),
            color= 'blue',
            opacity= 0.8
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'Mid-Value'")['Recency'],
        y=tx_graph.query("Segment == 'Mid-Value'")['Frequency'],
        mode='markers',
        name='Mid',
        marker= dict(size= 9,
            line= dict(width=1),
            color= 'green',
            opacity= 0.5
           )
    ),
        go.Scatter(
        x=tx_graph.query("Segment == 'High-Value'")['Recency'],
        y=tx_graph.query("Segment == 'High-Value'")['Frequency'],
        mode='markers',
        name='High',
        marker= dict(size= 11,
            line= dict(width=1),
            color= 'red',
            opacity= 0.9
           )
    ),
]

plot_layout = go.Layout(
        yaxis= {'title': "Frequency"},
        xaxis= {'title': "Recency"},
        title='Segments'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

#create a dataframe with CustomerID and Invoice Date
tx_day_order = tx_6m[['ClienteEvento','FechaEvento']]
#convert Invoice Datetime to day
tx_day_order['FechaEvento'] = tx_6m['FechaEvento'].dt.date
tx_day_order = tx_day_order.sort_values(['ClienteEvento','FechaEvento'])
#drop duplicates
tx_day_order = tx_day_order.drop_duplicates(subset=['ClienteEvento','FechaEvento'],keep='first')

#shifting last 3 purchase dates
tx_day_order['PrevInvoiceDate'] = tx_day_order.groupby('ClienteEvento')['FechaEvento'].shift(1)
tx_day_order['T2InvoiceDate'] = tx_day_order.groupby('ClienteEvento')['FechaEvento'].shift(2)
tx_day_order['T3InvoiceDate'] = tx_day_order.groupby('ClienteEvento')['FechaEvento'].shift(3)

tx_day_order.head()

#Let’s begin calculating the difference in days for each invoice date:
tx_day_order['DayDiff'] = (tx_day_order['FechaEvento'] - tx_day_order['PrevInvoiceDate']).dt.days
tx_day_order['DayDiff2'] = (tx_day_order['FechaEvento'] - tx_day_order['T2InvoiceDate']).dt.days
tx_day_order['DayDiff3'] = (tx_day_order['FechaEvento'] - tx_day_order['T3InvoiceDate']).dt.days

tx_day_order.head()

tx_day_diff = tx_day_order.groupby('ClienteEvento').agg({'DayDiff': ['mean','std']}).reset_index()
tx_day_diff.columns = ['ClienteEvento', 'DayDiffMean','DayDiffStd']

"""We only keep customers who have > 3 purchases by using the following line:"""

tx_day_order_last = tx_day_order.drop_duplicates(subset=['ClienteEvento'],keep='last')

tx_day_order_last = tx_day_order_last.dropna()
tx_day_order_last = pd.merge(tx_day_order_last, tx_day_diff, on='ClienteEvento')
tx_user = pd.merge(tx_user, tx_day_order_last[['ClienteEvento','DayDiff','DayDiff2','DayDiff3','DayDiffMean','DayDiffStd']], on='ClienteEvento')
#create tx_class as a copy of tx_user before applying get_dummies
tx_class = tx_user.copy()
tx_class = pd.get_dummies(tx_class)

tx_user.NextPurchaseDay.describe()

"""- 0–20: Customers that will purchase in 0–20 days — Class name: 2
- 21–49: Customers that will purchase in 21–49 days — Class name: 1
- ≥ 50: Customers that will purchase in more than 50 days — Class name: 0
"""

tx_class['NextPurchaseDayRange'] = 2
tx_class.loc[tx_class.NextPurchaseDay>20,'NextPurchaseDayRange'] = 1
tx_class.loc[tx_class.NextPurchaseDay>50,'NextPurchaseDayRange'] = 0

tx_class.info()

tx_class.head()

tx_class.groupby('NextPurchaseDayRange').size()

#Correlation Matrix FOCUSED ON NEXT PURCHASE DAY RANGE
corr = tx_class[tx_class.columns].corr()
plt.figure(figsize = (30,20))
sns.heatmap(corr, annot = True, linewidths=0.2, fmt=".2f")

#import machine learning related libraries
from sklearn.svm import SVC
from sklearn.multioutput import MultiOutputClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
import xgboost as xgb
from sklearn.model_selection import KFold, cross_val_score, train_test_split

"""we want to use the model which gives the highest accuracy. Let’s split train and test tests and measure the accuracy of different models:"""

#CROSS VALIDATION

#train & test split
tx_class = tx_class.drop('NextPurchaseDay',axis=1)
X, y = tx_class.drop('NextPurchaseDayRange',axis=1), tx_class.NextPurchaseDayRange
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=44)

#create an array of models
models = []
models.append(("LR",LogisticRegression()))
models.append(("NB",GaussianNB()))
models.append(("RF",RandomForestClassifier()))
models.append(("SVC",SVC()))
models.append(("Dtree",DecisionTreeClassifier()))
models.append(("XGB",xgb.XGBClassifier()))
models.append(("KNN",KNeighborsClassifier()))

#measure the accuracy 
for name,model in models:
    kfold = KFold(n_splits=2, random_state=22)
    cv_result = cross_val_score(model,X_train,y_train, cv = kfold,scoring = "accuracy")
    print(name, cv_result)

"""From this result, we see that XGBoost is the best performing one.

### Multi-Classification Model
"""

xgb_model = xgb.XGBClassifier().fit(X_train, y_train)
print('Accuracy of XGB classifier on training set: {:.2f}'
       .format(xgb_model.score(X_train, y_train)))
print('Accuracy of XGB classifier on test set: {:.2f}'
       .format(xgb_model.score(X_test[X_train.columns], y_test)))

"""XGBClassifier has many parameters. The code below will generate the best values for these parameters:"""

from sklearn.model_selection import GridSearchCV
param_test1 = {
 'max_depth':range(3,10,2),
 'min_child_weight':range(1,6,2)
}
gsearch1 = GridSearchCV(estimator = xgb.XGBClassifier(), 
param_grid = param_test1, scoring='accuracy',n_jobs=-1,iid=False, cv=2)
gsearch1.fit(X_train,y_train)
gsearch1.best_params_, gsearch1.best_score_

xgb_model = xgb.XGBClassifier(max_depth=3,min_child_weight=1).fit(X_train, y_train)
print('Accuracy of XGB classifier on training set: {:.2f}'
       .format(xgb_model.score(X_train, y_train)))
print('Accuracy of XGB classifier on test set: {:.2f}'
       .format(xgb_model.score(X_test[X_train.columns], y_test)))

"""# PREDICTING SALES"""

# Commented out IPython magic to ensure Python compatibility.
from datetime import datetime, timedelta,date
import pandas as pd
# %matplotlib inline
import matplotlib.pyplot as plt
import numpy as np
from __future__ import division

import warnings
warnings.filterwarnings("ignore")


import plotly.offline as pyoff
import plotly.graph_objs as go

#import Keras
import keras
from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import Adam 
from keras.callbacks import EarlyStopping
from keras.utils import np_utils
from keras.layers import LSTM
from sklearn.model_selection import KFold, cross_val_score, train_test_split

events= dfevent.sort_values(by=['FechaEvento'])
events['ClienteEvento'] = events.ClienteEvento.map(lambda x: str(x)[:-2])
events = events.merge(id_nombre,left_on='ClienteEvento', right_on='CodigoCliente')
events = events[['ClienteEvento','FechaEvento','CodigoEvento','CantidadArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento']]
events['FechaEvento'] = pd.to_datetime(events['FechaEvento'])
events['sales'] = events["CantidadArticuloEvento"] * events["TarifaArticuloEvento"] * (100 - events["DescuentoArticuloEvento"])/100
events

#represent month in date field as its first day
events['date'] = events['FechaEvento'].dt.year.astype('str') + '-' + events['FechaEvento'].dt.month.astype('str') + '-01'
events['date'] = pd.to_datetime(events['date'])
#groupby date and sum the sales
df_sales = events.groupby('date').sales.sum().reset_index()

df_sales.head(10)

"""- We will convert the data to stationary if it is not
- Converting from time series to supervised for having the feature set of our LSTM model
- Scale the data
"""

#plot monthly sales
plot_data = [
    go.Scatter(
        x=df_sales['date'],
        y=df_sales['sales'],
    )
]
plot_layout = go.Layout(
        title='Montly Sales'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""Obviously, it is not stationary and has an increasing trend over the months. One method is to get the difference in sales compared to the previous month and build the model on it"""

#create a new dataframe to model the difference
df_diff = df_sales.copy()
#add previous sales to the next row
df_diff['prev_sales'] = df_diff['sales'].shift(1)
#drop the null values and calculate the difference
df_diff = df_diff.dropna()
df_diff['diff'] = (df_diff['sales'] - df_diff['prev_sales'])
df_diff.head(10)

#plot sales diff
plot_data = [
    go.Scatter(
        x=df_diff['date'],
        y=df_diff['diff'],
    )
]
plot_layout = go.Layout(
        title='Montly Sales Diff'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)

"""Now we can start building our feature set. We need to use previous monthly sales data to forecast the next ones. The look-back period may vary for every model. Ours will be 12 for this example."""

#create dataframe for transformation from time series to supervised
df_supervised = df_diff.drop(['prev_sales'],axis=1)
#adding lags
for inc in range(1,13):
    field_name = 'lag_' + str(inc)
    df_supervised[field_name] = df_supervised['diff'].shift(inc)
#drop null values
df_supervised = df_supervised.dropna().reset_index(drop=True)

df_supervised

"""How useful are our features for prediction?
Adjusted R-squared is the answer. It tells us how good our features explain the variation in our label (lag_1 to lag_12 for diff, in our example).
"""

# Import statsmodels.formula.api
import statsmodels.formula.api as smf
# Define the regression formula
model = smf.ols(formula='diff ~ lag_1 + lag_2 + lag_3+ lag_4 + lag_5 + lag_6 + lag_7 + lag_8 + lag_9 + lag_10 + lag_11 + lag_12', data=df_supervised)
# Fit the regression
model_fit = model.fit()
# Extract the adjusted r-squared
regression_adj_rsq = model_fit.rsquared_adj
print(regression_adj_rsq)

"""Now we can confidently build our model after scaling our data. But there is one more step before scaling. We should split our data into train and test sets. As the test set, we have selected the last 6 months’ sales."""

#import MinMaxScaler and create a new dataframe for LSTM model
from sklearn.preprocessing import MinMaxScaler
df_model = df_supervised.drop(['sales','date'],axis=1)
#split train and test set
train_set, test_set = df_model[0:-6].values, df_model[-6:].values

"""As the scaler, we are going to use MinMaxScaler, which will scale each future between -1 and 1:"""

#apply Min Max Scaler
scaler = MinMaxScaler(feature_range=(-1, 1))
scaler = scaler.fit(train_set)
# reshape training set
train_set = train_set.reshape(train_set.shape[0], train_set.shape[1])
train_set_scaled = scaler.transform(train_set)
# reshape test set
test_set = test_set.reshape(test_set.shape[0], test_set.shape[1])
test_set_scaled = scaler.transform(test_set)

"""### Build the LSTM Model -> deep learning model"""

X_train, y_train = train_set_scaled[:, 1:], train_set_scaled[:, 0:1]
X_train = X_train.reshape(X_train.shape[0], 1, X_train.shape[1])
X_test, y_test = test_set_scaled[:, 1:], test_set_scaled[:, 0:1]
X_test = X_test.reshape(X_test.shape[0], 1, X_test.shape[1])

#Let’s fit our LSTM model:
model = Sequential()
model.add(LSTM(4, batch_input_shape=(1, X_train.shape[1], X_train.shape[2]), stateful=True))
model.add(Dense(1))
model.compile(loss='mean_squared_error', optimizer='adam')
model.fit(X_train, y_train, epochs=100, batch_size=1, verbose=1, shuffle=False)

#Let’s do the prediction and see how the results look like:
y_pred = model.predict(X_test,batch_size=1)
#for multistep prediction, you need to replace X_test values with the predictions coming from t-1

y_pred

y_test

"""Results look similar but it doesn’t tell us much because these are scaled data that shows the difference. How we can see the actual sales prediction?
First, we need to do the inverse transformation for scaling:
"""

#reshape y_pred
y_pred = y_pred.reshape(y_pred.shape[0], 1, y_pred.shape[1])
#rebuild test set for inverse transform
pred_test_set = []
for index in range(0,len(y_pred)):
    print(np.concatenate([y_pred[index],X_test[index]],axis=1))
    pred_test_set.append(np.concatenate([y_pred[index],X_test[index]],axis=1))
#reshape pred_test_set
pred_test_set = np.array(pred_test_set)
pred_test_set = pred_test_set.reshape(pred_test_set.shape[0], pred_test_set.shape[2])
#inverse transform
pred_test_set_inverted = scaler.inverse_transform(pred_test_set)

y_pred

"""Second, we need to build the dataframe has the dates and the predictions. Transformed predictions are showing the difference. We should calculate the predicted sales numbers:"""

#create dataframe that shows the predicted sales
result_list = []
sales_dates = list(df_sales[-7:].date)
act_sales = list(df_sales[-7:].sales)
for index in range(0,len(pred_test_set_inverted)):
    result_dict = {}
    result_dict['pred_value'] = int(pred_test_set_inverted[index][0] + act_sales[index])
    result_dict['date'] = sales_dates[index+1]
    result_list.append(result_dict)
df_result = pd.DataFrame(result_list)
#for multistep prediction, replace act_sales with the predicted sales

df_result.head(10)

#merge with actual sales dataframe
df_sales_pred = pd.merge(df_sales,df_result,on='date',how='left')
#plot actual and predicted
plot_data = [
    go.Scatter(
        x=df_sales_pred['date'],
        y=df_sales_pred['sales'],
        name='actual'
    ),
        go.Scatter(
        x=df_sales_pred['date'],
        y=df_sales_pred['pred_value'],
        name='predicted'
    )
    
]
plot_layout = go.Layout(
        title='Sales Prediction'
    )
fig = go.Figure(data=plot_data, layout=plot_layout)
pyoff.iplot(fig)