"""
Script para analizar los rangos de valores de índices de vegetación en todas las imágenes descargadas.
Soporta: NDVI, NDRE, MSAVI, RECI, NDMI
Muestra estadísticas detalladas para ayudar a decidir qué valores filtrar.
Permite analizar múltiples índices de forma interactiva.
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
import rasterio
from datetime import datetime

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

RUTA_BASE = r"c:\Users\XMK0181\Documents\TT\Tesis_DESCARGAS\descargas\UPIITA_contours_25nov.2025"

# Información de índices disponibles
INDICES_INFO = {
    "NDVI": "Índice de Vegetación Normalizado",
    "NDRE": "Red Edge Normalizado",
    "MSAVI": "Índice Ajustado de Vegetación",
    "RECI": "Índice de Clorofila Red Edge",
    "NDMI": "Índice de Humedad"
}

# ============================================================================
# FUNCIONES
# ============================================================================

def analizar_imagen_tiff(ruta_tiff):
    """
    Analiza una imagen TIFF y retorna estadísticas de sus valores.
    """
    try:
        with rasterio.open(ruta_tiff) as src:
            datos = src.read(1)  # Lee la primera banda
            
            # Reemplazar valores no válidos (NaN, inf)
            datos_validos = datos[~np.isnan(datos) & ~np.isinf(datos)]
            
            if len(datos_validos) == 0:
                return None
            
            estadisticas = {
                'min': np.min(datos_validos),
                'max': np.max(datos_validos),
                'media': np.mean(datos_validos),
                'mediana': np.median(datos_validos),
                'std': np.std(datos_validos),
                'p01': np.percentile(datos_validos, 1),
                'p05': np.percentile(datos_validos, 5),
                'p25': np.percentile(datos_validos, 25),
                'p75': np.percentile(datos_validos, 75),
                'p95': np.percentile(datos_validos, 95),
                'p99': np.percentile(datos_validos, 99),
                'total_pixeles': datos.size,
                'pixeles_validos': len(datos_validos)
            }
            
            return estadisticas
    except Exception as e:
        print(f"Error al leer {ruta_tiff}: {e}")
        return None


def analizar_csv(ruta_csv):
    """
    Analiza un archivo CSV de valores de píxeles.
    """
    try:
        df = pd.read_csv(ruta_csv)
        
        if 'NDVI' not in df.columns:
            return None
        
        ndvi_values = df['NDVI'].dropna()
        
        if len(ndvi_values) == 0:
            return None
        
        estadisticas = {
            'min': ndvi_values.min(),
            'max': ndvi_values.max(),
            'media': ndvi_values.mean(),
            'mediana': ndvi_values.median(),
            'std': ndvi_values.std(),
            'p01': ndvi_values.quantile(0.01),
            'p05': ndvi_values.quantile(0.05),
            'p25': ndvi_values.quantile(0.25),
            'p75': ndvi_values.quantile(0.75),
            'p95': ndvi_values.quantile(0.95),
            'p99': ndvi_values.quantile(0.99),
            'total_pixeles': len(df),
            'pixeles_validos': len(ndvi_values)
        }
        
        return estadisticas
    except Exception as e:
        print(f"Error al leer {ruta_csv}: {e}")
        return None


def obtener_fecha_carpeta(nombre_carpeta):
    """
    Extrae la fecha del nombre de la carpeta.
    Ejemplo: UPIITA_contours_25nov.2025_20200107_20251127_143833 -> 2020-01-07
    """
    try:
        partes = nombre_carpeta.split('_')
        for parte in partes:
            if len(parte) == 8 and parte.isdigit():
                fecha_str = parte
                fecha = datetime.strptime(fecha_str, '%Y%m%d')
                return fecha.strftime('%Y-%m-%d')
    except:
        pass
    return nombre_carpeta


def obtener_indices_disponibles():
    """
    Busca qué índices tienen datos disponibles en la carpeta de descargas.
    """
    if not os.path.exists(RUTA_BASE):
        return []
    
    indices_disponibles = []
    for item in os.listdir(RUTA_BASE):
        ruta_item = os.path.join(RUTA_BASE, item)
        if os.path.isdir(ruta_item) and item in INDICES_INFO:
            # Verificar que tenga carpetas de fechas
            carpetas = [d for d in os.listdir(ruta_item) 
                       if os.path.isdir(os.path.join(ruta_item, d))]
            if carpetas:
                indices_disponibles.append(item)
    
    return sorted(indices_disponibles)


def seleccionar_indices():
    """
    Muestra menú interactivo para que el usuario seleccione índices a analizar.
    Valida que los índices seleccionados estén disponibles.
    """
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("ERROR: No se encontraron índices con datos en:")
        print(f"{RUTA_BASE}")
        return []
    
    while True:
        print("\n" + "="*80)
        print("ÍNDICES DISPONIBLES:")
        print("="*80)
        
        # Crear mapeo de números a índices
        indice_map = {}
        numero = 1
        for key in ["NDVI", "NDRE", "MSAVI", "RECI", "NDMI"]:
            if key in indices_disponibles:
                estado = "✓ Disponible"
                indice_map[numero] = key
            else:
                estado = "✗ No encontrado"
            
            print(f"  {numero}. {key:<8} - {INDICES_INFO[key]:<40} {estado}")
            numero += 1
        
        print("\n" + "-"*80)
        
        # Mostrar advertencia si hay índices no disponibles
        indices_no_disponibles = set(INDICES_INFO.keys()) - set(indices_disponibles)
        if indices_no_disponibles:
            print(f"\n⚠️  NOTA: Los siguientes índices NO están disponibles:")
            for idx in sorted(indices_no_disponibles):
                print(f"    • {idx}")
            print("\n    Solo puedes seleccionar índices marcados como '✓ Disponible'")
        
        print("\n" + "="*80)
        entrada = input("Ingresa los números separados por comas (ej: 1,2,5) o 'salir': ").strip()
        
        if entrada.lower() == 'salir':
            return []
        
        # Parsear entrada
        try:
            numeros = [int(n.strip()) for n in entrada.split(',')]
            indices_seleccionados = []
            indices_invalidos = []
            
            for num in numeros:
                if num in indice_map:
                    indices_seleccionados.append(indice_map[num])
                else:
                    indices_invalidos.append(num)
            
            # Validar selección
            if indices_invalidos:
                print(f"\n❌ ERROR: Los siguientes números no son válidos o no están disponibles: {indices_invalidos}")
                print("   Por favor, selecciona solo números de índices disponibles.")
                continue
            
            if not indices_seleccionados:
                print("\n❌ ERROR: No seleccionaste ningún índice válido.")
                continue
            
            # Confirmar selección
            print(f"\n✓ Seleccionaste: {', '.join(indices_seleccionados)}")
            confirmacion = input("¿Continuar con estos índices? (s/n): ").strip().lower()
            
            if confirmacion == 's':
                return indices_seleccionados
            
        except ValueError:
            print("\n❌ ERROR: Entrada inválida. Usa números separados por comas.")


def analizar_indice(indice):
    """
    Analiza un índice específico y retorna las estadísticas.
    """
    RUTA_DESCARGAS = os.path.join(RUTA_BASE, indice)
    
    print("\n" + "="*80)
    print(f"ANÁLISIS DE RANGOS DE VALORES {indice}")
    print("="*80)
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]}")
    print(f"Buscando imágenes en: {RUTA_DESCARGAS}\n")
    
    # Verificar que la carpeta existe
    if not os.path.exists(RUTA_DESCARGAS):
        print(f"ERROR: No se encontró la carpeta para el índice {indice}")
        return None
    
    # Buscar todas las carpetas con fechas
    carpetas_fechas = sorted([d for d in os.listdir(RUTA_DESCARGAS) 
                              if os.path.isdir(os.path.join(RUTA_DESCARGAS, d))])
    
    if not carpetas_fechas:
        print(f"No se encontraron carpetas de fechas para {indice}.")
        return None
    
    print(f"Encontradas {len(carpetas_fechas)} imágenes\n")
    
    # Lista para almacenar resultados
    resultados = []
    
    # Analizar cada carpeta
    for carpeta in carpetas_fechas:
        ruta_carpeta = os.path.join(RUTA_DESCARGAS, carpeta)
        fecha = obtener_fecha_carpeta(carpeta)
        
        # Buscar archivo TIFF
        archivos_tiff = [f for f in os.listdir(ruta_carpeta) if f.endswith('.tiff') or f.endswith('.tif')]
        
        if archivos_tiff:
            ruta_tiff = os.path.join(ruta_carpeta, archivos_tiff[0])
            print(f"Analizando {fecha}... ", end='')
            
            stats = analizar_imagen_tiff(ruta_tiff)
            
            if stats:
                stats['fecha'] = fecha
                stats['archivo'] = archivos_tiff[0]
                resultados.append(stats)
                print(f"✓ (Min: {stats['min']:.4f}, Max: {stats['max']:.4f}, Media: {stats['media']:.4f})")
            else:
                print("✗ (Sin datos válidos)")
    
    if not resultados:
        print(f"\nNo se pudieron analizar las imágenes de {indice}.")
        return None
    
    # Crear DataFrame con resultados
    df_resultados = pd.DataFrame(resultados)
    
    # Mostrar estadísticas globales
    print("\n" + "="*80)
    print(f"ESTADÍSTICAS GLOBALES DE TODAS LAS IMÁGENES - {indice}")
    print("="*80)
    
    print(f"\nTotal de imágenes analizadas: {len(resultados)}")
    print(f"\nValor mínimo encontrado: {df_resultados['min'].min():.6f}")
    print(f"Valor máximo encontrado: {df_resultados['max'].max():.6f}")
    print(f"Media global: {df_resultados['media'].mean():.6f}")
    print(f"Desviación estándar promedio: {df_resultados['std'].mean():.6f}")
    
    print("\n" + "-"*80)
    print("PERCENTILES GLOBALES (promedio de todas las imágenes)")
    print("-"*80)
    print(f"  1%:  {df_resultados['p01'].mean():.6f}")
    print(f"  5%:  {df_resultados['p05'].mean():.6f}")
    print(f" 25%:  {df_resultados['p25'].mean():.6f}")
    print(f" 50%:  {df_resultados['mediana'].mean():.6f} (mediana)")
    print(f" 75%:  {df_resultados['p75'].mean():.6f}")
    print(f" 95%:  {df_resultados['p95'].mean():.6f}")
    print(f" 99%:  {df_resultados['p99'].mean():.6f}")
    
    # Distribución de valores
    print("\n" + "="*80)
    print("DISTRIBUCIÓN DE VALORES POR IMAGEN")
    print("="*80)
    print(f"{'Fecha':<12} {'Min':<10} {'Max':<10} {'Media':<10} {'P5':<10} {'P95':<10}")
    print("-"*80)
    
    for _, row in df_resultados.iterrows():
        print(f"{row['fecha']:<12} {row['min']:<10.4f} {row['max']:<10.4f} "
              f"{row['media']:<10.4f} {row['p05']:<10.4f} {row['p95']:<10.4f}")
    
    # Recomendaciones para filtrado
    print("\n" + "="*80)
    print(f"RECOMENDACIONES PARA FILTRADO - {indice}")
    print("="*80)
    
    # Información específica por índice
    interpretaciones = {
        "NDVI": {
            "rango": "[-1, 1]",
            "interpretacion": [
                "  • Valores < 0:     Agua, nubes, nieve",
                "  • Valores 0-0.2:   Suelo desnudo, rocas, construcciones",
                "  • Valores 0.2-0.5: Vegetación escasa o estresada",
                "  • Valores 0.5-0.8: Vegetación moderada a densa",
                "  • Valores > 0.8:   Vegetación muy densa y saludable"
            ]
        },
        "NDRE": {
            "rango": "[-1, 1]",
            "interpretacion": [
                "  • Sensible al contenido de clorofila",
                "  • Útil para detectar estrés temprano en plantas",
                "  • Valores más altos indican mayor contenido de clorofila"
            ]
        },
        "MSAVI": {
            "rango": "[-1, 1]",
            "interpretacion": [
                "  • Minimiza el efecto del suelo desnudo",
                "  • Útil en áreas con poca cobertura vegetal",
                "  • Valores más altos indican más vegetación"
            ]
        },
        "RECI": {
            "rango": "[0, 20+]",
            "interpretacion": [
                "  • Correlacionado con contenido de clorofila",
                "  • Valores típicos: 0-10",
                "  • Valores más altos indican más clorofila"
            ]
        },
        "NDMI": {
            "rango": "[-1, 1]",
            "interpretacion": [
                "  • Sensible al contenido de humedad",
                "  • Valores más altos indican mayor humedad",
                "  • Útil para detectar estrés hídrico"
            ]
        }
    }
    
    info = interpretaciones.get(indice, {"rango": "Variable", "interpretacion": ["  • Consulte documentación específica"]})
    
    print(f"\nEl índice {indice} típicamente tiene valores en el rango {info['rango']}:")
    for linea in info['interpretacion']:
        print(linea)
    
    print(f"\nEn tus datos de {indice}:")
    print(f"  • Rango real: [{df_resultados['min'].min():.4f}, {df_resultados['max'].max():.4f}]")
    print(f"  • Media global: {df_resultados['media'].mean():.4f}")
    
    # Sugerencias de umbral
    umbral_inferior_sugerido = df_resultados['p05'].mean()
    umbral_superior_sugerido = df_resultados['p95'].mean()
    
    print(f"\n  Sugerencia de umbrales para eliminar outliers:")
    print(f"    - Umbral inferior: {umbral_inferior_sugerido:.4f} (percentil 5)")
    print(f"    - Umbral superior: {umbral_superior_sugerido:.4f} (percentil 95)")
    
    # Guardar resultados en CSV
    carpeta_reportes = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'reportes')
    os.makedirs(carpeta_reportes, exist_ok=True)
    archivo_salida = os.path.join(carpeta_reportes, f'estadisticas_{indice}.csv')
    df_resultados.to_csv(archivo_salida, index=False)
    print(f"\n✓ Estadísticas guardadas en: {archivo_salida}")
    
    return {
        'indice': indice,
        'archivo': archivo_salida,
        'umbral_inferior': umbral_inferior_sugerido,
        'umbral_superior': umbral_superior_sugerido
    }


def main():
    """
    Función principal que gestiona el análisis de múltiples índices.
    """
    print("="*80)
    print("ANÁLISIS DE ÍNDICES DE VEGETACIÓN")
    print("="*80)
    print("\nEste script analizará los índices seleccionados y generará estadísticas")
    print("para ayudarte a decidir los umbrales de filtrado.\n")
    
    # Seleccionar índices
    indices_seleccionados = seleccionar_indices()
    
    if not indices_seleccionados:
        print("\nAnálisis cancelado.")
        return
    
    # Analizar cada índice
    resultados_analisis = []
    
    for i, indice in enumerate(indices_seleccionados, 1):
        print(f"\n{'#'*80}")
        print(f"# PROCESANDO ÍNDICE {i}/{len(indices_seleccionados)}: {indice}")
        print(f"{'#'*80}")
        
        resultado = analizar_indice(indice)
        if resultado:
            resultados_analisis.append(resultado)
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL DEL ANÁLISIS")
    print("="*80)
    
    if resultados_analisis:
        print(f"\n✓ Se analizaron exitosamente {len(resultados_analisis)} índices:")
        print("\n" + "-"*80)
        print(f"{'Índice':<10} {'Umbral Min Sugerido':<25} {'Umbral Max Sugerido':<25}")
        print("-"*80)
        
        for res in resultados_analisis:
            print(f"{res['indice']:<10} {res['umbral_inferior']:<25.4f} {res['umbral_superior']:<25.4f}")
        
        print("\n" + "-"*80)
        print("\nArchivos generados:")
        for res in resultados_analisis:
            print(f"  • {res['archivo']}")
        
        print("\n" + "="*80)
        print("SIGUIENTE PASO: FILTRAR DATOS")
        print("="*80)
        print("\nAhora puedes ejecutar el script de filtrado:")
        print("  python filtrar_datos_indices.py")
        print("\nEl script te permitirá seleccionar los índices a filtrar")
        print("y configurar los umbrales basándote en estas estadísticas.")
    else:
        print("\n❌ No se pudo analizar ningún índice.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
