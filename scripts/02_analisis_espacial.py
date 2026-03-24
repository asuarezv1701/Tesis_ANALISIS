"""
Análisis Espacial de Índices de Vegetación

Este script realiza análisis espacial completo:
1. Mapas de calor con estadísticas espaciales
2. Detección de hotspots y coldspots
3. Clustering espacial (K-means y DBSCAN)
4. Autocorrelación espacial (Moran's I)
5. Análisis de diferencias temporales
6. Estadísticas por cuadrantes

ANÁLISIS CLAVE PARA IDENTIFICAR PATRONES ESPACIALES
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
    calcular_estadisticas_espaciales,
    suavizar_imagen,
    detectar_hotspots,
    etiquetar_regiones,
    clustering_kmeans,
    clustering_dbscan,
    calcular_moran_i,
    calcular_diferencia_temporal,
    dividir_en_cuadrantes
)
from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_SHAPEFILE,
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    INDICES_INFO,
    obtener_indices_disponibles
)

# Crear carpeta específica para reportes espaciales
RUTA_REPORTES_ESPACIAL = RUTA_REPORTES / "02_espacial"
RUTA_REPORTES_ESPACIAL.mkdir(exist_ok=True, parents=True)

warnings.filterwarnings('ignore')


# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

def analizar_espacial_imagen(ruta_imagen, indice, fecha_str):
    """
    Realiza análisis espacial completo de una imagen.
    """
    print(f"\n{'='*80}")
    print(f"ANÁLISIS ESPACIAL: {indice} - {fecha_str}")
    print(f"{'='*80}")
    
    # Cargar imagen
    print("\n[1] Cargando imagen...")
    datos = cargar_imagen_enmascarada(ruta_imagen, RUTA_SHAPEFILE)
    print(f"   ✓ Cargada: {datos.shape[0]}x{datos.shape[1]} pixeles")
    print(f"   ✓ Datos válidos: {np.sum(~np.isnan(datos))}")
    
    resultados = {
        'indice': indice,
        'fecha': fecha_str,
        'imagen': datos,
        'shape': datos.shape
    }
    
    # 2. Estadísticas espaciales básicas
    print("\n[2] Calculando estadísticas espaciales...")
    stats = calcular_estadisticas_espaciales(datos)
    if stats:
        print(f"   • Media: {stats['media']:.4f}")
        print(f"   • Rango: [{stats['min']:.4f}, {stats['max']:.4f}]")
        print(f"   • CV: {stats['cv']:.4f}")
        resultados['estadisticas'] = stats
    
    # 3. Detección de hotspots
    print("\n[3] Detectando hotspots y coldspots...")
    hotspots_result = detectar_hotspots(datos, metodo='percentil', umbral=10)
    if hotspots_result:
        print(f"   • Hotspots: {hotspots_result['n_hotspots']} "
              f"({hotspots_result['porcentaje_hotspots']:.2f}%)")
        print(f"   • Coldspots: {hotspots_result['n_coldspots']} "
              f"({hotspots_result['porcentaje_coldspots']:.2f}%)")
        print(f"   • Media hotspots: {hotspots_result['media_hotspots']:.4f}")
        print(f"   • Media coldspots: {hotspots_result['media_coldspots']:.4f}")
        resultados['hotspots'] = hotspots_result
        
        # Etiquetar regiones de hotspots
        print("   • Etiquetando regiones de hotspots...")
        regiones_hot = etiquetar_regiones(hotspots_result['hotspots'])
        print(f"     - {regiones_hot['n_regiones']} regiones identificadas")
        if regiones_hot['n_regiones'] > 0:
            print(f"     - Tamaño promedio: {regiones_hot['tamaño_promedio']:.0f} pixeles")
        resultados['regiones_hotspots'] = regiones_hot
    
    # 4. Clustering K-means
    print("\n[4] Aplicando clustering K-means...")
    kmeans_result = clustering_kmeans(datos, n_clusters=5, incluir_coords=True)
    if kmeans_result:
        print(f"   • {kmeans_result['n_clusters']} clusters identificados")
        print(f"   • Inercia: {kmeans_result['inercia']:.2f}")
        print("   • Distribución de clusters:")
        for cluster_info in kmeans_result['stats_clusters']:
            print(f"     - Cluster {cluster_info['cluster']}: "
                  f"{cluster_info['n_pixeles']} px ({cluster_info['porcentaje']:.1f}%), "
                  f"Media={cluster_info['media']:.4f}")
        resultados['kmeans'] = kmeans_result
    
    # 5. Autocorrelación espacial (Moran's I)
    print("\n[5] Calculando autocorrelación espacial (Moran's I)...")
    moran = calcular_moran_i(datos, vecindad='queen')
    if moran:
        print(f"   • I de Moran: {moran['moran_i']:.4f}")
        print(f"   • Esperado: {moran['esperado']:.4f}")
        print(f"   • Z-score: {moran['z_score']:.4f}")
        print(f"   • P-valor: {moran['p_valor']:.6f}")
        print(f"   • {moran['interpretacion']}")
        resultados['moran'] = moran
    
    # 6. División en cuadrantes
    print("\n[6] Analizando por cuadrantes...")
    cuadrantes = dividir_en_cuadrantes(datos, n_filas=3, n_cols=3)
    print(f"   • Dividido en {cuadrantes['n_total_cuadrantes']} cuadrantes")
    print("   • Estadísticas por cuadrante:")
    for cuad in cuadrantes['cuadrantes']:
        if cuad['n_pixeles'] > 0:
            print(f"     - Cuadrante {cuad['cuadrante']}: "
                  f"Media={cuad['media']:.4f}, Std={cuad['std']:.4f}")
    resultados['cuadrantes'] = cuadrantes
    
    print(f"\n{'='*80}")
    print("\nANÁLISIS ESPACIAL COMPLETADO")
    print(f"{'='*80}")
    
    return resultados


def analizar_diferencias_temporales(indice):
    """
    Analiza diferencias espaciales entre fechas consecutivas.
    """
    print(f"\n{'#'*80}")
    print(f"# ANÁLISIS DE DIFERENCIAS TEMPORALES: {indice}")
    print(f"{'#'*80}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if len(imagenes) < 2:
        print("\n⚠️  Se necesitan al menos 2 imágenes para análisis temporal")
        return None
    
    print(f"\nEncontradas {len(imagenes)} imágenes")
    
    # Analizar diferencias entre fechas consecutivas
    diferencias = []
    
    for i in range(len(imagenes) - 1):
        img1_info = imagenes[i]
        img2_info = imagenes[i + 1]
        
        fecha1_str = img1_info['fecha_str'] or img1_info['carpeta']
        fecha2_str = img2_info['fecha_str'] or img2_info['carpeta']
        
        print(f"\n{'-'*80}")
        print(f"Comparando: {fecha1_str} → {fecha2_str}")
        
        # Cargar imágenes de forma optimizada
        datos1, _ = cargar_datos_optimizado(img1_info, usar_csv=True)
        datos2, _ = cargar_datos_optimizado(img2_info, usar_csv=True)
        
        # NOTA: Para análisis espacial necesitamos reconstruir la imagen 2D desde datos 1D
        # Por ahora usamos TIFF para mantener estructura espacial
        datos1 = cargar_imagen_enmascarada(img1_info['ruta'], RUTA_SHAPEFILE)
        datos2 = cargar_imagen_enmascarada(img2_info['ruta'], RUTA_SHAPEFILE)
        
        # Calcular diferencia
        from analizador_tesis.espacial import calcular_diferencia_temporal
        diff_result = calcular_diferencia_temporal(datos1, datos2)
        
        if diff_result:
            print(f"   • Cambio medio: {diff_result['diferencia_media']:+.4f}")
            print(f"   • Aumento fuerte: {diff_result['n_aumento']} px "
                  f"({diff_result['porcentaje_aumento']:.2f}%)")
            print(f"   • Disminución fuerte: {diff_result['n_disminucion']} px "
                  f"({diff_result['porcentaje_disminucion']:.2f}%)")
            print(f"   • Sin cambio: {diff_result['n_sin_cambio']} px "
                  f"({diff_result['porcentaje_sin_cambio']:.2f}%)")
            
            diferencias.append({
                'fecha1': fecha1_str,
                'fecha2': fecha2_str,
                'fecha1_obj': img1_info['fecha'],
                'fecha2_obj': img2_info['fecha'],
                **diff_result
            })
    
    print(f"\n{'='*80}")
    print(f"\nAnalizadas {len(diferencias)} transiciones")
    print(f"{'='*80}")
    
    return {
        'indice': indice,
        'n_transiciones': len(diferencias),
        'diferencias': diferencias
    }


def analizar_espacial_indice(indice):
    """
    Realiza análisis espacial completo de un índice.
    Analiza TODAS las imágenes disponibles.
    """
    print(f"\n{'#'*80}")
    print(f"# ANÁLISIS ESPACIAL: {indice}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"\nADVERTENCIA: No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes")
    print("Analizando TODAS las imágenes...")
    
    resultados_imagenes = []
    
    # Analizar todas las imágenes
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        print(f"\n[{i}/{len(imagenes)}] {fecha_str}")
        
        try:
            resultado = analizar_espacial_imagen(img_info['ruta'], indice, fecha_str)
            resultados_imagenes.append(resultado)
        except Exception as e:
            print(f"⚠️  Error al analizar {fecha_str}: {e}")
    
    # Analizar diferencias temporales
    print(f"\n{'='*80}")
    print("ANÁLISIS DE DIFERENCIAS TEMPORALES")
    print(f"{'='*80}")
    
    resultado_diff = analizar_diferencias_temporales(indice)
    
    # Guardar reportes
    guardar_reportes_espaciales(indice, resultados_imagenes, resultado_diff)
    
    # Generar visualizaciones
    generar_visualizaciones_espaciales(indice, resultados_imagenes, resultado_diff)
    
    return {
        'indice': indice,
        'resultados_imagenes': resultados_imagenes,
        'diferencias_temporales': resultado_diff
    }


# ============================================================================
# GUARDAR REPORTES
# ============================================================================

def guardar_reportes_espaciales(indice, resultados_imagenes, resultado_diff):
    """
    Guarda reportes del análisis espacial.
    """
    print("\n📊 Guardando reportes...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_reportes = RUTA_REPORTES_ESPACIAL
    carpeta_reportes.mkdir(exist_ok=True, parents=True)
    
    archivos = []
    
    # 1. Reporte de estadísticas espaciales
    if resultados_imagenes:
        datos_stats = []
        for res in resultados_imagenes:
            if 'estadisticas' in res:
                fila = {'fecha': res['fecha'], **res['estadisticas']}
                datos_stats.append(fila)
        
        if datos_stats:
            df_stats = pd.DataFrame(datos_stats)
            archivo = carpeta_reportes / f"estadisticas_espaciales_{indice}_{timestamp}.csv"
            df_stats.to_csv(archivo, index=False)
            archivos.append(archivo.name)
    
    # 2. Reporte de hotspots
    if resultados_imagenes:
        datos_hot = []
        for res in resultados_imagenes:
            if 'hotspots' in res:
                fila = {
                    'fecha': res['fecha'],
                    'n_hotspots': res['hotspots']['n_hotspots'],
                    'porcentaje_hotspots': res['hotspots']['porcentaje_hotspots'],
                    'media_hotspots': res['hotspots']['media_hotspots'],
                    'n_coldspots': res['hotspots']['n_coldspots'],
                    'porcentaje_coldspots': res['hotspots']['porcentaje_coldspots'],
                    'media_coldspots': res['hotspots']['media_coldspots']
                }
                datos_hot.append(fila)
        
        if datos_hot:
            df_hot = pd.DataFrame(datos_hot)
            archivo = carpeta_reportes / f"hotspots_{indice}_{timestamp}.csv"
            df_hot.to_csv(archivo, index=False)
            archivos.append(archivo.name)
    
    # 3. Reporte de clustering
    if resultados_imagenes:
        datos_cluster = []
        for res in resultados_imagenes:
            if 'kmeans' in res:
                for cluster_info in res['kmeans']['stats_clusters']:
                    fila = {
                        'fecha': res['fecha'],
                        **cluster_info
                    }
                    datos_cluster.append(fila)
        
        if datos_cluster:
            df_cluster = pd.DataFrame(datos_cluster)
            archivo = carpeta_reportes / f"clustering_{indice}_{timestamp}.csv"
            df_cluster.to_csv(archivo, index=False)
            archivos.append(archivo.name)
    
    # 4. Reporte de Moran's I
    if resultados_imagenes:
        datos_moran = []
        for res in resultados_imagenes:
            if 'moran' in res:
                fila = {
                    'fecha': res['fecha'],
                    'moran_i': res['moran']['moran_i'],
                    'z_score': res['moran']['z_score'],
                    'p_valor': res['moran']['p_valor'],
                    'interpretacion': res['moran']['interpretacion']
                }
                datos_moran.append(fila)
        
        if datos_moran:
            df_moran = pd.DataFrame(datos_moran)
            archivo = carpeta_reportes / f"autocorrelacion_{indice}_{timestamp}.csv"
            df_moran.to_csv(archivo, index=False)
            archivos.append(archivo.name)
    
    # 5. Reporte de diferencias temporales
    if resultado_diff and resultado_diff['diferencias']:
        datos_diff = []
        for diff in resultado_diff['diferencias']:
            datos_diff.append({
                'fecha1': diff['fecha1'],
                'fecha2': diff['fecha2'],
                'diferencia_media': diff['diferencia_media'],
                'diferencia_std': diff['diferencia_std'],
                'n_aumento': diff['n_aumento'],
                'porcentaje_aumento': diff['porcentaje_aumento'],
                'n_disminucion': diff['n_disminucion'],
                'porcentaje_disminucion': diff['porcentaje_disminucion'],
                'n_sin_cambio': diff['n_sin_cambio'],
                'porcentaje_sin_cambio': diff['porcentaje_sin_cambio']
            })
        
        df_diff = pd.DataFrame(datos_diff)
        archivo = carpeta_reportes / f"diferencias_temporales_{indice}_{timestamp}.csv"
        df_diff.to_csv(archivo, index=False)
        archivos.append(archivo.name)
    
    print(f"✓ Guardados {len(archivos)} reportes")
    for nombre in archivos:
        print(f"  • {nombre}")
    
    # 6. Generar archivo TXT explicativo de colores
    generar_explicacion_colores_txt(indice, resultados_imagenes, timestamp, carpeta_reportes)


def generar_explicacion_colores_txt(indice, resultados_imagenes, timestamp, carpeta_reportes):
    """
    Genera un archivo TXT que explica detalladamente qué significa
    cada color en las visualizaciones del análisis espacial.
    """
    from configuracion.config import INDICES_INFO
    
    archivo_txt = carpeta_reportes / f"EXPLICACION_COLORES_{indice}_{timestamp}.txt"
    
    contenido = f"""
