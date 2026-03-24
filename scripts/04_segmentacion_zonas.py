"""
Segmentación de Zonas y Análisis por Región

Este script realiza segmentación del área de estudio y análisis por zonas:
1. Segmentación espacial (clustering, cuadrantes, percentiles)
2. Estadísticas por zona
3. Evolución temporal de cada zona
4. Comparación entre zonas
5. Identificación de zonas problemáticas/saludables
6. Mapas de zonificación

ANÁLISIS CLAVE PARA IDENTIFICAR HETEROGENEIDAD ESPACIAL
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

# Agregar rutas para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from analizador_tesis.procesador_base import (
    cargar_imagen_enmascarada,
    listar_imagenes_indice,
    cargar_datos_optimizado
)
from analizador_tesis.espacial import (
    clustering_kmeans,
    dividir_en_cuadrantes,
    detectar_hotspots,
    calcular_estadisticas_espaciales
)
from analizador_tesis.temporal import (
    calcular_tendencia_lineal,
    test_mann_kendall
)
from analizador_tesis.estadisticas import calcular_estadisticas_basicas
from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_SHAPEFILE,
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    INDICES_INFO,
    obtener_indices_disponibles
)

# Crear carpeta específica para reportes de segmentación
RUTA_REPORTES_SEGMENTACION = RUTA_REPORTES / "04_segmentacion"
RUTA_REPORTES_SEGMENTACION.mkdir(exist_ok=True, parents=True)

warnings.filterwarnings('ignore')


# ============================================================================
# FUNCIONES DE SEGMENTACIÓN
# ============================================================================

def segmentar_por_clustering(imagenes_datos, n_zonas=5):
    """
    Segmenta el área usando clustering K-means sobre la imagen promedio.
    
    Args:
        imagenes_datos: Lista de arrays 2D (una por fecha)
        n_zonas: Número de zonas a identificar
        
    Returns:
        dict con máscara de zonas y estadísticas
    """
    print(f"\n{'='*80}")
    print(f"SEGMENTACIÓN POR CLUSTERING ({n_zonas} zonas)")
    print(f"{'='*80}")
    
    # Calcular imagen promedio
    print("\n[1] Calculando imagen promedio temporal...")
    imagen_promedio = np.nanmean(imagenes_datos, axis=0)
    n_validos = np.sum(~np.isnan(imagen_promedio))
    print(f"   ✓ Píxeles válidos: {n_validos}")
    
    # Aplicar clustering
    print(f"\n[2] Aplicando K-means con {n_zonas} clusters...")
    resultado_cluster = clustering_kmeans(imagen_promedio, n_clusters=n_zonas, incluir_coords=True)
    
    if not resultado_cluster:
        print("   ERROR: Error en clustering")
        return None
    
    # Crear máscara de zonas (reordenar por media)
    mascara_zonas = resultado_cluster['clusters_2d'].copy()
    
    # Mapear clusters a zonas (0=más bajo, n_zonas-1=más alto)
    cluster_a_zona = {}
    for i, cluster_info in enumerate(resultado_cluster['stats_clusters']):
        cluster_a_zona[cluster_info['cluster']] = i
    
    # Aplicar mapeo
    mascara_zonas_ordenada = np.full_like(mascara_zonas, np.nan)
    for cluster_id, zona_id in cluster_a_zona.items():
        mascara = (resultado_cluster['clusters_2d'] == cluster_id)
        mascara_zonas_ordenada[mascara] = zona_id
    
    print("\n[3] Estadísticas de zonas:")
    for i, cluster_info in enumerate(resultado_cluster['stats_clusters']):
        print(f"   • Zona {i}: {cluster_info['n_pixeles']} px ({cluster_info['porcentaje']:.1f}%), "
              f"Media={cluster_info['media']:.4f}")
    
    return {
        'metodo': 'clustering',
        'n_zonas': n_zonas,
        'mascara_zonas': mascara_zonas_ordenada,
        'stats_zonas': resultado_cluster['stats_clusters'],
        'imagen_promedio': imagen_promedio
    }


def segmentar_por_cuadrantes(imagen_referencia, n_filas=3, n_cols=3):
    """
    Segmenta el área en cuadrantes regulares.
    
    Args:
        imagen_referencia: Array 2D de referencia
        n_filas: Número de divisiones verticales
        n_cols: Número de divisiones horizontales
        
    Returns:
        dict con máscara de zonas y estadísticas
    """
    print(f"\n{'='*80}")
    print(f"SEGMENTACIÓN POR CUADRANTES ({n_filas}x{n_cols})")
    print(f"{'='*80}")
    
    filas, cols = imagen_referencia.shape
    
    # Crear máscara de zonas
    mascara_zonas = np.full((filas, cols), np.nan)
    
    alto_cuadrante = filas // n_filas
    ancho_cuadrante = cols // n_cols
    
    zona_id = 0
    stats_zonas = []
    
    print("\n📍 Definiendo cuadrantes...")
    for i in range(n_filas):
        for j in range(n_cols):
            # Calcular límites
            f_inicio = i * alto_cuadrante
            f_fin = (i + 1) * alto_cuadrante if i < n_filas - 1 else filas
            c_inicio = j * ancho_cuadrante
            c_fin = (j + 1) * ancho_cuadrante if j < n_cols - 1 else cols
            
            # Asignar zona
            mascara_zonas[f_inicio:f_fin, c_inicio:c_fin] = zona_id
            
            # Calcular estadísticas en la referencia
            cuadrante_datos = imagen_referencia[f_inicio:f_fin, c_inicio:c_fin]
            valores = cuadrante_datos[~np.isnan(cuadrante_datos)]
            
            if len(valores) > 0:
                stats_zonas.append({
                    'cluster': zona_id,
                    'n_pixeles': len(valores),
                    'porcentaje': len(valores) / np.sum(~np.isnan(imagen_referencia)) * 100,
                    'media': float(np.mean(valores)),
                    'std': float(np.std(valores)),
                    'min': float(np.min(valores)),
                    'max': float(np.max(valores)),
                    'posicion': f"Fila {i}, Col {j}"
                })
                print(f"   • Zona {zona_id} (F{i}C{j}): {len(valores)} px, Media={np.mean(valores):.4f}")
            
            zona_id += 1
    
    # Restaurar NaN donde no hay datos
    mascara_zonas[np.isnan(imagen_referencia)] = np.nan
    
    return {
        'metodo': 'cuadrantes',
        'n_zonas': n_filas * n_cols,
        'n_filas': n_filas,
        'n_cols': n_cols,
        'mascara_zonas': mascara_zonas,
        'stats_zonas': stats_zonas
    }


def segmentar_por_percentiles(imagen_referencia, n_zonas=5):
    """
    Segmenta el área por percentiles de valores.
    
    Args:
        imagen_referencia: Array 2D de referencia
        n_zonas: Número de zonas (basado en percentiles)
        
    Returns:
        dict con máscara de zonas
    """
    print(f"\n{'='*80}")
    print(f"SEGMENTACIÓN POR PERCENTILES ({n_zonas} zonas)")
    print(f"{'='*80}")
    
    # Calcular percentiles
    valores = imagen_referencia[~np.isnan(imagen_referencia)]
    percentiles = np.linspace(0, 100, n_zonas + 1)
    limites = np.percentile(valores, percentiles)
    
    print(f"\n📊 Límites de zonas (percentiles):")
    for i in range(n_zonas):
        print(f"   • Zona {i}: [{limites[i]:.4f}, {limites[i+1]:.4f}]")
    
    # Crear máscara de zonas
    mascara_zonas = np.full_like(imagen_referencia, np.nan)
    stats_zonas = []
    
    for i in range(n_zonas):
        if i == n_zonas - 1:
            # Última zona incluye el máximo
            mascara = (imagen_referencia >= limites[i]) & (imagen_referencia <= limites[i+1])
        else:
            mascara = (imagen_referencia >= limites[i]) & (imagen_referencia < limites[i+1])
        
        mascara_zonas[mascara] = i
        
        valores_zona = imagen_referencia[mascara]
        
        stats_zonas.append({
            'cluster': i,
            'n_pixeles': int(np.sum(mascara)),
            'porcentaje': float(np.sum(mascara) / len(valores) * 100),
            'media': float(np.mean(valores_zona)),
            'std': float(np.std(valores_zona)),
            'min': float(np.min(valores_zona)),
            'max': float(np.max(valores_zona)),
            'limite_inferior': float(limites[i]),
            'limite_superior': float(limites[i+1])
        })
    
    return {
        'metodo': 'percentiles',
        'n_zonas': n_zonas,
        'mascara_zonas': mascara_zonas,
        'stats_zonas': stats_zonas,
        'limites': limites
    }


# ============================================================================
# ANÁLISIS TEMPORAL POR ZONA
# ============================================================================

def analizar_evolucion_zonas(mascara_zonas, imagenes_info, indice):
    """
    Analiza la evolución temporal de cada zona.
    
    Args:
        mascara_zonas: Array 2D con IDs de zonas
        imagenes_info: Lista de diccionarios con info de imágenes
        indice: Nombre del índice
        
    Returns:
        dict con series temporales por zona
    """
    print(f"\n{'='*80}")
    print("ANÁLISIS TEMPORAL POR ZONA")
    print(f"{'='*80}")
    
    n_zonas = int(np.nanmax(mascara_zonas)) + 1
    
    # Inicializar estructuras
    series_zonas = {i: [] for i in range(n_zonas)}
    fechas = []
    
    print(f"\n📅 Procesando {len(imagenes_info)} fechas...")
    
    # Procesar cada fecha
    for img_info in imagenes_info:
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        fecha = img_info['fecha']
        
        # Cargar imagen (NOTA: Necesita estructura 2D, usar TIFF)
        datos = cargar_imagen_enmascarada(img_info['ruta'], RUTA_SHAPEFILE)
        
        fechas.append(fecha)
        
        # Calcular estadísticas por zona
        for zona_id in range(n_zonas):
            mascara_zona = (mascara_zonas == zona_id)
            valores_zona = datos[mascara_zona & ~np.isnan(datos)]
            
            if len(valores_zona) > 0:
                media = float(np.mean(valores_zona))
            else:
                media = np.nan
            
            series_zonas[zona_id].append({
                'fecha': fecha,
                'fecha_str': fecha_str,
                'media': media,
                'n_pixeles': len(valores_zona)
            })
    
    print(f"   ✓ Procesadas {len(fechas)} fechas")
    
    # Convertir a DataFrames y calcular tendencias
    print(f"\nGenerando tendencias por zona...")
    resultados_zonas = {}
    
    for zona_id in range(n_zonas):
        df_zona = pd.DataFrame(series_zonas[zona_id])
        
        if len(df_zona) > 3:  # Mínimo para tendencia
            # Calcular tendencia
            tendencia = calcular_tendencia_lineal(df_zona, 'fecha', 'media')
            
            # Test Mann-Kendall
            mk = test_mann_kendall(df_zona['media'].values)
            
            resultados_zonas[zona_id] = {
                'df': df_zona,
                'tendencia': tendencia,
                'mann_kendall': mk,
                'media_global': float(df_zona['media'].mean()),
                'std_global': float(df_zona['media'].std()),
                'min_global': float(df_zona['media'].min()),
                'max_global': float(df_zona['media'].max())
            }
            
            if tendencia:
                print(f"   • Zona {zona_id}: {tendencia['tendencia']}, "
                      f"Pendiente={tendencia['pendiente']:.6f}, "
                      f"R²={tendencia['r2']:.3f}")
        else:
            resultados_zonas[zona_id] = {
                'df': df_zona,
                'tendencia': None,
                'mann_kendall': None
            }
    
    return resultados_zonas


def comparar_zonas(resultados_zonas):
    """
    Compara estadísticas entre zonas.
    
    Args:
        resultados_zonas: dict con resultados por zona
        
    Returns:
        DataFrame con comparación
    """
    print(f"\n{'='*80}")
    print("COMPARACIÓN ENTRE ZONAS")
    print(f"{'='*80}")
    
    comparacion = []
    
    for zona_id, resultado in resultados_zonas.items():
        fila = {
            'zona': zona_id,
            'media_global': resultado.get('media_global', np.nan),
            'std_global': resultado.get('std_global', np.nan),
            'min_global': resultado.get('min_global', np.nan),
            'max_global': resultado.get('max_global', np.nan),
            'n_fechas': len(resultado['df'])
        }
        
        if resultado['tendencia']:
            fila.update({
                'pendiente': resultado['tendencia']['pendiente'],
                'r2': resultado['tendencia']['r2'],
                'p_valor': resultado['tendencia']['p_valor'],
                'tendencia': resultado['tendencia']['tendencia']
            })
        
        if resultado['mann_kendall']:
            fila['mk_tau'] = resultado['mann_kendall']['tau']
            fila['mk_p_valor'] = resultado['mann_kendall']['p_valor']
        
        comparacion.append(fila)
    
    df_comp = pd.DataFrame(comparacion)
    
    print("\n📊 Resumen por zona:")
    print(df_comp.to_string(index=False))
    
    # Identificar zonas extremas
    if 'media_global' in df_comp.columns:
        zona_mejor = df_comp.loc[df_comp['media_global'].idxmax(), 'zona']
        zona_peor = df_comp.loc[df_comp['media_global'].idxmin(), 'zona']
        
        print(f"\n🏆 Zona con MEJOR media: Zona {int(zona_mejor)}")
        print(f"ADVERTENCIA: Zona con PEOR media: Zona {int(zona_peor)}")
    
    return df_comp


# ============================================================================
# FUNCIÓN PRINCIPAL DE SEGMENTACIÓN
# ============================================================================

def analizar_segmentacion_indice(indice, metodo='clustering', n_zonas=5):
    """
    Realiza segmentación y análisis por zonas de un índice.
    
    Args:
        indice: Nombre del índice
        metodo: 'clustering', 'cuadrantes', o 'percentiles'
        n_zonas: Número de zonas (depende del método)
    """
    print(f"\n{'#'*80}")
    print(f"# SEGMENTACIÓN DE ZONAS: {indice}")
    print(f"# Método: {metodo.upper()}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"\nADVERTENCIA: No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes")
    
    # Cargar todas las imágenes
    print(f"\n📥 Cargando imágenes...")
    imagenes_datos = []
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        print(f"   [{i}/{len(imagenes)}] {fecha_str}... ", end='', flush=True)
        try:
            datos = cargar_imagen_enmascarada(img_info['ruta'], RUTA_SHAPEFILE)
            imagenes_datos.append(datos)
            print("✓")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if not imagenes_datos:
        print("\nERROR: No se pudieron cargar imágenes")
        return None
    
    print(f"\nCargadas {len(imagenes_datos)} imágenes")
    
    # Realizar segmentación
    if metodo == 'clustering':
        segmentacion = segmentar_por_clustering(imagenes_datos, n_zonas=n_zonas)
    elif metodo == 'cuadrantes':
        # Usar imagen promedio como referencia
        imagen_ref = np.nanmean(imagenes_datos, axis=0)
        if n_zonas == 4:
            segmentacion = segmentar_por_cuadrantes(imagen_ref, n_filas=2, n_cols=2)
        elif n_zonas == 9:
            segmentacion = segmentar_por_cuadrantes(imagen_ref, n_filas=3, n_cols=3)
        else:
            # Calcular mejor distribución
            n_filas = int(np.sqrt(n_zonas))
            n_cols = int(np.ceil(n_zonas / n_filas))
            segmentacion = segmentar_por_cuadrantes(imagen_ref, n_filas=n_filas, n_cols=n_cols)
    elif metodo == 'percentiles':
        imagen_ref = np.nanmean(imagenes_datos, axis=0)
        segmentacion = segmentar_por_percentiles(imagen_ref, n_zonas=n_zonas)
    else:
        print(f"\nERROR: Método '{metodo}' no reconocido")
        return None
    
    if not segmentacion:
        print("\nERROR: Error en segmentación")
        return None
    
    # Análisis temporal por zona
    resultados_zonas = analizar_evolucion_zonas(
        segmentacion['mascara_zonas'],
        imagenes,
        indice
    )
    
    # Comparar zonas
    df_comparacion = comparar_zonas(resultados_zonas)
    
    # Guardar resultados
    guardar_reportes_segmentacion(indice, metodo, segmentacion, resultados_zonas, df_comparacion)
    
    # Generar visualizaciones
    generar_visualizaciones_segmentacion(indice, metodo, segmentacion, resultados_zonas)
    
    return {
        'indice': indice,
        'metodo': metodo,
        'segmentacion': segmentacion,
        'resultados_zonas': resultados_zonas,
        'comparacion': df_comparacion
    }


# ============================================================================
# GUARDAR REPORTES
# ============================================================================

def guardar_reportes_segmentacion(indice, metodo, segmentacion, resultados_zonas, df_comparacion):
    """
    Guarda reportes de segmentación.
    """
    print(f"\n📊 Guardando reportes...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_reportes = RUTA_REPORTES_SEGMENTACION
    carpeta_reportes.mkdir(exist_ok=True, parents=True)
    
    archivos = []
    
    # 1. Comparación entre zonas
    archivo = carpeta_reportes / f"comparacion_zonas_{indice}_{metodo}_{timestamp}.csv"
    df_comparacion.to_csv(archivo, index=False)
    archivos.append(archivo.name)
    
    # 2. Series temporales por zona
    for zona_id, resultado in resultados_zonas.items():
        archivo = carpeta_reportes / f"serie_zona{zona_id}_{indice}_{metodo}_{timestamp}.csv"
        resultado['df'].to_csv(archivo, index=False)
        archivos.append(archivo.name)
    
    # 3. Estadísticas de segmentación
    df_stats = pd.DataFrame(segmentacion['stats_zonas'])
    archivo = carpeta_reportes / f"estadisticas_segmentacion_{indice}_{metodo}_{timestamp}.csv"
    df_stats.to_csv(archivo, index=False)
    archivos.append(archivo.name)
    
    print(f"✓ Guardados {len(archivos)} reportes")
    for nombre in archivos[:5]:
        print(f"  • {nombre}")
    if len(archivos) > 5:
        print(f"  ... y {len(archivos)-5} más")


# ============================================================================
# VISUALIZACIONES
# ============================================================================

def generar_visualizaciones_segmentacion(indice, metodo, segmentacion, resultados_zonas):
    """
    Genera visualizaciones de segmentación.
    """
    print(f"\nGenerando visualizaciones...")
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_vis = RUTA_VISUALIZACIONES / indice / "segmentacion"
    carpeta_vis.mkdir(exist_ok=True, parents=True)
    
    visualizaciones = []
    
    # 1. Mapa de zonas
    archivo = carpeta_vis / f"mapa_zonas_{indice}_{metodo}_{timestamp}.png"
    fig, ax = plt.subplots(figsize=(10, 8))
    
    im = ax.imshow(segmentacion['mascara_zonas'], cmap='tab10', interpolation='nearest')
    plt.colorbar(im, ax=ax, label='Zona ID')
    ax.set_title(f'{indice} - Segmentación de Zonas\nMétodo: {metodo}')
    ax.axis('off')
    
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.close()
    visualizaciones.append(archivo.name)
    
    # 2. Mapa con estadísticas
    archivo = carpeta_vis / f"mapa_estadisticas_{indice}_{metodo}_{timestamp}.png"
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    # Zonas
    ax = axes[0]
    im = ax.imshow(segmentacion['mascara_zonas'], cmap='tab10', interpolation='nearest')
    ax.set_title('Zonas Identificadas')
    ax.axis('off')
    
    # Imagen promedio o referencia
    ax = axes[1]
    if 'imagen_promedio' in segmentacion:
        im = ax.imshow(segmentacion['imagen_promedio'], cmap='RdYlGn', interpolation='nearest')
    else:
        # Usar primera imagen
        im = ax.imshow(segmentacion['mascara_zonas'], cmap='RdYlGn', interpolation='nearest')
    plt.colorbar(im, ax=ax, label=indice)
    ax.set_title('Valores Promedio')
    ax.axis('off')
    
    plt.suptitle(f'{indice} - Segmentación: {metodo} ({segmentacion["n_zonas"]} zonas)', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.close()
    visualizaciones.append(archivo.name)
    
    # 3. Series temporales por zona
    archivo = carpeta_vis / f"series_temporales_{indice}_{metodo}_{timestamp}.png"
    
    n_zonas = segmentacion['n_zonas']
    n_cols = min(3, n_zonas)
    n_rows = int(np.ceil(n_zonas / n_cols))
    
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4*n_rows))
    if n_zonas == 1:
        axes = np.array([axes])
    axes = axes.flatten()
    
    for zona_id in range(n_zonas):
        ax = axes[zona_id]
        df_zona = resultados_zonas[zona_id]['df']
        
        ax.plot(df_zona['fecha'], df_zona['media'], 'o-', linewidth=2, markersize=6)
        
        # Línea de tendencia si existe
        if resultados_zonas[zona_id]['tendencia']:
            tend = resultados_zonas[zona_id]['tendencia']
            fecha_inicial = df_zona['fecha'].min()
            dias = (df_zona['fecha'] - fecha_inicial).dt.days
            y_pred = tend['intercepto'] + tend['pendiente'] * dias
            ax.plot(df_zona['fecha'], y_pred, 'r--', linewidth=2, alpha=0.7,
                   label=f"Tendencia (R²={tend['r2']:.3f})")
            ax.legend()
        
        ax.set_title(f'Zona {zona_id}')
        ax.set_xlabel('Fecha')
        ax.set_ylabel(indice)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
    
    # Ocultar axes sobrantes
    for i in range(n_zonas, len(axes)):
        axes[i].axis('off')
    
    plt.suptitle(f'{indice} - Evolución Temporal por Zona', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.close()
    visualizaciones.append(archivo.name)
    
    # 4. Comparación de tendencias
    archivo = carpeta_vis / f"comparacion_tendencias_{indice}_{metodo}_{timestamp}.png"
    fig, ax = plt.subplots(figsize=(12, 6))
    
    tendencias_data = []
    for zona_id in range(n_zonas):
        if resultados_zonas[zona_id]['tendencia']:
            tend = resultados_zonas[zona_id]['tendencia']
            tendencias_data.append({
                'zona': zona_id,
                'pendiente': tend['pendiente'],
                'r2': tend['r2']
            })
    
    if tendencias_data:
        df_tend = pd.DataFrame(tendencias_data)
        colors = ['green' if p > 0 else 'red' for p in df_tend['pendiente']]
        
        bars = ax.bar(df_tend['zona'], df_tend['pendiente'], color=colors, alpha=0.7)
        ax.axhline(0, color='black', linewidth=1)
        ax.set_xlabel('Zona')
        ax.set_ylabel('Pendiente de Tendencia')
        ax.set_title(f'{indice} - Comparación de Tendencias por Zona')
        ax.grid(True, alpha=0.3, axis='y')
        
        # Agregar valores de R²
        for i, (zona, pend, r2) in enumerate(zip(df_tend['zona'], df_tend['pendiente'], df_tend['r2'])):
            ax.text(i, pend, f'R²={r2:.2f}', ha='center', va='bottom' if pend > 0 else 'top', fontsize=9)
    
    plt.tight_layout()
    plt.savefig(archivo, dpi=150, bbox_inches='tight')
    plt.close()
    visualizaciones.append(archivo.name)
    
    print(f"✓ Generadas {len(visualizaciones)} visualizaciones")
    for nombre in visualizaciones:
        print(f"  • {nombre}")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu_principal():
    """Menú interactivo."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                  SEGMENTACIÓN DE ZONAS Y ANÁLISIS                         ║
