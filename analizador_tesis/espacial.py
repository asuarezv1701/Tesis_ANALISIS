"""
Módulo de Análisis Espacial de Índices de Vegetación

Este módulo contiene funciones para análisis espacial:
- Mapas de calor (heatmaps)
- Detección de hotspots/coldspots
- Autocorrelación espacial (Moran's I)
- Clustering espacial (K-means, DBSCAN)
- Mapas de diferencias temporales
- Estadísticas por regiones

Autor: Sistema de Análisis de Tesis
"""

import numpy as np
import pandas as pd
from scipy import ndimage, stats
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
import warnings

warnings.filterwarnings('ignore')


# ============================================================================
# MAPAS DE CALOR Y VISUALIZACIÓN
# ============================================================================

def calcular_estadisticas_espaciales(imagen):
    """
    Calcula estadísticas espaciales básicas de una imagen.
    
    Args:
        imagen: Array 2D con datos de la imagen
        
    Returns:
        dict: Estadísticas espaciales
    """
    datos = imagen[~np.isnan(imagen)]
    
    if len(datos) == 0:
        return None
    
    # Calcular estadísticas básicas
    stats_basicas = {
        'media': float(np.mean(datos)),
        'mediana': float(np.median(datos)),
        'std': float(np.std(datos)),
        'min': float(np.min(datos)),
        'max': float(np.max(datos)),
        'rango': float(np.ptp(datos)),
        'cv': float(np.std(datos) / np.mean(datos)) if np.mean(datos) != 0 else 0
    }
    
    # Calcular percentiles
    percentiles = np.percentile(datos, [5, 25, 75, 95])
    stats_basicas.update({
        'p05': float(percentiles[0]),
        'p25': float(percentiles[1]),
        'p75': float(percentiles[2]),
        'p95': float(percentiles[3])
    })
    
    return stats_basicas


def suavizar_imagen(imagen, sigma=1.0):
    """
    Aplica suavizado gaussiano a la imagen.
    
    Args:
        imagen: Array 2D con datos
        sigma: Desviación estándar del kernel gaussiano
        
    Returns:
        Array 2D suavizado
    """
    # Crear máscara de valores válidos
    mascara = ~np.isnan(imagen)
    
    # Rellenar NaN con la mediana para el suavizado
    imagen_rellenada = imagen.copy()
    if np.any(mascara):
        mediana = np.nanmedian(imagen)
        imagen_rellenada[~mascara] = mediana
        
        # Aplicar filtro gaussiano
        imagen_suavizada = ndimage.gaussian_filter(imagen_rellenada, sigma=sigma)
        
        # Restaurar NaN
        imagen_suavizada[~mascara] = np.nan
        
        return imagen_suavizada
    else:
        return imagen


# ============================================================================
# DETECCIÓN DE HOTSPOTS Y COLDSPOTS
# ============================================================================