================================================================================
  GUÍA DE INTERPRETACIÓN DE COLORES - ANÁLISIS ESPACIAL
  Índice: {indice} - {INDICES_INFO[indice]['nombre']}
================================================================================

Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Este documento explica el significado de los colores en las visualizaciones
del análisis espacial. Use esta guía como referencia para interpretar
correctamente los mapas generados.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. MAPA DE CALOR (mapa_calor_*.png)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Los mapas de calor usan una paleta de degradado que representa la salud
de la vegetación:

  COLOR           VALOR {indice:<6}  SIGNIFICADO
  ─────────────────────────────────────────────────────────────────────
  🟤 Marrón       < 0.2           Suelo desnudo o vegetación muy escasa
                                  → Áreas sin cobertura vegetal significativa
  
  🟡 Amarillo     0.2 - 0.4       Vegetación dispersa o con estrés
                                  → Posible sequía, enfermedad o baja densidad
  
  🟢 Verde claro  0.4 - 0.6       Vegetación moderada
                                  → Cobertura vegetal en condiciones normales
  
  🟢 Verde medio  0.6 - 0.8       Vegetación densa y saludable
                                  → Buena actividad fotosintética
  
  🟢 Verde oscuro > 0.8           Vegetación muy densa y vigorosa
                                  → Excelente salud vegetal

