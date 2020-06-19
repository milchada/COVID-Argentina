import pandas as pd
import geopandas as gpd
import matplotlib.pylab as plt

map_df = gpd.read_file('departamento.shp')                                                                                          

casefilename = 'covid_arg-cases.csv'
cases = pd.read_csv(casefilename)      
plotName = None                              

# cases.clasificacion_resumen.unique()                                          
# array(['Descartado', 'Sospechoso', 'Confirmado', 'Sin Clasificar'],
      # dtype=object)

cases=cases[cases.clasificacion_resumen == 'Confirmado']                      

# cases.keys()                                                                  

# Index(['id_evento_caso', 'sexo', 'edad', 'edad_años_meses',
#        'residencia_pais_nombre', 'residencia_provincia_nombre',
#        'residencia_departamento_nombre', 'carga_provincia_nombre',
#        'fecha_inicio_sintomas', 'fecha_apertura', 'sepi_apertura',
#        'fecha_internacion', 'cuidado_intensivo', 'fecha_cui_intensivo',
#        'fallecido', 'fecha_fallecimiento', 'asistencia_respiratoria_mecanica',
#        'carga_provincia_id', 'origen_financiamiento', 'Clasificacion',
#        'clasificacion_resumen', 'residencia_provincia_id', 'fecha_diagnostico',
#        'residencia_departamento_id', 'ultima_actualizacion'],
#       dtype='object')

merged = map_df.set_index('nam').join(cases.set_index('residencia_departamento_nombre'))                                                                    

for i in range(len(merged)):
  sub = cases[cases.residencia_departamento_nombre == merged.index[i]] 
  merged.positivos[i] = len(sub[sub.clasificacion_resumen == 'Confirmado']) 
                                                                               

if plotName:
  merged.plot(column='positivos',cmap='Blues',vmin=50,vmax=np.nanmax(pos),linewidth=0.8, ax=plt.gca(), edgecolor='0.8')                                    
  plt.xlim(-75,-50)
  plt.ylim(-60,-20)
  plt.savefig(plotName)                                                  

merged.to_csv(casefilename+'-gpd.csv')                                              