def detectar_hotspots(imagen, metodo='zscore', umbral=1.5):
    """
    Detecta hotspots (zonas con valores altos) en la imagen.
    
    Args:
        imagen: Array 2D con datos
        metodo: 'zscore', 'percentil', o 'iqr'
        umbral: Umbral para detección (sigma para zscore, percentil para percentil)
        
    Returns:
        dict con máscaras de hotspots, coldspots, y estadísticas
    """
    datos_validos = imagen[~np.isnan(imagen)]
    
    if len(datos_validos) == 0:
        return None
    
    if metodo == 'zscore':
        # Método Z-score
        media = np.nanmean(imagen)
        std = np.nanstd(imagen)
        
        z_scores = (imagen - media) / std if std > 0 else np.zeros_like(imagen)
        
        hotspots = z_scores > umbral
        coldspots = z_scores < -umbral
        
    elif metodo == 'percentil':
        # Método por percentiles
        p_alto = np.nanpercentile(imagen, 100 - umbral)
        p_bajo = np.nanpercentile(imagen, umbral)
        
        hotspots = imagen > p_alto
        coldspots = imagen < p_bajo
        
    elif metodo == 'iqr':
        # Método IQR (Interquartile Range)
        Q1 = np.nanpercentile(imagen, 25)
        Q3 = np.nanpercentile(imagen, 75)
        IQR = Q3 - Q1
        
        limite_superior = Q3 + umbral * IQR
        limite_inferior = Q1 - umbral * IQR
        
        hotspots = imagen > limite_superior
        coldspots = imagen < limite_inferior
        
    else:
        raise ValueError(f"Método '{metodo}' no reconocido")
    
    # Remover NaN de las máscaras
    hotspots[np.isnan(imagen)] = False
    coldspots[np.isnan(imagen)] = False
    
    # Calcular estadísticas
    n_hotspots = np.sum(hotspots)
    n_coldspots = np.sum(coldspots)
    n_total = np.sum(~np.isnan(imagen))
    
    return {
        'hotspots': hotspots,
        'coldspots': coldspots,
        'n_hotspots': int(n_hotspots),
        'n_coldspots': int(n_coldspots),
        'n_total': int(n_total),
        'porcentaje_hotspots': float(n_hotspots / n_total * 100) if n_total > 0 else 0,
        'porcentaje_coldspots': float(n_coldspots / n_total * 100) if n_total > 0 else 0,
        'media_hotspots': float(np.mean(imagen[hotspots])) if n_hotspots > 0 else np.nan,
        'media_coldspots': float(np.mean(imagen[coldspots])) if n_coldspots > 0 else np.nan
    }


def etiquetar_regiones(mascara):
    """
    Etiqueta regiones conectadas en una máscara binaria.
    
    Args:
        mascara: Array 2D booleano
        
    Returns:
        dict con etiquetas, número de regiones, y tamaños
    """
    # Etiquetar regiones conectadas
    etiquetas, n_regiones = ndimage.label(mascara)
    
    if n_regiones == 0:
        return {
            'etiquetas': etiquetas,
            'n_regiones': 0,
            'tamaños': [],
            'coordenadas': []
        }
    
    # Calcular tamaño de cada región
    tamaños = ndimage.sum(mascara, etiquetas, range(1, n_regiones + 1))
    
    # Encontrar centro de masa de cada región
    centros = ndimage.center_of_mass(mascara, etiquetas, range(1, n_regiones + 1))
    
    return {
        'etiquetas': etiquetas,
        'n_regiones': int(n_regiones),
        'tamaños': [int(t) for t in tamaños],
        'centros': centros,
        'tamaño_promedio': float(np.mean(tamaños)),
        'tamaño_max': int(np.max(tamaños)),
        'tamaño_min': int(np.min(tamaños))
    }


# ============================================================================
# CLUSTERING ESPACIAL
# ============================================================================

def clustering_kmeans(imagen, n_clusters=5, incluir_coords=True):
    """
    Aplica K-means clustering a la imagen.
    
    Args:
        imagen: Array 2D con datos
        n_clusters: Número de clusters
        incluir_coords: Si incluir coordenadas espaciales como features
        
    Returns:
        dict con etiquetas de clusters y estadísticas
    """
    # Preparar datos
    mascara = ~np.isnan(imagen)
    indices_y, indices_x = np.where(mascara)
    valores = imagen[mascara]
    
    if len(valores) < n_clusters:
        return None
    
    # Crear features
    if incluir_coords:
        # Normalizar coordenadas a [0, 1]
        coords_y = indices_y / imagen.shape[0]
        coords_x = indices_x / imagen.shape[1]
        
        features = np.column_stack([valores, coords_x, coords_y])
    else:
        features = valores.reshape(-1, 1)
    
    # Normalizar features
    scaler = StandardScaler()
    features_norm = scaler.fit_transform(features)
    
    # Aplicar K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    etiquetas_1d = kmeans.fit_predict(features_norm)
    
    # Reconstruir imagen de clusters
    clusters_2d = np.full(imagen.shape, np.nan)
    clusters_2d[indices_y, indices_x] = etiquetas_1d
    
    # Calcular estadísticas por cluster
    stats_clusters = []
    for i in range(n_clusters):
        mascara_cluster = (etiquetas_1d == i)
        valores_cluster = valores[mascara_cluster]
        
        stats_clusters.append({
            'cluster': i,
            'n_pixeles': int(np.sum(mascara_cluster)),
            'porcentaje': float(np.sum(mascara_cluster) / len(valores) * 100),
            'media': float(np.mean(valores_cluster)),
            'std': float(np.std(valores_cluster)),
            'min': float(np.min(valores_cluster)),
            'max': float(np.max(valores_cluster))
        })
    
    # Ordenar clusters por media (de menor a mayor)
    stats_clusters = sorted(stats_clusters, key=lambda x: x['media'])
    
    return {
        'clusters_2d': clusters_2d,
        'etiquetas_1d': etiquetas_1d,
        'n_clusters': n_clusters,
        'stats_clusters': stats_clusters,
        'inercia': float(kmeans.inertia_),
        'centroides': kmeans.cluster_centers_
    }


