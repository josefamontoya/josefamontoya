import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import glob
import os

# Inicializar la aplicación Dash
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Cargar los datos
def cargar_datos():
    # Datos meteorológicos
    archivos_tmy = {
        'Sevilla': 'josefamontoya/tmy_corregidos/Sevilla_tmy_corregido.csv',
        'Iquique': 'josefamontoya/tmy_corregidos/Iquique_tmy_corregido.csv',
        'Jodhpur': 'josefamontoya/tmy_corregidos/Jodhpur_tmy_corregido.csv'
    }
    
    dfs_tmy = {}
    for ciudad, archivo in archivos_tmy.items():
        df = pd.read_csv(archivo, skiprows=2)
        df['Ciudad'] = ciudad
        df['Fecha'] = pd.to_datetime(df[['Year', 'Month', 'Day', 'Hour', 'Minute']])
        dfs_tmy[ciudad] = df
    
    # Datos de LCOE
    archivos_lcoe = {
        'Sevilla': {
            'PV': 'josefamontoya/Resultados_LCOE/sensibilidad_PV_Sevilla.csv',
            'CSP': 'josefamontoya/Resultados_LCOE/sensibilidad_CSP_Sevilla.csv'
        },
        'Iquique': {
            'PV': 'josefamontoya/Resultados_LCOE/sensibilidad_PV_Iquique.csv',
            'CSP': 'josefamontoya/Resultados_LCOE/sensibilidad_CSP_Iquique.csv'
        },
        'Jodhpur': {
            'PV': 'josefamontoya/Resultados_LCOE/sensibilidad_PV_Jodhpur.csv',
            'CSP': 'josefamontoya/Resultados_LCOE/sensibilidad_CSP_Jodhpur.csv'
        }
    }
    
    dfs_lcoe = {}
    for ciudad, archivos in archivos_lcoe.items():
        dfs_lcoe[ciudad] = {}
        for tecnologia, archivo in archivos.items():
            df = pd.read_csv(archivo)
            df['Ciudad'] = ciudad
            df['Tecnología'] = tecnologia
            dfs_lcoe[ciudad][tecnologia] = df
    
    # Datos de generación de energía
    archivos_energia = {
        'PV': {
            'Sevilla': 'josefamontoya/Resultados_pv/pv_lcoe_results_Sevilla.csv',
            'Iquique': 'josefamontoya/Resultados_pv/pv_lcoe_results_Iquique.csv',
            'Jodhpur': 'josefamontoya/Resultados_pv/pv_lcoe_results_Jodhpur.csv'
        },
        'CSP': {
            'Sevilla': 'josefamontoya/Resultados_csp/resultados_anuales.csv',
            'Iquique': 'josefamontoya/Resultados_csp/resultados_anuales.csv',
            'Jodhpur': 'josefamontoya/Resultados_csp/resultados_anuales.csv'
        }
    }
    
    dfs_energia = {}
    for tecnologia, ciudades in archivos_energia.items():
        dfs_energia[tecnologia] = {}
        for ciudad, archivo in ciudades.items():
            df = pd.read_csv(archivo)
            df['Ciudad'] = ciudad
            df['Tecnología'] = tecnologia
            dfs_energia[tecnologia][ciudad] = df
    
    return dfs_tmy, dfs_lcoe, dfs_energia

# Cargar los datos al inicio
datos_tmy, datos_lcoe, datos_energia = cargar_datos()

# Layout del dashboard
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Dashboard de Energía Solar", className="text-center my-4"), width=12)
    ]),
    
    dbc.Tabs([
        dbc.Tab(label="Datos Meteorológicos", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Filtros", className="mb-3"),
                    dcc.Dropdown(
                        id='ciudad-dropdown',
                        options=[
                            {'label': 'Sevilla', 'value': 'Sevilla'},
                            {'label': 'Iquique', 'value': 'Iquique'},
                            {'label': 'Jodhpur', 'value': 'Jodhpur'}
                        ],
                        value='Sevilla',
                        className="mb-3"
                    ),
                    dcc.Dropdown(
                        id='variable-dropdown',
                        options=[
                            {'label': 'Radiación Global (GHI)', 'value': 'GHI'},
                            {'label': 'Radiación Directa (DNI)', 'value': 'DNI'},
                            {'label': 'Radiación Difusa (DHI)', 'value': 'DHI'},
                            {'label': 'Temperatura', 'value': 'Temperature'},
                            {'label': 'Velocidad del Viento', 'value': 'Wind Speed'}
                        ],
                        value='GHI',
                        className="mb-3"
                    ),
                    dcc.DatePickerRange(
                        id='fecha-range',
                        start_date=pd.to_datetime('2022-01-01'),
                        end_date=pd.to_datetime('2022-12-31'),
                        display_format='DD/MM/YYYY'
                    )
                ], width=3),
                
                dbc.Col([
                    dcc.Graph(id='serie-temporal-graph'),
                    dcc.Graph(id='boxplot-graph')
                ], width=9)
            ])
        ]),
        
        dbc.Tab(label="Análisis de Energía", children=[
            dbc.Row([
                dbc.Col([
                    html.H4("Filtros", className="mb-3"),
                    dcc.Dropdown(
                        id='ciudad-energia-dropdown',
                        options=[
                            {'label': 'Sevilla', 'value': 'Sevilla'},
                            {'label': 'Iquique', 'value': 'Iquique'},
                            {'label': 'Jodhpur', 'value': 'Jodhpur'}
                        ],
                        value='Sevilla',
                        className="mb-3"
                    ),
                    dcc.Dropdown(
                        id='tecnologia-energia-dropdown',
                        options=[
                            {'label': 'PV', 'value': 'PV'},
                            {'label': 'CSP', 'value': 'CSP'}
                        ],
                        value='PV',
                        className="mb-3"
                    )
                ], width=3),
                
                dbc.Col([
                    dcc.Graph(id='energia-anual-graph'),
                    dcc.Graph(id='energia-mensual-graph')
                ], width=9)
            ])
        ])
    ])
], fluid=True)

