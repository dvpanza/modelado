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

plot_time= 20         #En que tiempo vamos a hacer el grafico (arrancando desde 0)
figure_name= 'T_uv'   #Un nombre que distinga esta figura de otros tipos de figuras.
nivel      = 200      #Altura del nivel (m) a donde interpolaremos los datos.

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
#Obtengo el tamanio del dominio a partir de la dimension de z.
nz=to_np(z).shape[0]
ny=to_np(z).shape[1]
nx=to_np(z).shape[2]

[um , vm] = getvar(ncfile, "uvmet", units="m s-1")
tk = getvar(ncfile, "tk")

#Interpolamos verticalmente a la altura seleccionada
um_z = interplevel(um, z, nivel)
vm_z = interplevel(vm, z, nivel)
t_z  = interplevel(tk, z, nivel)

#Calculo la velocidad del viento
wspd_z = np.sqrt(um_z**2 + vm_z**2)

# Creamos la figura.
fig = plt.figure()

# Graficamos la temperatura en contornos
levels = np.arange(np.round(to_np(t_z).min())-2.,np.round(to_np(t_z).max())+2., 2.)
plt.contourf(np.arange(nx),np.arange(ny),to_np(t_z), levels=levels,cmap='rainbow')
plt.colorbar()

# Agregamos los contornos de velocidad de viento.
levels = [1,5,10,15]
contour=plt.contour(np.arange(nx),np.arange(ny),to_np(wspd_z),levels=levels,colors='k')
plt.clabel(contour,inline=1, fontsize=10, fmt="%i")

# Agregamos el viento en barbas pero graficando solo cada 10 puntos de reticula.
skip=2
plt.barbs(np.arange(nx)[::skip],np.arange(ny)[::skip],to_np(um_z[::skip, ::skip]),to_np(vm_z[::skip, ::skip]),length=3)

#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ 0 , nx-1 , 0 , ny-1 ] )
#Agregamos un titulo para la figura
plt.title('Temperatura (K) y viento (m/s)')
#Guardamos la figura en un archivo, el nombre del archivo incluye el tiempo y el nivel asi como el figure_name que definimos al principio
plt.savefig( './' + figure_name + '_tiempo_' + str( plot_time ) + '_altura_' + str( nivel ) + '.png' )
#El plt.show es opcional solo si se desea ver la figura en tiempo real. Sino se guarda automaticamente la figura en el archivo y no se
#muestra por pantalla.
plt.show()

