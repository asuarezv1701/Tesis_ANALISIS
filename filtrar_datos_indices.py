"""
Script para filtrar datos de índices de vegetación según umbrales definidos por el usuario.
Soporta: NDVI, NDRE, MSAVI, RECI, NDMI
Crea una nueva carpeta con las imágenes filtradas.
Permite filtrar múltiples índices de forma interactiva.
"""

import os
import numpy as np
import pandas as pd
import rasterio
from pathlib import Path
from datetime import datetime
import shutil

# ============================================================================
# CONFIGURACIÓN DE RUTAS
# ============================================================================

RUTA_BASE = r"c:\Users\XMK0181\Documents\TT\Tesis_DESCARGAS\descargas\UPIITA_contours_25nov.2025"
RUTA_SALIDA_BASE = r"c:\Users\XMK0181\Documents\TT\Tesis_ANALISIS\datos_filtrados"

# Opciones adicionales
CREAR_CSV_FILTRADOS = True  # Si deseas crear CSVs con los datos filtrados
MANTENER_METADATOS = True   # Mantener archivos shapefile y metadatos

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

def obtener_fecha_carpeta(nombre_carpeta):
    """
    Extrae la fecha del nombre de la carpeta.
    """
    try:
        partes = nombre_carpeta.split('_')
        for parte in partes:
            if len(parte) == 8 and parte.isdigit():
                return parte
    except:
        pass
    return None


def filtrar_imagen_tiff(ruta_entrada, ruta_salida, umbral_min, umbral_max, rangos_desactivar=None, percentiles=None):
    """
    Filtra una imagen TIFF aplicando umbrales y guarda el resultado.
    """
    try:
        with rasterio.open(ruta_entrada) as src:
            # Leer datos
            datos = src.read(1)
            perfil = src.profile.copy()
            
            # Convertir ceros a NaN para evitar que afecten el análisis
            datos[datos == 0] = np.nan

            # Contar píxeles originales válidos
            pixeles_originales = np.sum(~np.isnan(datos) & ~np.isinf(datos))

            # Aplicar filtros
            datos_filtrados = datos.copy()
            mascara = (datos_filtrados < umbral_min) | (datos_filtrados > umbral_max)
            datos_filtrados[mascara] = np.nan

            # Desactivar rangos seleccionados por el usuario
            if rangos_desactivar:
                p25 = percentiles.get('p25') if percentiles else None
                p75 = percentiles.get('p75') if percentiles else None
                p95 = percentiles.get('p95') if percentiles else None

                # 1) Valores < 0
                if 1 in rangos_desactivar:
                    datos_filtrados[datos_filtrados < 0] = np.nan
                # 2) Igual a 0 (ya convertidos a NaN arriba, pero por claridad)
                if 2 in rangos_desactivar:
                    datos_filtrados[datos_filtrados == 0] = np.nan
                # 3) 0 – P25
                if 3 in rangos_desactivar and p25 is not None:
                    mask = (datos_filtrados >= 0) & (datos_filtrados < p25)
                    datos_filtrados[mask] = np.nan
                # 4) P25 – P75
                if 4 in rangos_desactivar and p25 is not None and p75 is not None:
                    mask = (datos_filtrados >= p25) & (datos_filtrados < p75)
                    datos_filtrados[mask] = np.nan
                # 5) P75 – P95
                if 5 in rangos_desactivar and p75 is not None and p95 is not None:
                    mask = (datos_filtrados >= p75) & (datos_filtrados < p95)
                    datos_filtrados[mask] = np.nan
                # 6) > P95
                if 6 in rangos_desactivar and p95 is not None:
                    datos_filtrados[datos_filtrados > p95] = np.nan
            
            # Contar píxeles después del filtrado
            pixeles_filtrados = np.sum(~np.isnan(datos_filtrados) & ~np.isinf(datos_filtrados))
            pixeles_eliminados = pixeles_originales - pixeles_filtrados
            
            # Guardar imagen filtrada
            with rasterio.open(ruta_salida, 'w', **perfil) as dst:
                dst.write(datos_filtrados, 1)
            
            # Estadísticas
            if pixeles_filtrados > 0:
                datos_validos = datos_filtrados[~np.isnan(datos_filtrados)]
                estadisticas = {
                    'pixeles_originales': int(pixeles_originales),
                    'pixeles_filtrados': int(pixeles_filtrados),
                    'pixeles_eliminados': int(pixeles_eliminados),
                    'porcentaje_retenido': (pixeles_filtrados / pixeles_originales * 100) if pixeles_originales > 0 else 0,
                    'min': float(np.min(datos_validos)),
                    'max': float(np.max(datos_validos)),
                    'media': float(np.mean(datos_validos)),
                    'mediana': float(np.median(datos_validos))
                }
            else:
                estadisticas = {
                    'pixeles_originales': int(pixeles_originales),
                    'pixeles_filtrados': 0,
                    'pixeles_eliminados': int(pixeles_originales),
                    'porcentaje_retenido': 0,
                    'min': None,
                    'max': None,
                    'media': None,
                    'mediana': None
                }
            
            return estadisticas
            
    except Exception as e:
        print(f"Error al procesar {ruta_entrada}: {e}")
        return None


