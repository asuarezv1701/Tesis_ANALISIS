"""
Análisis Exploratorio de Índices de Vegetación - VERSIÓN MEJORADA

Este script:
1. Carga imágenes CON ENMASCARAMIENTO automático del shapefile
2. Calcula estadísticas avanzadas (media, std, CV, percentiles, skewness, kurtosis)
3. Genera reportes detallados por índice y por fecha
4. Crea visualizaciones de distribución y evolución temporal
5. Identifica imágenes con problemas de calidad

MEJORAS RESPECTO A LA VERSIÓN ANTERIOR:
- Enmascaramiento automático (solo píxeles dentro del polígono)
- Estadísticas más completas (CV, heterogeneidad, outliers)
- Reportes por fecha e índice
- Visualizaciones automáticas
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
from analizador_tesis.estadisticas import (
    calcular_estadisticas_avanzadas,
    calcular_coeficiente_variacion,
    clasificar_heterogeneidad,
    detectar_outliers_zscore
)
from analizador_tesis.visualizador import (
    graficar_serie_temporal,
    graficar_evolucion_cv,
    generar_dashboard_indice
)
from analizador_tesis.visualizador_comparativo import (
    generar_dashboard_comparativo
)
from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_SHAPEFILE,
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    INDICES_INFO,
    obtener_indices_disponibles
)

# Crear carpeta específica para reportes exploratorios
RUTA_REPORTES_EXPLORATORIO = RUTA_REPORTES / "01_exploratorio"
RUTA_REPORTES_EXPLORATORIO.mkdir(exist_ok=True, parents=True)

warnings.filterwarnings('ignore')


# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

def analizar_imagen(info_imagen, indice):
    """
    Analiza una imagen individual usando CSV optimizado o TIFF.
    
    NOTA: Ahora usa CSVs cuando están disponibles (10-50x más rápido)
    
    Args:
        info_imagen: Dict de listar_imagenes_indice con ruta, fecha, csv_pixeles
        indice: Nombre del índice (NDVI, NDRE, etc.)
    
    Returns:
        dict: Estadísticas completas de la imagen
    """
    try:
        fecha_str = info_imagen['fecha_str']
        
        # Cargar datos de forma optimizada (CSV si existe, sino TIFF)
        datos, fuente = cargar_datos_optimizado(info_imagen, usar_csv=True)
        
        # Calcular estadísticas avanzadas
        stats = calcular_estadisticas_avanzadas(datos)
        
        if stats['n'] == 0:
            return {
                'fecha': fecha_str,
                'indice': indice,
                'archivo': info_imagen['nombre_archivo'],
                'pixeles_validos': 0,
                'fuente': fuente,
                'error': 'Sin píxeles válidos'
            }
        
        # Detectar outliers
        outliers_mask = detectar_outliers_zscore(datos, umbral=3)
        n_outliers = np.sum(outliers_mask[~np.isnan(datos)])
        pct_outliers = (n_outliers / stats['n'] * 100) if stats['n'] > 0 else 0
        
        # Clasificación de calidad
        calidad = clasificar_calidad_imagen(stats, pct_outliers)
        
        # Resultado completo
        resultado = {
            'fecha': fecha_str,
            'indice': indice,
            'archivo': info_imagen['nombre_archivo'],
            'fuente_datos': fuente,  # 'csv' o 'tiff'
            
            # Conteos
            'pixeles_validos': stats['n'],
            'outliers_detectados': int(n_outliers),
            'pct_outliers': round(pct_outliers, 2),
            
            # Estadísticas básicas
            'media': round(stats['media'], 6),
            'mediana': round(stats['mediana'], 6),
            'std': round(stats['std'], 6),
            'min': round(stats['min'], 6),
            'max': round(stats['max'], 6),
            'rango': round(stats['rango'], 6),
            
            # Percentiles
            'p01': round(stats['p01'], 6),
            'p05': round(stats['p05'], 6),
            'p25': round(stats['p25'], 6),
            'p50': round(stats['p50'], 6),
            'p75': round(stats['p75'], 6),
            'p95': round(stats['p95'], 6),
            'p99': round(stats['p99'], 6),
            
            # Estadísticas avanzadas
            'cv': round(stats['cv'], 2) if stats['cv'] is not None else None,
            'skewness': round(stats['skewness'], 4),
            'kurtosis': round(stats['kurtosis'], 4),
            'iqr': round(stats['iqr'], 6),
            
            # Clasificaciones
            'heterogeneidad': clasificar_heterogeneidad(stats['cv']),
            'calidad': calidad
        }
        
        return resultado
        
    except Exception as e:
        return {
            'fecha': info_imagen.get('fecha_str', 'desconocida'),
            'indice': indice,
            'archivo': info_imagen.get('nombre_archivo', 'desconocido'),
            'pixeles_validos': 0,
            'error': str(e)
        }


def clasificar_calidad_imagen(stats, pct_outliers):
    """
    Clasifica la calidad de una imagen según sus estadísticas.
    """
    if stats['n'] < 100:
        return 'MUY BAJA (pocos píxeles)'
    
    if pct_outliers > 10:
        return 'BAJA (muchos outliers)'
    
    if stats['cv'] is None:
        return 'DESCONOCIDA'
    
    if stats['cv'] > 50:
        return 'BAJA (muy heterogéneo)'
    elif stats['cv'] > 30:
        return 'MEDIA (heterogéneo)'
    elif stats['cv'] < 15:
        return 'BUENA (homogéneo)'
    else:
        return 'BUENA'


def analizar_indice(indice):
    """
    Analiza todas las imágenes de un índice.
    """
    print(f"\n{'#'*80}")
    print(f"# ANALIZANDO: {indice}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    print(f"Shapefile: {RUTA_SHAPEFILE}")
    print(f"Rango teórico: {INDICES_INFO[indice]['rango_teorico']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"\nADVERTENCIA: No se encontraron imágenes para {indice}")
        return None
    
    print(f"\nEncontradas {len(imagenes)} imágenes")
    print("\n" + "-"*80)
    
    resultados = []
    
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        fuente_icono = "[CSV]" if img_info.get('csv_pixeles') else "[TIFF]"
        print(f"[{i}/{len(imagenes)}] {fuente_icono} {fecha_str}... ", end='', flush=True)
        
        resultado = analizar_imagen(img_info, indice)
        resultados.append(resultado)
        
        # Mostrar resultado
        if 'error' in resultado:
            print(f"[ERROR] {resultado['error']}")
        else:
            fuente_tag = f"[{resultado.get('fuente_datos', 'tiff').upper()}]"
            print(f"[OK] {fuente_tag} {resultado['pixeles_validos']:,} px | "
                  f"Media: {resultado['media']:.4f} | "
                  f"CV: {resultado['cv']:.1f}% | "
                  f"{resultado['calidad']}")
    
    # Crear DataFrame
    df = pd.DataFrame(resultados)
    
    # Mostrar resumen
    mostrar_resumen_indice(df, indice)
    
    # Guardar reportes
    guardar_reportes(df, indice)
    
    # Generar visualizaciones
    generar_visualizaciones(df, indice)
    
    return df


def mostrar_resumen_indice(df, indice):
    """
    Muestra resumen estadístico del índice.
    """
    print("\n" + "="*80)
    print(f"RESUMEN ESTADÍSTICO - {indice}")
    print("="*80)
    
    # Filtrar solo imágenes válidas
    df_validas = df[df['pixeles_validos'] > 0].copy()
    
    if len(df_validas) == 0:
        print("\nERROR: No hay imágenes válidas para analizar")
        return
    
    n_total = len(df)
    n_validas = len(df_validas)
    n_errores = n_total - n_validas
    
    print(f"\nIMÁGENES:")
    print(f"  • Total analizadas: {n_total}")
    print(f"  • Válidas: {n_validas} ({n_validas/n_total*100:.1f}%)")
    if n_errores > 0:
        print(f"  • Con errores: {n_errores}")
    
    print(f"\nESTADÍSTICAS GLOBALES:")
    print(f"  • Media global: {df_validas['media'].mean():.6f}")
    print(f"  • Mediana global: {df_validas['mediana'].mean():.6f}")
    print(f"  • Desv. estándar promedio: {df_validas['std'].mean():.6f}")
    print(f"  • Valor mínimo absoluto: {df_validas['min'].min():.6f}")
    print(f"  • Valor máximo absoluto: {df_validas['max'].max():.6f}")
    
    print(f"\nPERCENTILES PROMEDIO:")
    print(f"  •  1%: {df_validas['p01'].mean():.6f}")
    print(f"  •  5%: {df_validas['p05'].mean():.6f}")
    print(f"  • 25%: {df_validas['p25'].mean():.6f}")
    print(f"  • 50%: {df_validas['p50'].mean():.6f} (mediana)")
    print(f"  • 75%: {df_validas['p75'].mean():.6f}")
    print(f"  • 95%: {df_validas['p95'].mean():.6f}")
    print(f"  • 99%: {df_validas['p99'].mean():.6f}")
    
    print(f"\nHETEROGENEIDAD:")
    cv_promedio = df_validas['cv'].mean()
    print(f"  • CV promedio: {cv_promedio:.2f}%")
    print(f"  • Clasificación: {clasificar_heterogeneidad(cv_promedio)}")
    
    # Distribución de heterogeneidad
    print(f"\n  Distribución por fecha:")
    for categoria in ['HOMOGÉNEO', 'MODERADAMENTE HETEROGÉNEO', 'HETEROGÉNEO', 'MUY HETEROGÉNEO']:
        n = len(df_validas[df_validas['heterogeneidad'] == categoria])
        if n > 0:
            print(f"    • {categoria}: {n} imágenes ({n/len(df_validas)*100:.1f}%)")
    
    print(f"\nCALIDAD DE IMÁGENES:")
    for calidad in df_validas['calidad'].unique():
        n = len(df_validas[df_validas['calidad'] == calidad])
        print(f"  • {calidad}: {n} imágenes ({n/len(df_validas)*100:.1f}%)")
    
    # Outliers
    outliers_promedio = df_validas['pct_outliers'].mean()
    if outliers_promedio > 0:
        print(f"\nOUTLIERS:")
        print(f"  • Promedio de outliers: {outliers_promedio:.2f}%")
        print(f"  • Máximo detectado: {df_validas['pct_outliers'].max():.2f}%")
    
    # Recomendaciones de umbrales
    print(f"\nRECOMENDACIONES PARA FILTRADO:")
    p05_promedio = df_validas['p05'].mean()
    p95_promedio = df_validas['p95'].mean()
    print(f"  • Umbral inferior sugerido: {p05_promedio:.4f} (percentil 5)")
    print(f"  • Umbral superior sugerido: {p95_promedio:.4f} (percentil 95)")
    print(f"  • Esto eliminaría ~10% de valores extremos por ambos lados")


def guardar_reportes(df, indice):
    """
    Guarda reportes en CSV.
    """
    # Reporte completo por fecha
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_completo = RUTA_REPORTES_EXPLORATORIO / f"analisis_exploratorio_{indice}_{timestamp}.csv"
    df.to_csv(archivo_completo, index=False)
    print(f"\n✓ Reporte completo guardado: {archivo_completo.name}")
    
    # Reporte resumen (solo imágenes válidas)
    df_validas = df[df['pixeles_validos'] > 0].copy()
    if len(df_validas) > 0:
        columnas_resumen = ['fecha', 'media', 'mediana', 'std', 'cv', 'min', 'max', 
                           'p05', 'p95', 'heterogeneidad', 'calidad']
        archivo_resumen = RUTA_REPORTES_EXPLORATORIO / f"resumen_{indice}_{timestamp}.csv"
        df_validas[columnas_resumen].to_csv(archivo_resumen, index=False)
        print(f"✓ Reporte resumen guardado: {archivo_resumen.name}")
    
    # Reporte de problemas (si hay)
    df_problemas = df[df['pixeles_validos'] == 0]
    if len(df_problemas) > 0:
        archivo_problemas = RUTA_REPORTES_EXPLORATORIO / f"problemas_{indice}_{timestamp}.csv"
        df_problemas.to_csv(archivo_problemas, index=False)
        print(f"⚠️  Reporte de problemas guardado: {archivo_problemas.name}")


def generar_visualizaciones(df, indice):
    """
    Genera visualizaciones del análisis.
    """
    df_validas = df[df['pixeles_validos'] > 0].copy()
    
    if len(df_validas) == 0:
        print("\nADVERTENCIA: No hay datos válidos para generar visualizaciones")
        return
    
    print(f"\nGenerando visualizaciones para {indice}...")
    
    # Crear carpeta para el índice
    carpeta_indice = RUTA_VISUALIZACIONES / indice
    carpeta_indice.mkdir(exist_ok=True, parents=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    try:
        # 1. Dashboard completo
        archivo_dashboard = carpeta_indice / f"dashboard_{indice}_{timestamp}.png"
        generar_dashboard_indice(df_validas, indice, archivo_dashboard)
        print(f"  ✓ Dashboard generado: {archivo_dashboard.name}")
        
        # 2. Serie temporal
        archivo_serie = carpeta_indice / f"serie_temporal_{indice}_{timestamp}.png"
        graficar_serie_temporal(
            df_validas, 'fecha', 'media',
            f'{indice} - Evolución Temporal',
            archivo_serie, con_bandas=True
        )
        print(f"  ✓ Serie temporal generada: {archivo_serie.name}")
        
        # 3. Evolución del CV
        archivo_cv = carpeta_indice / f"evolucion_cv_{indice}_{timestamp}.png"
        graficar_evolucion_cv(
            df_validas, 'fecha', 'cv',
            f'{indice} - Evolución del Coeficiente de Variación',
            archivo_cv
        )
        print(f"  ✓ Gráfica de CV generada: {archivo_cv.name}")
        
        print(f"\nVisualizaciones guardadas en: {carpeta_indice}")
        
    except Exception as e:
        print(f"\nADVERTENCIA: Error al generar visualizaciones: {e}")
        archivo_problemas = RUTA_REPORTES_EXPLORATORIO / f"problemas_{indice}_{timestamp}.csv"
        df_problemas.to_csv(archivo_problemas, index=False)
        print(f"ADVERTENCIA: Reporte de problemas guardado: {archivo_problemas.name}")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu_principal():
    """
    Menú interactivo para análisis exploratorio.
    """
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              ANÁLISIS EXPLORATORIO DE ÍNDICES DE VEGETACIÓN               ║
║                         (CON ENMASCARAMIENTO)                             ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    print("Este script analiza índices de vegetación aplicando:")
    print("  ✓ Enmascaramiento automático con shapefile")
    print("  ✓ Estadísticas avanzadas (CV, skewness, kurtosis)")
    print("  ✓ Detección de outliers")
    print("  ✓ Clasificación de heterogeneidad")
    
    # Obtener índices disponibles
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
        
        print("\nOPCIONES:")
        print("  A. Analizar TODOS los índices")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            print("\nSaliendo...")
            break
        
        elif opcion == 'A':
            print("\n" + "="*80)
            print("ANALIZANDO TODOS LOS ÍNDICES")
            print("="*80)
            
            resultados_globales = {}
            
            for indice in indices_disponibles:
                df = analizar_indice(indice)
                if df is not None:
                    resultados_globales[indice] = df
            
            # Resumen global
            if resultados_globales:
                mostrar_resumen_global(resultados_globales)
                
                # Generar visualizaciones comparativas
                print("\n" + "="*80)
                print("GENERANDO VISUALIZACIONES COMPARATIVAS")
                print("="*80)
                
                # Preparar datos para visualización comparativa
                datos_comparativos = {}
                for indice, df in resultados_globales.items():
                    df_validas = df[df['pixeles_validos'] > 0].copy()
                    if len(df_validas) > 0:
                        # Convertir fecha a datetime si no lo es
                        if not pd.api.types.is_datetime64_any_dtype(df_validas['fecha']):
                            df_validas['fecha'] = pd.to_datetime(df_validas['fecha'])
                        datos_comparativos[indice] = df_validas[['fecha', 'media', 'std']].copy()
                
                if datos_comparativos:
                    generar_dashboard_comparativo(
                        datos_comparativos,
                        RUTA_VISUALIZACIONES / "comparativas"
                    )
        
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                analizar_indice(indices_disponibles[num])
            else:
                print("\nERROR: Número inválido")
        
        else:
            print("\nERROR: Opción no válida")


def mostrar_resumen_global(resultados):
    """
    Muestra resumen comparativo de todos los índices.
    """
    print("\n" + "="*80)
    print("RESUMEN COMPARATIVO DE ÍNDICES")
    print("="*80)
    
    datos_comparacion = []
    
    for indice, df in resultados.items():
        df_validas = df[df['pixeles_validos'] > 0]
        
        if len(df_validas) > 0:
            datos_comparacion.append({
                'Índice': indice,
                'Imágenes': len(df_validas),
                'Media': df_validas['media'].mean(),
                'CV (%)': df_validas['cv'].mean(),
                'Heterogeneidad': clasificar_heterogeneidad(df_validas['cv'].mean()),
                'Min': df_validas['min'].min(),
                'Max': df_validas['max'].max()
            })
    
    if datos_comparacion:
        df_comparacion = pd.DataFrame(datos_comparacion)
        print("\n" + df_comparacion.to_string(index=False))
        
        # Guardar resumen comparativo
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archivo = RUTA_REPORTES_EXPLORATORIO / f"comparacion_indices_{timestamp}.csv"
        df_comparacion.to_csv(archivo, index=False)
        print(f"\n✓ Resumen comparativo guardado: {archivo.name}")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    import os
    if os.environ.get('ANALISIS_AUTOMATICO') == '1':
        # Modo automático: analizar todos los índices sin menú
        print("\nModo automático: analizando TODOS los índices\n")
        indices_disponibles = obtener_indices_disponibles()
        
        resultados_globales = {}
        for indice in indices_disponibles:
            df = analizar_indice(indice)
            if df is not None:
                resultados_globales[indice] = df
        
        if resultados_globales:
            mostrar_resumen_global(resultados_globales)
    else:
        # Modo manual: mostrar menú interactivo
        menu_principal()
    
    print("\n" + "="*80)
    print("ANÁLISIS EXPLORATORIO COMPLETADO")
    print("="*80)
    print("\nReportes generados en: reportes/")
    print("\nPróximos pasos:")
    print("  1. Revisar los reportes CSV generados")
    print("  2. Usar umbrales sugeridos para filtrado")
    print("  3. Ejecutar análisis espacial (script 02)")
    print("  4. Ejecutar análisis temporal (script 03)")
