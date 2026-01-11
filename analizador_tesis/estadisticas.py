"""
Módulo de cálculos estadísticos avanzados.
"""

import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

# Importar configuración
import sys
sys.path.append(str(Path(__file__).parent.parent))
from configuracion.config import PERCENTILES_DEFAULT


# ============================================================================
# ESTADÍSTICAS BÁSICAS
# ============================================================================

def calcular_estadisticas_basicas(datos, incluir_percentiles=True):
    """
    Calcula estadísticas descriptivas básicas de un array.
    
    Args:
        datos (numpy.ndarray): Array de datos
        incluir_percentiles (bool): Si True, incluye percentiles
    
    Returns:
        dict: Diccionario con estadísticas
    """
    # Filtrar solo datos válidos
    datos_validos = datos[~np.isnan(datos) & ~np.isinf(datos)]
    
    if len(datos_validos) == 0:
        return {
            'n': 0,
            'media': None,
            'mediana': None,
            'std': None,
            'min': None,
            'max': None,
            'rango': None
        }
    
    estadisticas = {
        'n': len(datos_validos),
        'media': float(np.mean(datos_validos)),
        'mediana': float(np.median(datos_validos)),
        'std': float(np.std(datos_validos)),
        'min': float(np.min(datos_validos)),
        'max': float(np.max(datos_validos)),
        'rango': float(np.max(datos_validos) - np.min(datos_validos))
    }
    
    if incluir_percentiles:
        for p in PERCENTILES_DEFAULT:
            estadisticas[f'p{p:02d}'] = float(np.percentile(datos_validos, p))
    
    return estadisticas


def calcular_estadisticas_avanzadas(datos):
    """
    Calcula estadísticas avanzadas incluyendo CV, skewness, kurtosis.
    
    Args:
        datos (numpy.ndarray): Array de datos
    
    Returns:
        dict: Diccionario con estadísticas avanzadas
    """
    # Primero calcular básicas
    stats_basicas = calcular_estadisticas_basicas(datos, incluir_percentiles=True)
    
    if stats_basicas['n'] == 0:
        return stats_basicas
    
    datos_validos = datos[~np.isnan(datos) & ~np.isinf(datos)]
    
    # Estadísticas avanzadas
    stats_avanzadas = {
        'cv': calcular_coeficiente_variacion(datos_validos),
        'skewness': float(stats.skew(datos_validos)),
        'kurtosis': float(stats.kurtosis(datos_validos)),
        'varianza': float(np.var(datos_validos)),
        'iqr': float(np.percentile(datos_validos, 75) - np.percentile(datos_validos, 25)),
        'mad': float(np.median(np.abs(datos_validos - np.median(datos_validos))))  # Median Absolute Deviation
    }
    
    # Combinar con básicas
    return {**stats_basicas, **stats_avanzadas}


def calcular_coeficiente_variacion(datos):
    """
    Calcula el Coeficiente de Variación (CV).
    
    CV = (desviación estándar / media) * 100
    
    Args:
        datos (numpy.ndarray): Array de datos
    
    Returns:
        float: Coeficiente de variación en porcentaje
        None: Si media es 0 o no hay datos válidos
    """
    datos_validos = datos[~np.isnan(datos) & ~np.isinf(datos)]
    
    if len(datos_validos) == 0:
        return None
    
    media = np.mean(datos_validos)
    std = np.std(datos_validos)
    
    if media == 0:
        return None
    
    cv = (std / abs(media)) * 100
    return float(cv)


# ============================================================================
# ESTADÍSTICAS TEMPORALES
# ============================================================================

def calcular_tendencia_lineal(fechas, valores):
    """
    Calcula tendencia lineal usando regresión.
    
    Args:
        fechas (list o array): Fechas (datetime)
        valores (list o array): Valores correspondientes
    
    Returns:
        dict: Pendiente, intercepto, R², p-valor
    """
    # Convertir fechas a números (días desde primera fecha)
    if len(fechas) < 2:
        return None
    
    # Convertir a timestamps
    fechas_num = np.array([(f - fechas[0]).days for f in fechas])
    valores_array = np.array(valores)
    
    # Filtrar NaN
    mask = ~np.isnan(valores_array)
    fechas_num = fechas_num[mask]
    valores_array = valores_array[mask]
    
    if len(valores_array) < 2:
        return None
    
    # Regresión lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(fechas_num, valores_array)
    
    return {
        'pendiente': float(slope),
        'intercepto': float(intercept),
        'r2': float(r_value ** 2),
        'p_valor': float(p_value),
        'error_std': float(std_err),
        'significativo': p_value < 0.05  # Significancia al 5%
    }


