# -*- coding: utf-8 -*-
"""Cross-selling

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1qFWtBEsgX2xciul_njk7-d79r3pXoQD8

# TEST
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

from google.colab import drive
drive.mount('/content/drive')

"""1. Dataframe id evento, cliente, artículo
2. Hacer Dummies de artículo
3. Agrupar por pedido
4. Correlation Matrix
5. Extraer top ventas cruzadas de top artículos
"""

txt_event = '/content/drive/My Drive/TFM/03_DATASETS/eventos_2.rpt'
widths=[10,39,12,16,12,39,20,10,41,16,50,39,17,18,39,41,41,41,41,41,30,39] 

dfevent = pd.read_fwf(txt_event, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfevent.shape
dfevent=dfevent[0:(rowcl-3)]

new_header = ['TipoEvento','CodigoEvento','FechaEvento','UsuarioEvento','HoraEvento','ClienteEvento','CodigoPostalEvento','PaísEvento','RepresentanteEvento','TipoPortesEvento','FormaPagoEvento','PlazoPagoEvento','SkuArticuloEvento','TipoArticuloEvento','FamiliaArticuloEvento','SubfamiliaArticuloEvento','CantidadArticuloEvento','AlmacenArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento','MotivoEvento','CosteEvento']
dfevent.columns = new_header
dfevent

"""Cuántos eventos hay de cada tipo"""

events=dfevent

events=events.groupby(by=['TipoEvento','CodigoEvento'])

events.first()

# Load the dataset 
txt_articulos = '/content/drive/My Drive/TFM/03_DATASETS/articulos.rpt'

widths = [16, 31, 13, 40, 31, 40, 31,40, 40, 40, 40, 19, 18, 40, 40, 18]

dfart= pd.read_fwf(txt_articulos, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfart.shape
dfart=dfart[0:(rowcl-3)]

new_header = ['CodigoArt','Nombre_art','Tipocliente','CodigoFamiliaArt','DescripciónFamiliaArt','CodigoSubFamiliaArt','DescripcionSubfamiliaArticulo','LargoArticulo','AnchoArticulo','AltoArticulo','PesoArticulo','UnidadPesoArticulo','FechaAltaArticulo','UnidadesPorCajaArticulo', 'MargenTarifaArticulo','PaisOrigenArticulo']
#Tipo artículo
dfart.columns = new_header

dfart

"""Mergear eventos y artículos"""

#vamos a utilizar solo los últimos dos años
eventos = dfevent[(dfevent['FechaEvento'] >= '2016-01-01') &
          (dfevent['FechaEvento'] <= '2020-12-31')]

eventos=eventos[eventos['TipoEvento'] == 'PEDIDO']

#Change the name of the column in order to join 
eventos = eventos.rename(columns={'SkuArticuloEvento': 'CodigoArt'})

#Join 'display_name'
eventos=eventos.join(dfart.set_index('CodigoArt')['Nombre_art'], on='CodigoArt')

eventos

eventos.isna().sum()

eventos = eventos[eventos['Nombre_art'].notna()]

eventos

eventos.isna().sum()

"""PROBAR"""

new_df = eventos.merge(eventos, on='CodigoEvento')

cross_sales=new_df[new_df['Nombre_art_x'] < new_df['Nombre_art_y']].groupby(['Nombre_art_x','Nombre_art_y'])['CodigoEvento'].count()

cross_sales.to_csv('/content/drive/My Drive/cross_sales.csv',sep=';',decimal=',')

type(cross_sales)

cross_sales=cross_sales.to_frame(name='Producto')
cross_sales

cross_sales_by_product = pd.read_csv("/content/drive/My Drive/TFM/03_DATASETS/cross_sales.csv",sep=';',decimal=',',index_col=None, header=None)

cross_sales_by_product

new_header_cross_sales = ['art_base','art_complementario','n_pedidos']
#Nombre de las columnas del dataframe de ventas cruzadas
cross_sales_by_product.columns = new_header_cross_sales

cross_sales_by_product

art_most_sold=cross_sales_by_product

grouped_df = art_most_sold.groupby("art_base")

art_most_sold["sum_column"] = grouped_df[["n_pedidos"]].transform(sum)

art_most_sold = art_most_sold.sort_values("sum_column", ascending=False)

#art_most_sold = art_most_sold.drop("sum_column", axis=1)

print(art_most_sold)

df = cross_sales_by_product.sort_values('n_pedidos',ascending=False).head(15)

art_base_top = df.art_base.unique().tolist()
art_base_top

len(df.art_base.unique().tolist())

pd.set_option('display.max_rows', None)

cross_sales_by_product.loc[cross_sales_by_product['art_base'].isin(art_base_top)]

len(cross_sales_by_product.loc[cross_sales_by_product['art_base'].isin(['JG BARANDILLA VANTAGE-Q 500MET'])])

top_art_1=cross_sales_by_product.loc[cross_sales_by_product['art_base'].isin(['JG BARANDILLA VANTAGE-Q 500MET'])]
top_art_1['Frecuencia']=top_art_1['n_pedidos']/top_art_1['sum_column']*100
top_art_1[top_art_1['Frecuencia']>1].sort_values(by='Frecuencia',ascending=False)

top_art_2=cross_sales_by_product.loc[cross_sales_by_product['art_base'].isin(['CAJ VANTAGE-Q EXT T 83x500 GR'])]
top_art_2['Frecuencia']=top_art_2['n_pedidos']/top_art_2['sum_column']*100
top_art_2[top_art_2['Frecuencia']>1].sort_values(by='Frecuencia',ascending=False)

top_art_3=cross_sales_by_product.loc[cross_sales_by_product['art_base'].isin(['GUIA VANTAGE SOFT TEL 500 ZN'])]
top_art_3['Frecuencia']=top_art_3['n_pedidos']/top_art_3['sum_column']*100
top_art_3[top_art_3['Frecuencia']>1].sort_values(by='Frecuencia',ascending=False)

"""# Market Basket Analysis

