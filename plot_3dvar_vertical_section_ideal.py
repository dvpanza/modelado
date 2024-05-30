import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import (getvar, to_np, get_cartopy, latlon_coords, vertcross,
                 cartopy_xlim, cartopy_ylim, interpline, CoordPair)
import glob
import scipy.io as sio

#Grafico un mapa de 2 paneles. Uno indicando donde esta el corte.
#Otro mostrando el resultado del corte.

plot_time= 20          #En que tiempo vamos a hacer el grafico (arrancando desde 0)
figure_name= 'CrossRef'
plot_mat   = True     #Si es True grafica el mapa, sino ponerlo en False

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob('./wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ plot_time ])


#Definimos el punto de partida del corte y el punto de fin.
cross_start = CoordPair(x=10, y=10)
cross_end = CoordPair(x=49, y=10)

#Obtenemos las variables.
ht = getvar(ncfile, "z")      #Altura sobre el nivel del mar
#Obtengo el tamanio del dominio a partir de la dimension de z.
nz=to_np(ht).shape[0]
ny=to_np(ht).shape[1]
nx=to_np(ht).shape[2]

ter = getvar(ncfile, "ter")   #Altura de la topografia
landmask = getvar(ncfile,'LANDMASK')
[um,vm] = getvar(ncfile, "uvmet")   #Reflectividad de radar simulada
w = getvar(ncfile,'wa')

# Interpola dbz al corte vertical soliciado.
# Ademas dbz_cross tiene en su metadata la lat/lon de los puntos que componen el corte.
um_cross = vertcross(um, ht, wrfin=ncfile,
                    start_point=cross_start,
                    end_point=cross_end,
                    latlon=False, meta=True,autolevels=300)
w_cross = vertcross(w, ht, wrfin=ncfile,
                    start_point=cross_start,
                    end_point=cross_end,
                    latlon=False, meta=True,autolevels=300)



ter_line = interpline(ter, wrfin=ncfile, start_point=cross_start,
                      end_point=cross_end)

#Generamos la figura.
#Como vamos a hacer 2 paneles queremos un tamanio de figura que 
#sea el doble de ancho respecto al largo.
plt.figure(figsize=(9,4))

#Primer subplot con la ubicacion del corte.
plt.subplot(121)
plt.contourf(np.arange(nx),np.arange(ny),landmask,levels=[0,0.5,1,1.5],cmap='terrain',extend='max')
plt.plot( [ cross_start.x , cross_end.x ] , [ cross_start.y , cross_end.y ] , 'o-' )
plt.colorbar()
#Agregamos las gridlines
plt.grid()
#Ajustamos los limites de la figura al dominio del WRF
plt.axis( [ 0 , nx-1 , 0 , ny-1 ] )
plt.title('Ubicacion del corte')

#Segundo subplot con el corte vertical
plt.subplot(122)
# Make the cross section plot for dbz
xs = np.arange(0, um_cross.shape[-1], 1)
ys = to_np(um_cross.coords["vertical"])
levels=np.arange(-10.0,10.5,0.5)
plt.contourf(xs,ys,to_np(um_cross),levels=levels,cmap='bwr')
plt.colorbar()
plt.contour(xs,ys,to_np(w_cross),levels=[-1.0,-0.5,0.5,1.0,1.5,2.0,3.0] )
#Genero un sombreado con el terreno.
plt.fill_between(xs, 0, to_np(ter_line),facecolor='saddlebrown')

#Fijo el tope vertical del corte en 5 km.
plt.axis([xs.min(),xs.max(),0,5000])

# Add a title
plt.title('Corte vertical de viento zonal (somb.) y w (cont.)')


plt.savefig( './' + figure_name + '_tiempo_' + str( plot_time ) + '.png' )

plt.show()