NOTA: Los valores exactos pueden variar según el índice. Para NDMI (humedad),
      valores negativos indican vegetación seca.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. MAPA DE HOTSPOTS Y COLDSPOTS (hotspots_*.png)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este mapa identifica zonas que se desvían significativamente del promedio:

  COLOR           NOMBRE        QUÉ SIGNIFICA
  ─────────────────────────────────────────────────────────────────────
  🟠 Naranja      HOTSPOT       Zonas con valores EXCEPCIONALMENTE ALTOS
                                → Vegetación inusualmente saludable
                                → Posible área de interés positivo
                                → Revisar: ¿riego adicional? ¿microclima favorable?
  
  🔵 Azul        COLDSPOT       Zonas con valores EXCEPCIONALMENTE BAJOS
                                → Vegetación con problemas
                                → ATENCIÓN: Posible estrés, enfermedad o daño
                                → Requiere investigación en campo
  
  ⬜ Gris        NORMAL         Valores dentro del rango esperado
                                → Sin anomalías detectadas

MÉTODO: Se identifican usando estadística (valores fuera de 2 desviaciones
        estándar del promedio).


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. MAPA DE CLUSTERING K-MEANS (clustering_*.png)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

El clustering agrupa automáticamente zonas con características similares.
Los colores NO tienen un significado fijo - representan GRUPOS diferentes:

  COLOR           ZONA          QUÉ REPRESENTA
  ─────────────────────────────────────────────────────────────────────
  🔴 Rojo        Zona 1        Grupo de píxeles con valores similares
  🟠 Naranja     Zona 2        Otro grupo con características distintas
  🟡 Amarillo    Zona 3        Grupo intermedio
  🟢 Verde       Zona 4        Otro grupo diferenciado
  🔵 Azul        Zona 5        Grupo final