def clustering_dbscan(imagen, eps=0.5, min_samples=10, incluir_coords=True):
    """
    Aplica DBSCAN clustering a la imagen.
    
    Args:
        imagen: Array 2D con datos
        eps: Radio máximo para vecindad
        min_samples: Mínimo de muestras por cluster
        incluir_coords: Si incluir coordenadas espaciales
        
    Returns:
        dict con etiquetas de clusters y estadísticas
    """
    # Preparar datos
    mascara = ~np.isnan(imagen)
    indices_y, indices_x = np.where(mascara)
    valores = imagen[mascara]
    
    if len(valores) < min_samples:
        return None
    
    # Crear features
    if incluir_coords:
        coords_y = indices_y / imagen.shape[0]
        coords_x = indices_x / imagen.shape[1]
        features = np.column_stack([valores, coords_x, coords_y])
    else:
        features = valores.reshape(-1, 1)
    
    # Normalizar
    scaler = StandardScaler()
    features_norm = scaler.fit_transform(features)
    
    # Aplicar DBSCAN
    dbscan = DBSCAN(eps=eps, min_samples=min_samples)
    etiquetas_1d = dbscan.fit_predict(features_norm)
    
    # Reconstruir imagen
    clusters_2d = np.full(imagen.shape, np.nan)
    clusters_2d[indices_y, indices_x] = etiquetas_1d
    
    # Calcular estadísticas
    n_clusters = len(set(etiquetas_1d)) - (1 if -1 in etiquetas_1d else 0)
    n_ruido = np.sum(etiquetas_1d == -1)
    
    stats_clusters = []
    for cluster_id in set(etiquetas_1d):
        if cluster_id == -1:
            continue
            
        mascara_cluster = (etiquetas_1d == cluster_id)
        valores_cluster = valores[mascara_cluster]
        
        stats_clusters.append({
            'cluster': int(cluster_id),
            'n_pixeles': int(np.sum(mascara_cluster)),
            'porcentaje': float(np.sum(mascara_cluster) / len(valores) * 100),
            'media': float(np.mean(valores_cluster)),
            'std': float(np.std(valores_cluster)),
            'min': float(np.min(valores_cluster)),
            'max': float(np.max(valores_cluster))
        })
    
    return {
        'clusters_2d': clusters_2d,
        'etiquetas_1d': etiquetas_1d,
        'n_clusters': int(n_clusters),
        'n_ruido': int(n_ruido),
        'porcentaje_ruido': float(n_ruido / len(valores) * 100) if len(valores) > 0 else 0,
        'stats_clusters': stats_clusters
    }


# ============================================================================
# AUTOCORRELACIÓN ESPACIAL
# ============================================================================

