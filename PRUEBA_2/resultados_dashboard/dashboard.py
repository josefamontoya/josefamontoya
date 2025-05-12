# %% [markdown]
# # Dashboard de Análisis Fotovoltaico
# 
# Este dashboard permite visualizar los resultados de las simulaciones fotovoltaicas para diferentes ubicaciones y años.

# %%
import pandas as pd
import numpy as np
import json
import plotly.graph_objects as go
from ipywidgets import interact, widgets
from IPython.display import display, HTML

# %%
def load_data(location, year):
    base_path = './'
    power_file = f'{base_path}{location}_{year}_power.csv'
    kpis_file = f'{base_path}{location}_{year}_kpis.json'
    
    power_data = pd.read_csv(power_file)
    with open(kpis_file, 'r') as f:
        kpis_data = json.load(f)
    
    return power_data, kpis_data

# %%
def plot_power_curve(power_data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=power_data['timestamp'],
        y=power_data['Power (kW)'],
        mode='lines',
        name='Potencia'
    ))
    fig.update_layout(
        title='Curva Horaria de Potencia',
        xaxis_title='Fecha y hora',
        yaxis_title='Potencia (kW)',
        template='plotly_white',
        xaxis=dict(rangeslider=dict(visible=True))
    )
    return fig

# %%
def display_kpis(kpis_data):
    html = f"""
    <div style='display: flex; justify-content: space-around; margin: 20px 0;'>
        <div style='text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
            <h3>Energía Anual</h3>
            <p style='font-size: 24px;'>{kpis_data['annual_energy']:.2f} MWh</p>
        </div>
        <div style='text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
            <h3>LCOE</h3>
            <p style='font-size: 24px;'>{kpis_data['lcoe']:.2f} USD/MWh</p>
        </div>
        <div style='text-align: center; padding: 20px; background-color: #f0f0f0; border-radius: 10px;'>
            <h3>Factor de Capacidad</h3>
            <p style='font-size: 24px;'>{kpis_data['capacity_factor']:.2%}</p>
        </div>
    </div>
    """
    display(HTML(html))

# %%
def update_dashboard(location, year):
    power_data, kpis_data = load_data(location, year)
    display_kpis(kpis_data)
    fig = plot_power_curve(power_data)
    fig.show()

# %%
location_widget = widgets.Dropdown(
    options=['calama', 'Vallenar', 'salvador'],
    value='calama',
    description='Ubicación:'
)
year_widget = widgets.Dropdown(
    options=[2014],
    value=2014,
    description='Año:'
)
interact(update_dashboard, location=location_widget, year=year_widget) 