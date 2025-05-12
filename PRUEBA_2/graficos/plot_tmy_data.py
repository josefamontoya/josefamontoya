import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_tmy_data(file_path, title):
    """
    Grafica los datos de GHI, DNI y DHI de un archivo TMY en gráficos separados.
    
    Args:
        file_path (str): Ruta del archivo a graficar
        title (str): Título del gráfico
    """
    # Leer los datos
    df = pd.read_csv(file_path)
    
    # Crear gráficos separados para GHI, DNI y DHI
    for column in ['GHI', 'DNI', 'DHI']:
        plt.figure(figsize=(12, 6))
        plt.plot(df[column], label=column)
        plt.title(f'{title} - {column}')
        plt.xlabel('Índice de Registro')
        plt.ylabel('Valor')
        plt.legend()
        plt.grid(True)
        plt.savefig(file_path.replace('.csv', f'_{column}_plot.png'))
        plt.close()

def main():
    # Directorio base
    base_dir = '/home/josefa_montoya/Josefamontoya/josefamontoya/PRUEBA_2'
    
    # Lista de archivos a graficar
    files_to_plot = [
        'Vallenar_processed.csv',
        'calama_processed.csv',
        'salvador_processed.csv'
    ]
    
    # Graficar cada archivo
    for file_name in files_to_plot:
        file_path = os.path.join(base_dir, file_name)
        title = f'Datos de {file_name.replace("_processed.csv", "")}'
        plot_tmy_data(file_path, title)

if __name__ == "__main__":
    main() 