def calcular_moran_i(imagen, vecindad='queen'):
    """
    Calcula el índice I de Moran para autocorrelación espacial.
    
    Args:
        imagen: Array 2D con datos
        vecindad: 'queen' (8 vecinos) o 'rook' (4 vecinos)
        
    Returns:
        dict con I de Moran, valor esperado, y significancia
    """
    # Extraer datos válidos
    mascara = ~np.isnan(imagen)
    
    # Crear matriz de vecindad
    if vecindad == 'queen':
        # 8 vecinos (incluye diagonales)
        estructura = np.array([[1, 1, 1],
                              [1, 0, 1],
                              [1, 1, 1]])
    else:  # 'rook'
        # 4 vecinos (solo horizontal/vertical)
        estructura = np.array([[0, 1, 0],
                              [1, 0, 1],
                              [0, 1, 0]])
    
    # Calcular media global
    media = np.nanmean(imagen)
    
    # Calcular desviaciones
    desviaciones = imagen - media
    
    # Inicializar acumuladores
    numerador = 0
    denominador = 0
    W = 0  # Suma de pesos
    
    # Iterar sobre pixeles válidos
    filas, cols = imagen.shape
    for i in range(filas):
        for j in range(cols):
            if not mascara[i, j]:
                continue
            
            # Desviación del pixel actual
            dev_i = desviaciones[i, j]
            denominador += dev_i ** 2
            
            # Buscar vecinos
            for di in range(-1, 2):
                for dj in range(-1, 2):
                    # Verificar estructura de vecindad
                    if di == 0 and dj == 0:
                        continue
                    if estructura[di+1, dj+1] == 0:
                        continue
                    
                    ni, nj = i + di, j + dj
                    
                    # Verificar límites
                    if 0 <= ni < filas and 0 <= nj < cols:
                        if mascara[ni, nj]:
                            dev_j = desviaciones[ni, nj]
                            numerador += dev_i * dev_j
                            W += 1
    
    if W == 0 or denominador == 0:
        return None
    
    # Calcular I de Moran
    N = np.sum(mascara)
    moran_i = (N / W) * (numerador / denominador)
    
    # Valor esperado bajo hipótesis nula (aleatoriedad espacial)
    esperado = -1 / (N - 1)
    
    # Z-score aproximado
    # Varianza simplificada
    varianza = 1 / (N - 1)
    z_score = (moran_i - esperado) / np.sqrt(varianza)
    
    # P-valor (dos colas)
    p_valor = 2 * (1 - stats.norm.cdf(abs(z_score)))
    
    # Interpretación
    if p_valor < 0.05:
        if moran_i > esperado:
            interpretacion = "Autocorrelación positiva significativa (agrupamiento)"
        else:
            interpretacion = "Autocorrelación negativa significativa (dispersión)"
    else:
        interpretacion = "Sin autocorrelación significativa (aleatorio)"
    
    return {
        'moran_i': float(moran_i),
        'esperado': float(esperado),
        'z_score': float(z_score),
        'p_valor': float(p_valor),
        'n_pixeles': int(N),
        'interpretacion': interpretacion,
        'significativo': p_valor < 0.05
    }


# ============================================================================
# ANÁLISIS DE DIFERENCIAS TEMPORALES
# ============================================================================

