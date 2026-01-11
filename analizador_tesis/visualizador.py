"""
Módulo de visualización para análisis de índices de vegetación.
Genera gráficas profesionales y reutilizables.
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
from configuracion.config import DPI_GRAFICAS, FIGSIZE_DEFAULT, FIGSIZE_GRANDE

# Configurar estilo de gráficas
sns.set_style("whitegrid")
plt.rcParams['figure.dpi'] = DPI_GRAFICAS
plt.rcParams['font.size'] = 10


# ============================================================================
# GRÁFICAS DE DISTRIBUCIÓN
# ============================================================================

def graficar_histograma(datos, titulo, xlabel, archivo_salida=None, bins=50, rango=None):
    """
    Genera histograma de distribución de valores.
    
    Args:
        datos: Array de valores
        titulo: Título de la gráfica
        xlabel: Etiqueta del eje X
        archivo_salida: Path para guardar (opcional)
        bins: Número de bins
        rango: Tupla (min, max) para el rango
    """
    datos_validos = datos[~np.isnan(datos)]
    
    if len(datos_validos) == 0:
        print("No hay datos válidos para graficar")
        return
    
    fig, ax = plt.subplots(figsize=FIGSIZE_DEFAULT)
    
    # Histograma
    n, bins_edges, patches = ax.hist(
        datos_validos, 
        bins=bins, 
        range=rango,
        color='#2ecc71',
        alpha=0.7,
        edgecolor='black'
    )
    
    # Línea de media y mediana
    media = np.mean(datos_validos)
    mediana = np.median(datos_validos)
    
    ax.axvline(media, color='red', linestyle='--', linewidth=2, label=f'Media: {media:.4f}')
    ax.axvline(mediana, color='blue', linestyle='--', linewidth=2, label=f'Mediana: {mediana:.4f}')
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel('Frecuencia')
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def graficar_boxplot_temporal(df, columna_fecha, columna_valor, titulo, archivo_salida=None):
    """
    Genera boxplot de valores a lo largo del tiempo.
    
    Args:
        df: DataFrame con fechas y valores
        columna_fecha: Nombre de columna de fechas
        columna_valor: Nombre de columna de valores
        titulo: Título de la gráfica
        archivo_salida: Path para guardar (opcional)
    """
    fig, ax = plt.subplots(figsize=FIGSIZE_GRANDE)
    
    # Preparar datos
    df_sorted = df.sort_values(columna_fecha)
    fechas_unicas = df_sorted[columna_fecha].unique()
    
    # Crear boxplot
    datos_por_fecha = [df_sorted[df_sorted[columna_fecha] == fecha][columna_valor].values 
                       for fecha in fechas_unicas]
    
    bp = ax.boxplot(datos_por_fecha, 
                    labels=[str(f)[:10] for f in fechas_unicas],
                    patch_artist=True,
                    showfliers=True)
    
    # Colorear boxes
    for patch in bp['boxes']:
        patch.set_facecolor('#3498db')
        patch.set_alpha(0.7)
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel(columna_valor)
    ax.set_title(titulo)
    ax.grid(True, alpha=0.3, axis='y')
    
    # Rotar etiquetas
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# ============================================================================
# GRÁFICAS DE SERIES TEMPORALES
# ============================================================================

def graficar_serie_temporal(df, columna_fecha, columna_valor, titulo, 
                           archivo_salida=None, con_bandas=True):
    """
    Genera gráfica de serie temporal con bandas de confianza.
    
    Args:
        df: DataFrame con fechas y valores
        columna_fecha: Nombre de columna de fechas
        columna_valor: Nombre de columna de valores
        titulo: Título de la gráfica
        archivo_salida: Path para guardar (opcional)
        con_bandas: Si True, incluye bandas de desv. estándar
    """
    fig, ax = plt.subplots(figsize=FIGSIZE_GRANDE)
    
    # Ordenar por fecha
    df_sorted = df.sort_values(columna_fecha)
    
    # Convertir fechas a datetime si es necesario
    if not pd.api.types.is_datetime64_any_dtype(df_sorted[columna_fecha]):
        df_sorted[columna_fecha] = pd.to_datetime(df_sorted[columna_fecha])
    
    # Agrupar por fecha y calcular media y std
    stats_por_fecha = df_sorted.groupby(columna_fecha)[columna_valor].agg(['mean', 'std', 'median'])
    
    # Línea principal (media)
    ax.plot(stats_por_fecha.index, stats_por_fecha['mean'], 
            marker='o', linewidth=2, markersize=6, color='#2ecc71',
            label='Media')
    
    # Línea de mediana
    ax.plot(stats_por_fecha.index, stats_por_fecha['median'],
            marker='s', linewidth=1.5, markersize=5, color='#3498db',
            linestyle='--', label='Mediana')
    
    # Bandas de confianza (±1 desv. estándar)
    if con_bandas:
        ax.fill_between(
            stats_por_fecha.index,
            stats_por_fecha['mean'] - stats_por_fecha['std'],
            stats_por_fecha['mean'] + stats_por_fecha['std'],
            alpha=0.3, color='#2ecc71',
            label='±1 Desv. Estándar'
        )
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel(columna_valor)
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Rotar fechas
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def graficar_evolucion_cv(df, columna_fecha, columna_cv, titulo, archivo_salida=None):
    """
    Genera gráfica de evolución del Coeficiente de Variación.
    
    Args:
        df: DataFrame con fechas y CV
        columna_fecha: Nombre de columna de fechas
        columna_cv: Nombre de columna de CV
        titulo: Título de la gráfica
        archivo_salida: Path para guardar (opcional)
    """
    fig, ax = plt.subplots(figsize=FIGSIZE_GRANDE)
    
    # Ordenar por fecha
    df_sorted = df.sort_values(columna_fecha)
    
    # Convertir fechas
    if not pd.api.types.is_datetime64_any_dtype(df_sorted[columna_fecha]):
        df_sorted[columna_fecha] = pd.to_datetime(df_sorted[columna_fecha])
    
    # Graficar CV
    ax.plot(df_sorted[columna_fecha], df_sorted[columna_cv],
            marker='o', linewidth=2, markersize=6, color='#e74c3c')
    
    # Líneas de referencia
    ax.axhline(10, color='green', linestyle='--', alpha=0.5, label='CV 10% (Homogéneo)')
    ax.axhline(20, color='orange', linestyle='--', alpha=0.5, label='CV 20% (Moderado)')
    ax.axhline(30, color='red', linestyle='--', alpha=0.5, label='CV 30% (Heterogéneo)')
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Coeficiente de Variación (%)')
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# ============================================================================
# GRÁFICAS DE COMPARACIÓN
# ============================================================================

def graficar_comparacion_indices(datos_indices, titulo, archivo_salida=None):
    """
    Compara múltiples índices en un mismo gráfico.
    
    Args:
        datos_indices: Dict {indice: df} con DataFrames por índice
        titulo: Título de la gráfica
        archivo_salida: Path para guardar (opcional)
    """
    fig, ax = plt.subplots(figsize=FIGSIZE_GRANDE)
    
    colores = ['#e74c3c', '#3498db', '#2ecc71', '#f39c12', '#9b59b6']
    
    for i, (indice, df) in enumerate(datos_indices.items()):
        if 'fecha' in df.columns and 'media' in df.columns:
            df_sorted = df.sort_values('fecha')
            df_sorted['fecha'] = pd.to_datetime(df_sorted['fecha'])
            
            ax.plot(df_sorted['fecha'], df_sorted['media'],
                   marker='o', linewidth=2, label=indice,
                   color=colores[i % len(colores)])
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel('Valor Medio')
    ax.set_title(titulo)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


def graficar_matriz_correlacion(df, columnas, titulo, archivo_salida=None):
    """
    Genera matriz de correlación entre índices.
    
    Args:
        df: DataFrame con datos
        columnas: Lista de columnas a correlacionar
        titulo: Título de la gráfica
        archivo_salida: Path para guardar (opcional)
    """
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Calcular correlación
    corr = df[columnas].corr()
    
    # Heatmap
    sns.heatmap(corr, annot=True, fmt='.3f', cmap='coolwarm',
                center=0, square=True, linewidths=1,
                cbar_kws={"shrink": 0.8}, ax=ax)
    
    ax.set_title(titulo)
    
    plt.tight_layout()
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


# ============================================================================
# GRÁFICAS DE RESUMEN
# ============================================================================

def generar_dashboard_indice(df, indice, archivo_salida=None):
    """
    Genera dashboard con múltiples visualizaciones de un índice.
    
    Args:
        df: DataFrame con análisis del índice
        indice: Nombre del índice
        archivo_salida: Path para guardar (opcional)
    """
    fig = plt.figure(figsize=(16, 12))
    gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)
    
    # Filtrar datos válidos
    df_valido = df[df['pixeles_validos'] > 0].copy()
    
    if len(df_valido) == 0:
        print(f"No hay datos válidos para generar dashboard de {indice}")
        return
    
    # Convertir fecha
    df_valido['fecha'] = pd.to_datetime(df_valido['fecha'])
    df_valido = df_valido.sort_values('fecha')
    
    # 1. Serie temporal de media
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(df_valido['fecha'], df_valido['media'], marker='o', linewidth=2, color='#2ecc71')
    ax1.fill_between(df_valido['fecha'], 
                     df_valido['media'] - df_valido['std'],
                     df_valido['media'] + df_valido['std'],
                     alpha=0.3, color='#2ecc71')
    ax1.set_title(f'{indice} - Evolución Temporal (Media ± Desv. Estándar)')
    ax1.set_xlabel('Fecha')
    ax1.set_ylabel('Valor')
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 2. Boxplot temporal
    ax2 = fig.add_subplot(gs[1, 0])
    fechas_str = [str(f)[:10] for f in df_valido['fecha']]
    bp = ax2.boxplot([df_valido.iloc[i:i+1]['media'].values for i in range(len(df_valido))],
                     labels=fechas_str, patch_artist=True)
    for patch in bp['boxes']:
        patch.set_facecolor('#3498db')
    ax2.set_title('Distribución por Fecha')
    ax2.set_ylabel('Valor')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=90, ha='right', fontsize=8)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 3. Evolución del CV
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.plot(df_valido['fecha'], df_valido['cv'], marker='o', linewidth=2, color='#e74c3c')
    ax3.axhline(10, color='green', linestyle='--', alpha=0.5)
    ax3.axhline(20, color='orange', linestyle='--', alpha=0.5)
    ax3.axhline(30, color='red', linestyle='--', alpha=0.5)
    ax3.set_title('Evolución del Coeficiente de Variación')
    ax3.set_xlabel('Fecha')
    ax3.set_ylabel('CV (%)')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # 4. Histograma de valores medios
    ax4 = fig.add_subplot(gs[2, 0])
    ax4.hist(df_valido['media'], bins=20, color='#9b59b6', alpha=0.7, edgecolor='black')
    ax4.axvline(df_valido['media'].mean(), color='red', linestyle='--', linewidth=2)
    ax4.set_title('Distribución de Valores Medios')
    ax4.set_xlabel('Valor Medio')
    ax4.set_ylabel('Frecuencia')
    ax4.grid(True, alpha=0.3)
    
    # 5. Tabla de estadísticas
    ax5 = fig.add_subplot(gs[2, 1])
    ax5.axis('off')
    
    stats_texto = f"""
    ESTADÍSTICAS GLOBALES
    ════════════════════════════
    
    Imágenes analizadas: {len(df_valido)}
    
    Media global:        {df_valido['media'].mean():.6f}
    Mediana global:      {df_valido['mediana'].mean():.6f}
    Desv. estándar:      {df_valido['std'].mean():.6f}
    
    Rango absoluto:      [{df_valido['min'].min():.4f}, {df_valido['max'].max():.4f}]
    
    CV promedio:         {df_valido['cv'].mean():.2f}%
    Heterogeneidad:      {df_valido['heterogeneidad'].mode()[0] if len(df_valido['heterogeneidad'].mode()) > 0 else 'N/A'}
    
    Percentiles promedio:
      P5:  {df_valido['p05'].mean():.6f}
      P95: {df_valido['p95'].mean():.6f}
    """
    
    ax5.text(0.1, 0.9, stats_texto, transform=ax5.transAxes,
            fontsize=10, verticalalignment='top', fontfamily='monospace',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
    
    fig.suptitle(f'Dashboard de Análisis - {indice}', fontsize=16, fontweight='bold')
    
    if archivo_salida:
        plt.savefig(archivo_salida, dpi=DPI_GRAFICAS, bbox_inches='tight')
        plt.close()
    else:
        plt.show()


if __name__ == "__main__":
    # Prueba del módulo
    print("="*80)
    print("MÓDULO VISUALIZADOR - PRUEBA")
    print("="*80)
    
    # Datos de prueba
    np.random.seed(42)
    datos_test = np.random.normal(0.6, 0.1, 1000)
    
    print("\nGenerando gráficas de prueba...")
    graficar_histograma(datos_test, "Histograma de Prueba", "Valor NDVI")
    print("✓ Módulo funcionando correctamente")
