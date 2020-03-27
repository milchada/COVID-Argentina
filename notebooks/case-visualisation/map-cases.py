import numpy as np
import matplotlib.pylab as plt
from matplotlib import colors, cm
import pandas as pd
import geopandas as gpd 
import io
import scprep

routefile = 'PatientRoute.csv'
mapfile = 'KOR_adm0.shp'

def heatmap(routefile, mapfile):
	fig, ax = plt.subplots()
	df = pd.read_csv(routefile)
	map0 = gpd.read_file(mapfile)
	map0.plot(ax=ax, color='red', alpha=0.2)

	if not xmin:
		xmin, xmax = (df['longitude'].min(), df['longitude'].max())
	if not ymin:
		ymin, ymax = (df['latitude'].min(), df['latitude'].max())

	x = np.linspace(xmin, xmax, ncells)
	y = np.linspace(ymin, ymax, ncells)
	
	X, Y = np.meshgrid(x, y)
	heat = np.zeros_like(X)

	for xi,yi, p in zip(df['longitude'], df['latitude'], df['Probability_infected']):
	    xbin = np.argmin(abs(xi - x))
	    ybin = np.argmin(abs(yi - y))
	    heat[xbin-1, ybin-1] += p #the -1 is because of how bins work

	heat[heat < .1] = np.nan
	a1 = ax.pcolormesh(X, Y, heat.T, cmap=cm.RdBu_r)
	fig.colorbar(a1, ax=ax)
	ax.set_xlim(xmin, xmax)
	ax.set_ylim(ymin, ymax)

	fig2, ax2  = plt.subplots()
	colors = scprep.plot.colors.tab(len(np.unique(df['global_num']))).colors
	for patient in np.unique(df['global_num']):
	  plot_df = df.loc[df['global_num']==patient].sort_values('date')
	  for i in range(plot_df.shape[0]-1):
	    ax2.plot(plot_df.iloc[[i,i+1]]['longitude'], plot_df.iloc[[i,i+1]]['latitude'], color=cmap[patient], alpha=0.5)

	return fig, ax, fig2, ax2