def filtrar_csv(ruta_entrada, ruta_salida, umbral_min, umbral_max, nombre_columna, rangos_desactivar=None, percentiles=None):
    """
    Filtra un archivo CSV de valores de píxeles.
    """
    try:
        df = pd.read_csv(ruta_entrada)
        
        if nombre_columna not in df.columns:
            return None
        
        # Convertir ceros a NaN
        if nombre_columna in df.columns:
            df.loc[df[nombre_columna] == 0, nombre_columna] = np.nan

        # Aplicar filtro de umbrales
        serie = df[nombre_columna]
        mask_valid = serie.notna() & (serie >= umbral_min) & (serie <= umbral_max)

        # Desactivar rangos seleccionados
        if rangos_desactivar:
            p25 = percentiles.get('p25') if percentiles else None
            p75 = percentiles.get('p75') if percentiles else None
            p95 = percentiles.get('p95') if percentiles else None

            # 1) < 0
            if 1 in rangos_desactivar:
                mask_valid &= ~(serie < 0)
            # 2) == 0 (ya es NaN, por claridad)
            if 2 in rangos_desactivar:
                mask_valid &= ~(serie == 0)
            # 3) 0 – P25
            if 3 in rangos_desactivar and p25 is not None:
                mask_valid &= ~((serie >= 0) & (serie < p25))
            # 4) P25 – P75
            if 4 in rangos_desactivar and p25 is not None and p75 is not None:
                mask_valid &= ~((serie >= p25) & (serie < p75))
            # 5) P75 – P95
            if 5 in rangos_desactivar and p75 is not None and p95 is not None:
                mask_valid &= ~((serie >= p75) & (serie < p95))
            # 6) > P95
            if 6 in rangos_desactivar and p95 is not None:
                mask_valid &= ~(serie > p95)

        df_filtrado = df[mask_valid].copy()
        
        # Guardar
        df_filtrado.to_csv(ruta_salida, index=False)
        
        return {
            'registros_originales': len(df),
            'registros_filtrados': len(df_filtrado),
            'registros_eliminados': len(df) - len(df_filtrado),
            'porcentaje_retenido': (len(df_filtrado) / len(df) * 100) if len(df) > 0 else 0
        }
        
    except Exception as e:
        print(f"Error al filtrar CSV {ruta_entrada}: {e}")
        return None


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
    Muestra menú interactivo para que el usuario seleccione índices a filtrar.
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
            return indices_seleccionados
            
        except ValueError:
            print("\n❌ ERROR: Entrada inválida. Usa números separados por comas.")


