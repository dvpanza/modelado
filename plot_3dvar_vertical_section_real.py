import numpy as np
import matplotlib.pyplot as plt
from netCDF4 import Dataset
from wrf import (getvar, to_np, get_cartopy, latlon_coords, vertcross,
                 cartopy_xlim, cartopy_ylim, interpline, CoordPair)
import glob
import scipy.io as sio

#Grafico un mapa de 2 paneles. Uno indicando donde esta el corte.
#Otro mostrando el resultado del corte.

plot_time= 10          #En que tiempo vamos a hacer el grafico (arrancando desde 0)
figure_name= 'CrossRef'
plot_mat   = True     #Si es True grafica el mapa, sino ponerlo en False

#Busco en esta carpeta todos los archivos wrfout* y los ordeno cronologicamente. Guardo eso en una lista que se llama file_list.
file_list = glob.glob('./wrfout_d01_*')   #Busco todos los wrfout en la carpeta indicada.
file_list.sort()
ntimes = len( file_list ) #Encuentro la cantidad de tiempos disponibles.

# Abro el archivo netcdf correspondiente al tiempo indicado.
ncfile = Dataset(file_list[ plot_time ])


#Definimos el punto de partida del corte y el punto de fin.
cross_start = CoordPair(lat=-31.1, lon=-67.0)
cross_end = CoordPair(lat=-31.1, lon=-58.0)

#Obtenemos las variables.
ht = getvar(ncfile, "z")      #Altura sobre el nivel del mar
ter = getvar(ncfile, "ter")   #Altura de la topografia
dbz = getvar(ncfile, "dbz")   #Reflectividad de radar simulada

# Interpola dbz al corte vertical soliciado.
# Ademas dbz_cross tiene en su metadata la lat/lon de los puntos que componen el corte.
dbz_cross = vertcross(dbz, ht, wrfin=ncfile,
                    start_point=cross_start,
                    end_point=cross_end,
                    latlon=True, meta=True)

# Add back the attributes that xarray dropped from the operations above
#dbz_cross.attrs.update(dbz_cross.attrs)
#dbz_cross.attrs["description"] = "radar reflectivity cross section"
#dbz_cross.attrs["units"] = "dBZ"
# Obtenemos una transecta que representa la altura del terreno en la direccion del corte.
ter_line = interpline(ter, wrfin=ncfile, start_point=cross_start,
                      end_point=cross_end)

# Obtenemos las matrices de latitud y longitud para los graficos.
lats, lons = latlon_coords(dbz)
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
plt.plot( [ cross_start.lon , cross_end.lon ] , [ cross_start.lat , cross_end.lat ] , 'o-' )
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


plt.title('Ubicacion del corte')

#Segundo subplot con el corte vertical
plt.subplot(122)
# Make the cross section plot for dbz
xs = np.arange(0, dbz_cross.shape[-1], 1)
ys = to_np(dbz_cross.coords["vertical"])
levels=np.arange(0.0,60.0,5.0)
plt.contourf(xs,ys,to_np(dbz_cross),levels=levels,cmap='gist_ncar')
plt.colorbar()
#Genero un sombreado con el terreno.
plt.fill_between(xs, 0, to_np(ter_line),facecolor="saddlebrown")
#Esto permite mostrar el label de x en lat/lon
coord_pairs = to_np(dbz_cross.coords["xy_loc"])
x_ticks = np.arange(coord_pairs.shape[0])
x_labels=list()
for ii in range( coord_pairs.shape[0]  ) :
    x_labels.append( coord_pairs[ii].lon )

# Set the desired number of x ticks below
num_ticks = 5
thin = int((len(x_ticks) / num_ticks) + .5)
plt.xticks(x_ticks[::thin],labels=x_labels[::thin],rotation=45, fontsize=8)

#Fijo el tope vertical del corte en 15 km.
plt.axis([xs.min(),xs.max(),0,15000])

# Add a title
plt.title('Corte vertical de reflectividad (dBZ)')


plt.savefig( './' + figure_name + '_tiempo_' + str( plot_time ) + '.png' )

plt.show()