║            (Clustering, Cuadrantes, Evolución por Zona)                   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("\nERROR: No se encontraron índices con datos.")
        return
    
    while True:
        print("\n" + "="*80)
        print("ÍNDICES DISPONIBLES:")
        print("="*80)
        
        for i, indice in enumerate(indices_disponibles, 1):
            print(f"  {i}. {indice:<8} - {INDICES_INFO[indice]['nombre']}")
        
        print("\nMÉTODOS DE SEGMENTACIÓN:")
        print("  C. Clustering (K-means con coordenadas)")
        print("  Q. Cuadrantes (división regular del espacio)")
        print("  P. Percentiles (por rangos de valores)")
        print("  A. Analizar TODOS los índices con clustering")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            break
        
        elif opcion == 'A':
            # Todos los índices con clustering
            for indice in indices_disponibles:
                analizar_segmentacion_indice(indice, metodo='clustering', n_zonas=5)
        
        elif opcion in ['C', 'Q', 'P']:
            # Seleccionar índice
            print("\nSelecciona el índice:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice}")
            
            idx_str = input("Número: ").strip()
            if not idx_str.isdigit():
                continue
            
            idx = int(idx_str) - 1
            if not (0 <= idx < len(indices_disponibles)):
                continue
            
            indice_seleccionado = indices_disponibles[idx]
            
            # Seleccionar número de zonas
            if opcion == 'Q':
                print("\nNúmero de zonas (4, 9, 16, etc.):")
                n_str = input("Número (default=9): ").strip() or "9"
            else:
                n_str = input("Número de zonas (default=5): ").strip() or "5"
            
            try:
                n_zonas = int(n_str)
            except:
                n_zonas = 5 if opcion != 'Q' else 9
            
            # Ejecutar análisis
            metodo_map = {'C': 'clustering', 'Q': 'cuadrantes', 'P': 'percentiles'}
            analizar_segmentacion_indice(
                indice_seleccionado,
                metodo=metodo_map[opcion],
                n_zonas=n_zonas
            )
        
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                # Análisis rápido con clustering
                analizar_segmentacion_indice(indices_disponibles[num], metodo='clustering', n_zonas=5)


if __name__ == "__main__":
    import os
    if os.environ.get('ANALISIS_AUTOMATICO') == '1':
        # Modo automático: analizar todos los índices con clustering
        print("\nModo automático: segmentando TODOS los índices con clustering\n")
        indices_disponibles = obtener_indices_disponibles()
        for indice in indices_disponibles:
            analizar_segmentacion_indice(indice, metodo='clustering', n_zonas=5)
    else:
        # Modo manual: mostrar menú
        menu_principal()
    
    print("\n" + "="*80)
    print("SEGMENTACIÓN DE ZONAS COMPLETADA")
    print("="*80)
    print("\nReportes en: reportes/04_segmentacion/")
    print("Visualizaciones en: visualizaciones/[INDICE]/segmentacion/")
