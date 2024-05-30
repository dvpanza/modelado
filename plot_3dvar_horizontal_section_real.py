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

from wrf import getvar, interplevel, to_np, get_basemap, latlon_coords

plot_time= 0          #En que tiempo vamos a hacer el grafico (arrancando desde 0)
figure_name= 'T_uv'   #Un nombre que distinga esta figura de otros tipos de figuras.
nivel      = 5000      #Altura del nivel (m) a donde interpolaremos los datos.
plot_mat   = True     #Si es True grafica el mapa, sino ponerlo en False

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob('./wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ plot_time ])

# Extraigo la altura, la temperatura y las componentes del viento
#Notar que en el caso de las componentes del viento wrf-python rota dichas
#componentes para recuperar la orientacion zonal y meridional
z = getvar(ncfile, "height",units='m')
[um , vm] = getvar(ncfile, "uvmet", units="m s-1")
tk = getvar(ncfile, "tk")

#Interpolamos verticalmente a la altura seleccionada
um_z = interplevel(um, z, nivel)
vm_z = interplevel(vm, z, nivel)
t_z  = interplevel(tk, z, nivel)

#Calculo la velocidad del viento
wspd_z = np.sqrt(um_z**2 + vm_z**2)

# Obtenemos las lat y lons correspondientes a nuestras variables.
lats, lons = latlon_coords(t_z)
lats=to_np(lats)
lons=to_np(lons)
#Nota: Por defecto wrfpython genera variables que son objetos Xarray estos son 
#tipos de datos y metadatos. Para convertir los datos a arrays de numpy esta la
#funcion to_np que toma el Xarray, extrae los datos como un array de numpy.

# Creamos la figura.
fig = plt.figure()

# Graficamos la temperatura en contornos
levels = np.arange(np.round(to_np(t_z).min())-2.,np.round(to_np(t_z).max())+2., 2.)
plt.contourf(lons,lats,to_np(t_z), levels=levels,cmap='rainbow')
plt.colorbar()

# Agregamos los contornos de velocidad de viento.
levels = [1,5,10,15]
contour=plt.contour(lons,lats,to_np(wspd_z),levels=levels,colors='k')
plt.clabel(contour,inline=1, fontsize=10, fmt="%i")

# Agregamos el viento en barbas pero graficando solo cada 10 puntos de reticula.
skip=10
plt.barbs(lons[::skip,::skip],lats[::skip,::skip],to_np(um_z[::skip, ::skip]),to_np(vm_z[::skip, ::skip]),length=6)

#Finalmente agrego el mapa (Solo si plot_mat es True)
if plot_mat :
   mapa = sio.loadmat('./mapas.mat')
   plt.plot(mapa['provincias'][:,0],mapa['provincias'][:,1], color='k', lw=0.5, zorder=1)
   plt.plot(mapa['samerica'][:,0],mapa['samerica'][:,1], color='k', lw=0.5, zorder=1)

#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ lons.min() , lons.max() , lats.min() , lats.max() ] )
#Agregamos un titulo para la figura
plt.title('Temperatura (K) y viento (m/s)')
#Guardamos la figura en un archivo, el nombre del archivo incluye el tiempo y el nivel asi como el figure_name que definimos al principio
plt.savefig( './' + figure_name + '_tiempo_' + str( plot_time ) + '_altura_' + str( nivel ) + '.png' )
#El plt.show es opcional solo si se desea ver la figura en tiempo real. Sino se guarda automaticamente la figura en el archivo y no se
#muestra por pantalla.
plt.show()

