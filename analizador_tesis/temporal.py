"""
Módulo de análisis temporal para series temporales de índices de vegetación.
Incluye tendencias, estacionalidad, velocidad de cambio y comparaciones.
"""

import numpy as np
import pandas as pd
from scipy import stats
from datetime import datetime, timedelta
from pathlib import Path

# Importar configuración
import sys
sys.path.append(str(Path(__file__).parent.parent))


# ============================================================================
# PREPARACIÓN DE SERIES TEMPORALES
# ============================================================================

def preparar_serie_temporal(df, columna_fecha='fecha', columna_valor='media'):
    """
    Prepara un DataFrame para análisis temporal.
    
    Args:
        df: DataFrame con datos
        columna_fecha: Nombre de columna de fechas
        columna_valor: Nombre de columna de valores
    
    Returns:
        DataFrame ordenado y limpio
    """
    df_limpio = df.copy()
    
    # Convertir a datetime si es necesario
    if not pd.api.types.is_datetime64_any_dtype(df_limpio[columna_fecha]):
        df_limpio[columna_fecha] = pd.to_datetime(df_limpio[columna_fecha], errors='coerce')
    
    # Eliminar fechas inválidas
    df_limpio = df_limpio.dropna(subset=[columna_fecha])
    
    # Ordenar por fecha
    df_limpio = df_limpio.sort_values(columna_fecha)
    
    # Resetear índice
    df_limpio = df_limpio.reset_index(drop=True)
    
    return df_limpio


# ============================================================================
# ANÁLISIS DE TENDENCIAS
# ============================================================================