# Callbacks para actualizar los gráficos meteorológicos
@app.callback(
    [Output('serie-temporal-graph', 'figure'),
     Output('boxplot-graph', 'figure')],
    [Input('ciudad-dropdown', 'value'),
     Input('variable-dropdown', 'value'),
     Input('fecha-range', 'start_date'),
     Input('fecha-range', 'end_date')]
)
def update_meteorological_graphs(ciudad, variable, start_date, end_date):
    df = datos_tmy[ciudad].copy()
    df = df[(df['Fecha'] >= start_date) & (df['Fecha'] <= end_date)]
    
    # Gráfico de serie temporal
    fig_serie = px.line(
        df,
        x='Fecha',
        y=variable,
        title=f'{variable} en {ciudad}',
        labels={variable: f'{variable} (W/m²)' if variable in ['GHI', 'DNI', 'DHI'] else f'{variable} (°C)' if variable == 'Temperature' else f'{variable} (m/s)'}
    )
    
    # Gráfico de boxplot por mes
    df['Mes'] = df['Fecha'].dt.month_name()
    fig_box = px.box(
        df,
        x='Mes',
        y=variable,
        title=f'Distribución mensual de {variable} en {ciudad}',
        labels={variable: f'{variable} (W/m²)' if variable in ['GHI', 'DNI', 'DHI'] else f'{variable} (°C)' if variable == 'Temperature' else f'{variable} (m/s)'}
    )
    
    return fig_serie, fig_box

# Callbacks para actualizar los gráficos de energía
@app.callback(
    [Output('energia-anual-graph', 'figure'),
     Output('energia-mensual-graph', 'figure')],
    [Input('ciudad-energia-dropdown', 'value'),
     Input('tecnologia-energia-dropdown', 'value')]
)
def update_energy_graphs(ciudad, tecnologia):
    df = datos_energia[tecnologia][ciudad].copy()
    
    # Gráfico de energía anual
    if tecnologia == 'PV':
        # Para PV, usamos Annual_Energy_kWh
        fig_anual = px.bar(
            df,
            x='Ciudad',
            y='Annual_Energy_kWh',
            color='Tecnología',
            title=f'Energía Anual Generada por {tecnologia} en {ciudad}',
            labels={'Annual_Energy_kWh': 'Energía Anual (kWh)'}
        )
    else:
        # Para CSP, usamos Energía Anual (GWh)
        fig_anual = px.bar(
            df,
            x='Ciudad',
            y='Energía Anual (GWh)',
            color='Tecnología',
            title=f'Energía Anual Generada por {tecnologia} en {ciudad}',
            labels={'Energía Anual (GWh)': 'Energía Anual (GWh)'}
        )
    
    # Gráfico de energía mensual
    if tecnologia == 'CSP':
        # Para CSP, usamos los datos mensuales
        df_mensual = pd.read_csv('josefamontoya/Resultados_csp/resultados_mensuales.csv')
        df_mensual = df_mensual[df_mensual['Ubicación'] == ciudad]
        fig_mensual = px.line(
            df_mensual,
            x='Mes',
            y='Energía (GWh)',
            color='Configuración',
            title=f'Energía Mensual Generada por {tecnologia} en {ciudad}',
            labels={'Energía (GWh)': 'Energía Mensual (GWh)'}
        )
    else:
        # Para PV, mostramos un mensaje de que no hay datos mensuales disponibles
        fig_mensual = go.Figure()
        fig_mensual.add_annotation(
            text="Datos mensuales no disponibles para PV",
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=20)
        )
        fig_mensual.update_layout(
            title=f'Energía Mensual Generada por {tecnologia} en {ciudad}'
        )
    
    return fig_anual, fig_mensual

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050) 