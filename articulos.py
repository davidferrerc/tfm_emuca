# -*- coding: utf-8 -*-
"""ARTICULOS.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1LWqpTEkLB6_9Vwu_Hwy6KvgekUKo1sDy
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

txt_event = '/content/drive/My Drive/TFM/03_DATASETS/eventos_2.rpt'
widths=[10,39,12,16,12,39,20,10,41,16,50,39,17,18,39,41,41,41,41,41,30,39] 

dfevent = pd.read_fwf(txt_event, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfevent.shape
dfevent=dfevent[0:(rowcl-3)]

new_header = ['TipoEvento','CodigoEvento','FechaEvento','UsuarioEvento','HoraEvento','ClienteEvento','CodigoPostalEvento','PaísEvento','RepresentanteEvento','TipoPortesEvento','FormaPagoEvento','PlazoPagoEvento','SkuArticuloEvento','TipoArticuloEvento','FamiliaArticuloEvento','SubfamiliaArticuloEvento','CantidadArticuloEvento','AlmacenArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento','MotivoEvento','CosteEvento']
dfevent.columns = new_header
dfevent

#eliminamos los eventos que sean una oferta
indexNames = dfevent[ dfevent['TipoEvento'] == 'OFERTA' ].index
# Delete these row indexes from dataFrame
dfevent.drop(indexNames , inplace=True)

dfevent = dfevent[(dfevent['FechaEvento'] >= '2019-01-01') &
          (dfevent['FechaEvento'] <= '2019-12-31')]

events=dfevent.sort_values(by=['FechaEvento'])

# Load the dataset 
txt_articulos = '/content/drive/My Drive/TFM/03_DATASETS/articulos.rpt'

widths = [16, 31, 13, 40, 31, 40, 31,40, 40, 40, 40, 19, 18, 40, 40, 18]

dfart= pd.read_fwf(txt_articulos, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfart.shape
dfart=dfart[0:(rowcl-3)]

#Create new header and remove lines
new_header = ['CodigoArt','Descripción','Tipocliente','CodigoFamiliaArt','DescripciónFamiliaArt','CodigoSubFamiliaArt','DescripcionSubfamiliaArticulo','LargoArticulo','AnchoArticulo','AltoArticulo','PesoArticulo','UnidadPesoArticulo','FechaAltaArticulo','UnidadesPorCajaArticulo', 'MargenTarifaArticulo','PaisOrigenArticulo']
#Tipo artículo
dfart.columns = new_header
dfart

!pip install pandas_profiling==2.6.0
#check if the pivot table has any duplicated CodigoCliente
import pandas as pd
from pandas_profiling import ProfileReport

report = ProfileReport(dfart, minimal=True, title='Pandas Profiling Report', html={'style':{'full_width':True}})
report

dups_color = dfart.pivot_table(index=['DescripciónFamiliaArt'], aggfunc='size')
print (dups_color)

id_nombre = dfart[['CodigoArt','DescripciónFamiliaArt']]
id_nombre['Descripción'] = id_nombre['DescripciónFamiliaArt']

events = events.merge(id_nombre,left_on='SkuArticuloEvento', right_on='CodigoArt')

events

events['Revenue'] = events["CantidadArticuloEvento"] * events["TarifaArticuloEvento"] * (100 - events["DescuentoArticuloEvento"])/100

events = events[['Descripción', 'Revenue', 'CosteEvento']]

events

events['CosteEvento'] = pd.to_numeric(events['CosteEvento'],errors='coerce')

ventas_sku = events.groupby(['Descripción']).agg({'Revenue':'sum','CosteEvento':'sum'}).reset_index()

ventas_sku.dtypes

ventas_sku

ventas_sku['Margin'] = (ventas_sku["Revenue"] - ventas_sku["CosteEvento"])
ventas_sku['Margin_%'] = ventas_sku['Margin']/ventas_sku["Revenue"] * 100

ventas_sku = ventas_sku[(ventas_sku['Revenue'] > 0)]
ventas_sku = ventas_sku[(ventas_sku['CosteEvento'] > 0)]

ventas_sku=ventas_sku.sort_values(by=['Revenue'], ascending=False)

ventas_sku.round(2)

Total = ventas_sku['Revenue'].sum()

print (Total)

ventas_sku.dtypes