def calcular_tendencia_lineal(df, columna_fecha='fecha', columna_valor='media'):
    """
    Calcula tendencia lineal mediante regresión.
    
    Returns:
        dict: Resultados de regresión (pendiente, R², p-valor, etc.)
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    if len(df_prep) < 2:
        return None
    
    # Convertir fechas a números (días desde primera fecha)
    fecha_inicial = df_prep[columna_fecha].min()
    df_prep['dias'] = (df_prep[columna_fecha] - fecha_inicial).dt.days
    
    # Filtrar valores válidos
    mask = df_prep[columna_valor].notna()
    X = df_prep.loc[mask, 'dias'].values
    y = df_prep.loc[mask, columna_valor].values
    
    if len(y) < 2:
        return None
    
    # Regresión lineal
    slope, intercept, r_value, p_value, std_err = stats.linregress(X, y)
    
    # Calcular predicción
    y_pred = slope * X + intercept
    
    # Cambio total y porcentual
    valor_inicial = intercept
    valor_final = slope * X[-1] + intercept
    cambio_absoluto = valor_final - valor_inicial
    cambio_porcentual = (cambio_absoluto / abs(valor_inicial) * 100) if valor_inicial != 0 else None
    
    # Clasificación de tendencia
    if p_value < 0.05:
        if slope > 0:
            tendencia = "CRECIENTE (significativa)"
        else:
            tendencia = "DECRECIENTE (significativa)"
    else:
        tendencia = "SIN TENDENCIA (no significativa)"
    
    return {
        'pendiente': float(slope),
        'intercepto': float(intercept),
        'r2': float(r_value ** 2),
        'p_valor': float(p_value),
        'error_std': float(std_err),
        'significativo': p_value < 0.05,
        'tendencia': tendencia,
        'cambio_absoluto': float(cambio_absoluto),
        'cambio_porcentual': float(cambio_porcentual) if cambio_porcentual is not None else None,
        'valor_inicial_estimado': float(valor_inicial),
        'valor_final_estimado': float(valor_final),
        'n_puntos': len(y),
        'dias_total': int(X[-1] - X[0])
    }


def test_mann_kendall(serie_temporal):
    """
    Test de Mann-Kendall para detectar tendencias monotónicas.
    
    Args:
        serie_temporal: Array de valores en orden temporal
    
    Returns:
        dict: Resultados del test
    """
    from scipy.stats import kendalltau
    
    serie = np.array(serie_temporal)
    serie = serie[~np.isnan(serie)]
    
    if len(serie) < 3:
        return None
    
    # Crear índices temporales
    n = len(serie)
    indices = np.arange(n)
    
    # Calcular tau de Kendall
    tau, p_value = kendalltau(indices, serie)
    
    # Interpretación
    if p_value < 0.05:
        if tau > 0:
            resultado = "TENDENCIA CRECIENTE (significativa)"
        else:
            resultado = "TENDENCIA DECRECIENTE (significativa)"
    else:
        resultado = "SIN TENDENCIA MONOTÓNICA"
    
    return {
        'tau': float(tau),
        'p_valor': float(p_value),
        'significativo': p_value < 0.05,
        'resultado': resultado
    }


# ============================================================================
# VELOCIDAD DE CAMBIO
# ============================================================================

def calcular_velocidad_cambio(df, columna_fecha='fecha', columna_valor='media', ventana_dias=7):
    """
    Calcula velocidad de cambio entre fechas.
    
    Args:
        df: DataFrame con datos temporales
        columna_fecha: Columna de fechas
        columna_valor: Columna de valores
        ventana_dias: Ventana para calcular cambio
    
    Returns:
        DataFrame con velocidades calculadas
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    if len(df_prep) < 2:
        return None
    
    resultados = []
    
    for i in range(1, len(df_prep)):
        fecha_actual = df_prep.iloc[i][columna_fecha]
        fecha_anterior = df_prep.iloc[i-1][columna_fecha]
        
        valor_actual = df_prep.iloc[i][columna_valor]
        valor_anterior = df_prep.iloc[i-1][columna_valor]
        
        # Días transcurridos
        dias = (fecha_actual - fecha_anterior).days
        
        if dias > 0 and not np.isnan(valor_actual) and not np.isnan(valor_anterior):
            # Cambio absoluto
            cambio_absoluto = valor_actual - valor_anterior
            
            # Velocidad (cambio por día)
            velocidad = cambio_absoluto / dias
            
            # Cambio porcentual
            cambio_pct = (cambio_absoluto / abs(valor_anterior) * 100) if valor_anterior != 0 else None
            
            resultados.append({
                'fecha_inicio': fecha_anterior,
                'fecha_fin': fecha_actual,
                'dias_transcurridos': dias,
                'valor_inicio': valor_anterior,
                'valor_fin': valor_actual,
                'cambio_absoluto': cambio_absoluto,
                'velocidad_por_dia': velocidad,
                'cambio_porcentual': cambio_pct
            })
    
    if not resultados:
        return None
    
    return pd.DataFrame(resultados)


