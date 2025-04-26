import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Crear directorio para gráficos si no existe
if not os.path.exists('graficos'):
    os.makedirs('graficos')

# Cargar los datos limpios (si existen) o limpiar los datos originales
if os.path.exists('antofagasta_clean.csv'):
    print("Cargando datos limpios...")
    df = pd.read_csv('antofagasta_clean.csv')
    # Convertir la columna de fecha-hora a datetime si existe
    if 'Fecha_Hora' in df.columns:
        df['Fecha_Hora'] = pd.to_datetime(df['Fecha_Hora'])
    else:
        # Crear columna de fecha-hora si no existe
        df['Fecha_Hora'] = pd.to_datetime(
            df[['Year', 'Month', 'Day', 'Hour', 'Minute']]
        )
else:
    print("Cargando y limpiando datos originales...")
    # Cargar el archivo CSV original
    df = pd.read_csv('antofagasta_dirty.csv')
    
    # Limpiar valores extremos
    valores_extremos = {
        'GHI': [9500, 10500, -700],
        'DNI': [9500, 10500, -50],
        'DHI': [9500, 10500, -700],
        'Tdry': [-30, 70],
        'Wspd': [40, 55, -8]
    }
    
    for columna, valores in valores_extremos.items():
        for valor in valores:
            if valor < 0:
                df.loc[df[columna] <= valor, columna] = np.nan
            else:
                df.loc[df[columna] >= valor, columna] = np.nan
    
    # Valores negativos para variables que no deben ser negativas
    for col in ['GHI', 'DNI', 'DHI', 'Wspd']:
        df.loc[df[col] < 0, col] = np.nan
    
    # Crear columna de fecha-hora
    df['Fecha_Hora'] = pd.to_datetime(
        df[['Year', 'Month', 'Day', 'Hour', 'Minute']]
    )

print("Generando gráficos...")

# 1. Serie anual (valores promedios diarios de GHI)
print("Creando serie anual...")
# Crear columna de fecha sin hora
df['Fecha'] = df['Fecha_Hora'].dt.date
# Agrupar por fecha y calcular promedio diario de GHI
ghi_diario = df.groupby('Fecha')['GHI'].mean().reset_index()
ghi_diario['Fecha'] = pd.to_datetime(ghi_diario['Fecha'])

plt.figure(figsize=(15, 6))
plt.plot(ghi_diario['Fecha'], ghi_diario['GHI'])
plt.title('Serie Anual - Promedio Diario de Radiación Global Horizontal (GHI)')
plt.xlabel('Fecha')
plt.ylabel('GHI Promedio (W/m²)')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graficos/serie_anual_ghi.png', dpi=300)
print("Serie anual guardada en 'graficos/serie_anual_ghi.png'")

# 2. Histograma de GHI
print("Creando histograma de GHI...")
plt.figure(figsize=(10, 6))
sns.histplot(df['GHI'].dropna(), bins=50, kde=True)
plt.title('Distribución de Radiación Global Horizontal (GHI)')
plt.xlabel('GHI (W/m²)')
plt.ylabel('Frecuencia')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('graficos/histograma_ghi.png', dpi=300)
print("Histograma de GHI guardado en 'graficos/histograma_ghi.png'")

# 3. Matriz de correlación
print("Creando matriz de correlación...")
# Seleccionar solo columnas numéricas relevantes
columnas_numericas = ['GHI', 'DNI', 'DHI', 'Tdry', 'Tdew', 'RH', 'Pres', 'Wspd', 'Wdir']
matriz_corr = df[columnas_numericas].corr()

plt.figure(figsize=(12, 10))
mask = np.triu(np.ones_like(matriz_corr, dtype=bool))  # Máscara para mostrar solo la mitad inferior
cmap = sns.diverging_palette(220, 10, as_cmap=True)    # Paleta de colores

# Crear mapa de calor
sns.heatmap(matriz_corr, mask=mask, cmap=cmap, vmax=1, vmin=-1, center=0,
            square=True, linewidths=.5, annot=True, fmt='.2f', cbar_kws={"shrink": .75})

plt.title('Matriz de Correlación de Variables Meteorológicas')
plt.tight_layout()
plt.savefig('graficos/matriz_correlacion.png', dpi=300)
print("Matriz de correlación guardada en 'graficos/matriz_correlacion.png'")

print("\n¡Gráficos generados con éxito!")
print("Puedes encontrar todos los gráficos en la carpeta 'graficos/'.") 