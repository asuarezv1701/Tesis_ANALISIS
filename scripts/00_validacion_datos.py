"""
Script de validación de calidad de datos y enmascaramiento.

Este script:
1. Valida que el shapefile funcione correctamente
2. Analiza cuántos píxeles están dentro/fuera del polígono
3. Genera reporte de calidad por cada imagen
4. Identifica imágenes con problemas

EJECUTAR ANTES DE CUALQUIER ANÁLISIS
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime

# Agregar rutas para importar módulos
sys.path.append(str(Path(__file__).parent.parent))

from analizador_tesis.procesador_base import (
    validar_enmascaramiento,
    listar_imagenes_indice,
    cargar_imagen_enmascarada
)
from analizador_tesis.estadisticas import calcular_estadisticas_basicas
from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_SHAPEFILE,
    RUTA_REPORTES,
    INDICES_INFO,
    obtener_indices_disponibles
)

# Crear carpeta específica para reportes de validación
RUTA_REPORTES_VALIDACION = RUTA_REPORTES / "00_validacion"
RUTA_REPORTES_VALIDACION.mkdir(exist_ok=True, parents=True)


# ============================================================================
# FUNCIONES DE VALIDACIÓN
# ============================================================================

def validar_configuracion_inicial():
    """
    Valida que las rutas principales existan.
    """
    print("="*80)
    print("VALIDACIÓN DE CONFIGURACIÓN INICIAL")
    print("="*80)
    
    errores = []
    
    print(f"\nRuta de descargas: {RUTA_DESCARGAS}")
    if RUTA_DESCARGAS.exists():
        print("   ✓ Encontrada")
    else:
        print("   ✗ NO ENCONTRADA")
        errores.append("Carpeta de descargas no existe")
    
    print(f"\nRuta de shapefile: {RUTA_SHAPEFILE}")
    if RUTA_SHAPEFILE.exists():
        print("   ✓ Encontrado")
        
        # Información del shapefile
        import geopandas as gpd
        try:
            gdf = gpd.read_file(RUTA_SHAPEFILE)
            print(f"   • CRS: {gdf.crs}")
            print(f"   • Número de polígonos: {len(gdf)}")
            print(f"   • Área total: {gdf.geometry.area.sum():.2f} unidades²")
        except Exception as e:
            print(f"   ADVERTENCIA: Error al leer shapefile: {e}")
            errores.append("Shapefile no se puede leer")
    else:
        print("   ✗ NO ENCONTRADO")
        errores.append("Shapefile no existe")
    
    if errores:
        print("\n" + "="*80)
        print("ERRORES ENCONTRADOS:")
        for error in errores:
            print(f"   • {error}")
        print("\nPor favor, corrige estos errores antes de continuar.")
        return False
    
    print("\n" + "="*80)
    print("CONFIGURACIÓN VÁLIDA - LISTO PARA ANÁLISIS")
    print("="*80)
    return True


def validar_indice(indice):
    """
    Valida todas las imágenes de un índice.
    """
    print(f"\n{'#'*80}")
    print(f"# VALIDANDO: {indice}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"⚠️  No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes\n")
    print("-"*80)
    
    resultados = []
    
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        print(f"[{i}/{len(imagenes)}] Validando {fecha_str}... ", end='', flush=True)
        
        # Validar enmascaramiento
        resultado = validar_enmascaramiento(img_info['ruta'])
        resultado['fecha'] = fecha_str
        resultado['indice'] = indice
        
        resultados.append(resultado)
        
        # Mostrar resultado
        if resultado['calidad'] == 'ERROR':
            print(f"✗ ERROR: {resultado.get('error', 'Desconocido')}")
        elif resultado['calidad'] == 'SIN DATOS':
            print("⚠️  SIN DATOS DENTRO DEL POLÍGONO")
        else:
            pct = resultado['porcentaje_dentro_poligono']
            pixeles = resultado['pixeles_dentro_poligono']
            print(f"✓ {pixeles:,} píxeles ({pct:.2f}% del total)")
    
    # Crear DataFrame
    df_resultados = pd.DataFrame(resultados)
    
    # Resumen
    print("\n" + "="*80)
    print(f"RESUMEN DE VALIDACIÓN - {indice}")
    print("="*80)
    
    total_imagenes = len(resultados)
    imagenes_ok = len([r for r in resultados if r['calidad'] == 'BUENA'])
    imagenes_sin_datos = len([r for r in resultados if r['calidad'] == 'SIN DATOS'])
    imagenes_error = len([r for r in resultados if r['calidad'] == 'ERROR'])
    
    print(f"\nTotal de imágenes analizadas: {total_imagenes}")
    print(f"  ✓ Con datos válidos: {imagenes_ok} ({imagenes_ok/total_imagenes*100:.1f}%)")
    
    if imagenes_sin_datos > 0:
        print(f"  ⚠️  Sin datos en polígono: {imagenes_sin_datos}")
    
    if imagenes_error > 0:
        print(f"  ✗ Con errores: {imagenes_error}")
    
    # Estadísticas de píxeles
    if imagenes_ok > 0:
        pixeles_promedio = df_resultados[df_resultados['calidad'] == 'BUENA']['pixeles_dentro_poligono'].mean()
        pct_promedio = df_resultados[df_resultados['calidad'] == 'BUENA']['porcentaje_dentro_poligono'].mean()
        
        print(f"\nEstadísticas de píxeles dentro del polígono:")
        print(f"  • Promedio: {pixeles_promedio:,.0f} píxeles")
        print(f"  • Porcentaje promedio: {pct_promedio:.2f}%")
        print(f"  • Mínimo: {df_resultados['pixeles_dentro_poligono'].min():,} píxeles")
        print(f"  • Máximo: {df_resultados['pixeles_dentro_poligono'].max():,} píxeles")
    
    # Guardar reporte
    archivo_reporte = RUTA_REPORTES_VALIDACION / f"validacion_{indice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    df_resultados.to_csv(archivo_reporte, index=False)
    print(f"\n✓ Reporte guardado en: {archivo_reporte}")
    
    return {
        'indice': indice,
        'total': total_imagenes,
        'ok': imagenes_ok,
        'sin_datos': imagenes_sin_datos,
        'errores': imagenes_error,
        'archivo_reporte': str(archivo_reporte)
    }


def visualizar_ejemplo_enmascaramiento(indice, fecha_ejemplo=None):
    """
    Genera visualización de ejemplo del enmascaramiento.
    """
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap
    
    print(f"\n{'='*80}")
    print(f"GENERANDO VISUALIZACIÓN DE EJEMPLO - {indice}")
    print(f"{'='*80}")
    
    # Obtener imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"No hay imágenes para visualizar de {indice}")
        return
    
    # Seleccionar imagen (la primera o la especificada)
    if fecha_ejemplo:
        imagen_sel = next((img for img in imagenes if img['fecha_str'] == fecha_ejemplo), imagenes[0])
    else:
        imagen_sel = imagenes[len(imagenes)//2]  # Imagen del medio
    
    print(f"Cargando imagen: {imagen_sel['fecha_str']}")
    
    # Cargar imagen enmascarada
    datos_enmascarados, metadata = cargar_imagen_enmascarada(
        imagen_sel['ruta'], 
        retornar_metadata=True
    )
    
    # Calcular estadísticas
    stats = calcular_estadisticas_basicas(datos_enmascarados)
    
    # Crear figura
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Imagen enmascarada
    im1 = axes[0].imshow(datos_enmascarados, cmap='RdYlGn', vmin=stats['p05'], vmax=stats['p95'])
    axes[0].set_title(f"{indice} - Enmascarado\n{imagen_sel['fecha_str']}")
    axes[0].axis('off')
    plt.colorbar(im1, ax=axes[0], fraction=0.046, pad=0.04)
    
    # Máscara (dónde hay datos)
    mascara = ~np.isnan(datos_enmascarados)
    axes[1].imshow(mascara, cmap='gray')
    axes[1].set_title(f"Máscara del Polígono\n{stats['n']:,} píxeles válidos")
    axes[1].axis('off')
    
    plt.tight_layout()
    
    # Guardar
    from configuracion.config import RUTA_VISUALIZACIONES
    archivo_salida = RUTA_VISUALIZACIONES / f"validacion_enmascaramiento_{indice}_{imagen_sel['fecha_str']}.png"
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"✓ Visualización guardada en: {archivo_salida}")
    
    # Mostrar estadísticas
    print(f"\nEstadísticas de la imagen:")
    print(f"  • Píxeles válidos: {stats['n']:,}")
    print(f"  • Media: {stats['media']:.4f}")
    print(f"  • Rango: [{stats['min']:.4f}, {stats['max']:.4f}]")


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu_principal():
    """
    Menú interactivo para validación.
    """
    if not validar_configuracion_inicial():
        return
    
    # Obtener índices disponibles
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("\n❌ No se encontraron índices con datos.")
        return
    
    while True:
        print("\n" + "="*80)
        print("MENÚ DE VALIDACIÓN DE DATOS")
        print("="*80)
        
        print("\nÍNDICES DISPONIBLES:")
        for i, indice in enumerate(indices_disponibles, 1):
            print(f"  {i}. {indice} - {INDICES_INFO[indice]['nombre']}")
        
        print("\nOPCIONES:")
        print("  A. Validar TODOS los índices")
        print("  V. Generar visualización de ejemplo")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            print("\nSaliendo...")
            break
        
        elif opcion == 'A':
            print("\n" + "="*80)
            print("VALIDANDO TODOS LOS ÍNDICES")
            print("="*80)
            
            resumen_global = []
            
            for indice in indices_disponibles:
                resultado = validar_indice(indice)
                if resultado:
                    resumen_global.append(resultado)
            
            # Resumen final
            if resumen_global:
                print("\n" + "="*80)
                print("RESUMEN GLOBAL DE VALIDACIÓN")
                print("="*80)
                
                df_resumen = pd.DataFrame(resumen_global)
                print(f"\n{'Índice':<10} {'Total':<8} {'OK':<8} {'Sin Datos':<12} {'Errores':<10}")
                print("-"*80)
                
                for _, row in df_resumen.iterrows():
                    print(f"{row['indice']:<10} {row['total']:<8} {row['ok']:<8} "
                          f"{row['sin_datos']:<12} {row['errores']:<10}")
                
                # Guardar resumen
                archivo_resumen = RUTA_REPORTES_VALIDACION / f"resumen_validacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df_resumen.to_csv(archivo_resumen, index=False)
                print(f"\n✓ Resumen guardado en: {archivo_resumen}")
        
        elif opcion == 'V':
            print("\nÍndice a visualizar:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice}")
            
            try:
                sel = int(input("Número: ").strip()) - 1
                if 0 <= sel < len(indices_disponibles):
                    visualizar_ejemplo_enmascaramiento(indices_disponibles[sel])
            except:
                print("Opción inválida")
        
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                validar_indice(indices_disponibles[num])
        
        else:
            print("\nERROR: Opción no válida")


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

def ejecutar_validacion_automatica():
    """
    Ejecuta validación automática de todos los índices sin menú interactivo.
    """
    if not validar_configuracion_inicial():
        return False
    
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("\n❌ No se encontraron índices con datos.")
        return False
    
    resumen_global = []
    
    for indice in indices_disponibles:
        resultado = validar_indice(indice)
        if resultado:
            resumen_global.append(resultado)
    
    # Resumen final
    if resumen_global:
        print("\n" + "="*80)
        print("RESUMEN GLOBAL DE VALIDACIÓN")
        print("="*80)
        
        df_resumen = pd.DataFrame(resumen_global)
        print(f"\n{'Índice':<10} {'Total':<8} {'OK':<8} {'Sin Datos':<12} {'Errores':<10}")
        print("-"*80)
        
        for _, row in df_resumen.iterrows():
            print(f"{row['indice']:<10} {row['total']:<8} {row['ok']:<8} "
                  f"{row['sin_datos']:<12} {row['errores']:<10}")
        
        # Guardar resumen
        archivo_resumen = RUTA_REPORTES / f"resumen_validacion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df_resumen.to_csv(archivo_resumen, index=False)
        print(f"\n✓ Resumen guardado en: {archivo_resumen}")
    
    return True


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║           VALIDACIÓN DE CALIDAD DE DATOS Y ENMASCARAMIENTO                ║
║                                                                           ║
║  Este script verifica que el shapefile funcione correctamente y          ║
║  analiza la calidad de los datos dentro del polígono de interés.         ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Detectar si se ejecuta desde el sistema automático
    import os
    if os.environ.get('ANALISIS_AUTOMATICO') == '1':
        # Modo automático: ejecutar todo sin menú
        ejecutar_validacion_automatica()
    else:
        # Modo manual: mostrar menú interactivo
        menu_principal()
    
    print("\n" + "="*80)
    print("VALIDACIÓN COMPLETADA")
    print("="*80)
    print("\nPróximos pasos:")
    print("  1. Revisa los reportes en la carpeta 'reportes/'")
    print("  2. Si hay problemas, corrígelos antes de continuar")
    print("  3. Ejecuta los scripts de análisis (01, 02, 03...)")