def calcular_tasa_cambio_periodo(df, columna_fecha='fecha', columna_valor='media', periodo='M'):
    """
    Calcula tasa de cambio agrupada por periodo (mensual, trimestral, etc).
    
    Args:
        df: DataFrame con datos
        columna_fecha: Columna de fechas
        columna_valor: Columna de valores
        periodo: 'M' (mensual), 'Q' (trimestral), 'Y' (anual)
    
    Returns:
        DataFrame con tasas por periodo
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    # Crear columna de periodo
    df_prep['periodo'] = df_prep[columna_fecha].dt.to_period(periodo)
    
    # Agrupar por periodo
    df_agrupado = df_prep.groupby('periodo')[columna_valor].agg(['mean', 'std', 'count']).reset_index()
    
    if len(df_agrupado) < 2:
        return None
    
    # Calcular cambios entre periodos
    df_agrupado['cambio_absoluto'] = df_agrupado['mean'].diff()
    df_agrupado['cambio_porcentual'] = df_agrupado['mean'].pct_change() * 100
    
    return df_agrupado


# ============================================================================
# DESCOMPOSICIÓN DE SERIES TEMPORALES
# ============================================================================

def descomponer_serie_temporal(df, columna_fecha='fecha', columna_valor='media', modelo='additive'):
    """
    Descompone serie temporal en tendencia, estacionalidad y residuos.
    
    Args:
        df: DataFrame con datos
        columna_fecha: Columna de fechas
        columna_valor: Columna de valores
        modelo: 'additive' o 'multiplicative'
    
    Returns:
        dict con componentes: tendencia, estacional, residuo
    """
    from statsmodels.tsa.seasonal import seasonal_decompose
    
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    if len(df_prep) < 4:  # Mínimo necesario
        return None
    
    # Crear serie temporal con índice de fechas
    serie = df_prep.set_index(columna_fecha)[columna_valor]
    
    # Rellenar valores faltantes (interpolación)
    serie = serie.interpolate(method='linear')
    
    try:
        # Descomposición
        decomposition = seasonal_decompose(serie, model=modelo, period=min(12, len(serie)//2))
        
        return {
            'tendencia': decomposition.trend,
            'estacional': decomposition.seasonal,
            'residuo': decomposition.resid,
            'original': serie
        }
    except Exception as e:
        return None


# ============================================================================
# COMPARACIÓN ENTRE PERIODOS
# ============================================================================

def comparar_periodos(df, columna_fecha='fecha', columna_valor='media', 
                     fecha_corte=None, etiquetas=['Periodo 1', 'Periodo 2']):
    """
    Compara estadísticas entre dos periodos de tiempo.
    
    Args:
        df: DataFrame con datos
        columna_fecha: Columna de fechas
        columna_valor: Columna de valores
        fecha_corte: Fecha que separa los periodos (si None, divide a la mitad)
        etiquetas: Nombres para los periodos
    
    Returns:
        dict con comparación estadística
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    if len(df_prep) < 4:
        return None
    
    # Determinar fecha de corte
    if fecha_corte is None:
        idx_medio = len(df_prep) // 2
        fecha_corte = df_prep.iloc[idx_medio][columna_fecha]
    
    # Dividir en dos periodos
    periodo1 = df_prep[df_prep[columna_fecha] < fecha_corte]
    periodo2 = df_prep[df_prep[columna_fecha] >= fecha_corte]
    
    if len(periodo1) < 2 or len(periodo2) < 2:
        return None
    
    # Estadísticas de cada periodo
    stats1 = {
        'n': len(periodo1),
        'media': periodo1[columna_valor].mean(),
        'mediana': periodo1[columna_valor].median(),
        'std': periodo1[columna_valor].std(),
        'min': periodo1[columna_valor].min(),
        'max': periodo1[columna_valor].max()
    }
    
    stats2 = {
        'n': len(periodo2),
        'media': periodo2[columna_valor].mean(),
        'mediana': periodo2[columna_valor].median(),
        'std': periodo2[columna_valor].std(),
        'min': periodo2[columna_valor].min(),
        'max': periodo2[columna_valor].max()
    }
    
    # Test estadístico (t-test)
    from scipy.stats import ttest_ind
    t_stat, p_value = ttest_ind(
        periodo1[columna_valor].dropna(),
        periodo2[columna_valor].dropna()
    )
    
    # Cambio entre periodos
    cambio_absoluto = stats2['media'] - stats1['media']
    cambio_porcentual = (cambio_absoluto / abs(stats1['media']) * 100) if stats1['media'] != 0 else None
    
    return {
        'fecha_corte': fecha_corte,
        'etiqueta_periodo1': etiquetas[0],
        'etiqueta_periodo2': etiquetas[1],
        'periodo1': stats1,
        'periodo2': stats2,
        'cambio_absoluto': float(cambio_absoluto),
        'cambio_porcentual': float(cambio_porcentual) if cambio_porcentual is not None else None,
        't_statistic': float(t_stat),
        'p_valor': float(p_value),
        'significativo': p_value < 0.05,
        'interpretacion': f"Cambio {'significativo' if p_value < 0.05 else 'no significativo'}"
    }


