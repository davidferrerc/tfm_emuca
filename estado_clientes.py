# -*- coding: utf-8 -*-
"""estado_clientes

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AADrrtvqa1wj_WZAStnHiPj5sZu9LEG7
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

!pip install pandas_profiling==2.6.0

from google.colab import drive
drive.mount('/content/drive')

"""# LOAD EVENTOS"""

txt_event = '/content/drive/My Drive/TFM/03_DATASETS/eventos_2.rpt'
widths=[10,39,12,16,12,39,20,10,41,16,50,39,17,18,39,41,41,41,41,41,30,39] 

dfevent = pd.read_fwf(txt_event, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfevent.shape
dfevent=dfevent[0:(rowcl-3)]

new_header = ['TipoEvento','CodigoEvento','FechaEvento','UsuarioEvento','HoraEvento','ClienteEvento','CodigoPostalEvento','PaísEvento','RepresentanteEvento','TipoPortesEvento','FormaPagoEvento','PlazoPagoEvento','SkuArticuloEvento','TipoArticuloEvento','FamiliaArticuloEvento','SubfamiliaArticuloEvento','CantidadArticuloEvento','AlmacenArticuloEvento','TarifaArticuloEvento','DescuentoArticuloEvento','MotivoEvento','CosteEvento']
dfevent.columns = new_header
dfevent

#vamos a utilizar solo los últimos dos años
#dfevent = dfevent[(dfevent['FechaEvento'] >= '2016-01-01') &
          #(dfevent['FechaEvento'] <= '2020-12-31')]

#eliminamos los eventos que sean una oferta
indexNames = dfevent[ dfevent['TipoEvento'] == 'OFERTA' ].index
# Delete these row indexes from dataFrame
dfevent.drop(indexNames , inplace=True)

events= dfevent.sort_values(by=['FechaEvento'])

events['FechaEvento']

events.info()

"""# CLEAN THE DATASET EVENTOS"""

events['CantidadArticuloEvento'] = events['CantidadArticuloEvento'].astype(float)
events['TarifaArticuloEvento'] = events['TarifaArticuloEvento'].astype(float)
events['FechaEvento'] =  pd.to_datetime(events['FechaEvento'], format='%Y-%m-%d')
events['ClienteEvento'] = events['ClienteEvento'].astype(str)

eventos=events[['ClienteEvento','FechaEvento','CodigoEvento','CantidadArticuloEvento','TarifaArticuloEvento', "DescuentoArticuloEvento"]]#Calulate total purchase

#calculate the total import
eventos['TotalImporte'] = eventos["CantidadArticuloEvento"] * eventos["TarifaArticuloEvento"] * (100 - eventos["DescuentoArticuloEvento"])/100

eventos.info()

eventos.describe()

#sacamos el año del evento
eventos['año'] = eventos['FechaEvento'].apply(lambda x: x.strftime('%Y'))
eventos.head()

eventos=eventos.drop(['FechaEvento'], axis = 1) 
eventos

importe_anual = eventos.pivot_table(index=['ClienteEvento'],columns=['año'],values='TotalImporte',aggfunc='sum',fill_value=0).reset_index()
importe_anual.head()

#check if the pivot table has any duplicated CodigoCliente
import pandas as pd
from pandas_profiling import ProfileReport

report = ProfileReport(importe_anual, minimal=True, title='Pandas Profiling Report', html={'style':{'full_width':True}})
report

"""# MERGE WITH CLIENTES TO OBTAIN NOMBRECLIENTE AND CODIGOCLIENTE"""

# Load the dataset 
txt_client = '/content/drive/My Drive/TFM/03_DATASETS/clientes.rpt'

widths = [40, 31, 16, 21, 12, 51, 17, 40, 40, 15, 50]

dfclient = pd.read_fwf(txt_client, widths=widths, header=1, index_col=None, index=True)
rowcl,colcl = dfclient.shape
dfclient=dfclient[0:(rowcl-3)]

new_header = ['CodigoCliente','NombreCliente','NIFCliente','CodigoPostalCliente','PaisCliente','SegmentoCliente','FechaAltaCliente','RepresentanteCliente','AreaCliente','MercadoCliente','GrupoDescuentoCliente']

dfclient.columns = new_header
clientes = dfclient

id_nombre = clientes[['CodigoCliente','NombreCliente','SegmentoCliente', 'PaisCliente']]

#eliminamos los dos últimos carácteres de la variable ClienteEveno para poder hacer el merge
importe_anual['ClienteEvento'] = importe_anual['ClienteEvento'].map(lambda x: str(x)[:-2])

importe_anual

importe_anual = importe_anual.merge(id_nombre,left_on='ClienteEvento', right_on='CodigoCliente')

importe_anual.head()

importe_anual = importe_anual.drop(['ClienteEvento'], axis = 1)

importe_anual.head()

#reordenar las columnas
importe_anual = importe_anual[['CodigoCliente', 'NombreCliente', '2009','2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020']]
importe_anual

"""# DEFINICIÓN DE LOS ESTADOS DE LOS CLIENTES

- Clientes nuevos(facturan en 2020 por primera vez)
- Clientes maduros(han facturando los últimos 5 años)
- Clientes perdidos(llevan desde el 2018 sin facturar)
- Clientes dormidos (facturan en 2019 pero aún no en 2020)
- Clientes activos(facturan en 2020 pero no por primera vez)
"""

#si facturan = 1, si no facturan = 0
ed_importe_anual = importe_anual
ed_importe_anual['venta_2009'] = np.where(importe_anual['2009']>0, 1, 0)
ed_importe_anual['venta_2010'] = np.where(importe_anual['2010']>0, 1, 0)
ed_importe_anual['venta_2011'] = np.where(importe_anual['2011']>0, 1, 0)
ed_importe_anual['venta_2012'] = np.where(importe_anual['2012']>0, 1, 0)
ed_importe_anual['venta_2013'] = np.where(importe_anual['2013']>0, 1, 0)
ed_importe_anual['venta_2014'] = np.where(importe_anual['2014']>0, 1, 0)
ed_importe_anual['venta_2015'] = np.where(importe_anual['2015']>0, 1, 0)
ed_importe_anual['venta_2016'] = np.where(importe_anual['2016']>0, 1, 0)
ed_importe_anual['venta_2017'] = np.where(importe_anual['2017']>0, 1, 0)
ed_importe_anual['venta_2018'] = np.where(importe_anual['2018']>0, 1, 0)
ed_importe_anual['venta_2019'] = np.where(importe_anual['2019']>0, 1, 0)
ed_importe_anual['venta_2020'] = np.where(importe_anual['2020']>0, 2, 0)

ed_importe_anual

ed_importe_anual = ed_importe_anual.drop(['2009','2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020'], axis = 1)

ed_importe_anual

client_state = ed_importe_anual[['CodigoCliente','NombreCliente', 'venta_2019', 'venta_2020']]

client_state

client_state["rank_state"]=client_state["venta_2019"]+client_state["venta_2020"]

print(client_state.groupby("rank_state").size())

client_state['rank_state'] = client_state['rank_state'].replace([0,1,2,3],['dormido','dormido','nuevo','activo'])

client_state

client_state.rank_state.value_counts()

actives=client_state[(client_state['rank_state']=='activo')]

actives

"""Desglosamos los activos en maduros y activos"""

#si facturan = 1, si no facturan = 0
ed_importe_anual_5_years = importe_anual
ed_importe_anual_5_years['venta_2016'] = np.where(importe_anual['2016']>0, 1, 0)
ed_importe_anual_5_years['venta_2017'] = np.where(importe_anual['2017']>0, 1, 0)
ed_importe_anual_5_years['venta_2018'] = np.where(importe_anual['2018']>0, 1, 0)
ed_importe_anual_5_years['venta_2019'] = np.where(importe_anual['2019']>0, 1, 0)
ed_importe_anual_5_years['venta_2020'] = np.where(importe_anual['2020']>0, 1, 0)

ed_importe_anual_5_years = ed_importe_anual_5_years[['CodigoCliente','NombreCliente','venta_2016','venta_2017', 'venta_2018', 'venta_2019', 'venta_2020']]

ed_importe_anual_5_years

actives_mature = pd.merge(ed_importe_anual_5_years,
                 actives[['NombreCliente', 'rank_state']],
                 on='NombreCliente')
actives_mature

actives_mature['rank_state']=actives_mature['venta_2016']+actives_mature['venta_2017']+actives_mature['venta_2018']+actives_mature['venta_2019']+actives_mature['venta_2020']

actives_mature

print(actives_mature.groupby('rank_state').size())

actives_mature.loc[actives_mature['rank_state'] == 0]

actives.loc[actives['NombreCliente'] == "SELECT COMPONENTS LTD"]

"""Comprobamos que tenemos 12 clientes duplicados por nombre con diferente código cliente, hay que quedarse con los registros más recientes y eliminar los duplicados anteriores."""

actives_mature['rank_state'] = actives_mature['rank_state'].replace([0,1,2,3,4,5],['activo','activo','activo','activo','activo','maduro'])

actives_mature

actives_mature.rank_state.value_counts()

"""Desglosamos los clientes dormidos en inactivos y dormidos"""

asleep=client_state[(client_state['rank_state']=='dormido')]

asleep

#si facturan = 1, si no facturan = 0
ed_importe_anual_5_years_asleep = importe_anual
ed_importe_anual_5_years_asleep['venta_2016'] = np.where(importe_anual['2016']>0, 1, 0)
ed_importe_anual_5_years_asleep['venta_2017'] = np.where(importe_anual['2017']>0, 1, 0)
ed_importe_anual_5_years_asleep['venta_2018'] = np.where(importe_anual['2018']>0, 1, 0)
ed_importe_anual_5_years_asleep['venta_2019'] = np.where(importe_anual['2019']>0, 1, 0)
ed_importe_anual_5_years_asleep['venta_2020'] = np.where(importe_anual['2020']>0, 1, 0)

ed_importe_anual_5_years_asleep = ed_importe_anual_5_years_asleep[['CodigoCliente','NombreCliente','venta_2016','venta_2017', 'venta_2018', 'venta_2019', 'venta_2020']]

asleep_inactives = pd.merge(ed_importe_anual_5_years_asleep,
                 asleep[['NombreCliente', 'rank_state']],
                 on='NombreCliente')
asleep_inactives

asleep_inactives['rank_state'] = asleep_inactives['venta_2019'].replace([0,1],['inactivo','dormido'])

asleep_inactives

print(asleep_inactives.groupby('rank_state').size())

"""Extraemos los clientes nuevos de la primera clasificación que hemos hecho"""

nuevos=client_state[(client_state['rank_state']=='nuevo')]
nuevos

"""Unificamos en un solo dataframe todos los clientes clasificados"""

clients_class = pd.concat([actives_mature,asleep_inactives,nuevos])
clients_class

"""Localizamos los clientes duplicados

Filtramos por la última actualización de los clientes registrados para eliminar datos duplicados
"""

clients_class['CodigoCliente'] = clients_class['CodigoCliente'].astype(int)

clients_class = clients_class.sort_values('CodigoCliente', ascending=False)

clients_class

clients_class = clients_class.drop_duplicates(subset='NombreCliente', keep='first')
clients_class

clients_class.groupby('rank_state').size()

#clients_class.to_csv('/content/drive/My Drive/TFM/03_DATASETS/Estado_Clientes.csv',sep=';',decimal=',')

clients_class = clients_class[['CodigoCliente','NombreCliente','rank_state']]

clients_class

clients_class['CodigoCliente'] = clients_class['CodigoCliente'].astype(str)

id_nombre = clientes[['CodigoCliente','PaisCliente','SegmentoCliente']]

clients_class = clients_class.merge(id_nombre,left_on='CodigoCliente', right_on='CodigoCliente')
clients_class

clients_class.to_csv('/content/drive/My Drive/TFM/03_DATASETS/Estado_Clientes.csv',sep=';',decimal=',')