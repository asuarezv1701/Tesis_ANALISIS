"""
Análisis Espacial de Índices de Vegetación

Este script realiza análisis espacial completo:
1. Mapas de calor con estadísticas espaciales
2. Detección de hotspots y coldspots
3. Clustering espacial (K-means y DBSCAN)
4. Autocorrelación espacial (Moran's I)
5. Análisis de diferencias temporales
6. Estadísticas por cuadrantes

⭐ ANÁLISIS CLAVE PARA IDENTIFICAR PATRONES ESPACIALES
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
    print("\n1️⃣  Cargando imagen...")
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
    print("\n2️⃣  Calculando estadísticas espaciales...")
    stats = calcular_estadisticas_espaciales(datos)
    if stats:
        print(f"   • Media: {stats['media']:.4f}")
        print(f"   • Rango: [{stats['min']:.4f}, {stats['max']:.4f}]")
        print(f"   • CV: {stats['cv']:.4f}")
        resultados['estadisticas'] = stats
    
    # 3. Detección de hotspots
    print("\n3️⃣  Detectando hotspots y coldspots...")
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
    print("\n4️⃣  Aplicando clustering K-means...")
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
    print("\n5️⃣  Calculando autocorrelación espacial (Moran's I)...")
    moran = calcular_moran_i(datos, vecindad='queen')
    if moran:
        print(f"   • I de Moran: {moran['moran_i']:.4f}")
        print(f"   • Esperado: {moran['esperado']:.4f}")
        print(f"   • Z-score: {moran['z_score']:.4f}")
        print(f"   • P-valor: {moran['p_valor']:.6f}")
        print(f"   • {moran['interpretacion']}")
        resultados['moran'] = moran
    
    # 6. División en cuadrantes
    print("\n6️⃣  Analizando por cuadrantes...")
    cuadrantes = dividir_en_cuadrantes(datos, n_filas=3, n_cols=3)
    print(f"   • Dividido en {cuadrantes['n_total_cuadrantes']} cuadrantes")
    print("   • Estadísticas por cuadrante:")
    for cuad in cuadrantes['cuadrantes']:
        if cuad['n_pixeles'] > 0:
            print(f"     - Cuadrante {cuad['cuadrante']}: "
                  f"Media={cuad['media']:.4f}, Std={cuad['std']:.4f}")
    resultados['cuadrantes'] = cuadrantes
    
    print(f"\n{'='*80}")
    print("✅ ANÁLISIS ESPACIAL COMPLETADO")
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
    print(f"✅ Analizadas {len(diferencias)} transiciones")
    print(f"{'='*80}")
    
    return {
        'indice': indice,
        'n_transiciones': len(diferencias),
        'diferencias': diferencias
    }


def analizar_espacial_indice(indice, analizar_todas=False):
    """
    Realiza análisis espacial completo de un índice.
    """
    print(f"\n{'#'*80}")
    print(f"# ANÁLISIS ESPACIAL: {indice}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"\n⚠️  No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes")
    
    resultados_imagenes = []
    
    if analizar_todas:
        # Analizar todas las imágenes
        for i, img_info in enumerate(imagenes, 1):
            fecha_str = img_info['fecha_str'] or img_info['carpeta']
            print(f"\n[{i}/{len(imagenes)}] {fecha_str}")
            
            try:
                resultado = analizar_espacial_imagen(img_info['ruta'], indice, fecha_str)
                resultados_imagenes.append(resultado)
            except Exception as e:
                print(f"⚠️  Error al analizar {fecha_str}: {e}")
    else:
        # Analizar solo primera, última y mediana
        indices_analizar = [0, len(imagenes)//2, -1]
        etiquetas = ['Primera', 'Mediana', 'Última']
        
        for idx, etiqueta in zip(indices_analizar, etiquetas):
            img_info = imagenes[idx]
            fecha_str = img_info['fecha_str'] or img_info['carpeta']
            print(f"\n📅 {etiqueta} imagen: {fecha_str}")
            
            try:
                resultado = analizar_espacial_imagen(img_info['ruta'], indice, fecha_str)
                resultados_imagenes.append(resultado)
            except Exception as e:
                print(f"⚠️  Error: {e}")
    
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


# ============================================================================
# VISUALIZACIONES
# ============================================================================

def generar_visualizaciones_espaciales(indice, resultados_imagenes, resultado_diff):
    """
    Genera visualizaciones del análisis espacial.
    """
    print("\n📈 Generando visualizaciones...")
    
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_vis = RUTA_VISUALIZACIONES / indice / "espacial"
    carpeta_vis.mkdir(exist_ok=True, parents=True)
    
    visualizaciones = []
    
    # Visualizaciones para cada imagen analizada
    for res in resultados_imagenes:
        fecha = res['fecha']
        datos = res['imagen']
        
        # 1. Mapa de calor básico
        archivo = carpeta_vis / f"mapa_calor_{indice}_{fecha}_{timestamp}.png"
        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(datos, cmap='RdYlGn', interpolation='nearest')
        plt.colorbar(im, ax=ax, label=indice)
        ax.set_title(f'{indice} - Mapa de Calor\n{fecha}')
        ax.axis('off')
        plt.tight_layout()
        plt.savefig(archivo, dpi=150, bbox_inches='tight')
        plt.close()
        visualizaciones.append(archivo.name)
        
        # 2. Hotspots y coldspots
        if 'hotspots' in res:
            archivo = carpeta_vis / f"hotspots_{indice}_{fecha}_{timestamp}.png"
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Crear imagen RGB
            img_rgb = np.zeros((*datos.shape, 3))
            img_rgb[:, :, 1] = 0.5  # Fondo verde tenue
            
            # Hotspots en rojo
            img_rgb[res['hotspots']['hotspots'], 0] = 1.0
            img_rgb[res['hotspots']['hotspots'], 1] = 0.0
            
            # Coldspots en azul
            img_rgb[res['hotspots']['coldspots'], 2] = 1.0
            img_rgb[res['hotspots']['coldspots'], 1] = 0.0
            
            ax.imshow(img_rgb)
            ax.set_title(f'{indice} - Hotspots y Coldspots\n{fecha}')
            ax.axis('off')
            
            # Leyenda
            red_patch = mpatches.Patch(color='red', label=f"Hotspots ({res['hotspots']['n_hotspots']} px)")
            blue_patch = mpatches.Patch(color='blue', label=f"Coldspots ({res['hotspots']['n_coldspots']} px)")
            ax.legend(handles=[red_patch, blue_patch], loc='upper right')
            
            plt.tight_layout()
            plt.savefig(archivo, dpi=150, bbox_inches='tight')
            plt.close()
            visualizaciones.append(archivo.name)
        
        # 3. Clustering
        if 'kmeans' in res:
            archivo = carpeta_vis / f"clustering_{indice}_{fecha}_{timestamp}.png"
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(res['kmeans']['clusters_2d'], cmap='tab10', interpolation='nearest')
            plt.colorbar(im, ax=ax, label='Cluster')
            ax.set_title(f'{indice} - Clustering K-means\n{fecha}')
            ax.axis('off')
            plt.tight_layout()
            plt.savefig(archivo, dpi=150, bbox_inches='tight')
            plt.close()
            visualizaciones.append(archivo.name)
    
    # 4. Visualización de diferencias temporales
    if resultado_diff and resultado_diff['diferencias']:
        # Tomar primeras diferencias para visualizar
        for i, diff in enumerate(resultado_diff['diferencias'][:3]):  # Máximo 3
            archivo = carpeta_vis / f"diferencia_{indice}_{diff['fecha1']}_a_{diff['fecha2']}_{timestamp}.png"
            
            fig, ax = plt.subplots(figsize=(10, 8))
            im = ax.imshow(diff['diferencia'], cmap='RdBu_r', interpolation='nearest',
                          vmin=-np.nanstd(diff['diferencia'])*2,
                          vmax=np.nanstd(diff['diferencia'])*2)
            plt.colorbar(im, ax=ax, label='Diferencia')
            ax.set_title(f'{indice} - Diferencia Temporal\n{diff["fecha1"]} → {diff["fecha2"]}')
            ax.axis('off')
            plt.tight_layout()
            plt.savefig(archivo, dpi=150, bbox_inches='tight')
            plt.close()
            visualizaciones.append(archivo.name)
    
    print(f"✓ Generadas {len(visualizaciones)} visualizaciones")
    for nombre in visualizaciones[:5]:  # Mostrar solo primeras 5
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
        print("\n❌ No se encontraron índices con datos.")
        return
    
    while True:
        print("\n" + "="*80)
        print("ÍNDICES DISPONIBLES:")
        print("="*80)
        
        for i, indice in enumerate(indices_disponibles, 1):
            print(f"  {i}. {indice:<8} - {INDICES_INFO[indice]['nombre']}")
        
        print("\nOPCIONES:")
        print("  A. Analizar TODOS los índices (muestra representativa)")
        print("  F. Analizar TODAS las fechas de un índice")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            break
        elif opcion == 'A':
            for indice in indices_disponibles:
                analizar_espacial_indice(indice, analizar_todas=False)
        elif opcion == 'F':
            print("\nSelecciona el índice:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice}")
            idx_str = input("Número: ").strip()
            if idx_str.isdigit():
                idx = int(idx_str) - 1
                if 0 <= idx < len(indices_disponibles):
                    analizar_espacial_indice(indices_disponibles[idx], analizar_todas=True)
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                analizar_espacial_indice(indices_disponibles[num], analizar_todas=False)


if __name__ == "__main__":
    menu_principal()
    
    print("\n" + "="*80)
    print("ANÁLISIS ESPACIAL COMPLETADO")
    print("="*80)
    print("\nReportes en: reportes/espacial/")
    print("Visualizaciones en: visualizaciones/[INDICE]/espacial/")