# ============================================================================
# DETECCIÓN DE PUNTOS DE QUIEBRE
# ============================================================================

def detectar_punto_quiebre(df, columna_fecha='fecha', columna_valor='media'):
    """
    Detecta punto de quiebre (cambio estructural) en la serie temporal.
    
    Returns:
        dict con información del punto de quiebre
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    if len(df_prep) < 6:  # Mínimo necesario para detectar quiebre
        return None
    
    mejor_r2 = -np.inf
    mejor_punto = None
    mejor_stats = None
    
    # Probar diferentes puntos de quiebre
    for i in range(3, len(df_prep) - 3):  # Dejar margen en los extremos
        fecha_quiebre = df_prep.iloc[i][columna_fecha]
        
        # Dividir en dos segmentos
        seg1 = df_prep.iloc[:i]
        seg2 = df_prep.iloc[i:]
        
        # Calcular tendencias de cada segmento
        tend1 = calcular_tendencia_lineal(seg1, columna_fecha, columna_valor)
        tend2 = calcular_tendencia_lineal(seg2, columna_fecha, columna_valor)
        
        if tend1 and tend2:
            # Suma de R² (queremos el mejor ajuste global)
            r2_total = tend1['r2'] + tend2['r2']
            
            if r2_total > mejor_r2:
                mejor_r2 = r2_total
                mejor_punto = i
                mejor_stats = {
                    'fecha_quiebre': fecha_quiebre,
                    'indice': i,
                    'segmento1': tend1,
                    'segmento2': tend2,
                    'r2_total': r2_total
                }
    
    if mejor_stats:
        # Determinar tipo de cambio
        pend1 = mejor_stats['segmento1']['pendiente']
        pend2 = mejor_stats['segmento2']['pendiente']
        
        if pend1 > 0 and pend2 < 0:
            tipo_cambio = "DETERIORO (de creciente a decreciente)"
        elif pend1 < 0 and pend2 > 0:
            tipo_cambio = "MEJORA (de decreciente a creciente)"
        elif abs(pend2) > abs(pend1):
            tipo_cambio = "ACELERACIÓN de la tendencia"
        else:
            tipo_cambio = "DESACELERACIÓN de la tendencia"
        
        mejor_stats['tipo_cambio'] = tipo_cambio
    
    return mejor_stats


# ============================================================================
# ESTADÍSTICAS AGREGADAS
# ============================================================================

def calcular_estadisticas_por_mes(df, columna_fecha='fecha', columna_valor='media'):
    """
    Agrupa y calcula estadísticas por mes.
    """
    df_prep = preparar_serie_temporal(df, columna_fecha, columna_valor)
    
    df_prep['año'] = df_prep[columna_fecha].dt.year
    df_prep['mes'] = df_prep[columna_fecha].dt.month
    df_prep['mes_nombre'] = df_prep[columna_fecha].dt.strftime('%B')
    
    stats_mensuales = df_prep.groupby(['año', 'mes', 'mes_nombre'])[columna_valor].agg([
        'count', 'mean', 'median', 'std', 'min', 'max'
    ]).reset_index()
    
    return stats_mensuales


if __name__ == "__main__":
    # Prueba del módulo
    print("="*80)
    print("MÓDULO TEMPORAL - PRUEBA")
    print("="*80)
    
    # Datos de prueba
    fechas = pd.date_range('2024-01-01', periods=50, freq='W')
    valores = np.linspace(0.4, 0.7, 50) + np.random.normal(0, 0.05, 50)
    
    df_test = pd.DataFrame({
        'fecha': fechas,
        'media': valores
    })
    
    print("\nCalculando tendencia lineal...")
    tendencia = calcular_tendencia_lineal(df_test)
    if tendencia:
        print(f"  Pendiente: {tendencia['pendiente']:.6f}")
        print(f"  R²: {tendencia['r2']:.4f}")
        print(f"  Tendencia: {tendencia['tendencia']}")
    
    print("\n✓ Módulo funcionando correctamente")