IMPORTANTE - CÓMO INTERPRETAR:
  
  • Los colores identifican GRUPOS, no niveles de calidad
  • Para saber qué significa cada zona, revise el archivo CSV de clustering
  • En el CSV encontrará el VALOR MEDIO de cada zona
  • Zona con valor medio ALTO = vegetación más saludable
  • Zona con valor medio BAJO = vegetación menos saludable o suelo

EJEMPLO DE INTERPRETACIÓN:
  Si el CSV muestra:
    - Zona 1 (Rojo):    media = 0.25  → Vegetación escasa
    - Zona 2 (Naranja): media = 0.45  → Vegetación moderada
    - Zona 5 (Azul):    media = 0.72  → Vegetación densa

  Entonces el azul representa las mejores áreas y el rojo las más pobres.

"""
    
    # Agregar información específica de los clusters si está disponible
    if resultados_imagenes and len(resultados_imagenes) > 0:
        res = resultados_imagenes[-1]  # Usar el más reciente
        if 'kmeans' in res:
            contenido += f"""
DATOS DE CLUSTERING PARA {res['fecha']}:
────────────────────────────────────────
"""
            for i, cluster_info in enumerate(res['kmeans']['stats_clusters']):
                contenido += f"""
  Zona {i+1}:
    • Porcentaje del área: {cluster_info['porcentaje']:.1f}%
    • Valor medio {indice}: {cluster_info['media']:.4f}
    • Desviación estándar: {cluster_info['std']:.4f}
    • Valor mínimo: {cluster_info['min']:.4f}
    • Valor máximo: {cluster_info['max']:.4f}
"""
            
            # Ordenar zonas por valor medio para interpretación
            zonas_ordenadas = sorted(enumerate(res['kmeans']['stats_clusters']), 
                                    key=lambda x: x[1]['media'])
            
            contenido += f"""