def calcular_velocidad_cambio(serie_temporal, ventana=1):
    """
    Calcula la velocidad de cambio entre valores consecutivos.
    
    Args:
        serie_temporal (array): Valores en orden temporal
        ventana (int): Número de periodos para el cambio
    
    Returns:
        array: Velocidades de cambio
    """
    serie = np.array(serie_temporal)
    
    if len(serie) <= ventana:
        return np.array([])
    
    velocidades = np.diff(serie, n=ventana) / ventana
    
    return velocidades


def calcular_tasa_cambio_porcentual(serie_temporal, ventana=1):
    """
    Calcula tasa de cambio porcentual.
    
    Args:
        serie_temporal (array): Valores en orden temporal
        ventana (int): Número de periodos
    
    Returns:
        array: Tasas de cambio porcentuales
    """
    serie = np.array(serie_temporal)
    
    if len(serie) <= ventana:
        return np.array([])
    
    cambios = []
    for i in range(ventana, len(serie)):
        valor_anterior = serie[i - ventana]
        valor_actual = serie[i]
        
        if valor_anterior != 0:
            cambio_pct = ((valor_actual - valor_anterior) / abs(valor_anterior)) * 100
            cambios.append(cambio_pct)
        else:
            cambios.append(np.nan)
    
    return np.array(cambios)


# ============================================================================
# ESTADÍSTICAS ESPACIALES
# ============================================================================

def calcular_estadisticas_por_region(datos, etiquetas_regiones):
    """
    Calcula estadísticas para cada región etiquetada.
    
    Args:
        datos (numpy.ndarray): Array 2D de datos
        etiquetas_regiones (numpy.ndarray): Array 2D de etiquetas de regiones
    
    Returns:
        dict: Estadísticas por región
    """
    regiones_unicas = np.unique(etiquetas_regiones[~np.isnan(etiquetas_regiones)])
    
    resultados = {}
    
    for region in regiones_unicas:
        mascara = etiquetas_regiones == region
        datos_region = datos[mascara]
        
        stats_region = calcular_estadisticas_avanzadas(datos_region)
        resultados[f'region_{int(region)}'] = stats_region
    
    return resultados


def calcular_heterogeneidad_espacial(datos):
    """
    Calcula métricas de heterogeneidad espacial.
    
    Args:
        datos (numpy.ndarray): Array 2D de datos
    
    Returns:
        dict: Métricas de heterogeneidad
    """
    datos_validos = datos[~np.isnan(datos)]
    
    if len(datos_validos) == 0:
        return None
    
    # Coeficiente de variación (heterogeneidad global)
    cv = calcular_coeficiente_variacion(datos_validos)
    
    # Rango intercuartílico normalizado
    q25, q75 = np.percentile(datos_validos, [25, 75])
    iqr_norm = (q75 - q25) / np.median(datos_validos) if np.median(datos_validos) != 0 else None
    
    return {
        'cv': cv,
        'iqr_normalizado': float(iqr_norm) if iqr_norm is not None else None,
        'clasificacion': clasificar_heterogeneidad(cv)
    }


def clasificar_heterogeneidad(cv):
    """
    Clasifica el nivel de heterogeneidad según el CV.
    
    Args:
        cv (float): Coeficiente de variación
    
    Returns:
        str: Clasificación
    """
    if cv is None:
        return 'DESCONOCIDO'
    
    if cv < 10:
        return 'HOMOGÉNEO'
    elif cv < 20:
        return 'MODERADAMENTE HETEROGÉNEO'
    elif cv < 30:
        return 'HETEROGÉNEO'
    else:
        return 'MUY HETEROGÉNEO'


