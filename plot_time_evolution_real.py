import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import (getvar, to_np, ll_to_xy , latlon_coords  )
import glob
import scipy.io as sio

#Grafico un mapa de 2 paneles. Uno indicando donde esta el punto
#otro mostrando la serie temporal de una variable en ese punto.

figure_name= 'TimeEvolTyTd'
plot_mat   = True     #Si es True grafica el mapa, sino ponerlo en False

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob('./wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ 0 ])


#Definimos el punto donde hacemos la serie
point_lon = -60.0
point_lat = -35.0

#Convierto el punto de latitud y longitud en x e y de la reticula del WRF.
[point_x,point_y]=ll_to_xy(ncfile, point_lat, point_lon, meta=False)


#Obtengo la topografia.
ter = getvar(ncfile, "ter")   #Altura de la topografia

#Hago un loop sobre los tiempos para leer todos los archivos y asi recontruir la serie temporal de T2m y Td2m
t2m = np.zeros( ntimes ) #Genero las variables con 0s y luego vamos a ir leyendo y completando los valores para cada tiempo.
td2m= np.zeros( ntimes )
time= np.zeros( ntimes )
for ifile , my_file in enumerate( file_list ) :
    ncfile = Dataset(file_list[ ifile ])
    t2m[ ifile ] = getvar(ncfile, 'T2' )[point_y,point_x]-273.16    #Temperatura a 2 metros (por defecto viene en K)
    td2m[ ifile ]= getvar(ncfile, 'td2')[point_y,point_x]           #Td a 2 metros (el wrf-python la calcula en C)
    time[ ifile ]= getvar(ncfile,'times')

time = (time - time[0])/3600.0e9  #Pongo el tiempo en horas desde el inicio de la simulacion.

# Obtenemos las matrices de latitud y longitud para los graficos.
lats, lons = latlon_coords(ter)
lats=to_np(lats)
lons=to_np(lons)

#Generamos la figura.
#Como vamos a hacer 2 paneles queremos un tamanio de figura que 
#sea el doble de ancho respecto al largo.
plt.figure(figsize=(9,4))

#Primer subplot con la ubicacion del corte.
plt.subplot(121)
plot_ter = to_np(ter)
plot_ter[ plot_ter <= 1.0 ] = np.nan
plt.contourf(lons,lats,plot_ter,levels=np.arange(-1000,5000,500),cmap='terrain',extend='max')
plt.plot( point_lon , point_lat , 'o' )
plt.colorbar()
#Agrego el mapa (Solo si plot_mat es True)
if plot_mat :
   mapa = sio.loadmat('./mapas.mat')
   plt.plot(mapa['provincias'][:,0],mapa['provincias'][:,1], color='k', lw=0.5, zorder=1)
   plt.plot(mapa['samerica'][:,0],mapa['samerica'][:,1], color='k', lw=0.5, zorder=1)
#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ lons.min() , lons.max() , lats.min() , lats.max() ] )


plt.title('Ubicacion del meteograma')

#Segundo subplot con el corte vertical
plt.subplot(122)
#Grafico las series temporales de T y Td
plt.plot( time , t2m , 'ro-' ,label='T 2m')
plt.plot( time , td2m, 'bo-' ,label='Td 2m')
plt.legend()
# Agrego el titulo
plt.title('Meteograma de T y Td (dBZ)')


plt.savefig( './' + figure_name + '_lon_' + str(point_lon) + '_lat_' + str(point_lat) + '.png' )

plt.show()


