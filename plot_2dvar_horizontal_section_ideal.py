#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Basado en los ejemplos
https://wrf-python.readthedocs.io/en/latest/plot.html
"""

from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import get_cmap
import glob
import scipy.io as sio

from wrf import getvar, interplevel, to_np

plot_time= 20            #En que tiempo vamos a hacer el grafico (arrancando desde 0)
figure_name= 'T2m_uv10' #Un nombre que distinga esta figura de otros tipos de figuras.
plot_mat   = True       #Si es True grafica el mapa, sino ponerlo en False

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob('./wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ plot_time ])

# Extraigo la altura, la temperatura y las componentes del viento
#Notar que en el caso de las componentes del viento wrf-python rota dichas
#componentes para recuperar la orientacion zonal y meridional
[um10 , vm10 ] = getvar(ncfile, "uvmet10", units="m s-1")
t2m = getvar(ncfile, "T2")
nx = to_np(t2m).shape[1]
ny = to_np(t2m).shape[0]

#Calculo la velocidad del viento
wspd10 = np.sqrt(to_np(um10)**2 + to_np(vm10)**2)

# Creamos la figura.
fig = plt.figure()

# Graficamos la temperatura en contornos
levels = np.arange(np.round(to_np(t2m).min())-2.,np.round(to_np(t2m).max())+2., 2.)
plt.contourf(np.arange(nx),np.arange(ny),to_np(t2m), levels=levels,cmap='rainbow',extend='max')
plt.colorbar()

# Agregamos los contornos de velocidad de viento.
levels = [1,5,10,15]
contour=plt.contour(np.arange(nx),np.arange(ny),to_np(wspd10),levels=levels,colors='k')
plt.clabel(contour,inline=1, fontsize=10, fmt="%i")

# Agregamos el viento en barbas pero graficando solo cada 10 puntos de reticula.
skip=2
plt.barbs(np.arange(nx)[::skip],np.arange(ny)[::skip],to_np(um10[::skip, ::skip]),to_np(vm10[::skip, ::skip]),length=4)

#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ 0 , nx-1 , 0 , ny-1 ] )
#Agregamos un titulo para la figura
plt.title('Temperatura (K) y viento (m/s)')
#Guardamos la figura en un archivo, el nombre del archivo incluye el tiempo y el nivel asi como el figure_name que definimos al principio
plt.savefig( './' + figure_name + '_tiempo_' + str( plot_time ) + '.png' )
#El plt.show es opcional solo si se desea ver la figura en tiempo real. Sino se guarda automaticamente la figura en el archivo y no se
#muestra por pantalla.
plt.show()