INTERPRETACIÓN ORDENADA (de peor a mejor vegetación):
─────────────────────────────────────────────────────
"""
            for orden, (idx, info) in enumerate(zonas_ordenadas, 1):
                if info['media'] < 0.3:
                    estado = "⚠️  Vegetación escasa/suelo"
                elif info['media'] < 0.5:
                    estado = "🟡 Vegetación moderada"
                elif info['media'] < 0.7:
                    estado = "🟢 Vegetación saludable"
                else:
                    estado = "🌿 Vegetación muy vigorosa"
                
                contenido += f"  {orden}. Zona {idx+1}: media={info['media']:.3f}  {estado}\n"

    contenido += """

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. MAPA DE DIFERENCIAS TEMPORALES (diferencia_*.png)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Muestra cómo cambió la vegetación entre dos fechas:

  COLOR              CAMBIO           SIGNIFICADO
  ─────────────────────────────────────────────────────────────────────
  🔴 Rojo oscuro    Muy negativo     Deterioro severo de vegetación
                                     → Pérdida significativa de cobertura
  
  🔴 Rojo claro    Negativo          Disminución moderada
                                     → Posible estrés estacional o poda
  
  ⬜ Blanco        Sin cambio        Área estable
                                     → Condiciones mantenidas
  
  🟢 Verde claro   Positivo          Mejora moderada
                                     → Crecimiento de vegetación
  
  🟢 Verde oscuro  Muy positivo      Mejora significativa
                                     → Recuperación o nuevo crecimiento


================================================================================
RESUMEN RÁPIDO
================================================================================

  MAPA DE CALOR:     Degradado marrón→amarillo→verde = malo→regular→bueno
  HOTSPOTS:          Naranja=excepcionalmente alto, Azul=excepcionalmente bajo
  CLUSTERING:        Colores=grupos (ver CSV para valores de cada grupo)
  DIFERENCIAS:       Rojo=empeoró, Blanco=igual, Verde=mejoró