# ============================================================================
# DETECCIÓN DE ANOMALÍAS
# ============================================================================

def detectar_outliers_zscore(datos, umbral=2):
    """
    Detecta outliers usando Z-score.
    
    Args:
        datos (numpy.ndarray): Array de datos
        umbral (float): Umbral de Z-score (típicamente 2 o 3)
    
    Returns:
        numpy.ndarray: Máscara booleana (True = outlier)
    """
    datos_validos = datos[~np.isnan(datos)]
    
    if len(datos_validos) == 0:
        return np.zeros_like(datos, dtype=bool)
    
    media = np.mean(datos_validos)
    std = np.std(datos_validos)
    
    if std == 0:
        return np.zeros_like(datos, dtype=bool)
    
    z_scores = np.abs((datos - media) / std)
    
    return z_scores > umbral


def detectar_outliers_iqr(datos, factor=1.5):
    """
    Detecta outliers usando método IQR (Interquartile Range).
    
    Args:
        datos (numpy.ndarray): Array de datos
        factor (float): Factor multiplicador (típicamente 1.5 o 3)
    
    Returns:
        numpy.ndarray: Máscara booleana (True = outlier)
    """
    datos_validos = datos[~np.isnan(datos)]
    
    if len(datos_validos) == 0:
        return np.zeros_like(datos, dtype=bool)
    
    q25, q75 = np.percentile(datos_validos, [25, 75])
    iqr = q75 - q25
    
    limite_inferior = q25 - factor * iqr
    limite_superior = q75 + factor * iqr
    
    return (datos < limite_inferior) | (datos > limite_superior)


# ============================================================================
# COMPARACIÓN ENTRE CONJUNTOS
# ============================================================================

def comparar_distribuciones(datos1, datos2):
    """
    Compara dos distribuciones usando test estadístico.
    
    Args:
        datos1 (numpy.ndarray): Primera distribución
        datos2 (numpy.ndarray): Segunda distribución
    
    Returns:
        dict: Resultados de la comparación
    """
    d1 = datos1[~np.isnan(datos1)]
    d2 = datos2[~np.isnan(datos2)]
    
    if len(d1) < 2 or len(d2) < 2:
        return None
    
    # Test de Kolmogorov-Smirnov
    ks_stat, ks_pvalue = stats.ks_2samp(d1, d2)
    
    # Test t de Student
    t_stat, t_pvalue = stats.ttest_ind(d1, d2)
    
    # Test de Mann-Whitney (no paramétrico)
    u_stat, u_pvalue = stats.mannwhitneyu(d1, d2)
    
    return {
        'media_1': float(np.mean(d1)),
        'media_2': float(np.mean(d2)),
        'diferencia_medias': float(np.mean(d2) - np.mean(d1)),
        'diferencia_porcentual': float(((np.mean(d2) - np.mean(d1)) / np.mean(d1)) * 100) if np.mean(d1) != 0 else None,
        'ks_statistic': float(ks_stat),
        'ks_pvalue': float(ks_pvalue),
        't_statistic': float(t_stat),
        't_pvalue': float(t_pvalue),
        'mann_whitney_u': float(u_stat),
        'mann_whitney_pvalue': float(u_pvalue),
        'son_diferentes': ks_pvalue < 0.05  # Significancia al 5%
    }


if __name__ == "__main__":
    # Prueba del módulo
    print("="*80)
    print("MÓDULO ESTADÍSTICAS - PRUEBA")
    print("="*80)
    
    # Datos de prueba
    np.random.seed(42)
    datos_test = np.random.normal(0.6, 0.15, 1000)
    
    print("\nEstadísticas básicas:")
    stats_basicas = calcular_estadisticas_basicas(datos_test)
    for key, value in stats_basicas.items():
        print(f"  {key}: {value}")
    
    print("\nEstadísticas avanzadas:")
    stats_avanzadas = calcular_estadisticas_avanzadas(datos_test)
    print(f"  CV: {stats_avanzadas['cv']:.2f}%")
    print(f"  Clasificación: {clasificar_heterogeneidad(stats_avanzadas['cv'])}")
