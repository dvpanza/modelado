import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import (getvar, to_np, ll_to_xy , latlon_coords  )
import glob
import scipy.io as sio

#Grafico un mapa de 2 paneles. Uno indicando donde esta el punto
#otro mostrando la serie temporal de una variable en ese punto.

path_exp = "/home/mn09/modelado2/WRFLAB/EXP/ideal_rio"
figure_name= 'TimeEvolTyTd'

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob(f'{path_exp}/wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
print(file_list)
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ 0 ])


#Definimos el punto donde hacemos la serie
point_x = 21
point_y = 10


#Obtengo la topografia.
landmask = getvar(ncfile, "LANDMASK")   #Altura de la topografia

nx = to_np(landmask).shape[1]
ny = to_np(landmask).shape[0]

print(f"{nx},{ny}")
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


#Generamos la figura.
#Como vamos a hacer 2 paneles queremos un tamanio de figura que 
#sea el doble de ancho respecto al largo.
plt.figure(figsize=(9,4))

#Primer subplot con la ubicacion del corte.
plt.subplot(121)
plt.contourf(np.arange(nx),np.arange(ny),landmask,levels=[0,0.5,1,1.5],cmap='terrain',extend='max')
plt.plot( point_x , point_y , 'o' )
plt.colorbar()
#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ 0 , nx-1 , 0 , ny-1 ] )


plt.title('Ubicacion del meteograma')

#Segundo subplot con el corte vertical
plt.subplot(122)
#Grafico las series temporales de T y Td
plt.plot( time , t2m , 'ro-' ,label='T 2m')
plt.plot( time , td2m, 'bo-' ,label='Td 2m')
plt.legend()
# Agrego el titulo
plt.title('Meteograma de T y Td (dBZ)')


plt.savefig( f'{path_exp}/{figure_name}_lon_{point_x}_lat_{point_y}.png' )

plt.show()