================================================================================
Para más información, consulte los archivos CSV generados en esta misma carpeta.
================================================================================
"""
    
    with open(archivo_txt, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    print(f"  • {archivo_txt.name} (guía de interpretación de colores)")


# ============================================================================
# VISUALIZACIONES
# ============================================================================

def generar_visualizaciones_espaciales(indice, resultados_imagenes, resultado_diff):
    """
    Genera visualizaciones del análisis espacial con paletas de degradado
    y descripciones claras de lo que representa cada color.
    """
    print("\n📈 Generando visualizaciones...")
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.colorbar as cbar
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_vis = RUTA_VISUALIZACIONES / indice / "espacial"
    carpeta_vis.mkdir(exist_ok=True, parents=True)
    
    visualizaciones = []
    
    # Crear paleta de degradado personalizada (marrón -> amarillo -> verde)
    # Representa: vegetación escasa -> moderada -> saludable
    colores_degradado = [
        '#8B4513',  # Marrón (valores bajos - suelo/vegetación muy escasa)
        '#CD853F',  # Marrón claro
        '#DAA520',  # Dorado
        '#FFEB3B',  # Amarillo (valores medios)
        '#9ACD32',  # Verde amarillento
        '#32CD32',  # Verde lima (valores altos)
        '#006400'   # Verde oscuro (vegetación muy saludable)
    ]
    cmap_vegetacion = LinearSegmentedColormap.from_list('vegetacion', colores_degradado, N=256)
    
    # Interpretaciones por rango de valor según el índice
    def obtener_interpretacion(indice, valor):
        """Retorna interpretación del valor según el índice."""
        if indice in ['NDVI', 'NDRE', 'MSAVI', 'RECI']:
            if valor < 0:
                return 'Agua o suelo desnudo'
            elif valor < 0.2:
                return 'Suelo/Vegetación muy escasa'
            elif valor < 0.4:
                return 'Vegetación dispersa o stress'
            elif valor < 0.6:
                return 'Vegetación moderada'
            elif valor < 0.8:
                return 'Vegetación densa y saludable'
            else:
                return 'Vegetación muy densa'
        elif indice == 'NDMI':
            if valor < -0.3:
                return 'Vegetación muy seca'
            elif valor < 0:
                return 'Vegetación con bajo contenido de agua'
            elif valor < 0.2:
                return 'Contenido de agua moderado'
            elif valor < 0.4:
                return 'Buen contenido de agua'
            else:
                return 'Alto contenido de agua'
        return ''
    
    # Visualizaciones para cada imagen analizada
    for res in resultados_imagenes:
        fecha = res['fecha']
        datos = res['imagen']
        
        # 1. Mapa de calor mejorado con degradado y descripción detallada
        archivo = carpeta_vis / f"mapa_calor_{indice}_{fecha}_{timestamp}.png"
        
        fig = plt.figure(figsize=(14, 10))
        gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.05)
        
        ax_mapa = fig.add_subplot(gs[0, 0])
        ax_leyenda = fig.add_subplot(gs[0, 1])
        
        # Calcular rango de valores
        datos_validos = datos[~np.isnan(datos)]
        if len(datos_validos) > 0:
            vmin = np.percentile(datos_validos, 2)
            vmax = np.percentile(datos_validos, 98)
        else:
            vmin, vmax = -1, 1
        
        # Mostrar mapa con degradado
        im = ax_mapa.imshow(datos, cmap=cmap_vegetacion, interpolation='bilinear',
                           vmin=vmin, vmax=vmax)
        ax_mapa.set_title(f'{indice} - Mapa Espacial\\n{fecha}', fontsize=14, fontweight='bold')
        ax_mapa.axis('off')
        
        # Barra de color vertical
        cbar_ax = fig.add_axes([0.52, 0.15, 0.02, 0.7])
        cb = plt.colorbar(im, cax=cbar_ax)
        cb.set_label(f'Valor {indice}', fontsize=10)
        
        # Panel de leyenda explicativa
        ax_leyenda.axis('off')
        
        # Título de interpretación
        ax_leyenda.text(0.1, 0.95, '¿QUÉ ESTOY VIENDO?', fontsize=12, fontweight='bold',
                       transform=ax_leyenda.transAxes, va='top')
        
        ax_leyenda.text(0.1, 0.88, f'Mapa de {INDICES_INFO[indice]["nombre"]}', fontsize=10,
                       transform=ax_leyenda.transAxes, va='top', style='italic')
        
        # Descripción del índice
        ax_leyenda.text(0.1, 0.80, 'Este mapa muestra:', fontsize=10, fontweight='bold',
                       transform=ax_leyenda.transAxes, va='top')
        
        desc_wrap = INDICES_INFO[indice]['descripcion'][:150]
        ax_leyenda.text(0.1, 0.74, desc_wrap, fontsize=9, wrap=True,
                       transform=ax_leyenda.transAxes, va='top', color='#444444')
        
        # Guía de colores
        ax_leyenda.text(0.1, 0.60, 'GUÍA DE COLORES:', fontsize=11, fontweight='bold',
                       transform=ax_leyenda.transAxes, va='top', color='#2E86AB')
        
        guia_colores = [
            ('#006400', 'Verde oscuro', 'Vegetación muy saludable\\n(valores altos)'),
            ('#32CD32', 'Verde claro', 'Vegetación densa'),
            ('#FFEB3B', 'Amarillo', 'Vegetación moderada'),
            ('#DAA520', 'Dorado', 'Vegetación dispersa'),
            ('#8B4513', 'Marrón', 'Suelo o vegetación escasa\\n(valores bajos)')
        ]
        
        y_pos = 0.52
        for color, nombre, descripcion in guia_colores:
            # Caja de color
            rect = mpatches.FancyBboxPatch((0.1, y_pos - 0.025), 0.1, 0.035,
                                           boxstyle="round,pad=0.01",
                                           facecolor=color, edgecolor='#333333', linewidth=0.5,
                                           transform=ax_leyenda.transAxes)
            ax_leyenda.add_patch(rect)
            
            # Texto
            ax_leyenda.text(0.25, y_pos, nombre, fontsize=9, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='center')
            ax_leyenda.text(0.25, y_pos - 0.035, descripcion, fontsize=8, color='#666666',
                           transform=ax_leyenda.transAxes, va='top')
            y_pos -= 0.09
        
        # Estadísticas del área
        if len(datos_validos) > 0:
            ax_leyenda.text(0.1, 0.08, 'ESTADÍSTICAS:', fontsize=10, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top')
            stats_text = f'Media: {np.mean(datos_validos):.3f}\\nMín: {np.min(datos_validos):.3f}\\nMáx: {np.max(datos_validos):.3f}'
            ax_leyenda.text(0.1, 0.02, stats_text, fontsize=9, family='monospace',
                           transform=ax_leyenda.transAxes, va='top')
        
        plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()
        visualizaciones.append(archivo.name)
        
        # 2. Hotspots y coldspots mejorado
        if 'hotspots' in res:
            archivo = carpeta_vis / f"hotspots_{indice}_{fecha}_{timestamp}.png"
            
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.05)
            
            ax_mapa = fig.add_subplot(gs[0, 0])
            ax_leyenda = fig.add_subplot(gs[0, 1])
            
            # Crear imagen RGB con fondo neutro
            img_rgb = np.zeros((*datos.shape, 3))
            
            # Fondo gris para áreas normales
            mascara_normal = ~np.isnan(datos) & ~res['hotspots']['hotspots'] & ~res['hotspots']['coldspots']
            img_rgb[mascara_normal, 0] = 0.7
            img_rgb[mascara_normal, 1] = 0.7
            img_rgb[mascara_normal, 2] = 0.7
            
            # Hotspots en rojo-naranja
            img_rgb[res['hotspots']['hotspots'], 0] = 1.0
            img_rgb[res['hotspots']['hotspots'], 1] = 0.3
            img_rgb[res['hotspots']['hotspots'], 2] = 0.0
            
            # Coldspots en azul
            img_rgb[res['hotspots']['coldspots'], 0] = 0.0
            img_rgb[res['hotspots']['coldspots'], 1] = 0.4
            img_rgb[res['hotspots']['coldspots'], 2] = 0.9
            
            ax_mapa.imshow(img_rgb, interpolation='nearest')
            ax_mapa.set_title(f'{indice} - Zonas de Atención\\n{fecha}', fontsize=14, fontweight='bold')
            ax_mapa.axis('off')
            
            # Panel de leyenda
            ax_leyenda.axis('off')
            
            ax_leyenda.text(0.1, 0.95, '¿QUÉ ESTOY VIENDO?', fontsize=12, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top')
            
            ax_leyenda.text(0.1, 0.85, 'Zonas que requieren atención:', fontsize=10,
                           transform=ax_leyenda.transAxes, va='top')
            
            # Leyenda de colores
            leyenda_items = [
                ('#FF4D00', 'HOTSPOTS (Naranja)', f'{res["hotspots"]["n_hotspots"]:,} píxeles\\n({res["hotspots"]["porcentaje_hotspots"]:.1f}% del área)', 
                 'Zonas con valores MUY ALTOS.\\nPueden indicar vegetación\\nexcepcionalmente saludable.'),
                ('#0066E6', 'COLDSPOTS (Azul)', f'{res["hotspots"]["n_coldspots"]:,} píxeles\\n({res["hotspots"]["porcentaje_coldspots"]:.1f}% del área)',
                 'Zonas con valores MUY BAJOS.\\nPueden indicar estrés,\\nenfermedad o suelo desnudo.'),
                ('#B3B3B3', 'Zona Normal (Gris)', '', 'Valores dentro del rango\\nesperable para el área.')
            ]
            
            y_pos = 0.72
            for color, nombre, stats, descripcion in leyenda_items:
                rect = mpatches.FancyBboxPatch((0.1, y_pos - 0.02), 0.12, 0.04,
                                               boxstyle="round,pad=0.01",
                                               facecolor=color, edgecolor='#333333', linewidth=0.5,
                                               transform=ax_leyenda.transAxes)
                ax_leyenda.add_patch(rect)
                
                ax_leyenda.text(0.25, y_pos + 0.01, nombre, fontsize=10, fontweight='bold',
                               transform=ax_leyenda.transAxes, va='center')
                if stats:
                    ax_leyenda.text(0.25, y_pos - 0.045, stats, fontsize=9, color='#333333',
                                   transform=ax_leyenda.transAxes, va='top')
                ax_leyenda.text(0.25, y_pos - 0.11, descripcion, fontsize=8, color='#666666',
                               transform=ax_leyenda.transAxes, va='top')
                y_pos -= 0.22
            
            plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            visualizaciones.append(archivo.name)
        
        # 3. Clustering mejorado
        if 'kmeans' in res:
            archivo = carpeta_vis / f"clustering_{indice}_{fecha}_{timestamp}.png"
            
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.05)
            
            ax_mapa = fig.add_subplot(gs[0, 0])
            ax_leyenda = fig.add_subplot(gs[0, 1])
            
            # Paleta categórica clara
            colores_cluster = ['#E53935', '#FB8C00', '#FDD835', '#43A047', '#1E88E5']
            from matplotlib.colors import ListedColormap
            cmap_clusters = ListedColormap(colores_cluster)
            
            im = ax_mapa.imshow(res['kmeans']['clusters_2d'], cmap=cmap_clusters, 
                               interpolation='nearest', vmin=0, vmax=4)
            ax_mapa.set_title(f'{indice} - Segmentación por Zonas\\n{fecha}', fontsize=14, fontweight='bold')
            ax_mapa.axis('off')
            
            # Panel de leyenda
            ax_leyenda.axis('off')
            
            ax_leyenda.text(0.1, 0.95, '¿QUÉ ESTOY VIENDO?', fontsize=12, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top')
            
            ax_leyenda.text(0.1, 0.85, 'Agrupación automática de zonas\\nsimilares (K-means clustering)', 
                           fontsize=10, transform=ax_leyenda.transAxes, va='top')
            
            ax_leyenda.text(0.1, 0.72, 'ZONAS IDENTIFICADAS:', fontsize=10, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top', color='#2E86AB')
            
            y_pos = 0.65
            for i, cluster_info in enumerate(res['kmeans']['stats_clusters'][:5]):
                rect = mpatches.FancyBboxPatch((0.1, y_pos - 0.015), 0.1, 0.03,
                                               boxstyle="round,pad=0.01",
                                               facecolor=colores_cluster[i], edgecolor='#333333', linewidth=0.5,
                                               transform=ax_leyenda.transAxes)
                ax_leyenda.add_patch(rect)
                
                ax_leyenda.text(0.25, y_pos, f'Zona {i+1}', fontsize=10, fontweight='bold',
                               transform=ax_leyenda.transAxes, va='center')
                ax_leyenda.text(0.25, y_pos - 0.04, f'{cluster_info["porcentaje"]:.1f}% del área\\nValor medio: {cluster_info["media"]:.3f}',
                               fontsize=8, color='#666666', transform=ax_leyenda.transAxes, va='top')
                y_pos -= 0.12
            
            plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            visualizaciones.append(archivo.name)
    
    # 4. Visualización de diferencias temporales mejorada
    if resultado_diff and resultado_diff['diferencias']:
        # Paleta de degradado para diferencias (azul negativo - blanco neutro - rojo positivo)
        colores_diff = ['#0D47A1', '#2196F3', '#BBDEFB', '#FFFFFF', '#FFCDD2', '#F44336', '#B71C1C']
        cmap_diff = LinearSegmentedColormap.from_list('diferencias', colores_diff, N=256)
        
        for i, diff in enumerate(resultado_diff['diferencias'][:3]):
            archivo = carpeta_vis / f"diferencia_{indice}_{diff['fecha1']}_a_{diff['fecha2']}_{timestamp}.png"
            
            fig = plt.figure(figsize=(14, 10))
            gs = fig.add_gridspec(1, 2, width_ratios=[3, 1], wspace=0.05)
            
            ax_mapa = fig.add_subplot(gs[0, 0])
            ax_leyenda = fig.add_subplot(gs[0, 1])
            
            limite = np.nanstd(diff['diferencia']) * 2
            
            im = ax_mapa.imshow(diff['diferencia'], cmap=cmap_diff, interpolation='bilinear',
                              vmin=-limite, vmax=limite)
            ax_mapa.set_title(f'{indice} - Cambio Temporal\\n{diff["fecha1"]} → {diff["fecha2"]}', 
                             fontsize=14, fontweight='bold')
            ax_mapa.axis('off')
            
            # Barra de color
            cbar_ax = fig.add_axes([0.52, 0.15, 0.02, 0.7])
            cb = plt.colorbar(im, cax=cbar_ax)
            cb.set_label('Diferencia', fontsize=10)
            
            # Panel de leyenda
            ax_leyenda.axis('off')
            
            ax_leyenda.text(0.1, 0.95, '¿QUÉ ESTOY VIENDO?', fontsize=12, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top')
            
            ax_leyenda.text(0.1, 0.85, 'Cambio entre dos fechas:', fontsize=10,
                           transform=ax_leyenda.transAxes, va='top')
            
            guia = [
                ('#B71C1C', 'Rojo intenso', 'Aumento significativo'),
                ('#F44336', 'Rojo', 'Aumento moderado'),
                ('#FFFFFF', 'Blanco', 'Sin cambio'),
                ('#2196F3', 'Azul', 'Disminución moderada'),
                ('#0D47A1', 'Azul intenso', 'Disminución significativa')
            ]
            
            y_pos = 0.70
            for color, nombre, desc in guia:
                rect = mpatches.FancyBboxPatch((0.1, y_pos - 0.015), 0.1, 0.03,
                                               boxstyle="round,pad=0.01",
                                               facecolor=color, edgecolor='#333333', linewidth=0.5,
                                               transform=ax_leyenda.transAxes)
                ax_leyenda.add_patch(rect)
                ax_leyenda.text(0.25, y_pos, f'{nombre}: {desc}', fontsize=9,
                               transform=ax_leyenda.transAxes, va='center')
                y_pos -= 0.08
            
            # Estadísticas
            ax_leyenda.text(0.1, 0.25, 'RESUMEN:', fontsize=10, fontweight='bold',
                           transform=ax_leyenda.transAxes, va='top')
            stats = f"Mejoró: {diff['porcentaje_aumento']:.1f}%\\nEstable: {diff['porcentaje_sin_cambio']:.1f}%\\nEmpeoró: {diff['porcentaje_disminucion']:.1f}%"
            ax_leyenda.text(0.1, 0.18, stats, fontsize=9, family='monospace',
                           transform=ax_leyenda.transAxes, va='top')
            
            plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
            plt.close()
            visualizaciones.append(archivo.name)
    
    print(f"✓ Generadas {len(visualizaciones)} visualizaciones")
    for nombre in visualizaciones[:5]:
        print(f"  • {nombre}")
    if len(visualizaciones) > 5:
        print(f"  ... y {len(visualizaciones)-5} más")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu_principal():
    """Menú interactivo."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                    ANÁLISIS ESPACIAL DE ÍNDICES                           ║
║              (Mapas, Hotspots, Clustering, Autocorrelación)               ║
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
        
        print("\nOPCIONES:")
        print("  A. Analizar TODOS los índices")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            break
        elif opcion == 'A':
            for indice in indices_disponibles:
                analizar_espacial_indice(indice)
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                analizar_espacial_indice(indices_disponibles[num])


if __name__ == "__main__":
    import os
    if os.environ.get('ANALISIS_AUTOMATICO') == '1':
        # Modo automático: analizar todos los índices con todas las fechas
        print("\nModo automático: analizando TODOS los índices con TODAS las fechas\n")
        indices_disponibles = obtener_indices_disponibles()
        for indice in indices_disponibles:
            analizar_espacial_indice(indice)
    else:
        # Modo manual: mostrar menú
        menu_principal()
    
    print("\n" + "="*80)
    print("ANÁLISIS ESPACIAL COMPLETADO")
    print("="*80)
    print("\nReportes en: reportes/02_espacial/")
    print("Visualizaciones en: visualizaciones/[INDICE]/espacial/")
