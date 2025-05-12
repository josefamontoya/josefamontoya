# Análisis de Sistemas Fotovoltaicos

Este proyecto realiza un análisis completo de sistemas fotovoltaicos, desde el procesamiento de datos meteorológicos hasta el análisis financiero y de sensibilidad.

## Dependencias

Las dependencias se encuentran en el archivo `requirements.txt`. Para instalar todas las dependencias necesarias, ejecute:

```bash
pip install -r requirements.txt
```

## Guía de Ejecución

El proyecto debe ejecutarse en el siguiente orden:

1. **Procesamiento de datos TMY**
   - Archivo: `process_tmy_prueba2.ipynb`
   - Función: Limpia y procesa los archivos CSV de datos meteorológicos
   - Entrada: Archivos CSV corruptos
   - Salida: Archivos CSV procesados y reportes de calidad

2. **Preparación para PySAM**
   - Archivo: `process_csv_for_pysam.ipynb`
   - Función: Ajusta los datos procesados al formato requerido por PySAM
   - Entrada: Archivos CSV procesados del paso 1
   - Salida: Archivos CSV en formato PySAM

3. **Simulación PV**
   - Archivo: `pv_simulation.ipynb`
   - Función: Realiza la simulación del sistema fotovoltaico
   - Entrada: Archivos CSV en formato PySAM
   - Salida: Resultados de simulación

4. **Análisis Financiero**
   - Archivo: `financial_analysis.ipynb`
   - Función: Calcula LCOE y VAN
   - Entrada: Resultados de simulación PV
   - Salida: Análisis financiero

5. **Análisis de Sensibilidad y Gráficos**
   - Archivo: `process_results.ipynb`
   - Función: Genera gráficos tornado y análisis de sensibilidad
   - Entrada: Resultados financieros
   - Salida: Gráficos y análisis de sensibilidad

## Estructura de Archivos

```
resultados_pv/
├── process_tmy_prueba2.ipynb      # Procesamiento inicial de datos TMY
├── process_csv_for_pysam.ipynb    # Preparación para PySAM
├── pv_simulation.ipynb            # Simulación del sistema PV
├── financial_analysis.ipynb       # Análisis financiero
├── process_results.ipynb          # Análisis de sensibilidad y gráficos
├── requirements.txt               # Dependencias del proyecto
└── README.md                      # Este archivo
```

## Notas Importantes

- Cada notebook debe ejecutarse en orden secuencial
- Los resultados de cada paso son necesarios para el siguiente
- Se recomienda revisar los reportes de calidad generados en cada paso
- Los archivos de salida se guardan en el mismo directorio con sufijos descriptivos

## Requisitos del Sistema

- Python 3.8 o superior
- Jupyter Notebook o JupyterLab
- Espacio en disco suficiente para los archivos de datos y resultados
- Memoria RAM recomendada: 8GB o superior 