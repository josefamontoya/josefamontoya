import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Cargar el archivo CSV
print("Cargando datos...")
ruta_archivo = 'antofagasta_dirty.csv'
df = pd.read_csv(ruta_archivo)

# Ver la estructura de los datos
print("\nInformación del DataFrame:")
print(df.info())

# Verificar valores nulos
print("\nValores nulos por columna:")
print(df.isnull().sum())

# Estadísticas descriptivas
print("\nEstadísticas descriptivas:")
print(df.describe())

# Verificar valores extremos o anómalos
print("\nBuscando valores anómalos...")
# Valores extremos para GHI, DNI, DHI
valores_extremos = {
    'GHI': [9500, 10500, -700],
    'DNI': [9500, 10500, -50],
    'DHI': [9500, 10500, -700],
    'Tdry': [-30, 70],
    'Wspd': [40, 55, -8]
}

for columna, valores in valores_extremos.items():
    mask = pd.Series(False, index=df.index)
    for valor in valores:
        if valor < 0:
            # Buscamos valores menores que 0 para columnas que no deben tener negativos
            mask = mask | (df[columna] <= valor)
        else:
            # Buscamos valores muy grandes
            mask = mask | (df[columna] >= valor)
    
    if mask.any():
        print(f"Filas con valores extremos en {columna}: {mask.sum()}")
        print(df[mask].head())

# Función para limpiar los datos
def limpiar_datos(df):
    df_limpio = df.copy()
    
    # 1. Reemplazar valores extremos con NaN
    for columna, valores in valores_extremos.items():
        for valor in valores:
            if valor < 0:
                df_limpio.loc[df_limpio[columna] <= valor, columna] = np.nan
            else:
                df_limpio.loc[df_limpio[columna] >= valor, columna] = np.nan
    
    # 2. Asegurarse que las variables no tengan valores fuera de rangos lógicos
    # GHI, DNI, DHI no deben ser negativos
    for col in ['GHI', 'DNI', 'DHI']:
        df_limpio.loc[df_limpio[col] < 0, col] = np.nan
    
    # Velocidad del viento (Wspd) no debe ser negativa
    df_limpio.loc[df_limpio['Wspd'] < 0, 'Wspd'] = np.nan
    
    # Humedad relativa (RH) debe estar entre 0 y 100
    df_limpio.loc[(df_limpio['RH'] < 0) | (df_limpio['RH'] > 100), 'RH'] = np.nan
    
    # 3. Crear columna de fecha-hora
    df_limpio['Fecha_Hora'] = pd.to_datetime(
        df_limpio[['Year', 'Month', 'Day', 'Hour', 'Minute']]
    )
    
    return df_limpio

# Limpiar los datos
print("\nLimpiando datos...")
df_limpio = limpiar_datos(df)

# Estadísticas después de la limpieza
print("\nEstadísticas después de la limpieza:")
print(df_limpio.describe())

# Visualizaciones básicas
print("\nCreando visualizaciones...")

# Crear directorio para gráficos si no existe
if not os.path.exists('graficos'):
    os.makedirs('graficos')

# Gráfico de series temporales para variables principales
plt.figure(figsize=(15, 10))
plt.subplot(3, 1, 1)
plt.plot(df_limpio['Fecha_Hora'], df_limpio['GHI'])
plt.title('Radiación Global Horizontal (GHI)')
plt.ylabel('W/m²')

plt.subplot(3, 1, 2)
plt.plot(df_limpio['Fecha_Hora'], df_limpio['Tdry'])
plt.title('Temperatura (Tdry)')
plt.ylabel('°C')

plt.subplot(3, 1, 3)
plt.plot(df_limpio['Fecha_Hora'], df_limpio['RH'])
plt.title('Humedad Relativa (RH)')
plt.ylabel('%')
plt.xlabel('Fecha')
plt.tight_layout()
plt.savefig('graficos/series_temporales.png')

# Histogramas
variables = ['GHI', 'DNI', 'DHI', 'Tdry', 'RH', 'Wspd']
plt.figure(figsize=(15, 10))
for i, var in enumerate(variables):
    plt.subplot(2, 3, i+1)
    sns.histplot(df_limpio[var].dropna(), kde=True)
    plt.title(f'Distribución de {var}')
plt.tight_layout()
plt.savefig('graficos/histogramas.png')

# Guardar datos limpios
print("\nGuardando datos limpios...")
df_limpio.to_csv('antofagasta_clean.csv', index=False)

print("\n¡Proceso completado! Los datos limpios están en 'antofagasta_clean.csv'")
print(f"Se encontraron y limpiaron {df.shape[0] - df_limpio.dropna().shape[0]} filas con valores problemáticos.") 