def solicitar_umbrales(indice):
    """
    Solicita al usuario los umbrales de filtrado para un índice específico.
    """
    print(f"\n{'='*80}")
    print(f"CONFIGURACIÓN DE UMBRALES PARA {indice}")
    print(f"{'='*80}")
    
    # Buscar archivo de estadísticas si existe
    archivo_stats = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                  f'estadisticas_{indice}.csv')
    
    rangos_desactivar = []
    percentiles = None
    if os.path.exists(archivo_stats):
        try:
            df_stats = pd.read_csv(archivo_stats)
            print(f"\n📊 Estadísticas disponibles de análisis previo:")
            print(f"   • Mínimo global: {df_stats['min'].min():.4f}")
            print(f"   • Máximo global: {df_stats['max'].max():.4f}")
            print(f"   • Media global: {df_stats['media'].mean():.4f}")
            print(f"   • Percentil 5: {df_stats['p05'].mean():.4f}")
            print(f"   • Percentil 95: {df_stats['p95'].mean():.4f}")

            percentiles = {
                'p05': float(df_stats['p05'].mean()),
                'p25': float(df_stats['p25'].mean()) if 'p25' in df_stats.columns else None,
                'p75': float(df_stats['p75'].mean()) if 'p75' in df_stats.columns else None,
                'p95': float(df_stats['p95'].mean())
            }

            print("\nRangos disponibles para desactivar:")
            print("  1) Valores < 0")
            print("  2) Igual a 0 (se convertirán a N/A)")
            if percentiles['p25'] is not None and percentiles['p75'] is not None:
                print(f"  3) Entre 0 y P25 (0 – {percentiles['p25']:.4f})")
                print(f"  4) Entre P25 y P75 ({percentiles['p25']:.4f} – {percentiles['p75']:.4f})")
            if percentiles['p75'] is not None and percentiles['p95'] is not None:
                print(f"  5) Entre P75 y P95 ({percentiles['p75']:.4f} – {percentiles['p95']:.4f})")
            print(f"  6) > P95 ({percentiles['p95']:.4f} – +inf)")
            sel = input("Ingresa los números de rangos a desactivar (ej: 2,3) o deja vacío para ninguno: ").strip()
            if sel:
                try:
                    rangos_desactivar = [int(x.strip()) for x in sel.split(',') if x.strip()]
                except:
                    rangos_desactivar = []
        except:
            pass
    else:
        print(f"\n⚠️  No se encontró archivo de estadísticas previas.")
        print(f"   Ejecuta 'python analizar_rangos_indices.py' primero para ver estadísticas.")
    
    print("\n" + "-"*80)
    
    while True:
        try:
            umbral_min = float(input(f"Ingresa el umbral MÍNIMO para {indice}: ").strip())
            umbral_max = float(input(f"Ingresa el umbral MÁXIMO para {indice}: ").strip())
            
            if umbral_min >= umbral_max:
                print("\n❌ ERROR: El umbral mínimo debe ser menor que el máximo.")
                continue
            
            print(f"\n✓ Umbrales configurados:")
            print(f"   • Mínimo: {umbral_min}")
            print(f"   • Máximo: {umbral_max}")
            
            confirmacion = input("\n¿Continuar con estos umbrales? (s/n): ").strip().lower()
            if confirmacion == 's':
                return umbral_min, umbral_max, rangos_desactivar, percentiles
                
        except ValueError:
            print("\n❌ ERROR: Debes ingresar valores numéricos.")


