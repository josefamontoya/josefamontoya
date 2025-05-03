import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Configurar el estilo de matplotlib
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['axes.grid'] = True
plt.rcParams['grid.alpha'] = 0.3
plt.rcParams['font.size'] = 10
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12

# Leer los archivos CSV
archivos = {
    'Sevilla': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Sevilla_tmy_corregido.csv',
    'Iquique': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Iquique_tmy_corregido.csv',
    'Jodhpur': '/home/josefa_montoya/Josefamontoya/josefamontoya/tmy_corregidos/Jodhpur_tmy_corregido.csv'
}

datos = {}
promedios_mensuales = {}

for ciudad, archivo in archivos.items():
    # Leer datos
    df = pd.read_csv(archivo, skiprows=2)  # Saltamos las dos primeras filas de metadatos
    
    # Calcular promedios mensuales
    promedios = df.groupby('Month').agg({
        'GHI': 'mean',
        'Temperature': 'mean'
    }).reset_index()
    
    promedios_mensuales[ciudad] = promedios

# Crear gráfico de GHI
plt.figure(figsize=(12, 6))
colores = ['#1f77b4', '#ff7f0e', '#2ca02c']  # Azul, naranja, verde
for (ciudad, datos), color in zip(promedios_mensuales.items(), colores):
    plt.plot(datos['Month'], datos['GHI'], 'o-', label=ciudad, linewidth=2, color=color)

plt.title('Comparación de GHI Promedio Mensual')
plt.xlabel('Mes')
plt.ylabel('GHI (W/m²)')
plt.legend()
plt.xticks(range(1, 13))
plt.tight_layout()
plt.savefig('comparacion_ghi.png', bbox_inches='tight')
plt.close()

# Crear gráfico de temperatura
plt.figure(figsize=(12, 6))
for (ciudad, datos), color in zip(promedios_mensuales.items(), colores):
    plt.plot(datos['Month'], datos['Temperature'], 'o-', label=ciudad, linewidth=2, color=color)

plt.title('Comparación de Temperatura Promedio Mensual')
plt.xlabel('Mes')
plt.ylabel('Temperatura (°C)')
plt.legend()
plt.xticks(range(1, 13))
plt.tight_layout()
plt.savefig('comparacion_temperatura.png', bbox_inches='tight')
plt.close()

# Mostrar estadísticas
print("\nEstadísticas Anuales:")
for ciudad, datos in promedios_mensuales.items():
    print(f"\n{ciudad}:")
    print(f"GHI Promedio Anual: {datos['GHI'].mean():.2f} W/m²")
    print(f"GHI Máximo Mensual: {datos['GHI'].max():.2f} W/m²")
    print(f"Temperatura Promedio Anual: {datos['Temperature'].mean():.2f}°C")
    print(f"Temperatura Máxima Mensual: {datos['Temperature'].max():.2f}°C")
    print(f"Temperatura Mínima Mensual: {datos['Temperature'].min():.2f}°C")

print("\nLas gráficas se han guardado como 'comparacion_ghi.png' y 'comparacion_temperatura.png'") 