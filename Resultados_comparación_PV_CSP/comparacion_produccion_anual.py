import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from math import pi

# Configuración de estilo
plt.style.use('default')
sns.set_theme(style="whitegrid")
sns.set_palette("husl")

def cargar_datos_pv():
    """Carga y procesa los datos de PV"""
    pv_data = []
    for config in ['config1', 'config2', 'config3']:
        df = pd.read_csv(f'/home/josefa_montoya/Josefamontoya/josefamontoya/Resultados_pv/resultados_simulacion_{config}.csv')
        df['Tecnología'] = 'PV'
        df['Configuración'] = config
        pv_data.append(df)
    return pd.concat(pv_data)

def cargar_datos_csp():
    """Carga y procesa los datos de CSP"""
    csp_df = pd.read_csv('/home/josefa_montoya/Josefamontoya/josefamontoya/Resultados_csp/resultados_anuales.csv')
    csp_df['Tecnología'] = 'CSP'
    csp_df['Energía_Anual_kWh'] = csp_df['Energía Anual (GWh)'] * 1e6
    csp_df['Capacidad_kW'] = 100000  # 100 MW
    return csp_df

def crear_graficos_comparativos(pv_df, csp_df):
    # 1. Scatter plot con regresión lineal
    plt.figure(figsize=(14, 7))
    
    # Preparar datos
    pv_avg = pv_df.groupby(['Ubicación', 'Tecnología']).agg({
        'Energía_Anual_kWh': 'mean',
        'Factor_Capacidad_%': 'mean'
    }).reset_index()
    
    csp_avg = csp_df[csp_df['Configuración'] == 'default'].groupby(['Ubicación', 'Tecnología']).agg({
        'Energía_Anual_kWh': 'mean',
        'Factor de Capacidad (%)': 'mean'
    }).reset_index()
    csp_avg = csp_avg.rename(columns={'Factor de Capacidad (%)': 'Factor_Capacidad_%'})
    
    combined_avg = pd.concat([pv_avg, csp_avg])
    
    # Crear scatter plot con regresión
    sns.lmplot(data=combined_avg, x='Energía_Anual_kWh', y='Factor_Capacidad_%',
              hue='Tecnología', height=7, aspect=2, scatter_kws={'s': 100})
    
    plt.title('Relación entre Producción Anual y Factor de Capacidad con Regresión Lineal')
    plt.xlabel('Energía Anual (kWh)')
    plt.ylabel('Factor de Capacidad (%)')
    plt.tight_layout()
    plt.savefig('scatter_regresion_pv_csp.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 2. Heatmap de correlación
    plt.figure(figsize=(12, 8))
    
    # Preparar datos para heatmap
    correlation_data = combined_avg.pivot_table(
        index='Ubicación',
        columns='Tecnología',
        values=['Energía_Anual_kWh', 'Factor_Capacidad_%']
    )
    
    # Calcular matriz de correlación
    corr_matrix = correlation_data.corr()
    
    # Crear heatmap
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, fmt='.2f',
                square=True, linewidths=.5, cbar_kws={"shrink": .8})
    
    plt.title('Matriz de Correlación entre Variables')
    plt.tight_layout()
    plt.savefig('heatmap_correlacion.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 3. Scatter plot con facetas por ubicación
    plt.figure(figsize=(16, 10))
    
    # Crear scatter plot con facetas
    g = sns.FacetGrid(combined_avg, col='Ubicación', col_wrap=3, height=4)
    g.map(sns.scatterplot, 'Energía_Anual_kWh', 'Factor_Capacidad_%', 'Tecnología',
          s=100, alpha=0.7)
    g.add_legend()
    
    plt.suptitle('Relación Producción-Factor de Capacidad por Ubicación', y=1.02)
    plt.tight_layout()
    plt.savefig('scatter_facetas_ubicacion.png', dpi=300, bbox_inches='tight')
    plt.close()

    # 4. Heatmap de producción normalizada por ubicación
    plt.figure(figsize=(14, 8))
    
    # Preparar datos para heatmap de producción
    production_data = combined_avg.pivot_table(
        index='Ubicación',
        columns='Tecnología',
        values='Energía_Anual_kWh'
    )
    
    # Normalizar los datos
    production_normalized = production_data / production_data.max()
    
    # Crear heatmap
    sns.heatmap(production_normalized, annot=True, cmap='YlOrRd', fmt='.2f',
                linewidths=.5, cbar_kws={'label': 'Producción Normalizada'})
    
    plt.title('Producción Normalizada por Ubicación y Tecnología')
    plt.tight_layout()
    plt.savefig('heatmap_produccion.png', dpi=300, bbox_inches='tight')
    plt.close()

def main():
    print("Cargando datos de PV...")
    pv_df = cargar_datos_pv()
    
    print("Cargando datos de CSP...")
    csp_df = cargar_datos_csp()
    
    print("Generando gráficos comparativos...")
    crear_graficos_comparativos(pv_df, csp_df)
    
    print("\nGráficos generados:")
    print("- scatter_regresion_pv_csp.png")
    print("- heatmap_correlacion.png")
    print("- scatter_facetas_ubicacion.png")
    print("- heatmap_produccion.png")

if __name__ == "__main__":
    main() 