def filtrar_indice(indice, umbral_min, umbral_max, rangos_desactivar=None, percentiles=None):
    """
    Filtra un índice específico con los umbrales dados.
    """
    RUTA_ENTRADA = os.path.join(RUTA_BASE, indice)
    RUTA_SALIDA = os.path.join(RUTA_SALIDA_BASE, indice)
    
    print(f"\n{'#'*80}")
    print(f"# FILTRANDO: {indice}")
    print(f"{'#'*80}")
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]}")
    print(f"Umbrales: [{umbral_min}, {umbral_max}]")
    if rangos_desactivar:
        print(f"Rangos desactivados: {rangos_desactivar}")
    print(f"Carpeta de entrada: {RUTA_ENTRADA}")
    print(f"Carpeta de salida: {RUTA_SALIDA}\n")
    
    # Crear carpeta de salida
    os.makedirs(RUTA_SALIDA, exist_ok=True)
    
    # Buscar carpetas con fechas
    carpetas_fechas = sorted([d for d in os.listdir(RUTA_ENTRADA) 
                              if os.path.isdir(os.path.join(RUTA_ENTRADA, d))])
    
    if not carpetas_fechas:
        print(f"No se encontraron carpetas para procesar en {indice}.")
        return None
    
    print(f"Encontradas {len(carpetas_fechas)} carpetas para procesar\n")
    print("-"*80)
    
    # Lista para estadísticas
    resultados = []
    
    # Procesar cada carpeta
    for i, carpeta in enumerate(carpetas_fechas, 1):
        ruta_carpeta_entrada = os.path.join(RUTA_ENTRADA, carpeta)
        ruta_carpeta_salida = os.path.join(RUTA_SALIDA, carpeta)
        
        print(f"[{i}/{len(carpetas_fechas)}] Procesando: {carpeta}")
        
        # Crear carpeta de salida
        os.makedirs(ruta_carpeta_salida, exist_ok=True)
        
        # Buscar y procesar archivo TIFF
        archivos_tiff = [f for f in os.listdir(ruta_carpeta_entrada) 
                        if f.endswith('.tiff') or f.endswith('.tif')]
        
        if archivos_tiff:
            archivo_tiff = archivos_tiff[0]
            ruta_tiff_entrada = os.path.join(ruta_carpeta_entrada, archivo_tiff)
            ruta_tiff_salida = os.path.join(ruta_carpeta_salida, archivo_tiff)
            
            print(f"  → Filtrando TIFF: {archivo_tiff}")
            stats = filtrar_imagen_tiff(ruta_tiff_entrada, ruta_tiff_salida, 
                                        umbral_min, umbral_max, rangos_desactivar, percentiles)
            
            if stats:
                fecha = obtener_fecha_carpeta(carpeta)
                stats['fecha'] = fecha
                stats['carpeta'] = carpeta
                resultados.append(stats)
                
                print(f"     Píxeles retenidos: {stats['pixeles_filtrados']:,} de {stats['pixeles_originales']:,} "
                      f"({stats['porcentaje_retenido']:.1f}%)")
                if stats['media'] is not None:
                    print(f"     Rango filtrado: [{stats['min']:.4f}, {stats['max']:.4f}], Media: {stats['media']:.4f}")

            # Generar CSV por imagen con valores y coordenadas de pixeles retenidos
            try:
                with rasterio.open(ruta_tiff_salida) as src_out:
                    arr = src_out.read(1)
                    transform = src_out.transform
                    filas, cols = np.where(~np.isnan(arr))
                    if len(filas) > 0:
                        valores = arr[filas, cols]
                        xs = transform.c + cols * transform.a + filas * transform.b
                        ys = transform.f + cols * transform.d + filas * transform.e
                        df_img = pd.DataFrame({'x': xs, 'y': ys, indice: valores})
                        csv_img_path = os.path.join(ruta_carpeta_salida, f"pixeles_{indice}_{carpeta}.csv")
                        df_img.to_csv(csv_img_path, index=False)
                        print(f"     ✓ CSV por imagen: {csv_img_path}")
            except Exception as e:
                print(f"     ⚠️  No se pudo generar CSV por imagen: {e}")
        
        # Procesar carpeta valores_pixeles si existe y se solicita
        if CREAR_CSV_FILTRADOS:
            ruta_valores_entrada = os.path.join(ruta_carpeta_entrada, 'valores_pixeles')
            if os.path.exists(ruta_valores_entrada):
                ruta_valores_salida = os.path.join(ruta_carpeta_salida, 'valores_pixeles')
                os.makedirs(ruta_valores_salida, exist_ok=True)
                
                # Procesar CSV
                archivos_csv = [f for f in os.listdir(ruta_valores_entrada) if f.endswith('.csv')]
                if archivos_csv:
                    archivo_csv = archivos_csv[0]
                    ruta_csv_entrada = os.path.join(ruta_valores_entrada, archivo_csv)
                    ruta_csv_salida = os.path.join(ruta_valores_salida, archivo_csv)
                    
                    print(f"  → Filtrando CSV: {archivo_csv}")
                    csv_stats = filtrar_csv(ruta_csv_entrada, ruta_csv_salida, 
                                           umbral_min, umbral_max, indice, rangos_desactivar, percentiles)
                    if csv_stats:
                        print(f"     Registros retenidos: {csv_stats['registros_filtrados']:,} de "
                              f"{csv_stats['registros_originales']:,} ({csv_stats['porcentaje_retenido']:.1f}%)")
                
                # Copiar shapefiles si se solicita
                if MANTENER_METADATOS:
                    for archivo in os.listdir(ruta_valores_entrada):
                        if not archivo.endswith('.csv'):
                            shutil.copy2(
                                os.path.join(ruta_valores_entrada, archivo),
                                os.path.join(ruta_valores_salida, archivo)
                            )
        
        print()
    
    # Guardar reporte de estadísticas
    if resultados:
        df_resultados = pd.DataFrame(resultados)
        archivo_reporte = os.path.join(RUTA_SALIDA_BASE, f'reporte_filtrado_{indice}.csv')
        df_resultados.to_csv(archivo_reporte, index=False)
        
        print("="*80)
        print(f"RESUMEN DEL FILTRADO - {indice}")
        print("="*80)
        print(f"\nTotal de imágenes procesadas: {len(resultados)}")
        print(f"Píxeles totales originales: {df_resultados['pixeles_originales'].sum():,}")
        print(f"Píxeles totales filtrados: {df_resultados['pixeles_filtrados'].sum():,}")
        print(f"Píxeles totales eliminados: {df_resultados['pixeles_eliminados'].sum():,}")
        print(f"Porcentaje promedio retenido: {df_resultados['porcentaje_retenido'].mean():.2f}%")
        
        print(f"\n✓ Reporte guardado en: {archivo_reporte}")
        print(f"✓ Datos filtrados en: {RUTA_SALIDA}")
        
        return {
            'indice': indice,
            'archivo_reporte': archivo_reporte,
            'imagenes_procesadas': len(resultados),
            'porcentaje_retenido': df_resultados['porcentaje_retenido'].mean()
        }
    else:
        print(f"No se procesaron imágenes correctamente para {indice}.")
        return None