def calcular_diferencia_temporal(imagen1, imagen2):
    """
    Calcula la diferencia entre dos imágenes temporales.
    
    Args:
        imagen1: Array 2D (fecha anterior)
        imagen2: Array 2D (fecha posterior)
        
    Returns:
        dict con imagen de diferencia y estadísticas
    """
    # Calcular diferencia
    diferencia = imagen2 - imagen1
    
    # Estadísticas de la diferencia
    mascara = ~np.isnan(diferencia)
    valores_diff = diferencia[mascara]
    
    if len(valores_diff) == 0:
        return None
    
    # Clasificar cambios
    umbral_cambio = np.nanstd(diferencia) * 0.5
    
    aumento_fuerte = diferencia > umbral_cambio
    disminucion_fuerte = diferencia < -umbral_cambio
    sin_cambio = np.abs(diferencia) <= umbral_cambio
    
    # Remover NaN
    aumento_fuerte[np.isnan(diferencia)] = False
    disminucion_fuerte[np.isnan(diferencia)] = False
    sin_cambio[np.isnan(diferencia)] = False
    
    n_total = np.sum(mascara)
    
    return {
        'diferencia': diferencia,
        'diferencia_media': float(np.nanmean(diferencia)),
        'diferencia_std': float(np.nanstd(diferencia)),
        'diferencia_min': float(np.nanmin(diferencia)),
        'diferencia_max': float(np.nanmax(diferencia)),
        'diferencia_mediana': float(np.nanmedian(diferencia)),
        'aumento_fuerte': aumento_fuerte,
        'disminucion_fuerte': disminucion_fuerte,
        'sin_cambio': sin_cambio,
        'n_aumento': int(np.sum(aumento_fuerte)),
        'n_disminucion': int(np.sum(disminucion_fuerte)),
        'n_sin_cambio': int(np.sum(sin_cambio)),
        'porcentaje_aumento': float(np.sum(aumento_fuerte) / n_total * 100) if n_total > 0 else 0,
        'porcentaje_disminucion': float(np.sum(disminucion_fuerte) / n_total * 100) if n_total > 0 else 0,
        'porcentaje_sin_cambio': float(np.sum(sin_cambio) / n_total * 100) if n_total > 0 else 0,
        'umbral_usado': float(umbral_cambio)
    }


def calcular_velocidad_espacial(imagen1, imagen2, dias):
    """
    Calcula la velocidad de cambio espacial entre dos fechas.
    
    Args:
        imagen1: Array 2D (fecha inicial)
        imagen2: Array 2D (fecha final)
        dias: Número de días entre imágenes
        
    Returns:
        Array 2D con velocidad de cambio (unidades/día)
    """
    if dias == 0:
        return np.zeros_like(imagen1)
    
    diferencia = imagen2 - imagen1
    velocidad = diferencia / dias
    
    return velocidad


# ============================================================================
# ESTADÍSTICAS POR REGIONES
# ============================================================================

def dividir_en_cuadrantes(imagen, n_filas=2, n_cols=2):
    """
    Divide la imagen en cuadrantes y calcula estadísticas.
    
    Args:
        imagen: Array 2D con datos
        n_filas: Número de divisiones verticales
        n_cols: Número de divisiones horizontales
        
    Returns:
        dict con estadísticas por cuadrante
    """
    filas, cols = imagen.shape
    
    alto_cuadrante = filas // n_filas
    ancho_cuadrante = cols // n_cols
    
    cuadrantes = []
    
    for i in range(n_filas):
        for j in range(n_cols):
            # Calcular límites
            f_inicio = i * alto_cuadrante
            f_fin = (i + 1) * alto_cuadrante if i < n_filas - 1 else filas
            c_inicio = j * ancho_cuadrante
            c_fin = (j + 1) * ancho_cuadrante if j < n_cols - 1 else cols
            
            # Extraer cuadrante
            cuadrante = imagen[f_inicio:f_fin, c_inicio:c_fin]
            
            # Calcular estadísticas
            mascara = ~np.isnan(cuadrante)
            valores = cuadrante[mascara]
            
            if len(valores) > 0:
                stats = {
                    'cuadrante': f"{i}-{j}",
                    'fila': i,
                    'columna': j,
                    'limites': {
                        'fila_inicio': f_inicio,
                        'fila_fin': f_fin,
                        'col_inicio': c_inicio,
                        'col_fin': c_fin
                    },
                    'n_pixeles': int(len(valores)),
                    'media': float(np.mean(valores)),
                    'mediana': float(np.median(valores)),
                    'std': float(np.std(valores)),
                    'min': float(np.min(valores)),
                    'max': float(np.max(valores))
                }
            else:
                stats = {
                    'cuadrante': f"{i}-{j}",
                    'fila': i,
                    'columna': j,
                    'n_pixeles': 0
                }
            
            cuadrantes.append(stats)
    
    return {
        'n_filas': n_filas,
        'n_cols': n_cols,
        'n_total_cuadrantes': n_filas * n_cols,
        'cuadrantes': cuadrantes
    }