## Libraries
"""

!pip install pandas==0.21
import pandas as pd

import pandas as pd
from mlxtend.frequent_patterns import apriori
from mlxtend.frequent_patterns import association_rules
import matplotlib.pyplot as plt
from matplotlib import style
import numpy as np

"""## Google Drive"""

from google.colab import drive
drive.mount('/content/drive')

"""## Data Ingestion

### Events
"""

txt_event = '/content/drive/My Drive/TFM/03_DATASETS/eventos_2.rpt'
widths=[10,39,12,16,12,39,20,10,41,16,50,39,17,18,39,41,41,41,41,41,30,39] 

dfevent = pd.read_fwf(txt_event, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfevent.shape
dfevent=dfevent[0:(rowcl-3)]

new_header = ['TipoEvento','CodigoEvento','FechaEvento','UsuarioEvento','HoraEvento','ClienteEvento','CodigoPostalEvento','PaísEvento','RepresentanteEvento','TipoPortesEvento','FormaPagoEvento','PlazoPagoEvento','SkuArticuloEvento','TipoArticuloEvento','FamiliaArticuloEvento','SubfamiliaArticuloEvento','CantidadArticuloEvento','AlmacenArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento','MotivoEvento','CosteEvento']
dfevent.columns = new_header
dfevent

"""Ver los pedidos únicos"""

events=dfevent.groupby(by=['TipoEvento','CodigoEvento'])

events.first()

"""### Articles"""

# Load the dataset 
txt_articulos = '/content/drive/My Drive/TFM/03_DATASETS/articulos.rpt'

widths = [16, 31, 13, 40, 31, 40, 31,40, 40, 40, 40, 19, 18, 40, 40, 18]

dfart= pd.read_fwf(txt_articulos, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfart.shape
dfart=dfart[0:(rowcl-3)]

new_header = ['CodigoArt','Nombre_art','Tipocliente','CodigoFamiliaArt','DescripciónFamiliaArt','CodigoSubFamiliaArt','DescripcionSubfamiliaArticulo','LargoArticulo','AnchoArticulo','AltoArticulo','PesoArticulo','UnidadPesoArticulo','FechaAltaArticulo','UnidadesPorCajaArticulo', 'MargenTarifaArticulo','PaisOrigenArticulo']
#Tipo artículo
dfart.columns = new_header

dfart

"""### Merge events and articles data"""

#We are going to use only the last 5 years
eventos = dfevent[(dfevent['FechaEvento'] >= '2016-01-01') &
          (dfevent['FechaEvento'] <= '2020-12-31')]

#We only keep the events that are "Ordered"
eventos=eventos[eventos['TipoEvento'] == 'PEDIDO']

#Change the name of the column in order to join 
eventos = eventos.rename(columns={'SkuArticuloEvento': 'CodigoArt'})

#Join 'display_name'
eventos=eventos.join(dfart.set_index('CodigoArt')['Nombre_art'], on='CodigoArt')

#We show data
eventos

#We check that we do not have orders without articles
eventos.isna().sum()

#We delete records that do not have an item name because they are item codes that were withdrawn more than 5 years ago
df = eventos[eventos['Nombre_art'].notna()]

df.Nombre_art = pd.to_datetime(df.FechaEvento)
df['month_year']= pd.to_datetime(df.FechaEvento).dt.to_period('M')
df.sort_values(by = ['month_year'], inplace = True)
Ser = df.groupby('month_year').CodigoEvento.nunique()
x = np.arange(0,len(Ser),1)
style.use('ggplot')
fig = plt.figure(figsize = (30,10))
ax1 = fig.add_subplot(111)
ax1.plot(x, Ser, color = 'k')
ax1.fill_between(x, Ser, color = 'r', alpha = 0.5)
ax1.set_xticks(x)
ax1.set_xticklabels(Ser.index)
plt.xlabel('Time period')
plt.ylabel('No. of transactions')

"""Basically we are creating a column named month_year to divide the datapoints into the month in which they occurred. Then we are taking the no. of unique transaction occurring in each month and plotting it using matplotlib.

Lets explore the no. of items bought in each transaction.
"""

Ser = eventos.groupby('CodigoEvento').Nombre_art.nunique()
Ser.describe()

bins = [0,50,100,150,200,250,300,350,400,450,500,550]
fig = plt.figure(figsize = (10,10))
plt.hist(Ser, bins, histtype = 'bar', rwidth = 0.5)
plt.xlabel('No. of items')
plt.ylabel('No. of transactions')
plt.show()

bins = [0,10,20,30,40,50,60,70,80,90,100,110,120,130,140,150,160,170,180,190,200]
fig = plt.figure(figsize = (10,10))
ax1 = fig.add_subplot(111)
ax1.hist(Ser, bins, histtype = 'bar', rwidth = 0.5)
ax1.set_xticks(bins)
plt.xlabel('No. of items')
plt.ylabel('No. of transactions')
plt.show()

eventos['total_cost_item'] = eventos.CantidadArticuloEvento*eventos.TarifaArticuloEvento
Ser = eventos.groupby('Nombre_art').total_cost_item.sum()
Ser.sort_values(ascending = False, inplace = True)
Ser = Ser[:10]
fig = plt.figure(figsize = (10,10))
ax = fig.add_subplot(111)
ax.barh(Ser.index, Ser, height = 0.5)

df_set = eventos[(eventos['FechaEvento'] >= '2019-01-01') &
          (eventos['FechaEvento'] <= '2019-12-31')]

df_set = df_set.groupby(['CodigoEvento', 'Nombre_art'])['CantidadArticuloEvento'].sum().unstack().reset_index().fillna(0).set_index('CodigoEvento')

df_set

"""We need to make sure that any positive values are encoded to one and all the negative values(if any) to zero."""

def encode(x):
 if x <= 0:
   return 0
 else:
   return 1
df_set = df_set.applymap(encode)
df_set

"""As the data-frame is ready we can apply Apriori algorithm to get the frequently bought item-sets."""

frequent_itemsets = apriori(df_set, min_support = 0.015, use_colnames = True)

"""We then arrange the itemsets in descending order of their support values which gives us"""

frequent_itemsets = apriori(df_set, min_support = 0.005, use_colnames = True)
top_items = frequent_itemsets.sort_values('support', ascending = False)[:20]
for i in range(len(top_items.itemsets)):
    top_items.itemsets.iloc[i] = str(list(top_items.itemsets.iloc[i]))
fig = plt.figure(figsize = (10,10))
ax = fig.add_subplot(111)
ax.bar(top_items.itemsets, top_items.support)
for label in ax.xaxis.get_ticklabels():
    label.set_rotation(90)
plt.xlabel('Item')
plt.ylabel('Support')

"""We then apply the association rules to these item-sets formed by Apriori algorithm."""

frequent_itemsets

rules = association_rules(frequent_itemsets, metric = 'confidence', min_threshold = 0.02)

"""The metric used here is confidence and its minimum threshold value is set to be 0.2."""

top_rules = rules.sort_values('confidence', ascending = False)[:100]

top_rules.reset_index(inplace=True,drop=True)

top_rules

fig = plt.figure(figsize = (10,10))
ax = fig.add_subplot(111)
ax.scatter(top_rules.support, top_rules.confidence, top_rules.lift)

import networkx as nx
G1 = nx.DiGraph()

edges = G1.edges()

color_map = []
N = 50
colors = np.random.rand(N)
strs = ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7', 'r8', 'r9']
for i in range(10):
    G1.add_nodes_from('r'+str(i))
    for a in top_rules.iloc[i]['antecedents']:
        G1.add_nodes_from([a])
        G1.add_edge(a, 'r'+str(i), color = colors[i], weight = 2)
    for c in top_rules.iloc[i]['consequents']:
        G1.add_nodes_from([c])
        G1.add_edge('r'+str(i), c, color = colors[i], weight = 2)
for node in G1:
    found_a_string = False
    for item in strs:
        if node == item:
            found_a_string = True
    if found_a_string:
        color_map.append('red')
    else:
        color_map.append('black')
edges = G1.edges()
colors = [G1[u][v]['color'] for u,v in edges]
weights = [G1[u][v]['weight'] for u,v in edges]
pos = nx.spring_layout(G1, k = 16, scale = 1)
fig = plt.figure(figsize = (20,20))
nx.draw(G1, pos, edgelist = edges, node_color = color_map, edge_color = colors, width = weights, font_size = 16, with_labels = False)
for p in pos:
    pos[p][1] += 0.07
nx.draw_networkx_labels(G1, pos)
fig.savefig('demo.png', transparent=True)

"""The item-sets are filtered such that only those having the lift and confidence values above the mean values are included."""

rules[(rules.lift >= 9.388) & (rules.confidence >= 0.429)]