def main():
    """
    Función principal que gestiona el filtrado de múltiples índices.
    """
    print("="*80)
    print("FILTRADO DE DATOS DE ÍNDICES DE VEGETACIÓN")
    print("="*80)
    print("\nEste script filtrará los índices seleccionados según los umbrales que definas.")
    print("Se recomienda ejecutar 'analizar_rangos_indices.py' antes de filtrar.\n")
    
    # Seleccionar índices
    indices_seleccionados = seleccionar_indices()
    
    if not indices_seleccionados:
        print("\nFiltrado cancelado.")
        return
    
    # Solicitar umbrales/rangos para cada índice
    configuraciones = []
    for indice in indices_seleccionados:
        umbral_min, umbral_max, rangos_desactivar, percentiles = solicitar_umbrales(indice)
        configuraciones.append({
            'indice': indice,
            'umbral_min': umbral_min,
            'umbral_max': umbral_max,
            'rangos_desactivar': rangos_desactivar,
            'percentiles': percentiles
        })
    
    # Confirmar antes de proceder
    print("\n" + "="*80)
    print("RESUMEN DE CONFIGURACIÓN")
    print("="*80)
    print(f"\n{'Índice':<10} {'Umbral Mínimo':<20} {'Umbral Máximo':<20} {'Rangos desactivados':<25}")
    print("-"*80)
    for config in configuraciones:
        print(f"{config['indice']:<10} {config['umbral_min']:<20.4f} {config['umbral_max']:<20.4f} {str(config['rangos_desactivar'] or [])[:25]:<25}")
    
    print("\n" + "="*80)
    confirmacion = input("\n¿Deseas continuar con el filtrado? (s/n): ").strip().lower()
    if confirmacion != 's':
        print("Filtrado cancelado.")
        return
    
    # Filtrar cada índice
    resultados_filtrado = []
    
    for i, config in enumerate(configuraciones, 1):
        print(f"\n{'#'*80}")
        print(f"# PROCESANDO {i}/{len(configuraciones)}: {config['indice']}")
        print(f"{'#'*80}")
        
        resultado = filtrar_indice(config['indice'], config['umbral_min'], config['umbral_max'], config['rangos_desactivar'], config['percentiles'])
        if resultado:
            resultados_filtrado.append(resultado)
    
    # Resumen final
    print("\n" + "="*80)
    print("RESUMEN FINAL DEL FILTRADO")
    print("="*80)
    
    if resultados_filtrado:
        print(f"\n✓ Se filtraron exitosamente {len(resultados_filtrado)} índices:")
        print("\n" + "-"*80)
        print(f"{'Índice':<10} {'Imágenes':<15} {'% Retenido':<15}")
        print("-"*80)
        
        for res in resultados_filtrado:
            print(f"{res['indice']:<10} {res['imagenes_procesadas']:<15} {res['porcentaje_retenido']:<15.2f}%")
        
        print("\n" + "-"*80)
        print("\nArchivos generados:")
        for res in resultados_filtrado:
            print(f"  • {res['archivo_reporte']}")
        
        print(f"\n✓ Datos filtrados guardados en: {RUTA_SALIDA_BASE}")
        
        print("\n" + "="*80)
        print("FILTRADO COMPLETADO")
        print("="*80)
    else:
        print("\n❌ No se pudo filtrar ningún índice.")
    
    print("\n" + "="*80)


if __name__ == "__main__":
    main()
