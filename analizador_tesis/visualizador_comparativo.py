"""
Visualizaciones comparativas entre múltiples índices de vegetación.

NOTA: Este módulo genera gráficas comparativas para analizar
todos los índices juntos y facilitar la interpretación.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# Importar configuración
import sys
sys.path.append(str(Path(__file__).parent.parent))
from configuracion.config import DPI_GRAFICAS, FIGSIZE_GRANDE, INDICES_INFO

# Configurar estilo
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = DPI_GRAFICAS
plt.rcParams['font.size'] = 10


# Paleta de colores para cada índice
COLORES_INDICES = {
    'NDVI': '#2ecc71',   # Verde
    'NDRE': '#e74c3c',   # Rojo
    'MSAVI': '#3498db',  # Azul
    'NDMI': '#9b59b6',   # Morado
    'RECI': '#f39c12'    # Naranja
}


def graficar_indices_separados(datos_indices, titulo_base, archivo_salida):
    """
    Genera una imagen con gráficas separadas para cada índice (subplots).
    
    NOTA: Útil para comparar patrones temporales de cada índice por separado.
    
    Args:
        datos_indices: Dict {indice: DataFrame con columnas 'fecha' y 'media'}
        titulo_base: Título base para la gráfica
        archivo_salida: Path donde guardar la imagen
    """
    n_indices = len(datos_indices)
    
    if n_indices == 0:
        print("No hay datos para graficar")
        return
    
    # Crear subplots (2 columnas)
    n_cols = 2
    n_rows = (n_indices + 1) // 2
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4*n_rows))
    fig.suptitle(titulo_base, fontsize=16, fontweight='bold')
    
    # Aplanar axes si es necesario
    if n_indices == 1:
        axes = [axes]
    elif n_rows == 1:
        axes = axes
    else:
        axes = axes.flatten()
    
    for idx, (indice, df) in enumerate(datos_indices.items()):
        ax = axes[idx]
        
        # Ordenar por fecha
        df_sorted = df.sort_values('fecha')
        
        # Gráfica de líneas
        color = COLORES_INDICES.get(indice, '#34495e')
        ax.plot(df_sorted['fecha'], df_sorted['media'], 
                marker='o', linewidth=2, markersize=6,
                color=color, label=indice)
        
        # Banda de confianza (± 1 std si existe)
        if 'std' in df_sorted.columns:
            ax.fill_between(
                df_sorted['fecha'],
                df_sorted['media'] - df_sorted['std'],
                df_sorted['media'] + df_sorted['std'],
                alpha=0.2, color=color
            )
        
        # Formato
        ax.set_xlabel('Fecha', fontsize=10)
        ax.set_ylabel('Valor del índice', fontsize=10)
        ax.set_title(f'{indice} - {INDICES_INFO[indice]["nombre"]}', 
                     fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.legend(loc='best')
        
        # Rotar etiquetas de fecha
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Ocultar subplots vacíos
    for idx in range(n_indices, len(axes)):
        axes[idx].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfica separada guardada: {archivo_salida.name}")


def graficar_indices_juntos(datos_indices, titulo, archivo_salida):
    """
    Genera una imagen con todos los índices en la misma gráfica.
    
    NOTA: Útil para comparar directamente la evolución de todos los índices.
    
    Args:
        datos_indices: Dict {indice: DataFrame con columnas 'fecha' y 'media'}
        titulo: Título de la gráfica
        archivo_salida: Path donde guardar la imagen
    """
    if len(datos_indices) == 0:
        print("No hay datos para graficar")
        return
    
    fig, ax = plt.subplots(figsize=(14, 8))
    
    for indice, df in datos_indices.items():
        # Ordenar por fecha
        df_sorted = df.sort_values('fecha')
        
        # Gráfica de líneas
        color = COLORES_INDICES.get(indice, '#34495e')
        ax.plot(df_sorted['fecha'], df_sorted['media'],
                marker='o', linewidth=2.5, markersize=7,
                color=color, label=indice, alpha=0.8)
    
    # Formato
    ax.set_xlabel('Fecha', fontsize=12, fontweight='bold')
    ax.set_ylabel('Valor del índice', fontsize=12, fontweight='bold')
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    
    # Rotar etiquetas
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfica comparativa guardada: {archivo_salida.name}")


def graficar_barras_comparativas(datos_indices, metrica, titulo, archivo_salida):
    """
    Genera gráfica de barras comparando una métrica entre índices.
    
    Args:
        datos_indices: Dict {indice: valor_metrica}
        metrica: Nombre de la métrica (ej: 'Media Global')
        titulo: Título de la gráfica
        archivo_salida: Path donde guardar
    """
    if len(datos_indices) == 0:
        print("No hay datos para graficar")
        return
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    indices = list(datos_indices.keys())
    valores = list(datos_indices.values())
    colores = [COLORES_INDICES.get(idx, '#34495e') for idx in indices]
    
    # Gráfica de barras
    bars = ax.bar(indices, valores, color=colores, alpha=0.7, edgecolor='black', linewidth=1.5)
    
    # Agregar valores en las barras
    for bar, valor in zip(bars, valores):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{valor:.4f}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Formato
    ax.set_xlabel('Índice de Vegetación', fontsize=12, fontweight='bold')
    ax.set_ylabel(metrica, fontsize=12, fontweight='bold')
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Gráfica de barras guardada: {archivo_salida.name}")


def generar_dashboard_comparativo(datos_indices, carpeta_salida):
    """
    Genera un dashboard completo con todas las visualizaciones comparativas.
    
    Args:
        datos_indices: Dict {indice: DataFrame} con datos temporales
        carpeta_salida: Path de carpeta donde guardar las imágenes
    """
    carpeta_salida = Path(carpeta_salida)
    carpeta_salida.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print("\n📊 Generando visualizaciones comparativas...")
    
    # 1. Gráfica con índices separados (subplots)
    archivo_separados = carpeta_salida / f"comparativa_separados_{timestamp}.png"
    graficar_indices_separados(
        datos_indices,
        "Evolución Temporal de Índices de Vegetación (Individual)",
        archivo_separados
    )
    
    # 2. Gráfica con todos los índices juntos
    archivo_juntos = carpeta_salida / f"comparativa_juntos_{timestamp}.png"
    graficar_indices_juntos(
        datos_indices,
        "Evolución Temporal de Índices de Vegetación (Comparativa)",
        archivo_juntos
    )
    
    # 3. Gráfica de barras con medias globales
    medias_globales = {
        indice: df['media'].mean() 
        for indice, df in datos_indices.items()
    }
    
    archivo_barras = carpeta_salida / f"comparativa_barras_media_{timestamp}.png"
    graficar_barras_comparativas(
        medias_globales,
        "Media Global",
        "Comparación de Medias Globales por Índice",
        archivo_barras
    )
    
    print(f"\n✅ Dashboard comparativo generado en: {carpeta_salida}")
    print(f"   • Gráficas separadas: {archivo_separados.name}")
    print(f"   • Gráficas juntas: {archivo_juntos.name}")
    print(f"   • Barras comparativas: {archivo_barras.name}")


if __name__ == "__main__":
    print("Módulo de visualización comparativa")
    print("Importar y usar las funciones:")
    print("  - graficar_indices_separados()")
    print("  - graficar_indices_juntos()")
    print("  - graficar_barras_comparativas()")
    print("  - generar_dashboard_comparativo()")
