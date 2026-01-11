"""
Módulo de procesamiento base para imágenes satelitales.
Incluye funciones para cargar, enmascarar y limpiar datos.
"""

import numpy as np
import rasterio
from rasterio.mask import mask as rasterio_mask
import geopandas as gpd
from datetime import datetime
from pathlib import Path
import warnings

# Importar configuración
import sys
sys.path.append(str(Path(__file__).parent.parent))
from configuracion.config import VALORES_INVALIDOS, RUTA_SHAPEFILE


# ============================================================================
# FUNCIONES DE CARGA DE IMÁGENES
# ============================================================================

def cargar_imagen(ruta_tiff, retornar_metadata=False):
    """
    Carga una imagen TIFF sin aplicar enmascaramiento.
    
    Args:
        ruta_tiff (str o Path): Ruta al archivo TIFF
        retornar_metadata (bool): Si True, retorna también metadata
    
    Returns:
        numpy.ndarray: Datos de la imagen
        dict (opcional): Metadata si retornar_metadata=True
    """
    try:
        with rasterio.open(ruta_tiff) as src:
            datos = src.read(1)  # Lee la primera banda
            
            if retornar_metadata:
                metadata = {
                    'transform': src.transform,
                    'crs': src.crs,
                    'bounds': src.bounds,
                    'shape': datos.shape,
                    'dtype': datos.dtype
                }
                return datos, metadata
            
            return datos
            
    except Exception as e:
        raise IOError(f"Error al leer imagen {ruta_tiff}: {e}")


def cargar_csv_pixeles(ruta_csv, filtrar_ceros=True, filtrar_shapefile=False, ruta_shapefile=None):
    """
    Carga archivo CSV con valores de píxeles.
    
    NOTA: Los CSVs tienen formato: longitude, latitude, INDICE
    Los valores en 0 generalmente están fuera del polígono de interés.
    
    Args:
        ruta_csv (str o Path): Ruta al archivo CSV de píxeles
        filtrar_ceros (bool): Si True, elimina píxeles con valor = 0
        filtrar_shapefile (bool): Si True, filtra usando shapefile (más lento)
        ruta_shapefile (str o Path): Ruta al shapefile para filtrado espacial
    
    Returns:
        pandas.DataFrame: DataFrame con columnas [longitude, latitude, valor]
    """
    try:
        import pandas as pd
        df = pd.read_csv(ruta_csv)
        
        # Renombrar última columna a 'valor' para facilitar uso
        if len(df.columns) == 3:
            df.columns = ['longitude', 'latitude', 'valor']
        
        # FILTRADO 1: Eliminar valores en cero (fuera del área o inválidos)
        if filtrar_ceros:
            n_original = len(df)
            df = df[df['valor'] != 0].copy()
            n_filtrado = len(df)
            if n_filtrado < n_original:
                # Silencioso, solo filtra
                pass
        
        # FILTRADO 2: Verificar que estén dentro del shapefile (opcional)
        if filtrar_shapefile and ruta_shapefile:
            import geopandas as gpd
            from shapely.geometry import Point
            
            # Cargar shapefile
            gdf = gpd.read_file(ruta_shapefile)
            
            # Crear geometrías de puntos
            geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
            gdf_puntos = gpd.GeoDataFrame(df, geometry=geometry, crs=gdf.crs)
            
            # Filtrar puntos dentro del polígono
            df = gpd.sjoin(gdf_puntos, gdf, predicate='within', how='inner')
            df = df[['longitude', 'latitude', 'valor']].copy()
        
        return df
        
    except Exception as e:
        raise IOError(f"Error al leer CSV {ruta_csv}: {e}")


def cargar_datos_optimizado(info_imagen, usar_csv=True, filtrar_ceros=True):
    """
    Carga datos de forma optimizada: primero intenta CSV, si no existe usa TIFF.
    
    NOTA: Esta función hace el análisis 10-50x más rápido usando CSVs cuando están disponibles.
    Los CSVs ya tienen píxeles filtrados y enmascarados, evitando procesamiento pesado.
    
    Args:
        info_imagen (dict): Diccionario de listar_imagenes_indice con 'ruta' y 'csv_pixeles'
        usar_csv (bool): Si True, intenta usar CSV primero
        filtrar_ceros (bool): Si True, elimina valores = 0 del CSV
    
    Returns:
        numpy.ndarray: Array de valores del índice (solo píxeles válidos)
        str: Fuente de datos ('csv' o 'tiff')
    """
    # Intentar usar CSV si está disponible
    if usar_csv and info_imagen.get('csv_pixeles') and info_imagen['csv_pixeles'].exists():
        try:
            df = cargar_csv_pixeles(info_imagen['csv_pixeles'], filtrar_ceros=filtrar_ceros)
            # Retornar solo valores como array numpy
            valores = df['valor'].values
            return valores, 'csv'
        except Exception as e:
            warnings.warn(f"Error al leer CSV, usando TIFF: {e}")
    
    # Fallback a TIFF
    datos = cargar_imagen_enmascarada(info_imagen['ruta'])
    # Filtrar solo valores válidos (no NaN)
    valores = datos[~np.isnan(datos)]
    return valores, 'tiff'


def cargar_imagen(ruta_tiff, retornar_metadata=False):
    """
    Carga una imagen TIFF sin aplicar enmascaramiento.
    
    Args:
        ruta_tiff (str o Path): Ruta al archivo TIFF
        retornar_metadata (bool): Si True, retorna también metadata
    
    Returns:
        numpy.ndarray: Datos de la imagen
        dict (opcional): Metadata si retornar_metadata=True
    """
    try:
        with rasterio.open(ruta_tiff) as src:
            datos = src.read(1)  # Lee la primera banda
            
            if retornar_metadata:
                metadata = {
                    'transform': src.transform,
                    'crs': src.crs,
                    'bounds': src.bounds,
                    'shape': datos.shape,
                    'dtype': datos.dtype
                }
                return datos, metadata
            
            return datos
            
    except Exception as e:
        raise IOError(f"Error al leer imagen {ruta_tiff}: {e}")


def cargar_imagen_enmascarada(ruta_tiff, ruta_shapefile=None, retornar_metadata=False):
    """
    Carga imagen TIFF y aplica máscara del shapefile.
    Píxeles fuera del polígono se convierten a NaN.
    
    NOTA: Esta función es CLAVE para todo el análisis.
    Tuve que probar varias formas de hacer el enmascaramiento hasta que funcionó bien.
    
    Args:
        ruta_tiff (str o Path): Ruta al archivo TIFF
        ruta_shapefile (str o Path): Ruta al shapefile. Si None, usa el de config
        retornar_metadata (bool): Si True, retorna también metadata
    
    Returns:
        numpy.ndarray: Datos enmascarados (píxeles fuera = NaN)
        dict (opcional): Metadata si retornar_metadata=True
    """
    try:
        # Usar shapefile de configuración si no se especifica
        if ruta_shapefile is None:
            ruta_shapefile = RUTA_SHAPEFILE
        
        # Cargar shapefile
        gdf = gpd.read_file(ruta_shapefile)
        
        with rasterio.open(ruta_tiff) as src:
            # Reproyectar geometría al CRS de la imagen si es necesario
            if gdf.crs != src.crs:
                gdf = gdf.to_crs(src.crs)
            
            # Aplicar máscara
            datos_enmascarados, transform = rasterio_mask(
                src, 
                gdf.geometry, 
                crop=False,  # No recortar, mantener dimensiones originales
                nodata=np.nan,  # Píxeles fuera = NaN
                all_touched=False  # Solo píxeles completamente dentro
            )
            
            datos = datos_enmascarados[0]  # Primera banda
            
            # Limpiar datos
            datos = limpiar_datos(datos)
            
            if retornar_metadata:
                metadata = {
                    'transform': transform,
                    'crs': src.crs,
                    'bounds': src.bounds,
                    'shape': datos.shape,
                    'dtype': datos.dtype,
                    'shapefile_usado': str(ruta_shapefile)
                }
                return datos, metadata
            
            return datos
            
    except Exception as e:
        raise IOError(f"Error al cargar imagen enmascarada {ruta_tiff}: {e}")


def limpiar_datos(datos, valores_invalidos=None):
    """
    Limpia datos convirtiendo valores inválidos a NaN.
    
    # DUDA RESUELTA: Al principio no sabía si usar -9999 o np.nan para valores inválidos.
    # Después de investigar, np.nan es mejor porque no afecta los cálculos estadísticos.
    
    Args:
        datos (numpy.ndarray): Array de datos
        valores_invalidos (list): Lista de valores a considerar inválidos
    
    Returns:
        numpy.ndarray: Datos limpios con NaN en valores inválidos
    """
    if valores_invalidos is None:
        valores_invalidos = VALORES_INVALIDOS
    
    datos = datos.astype(float)
    
    # Convertir valores inválidos a NaN
    for valor in valores_invalidos:
        datos[datos == valor] = np.nan
    
    # Convertir inf a NaN
    datos[np.isinf(datos)] = np.nan
    
    return datos


# ============================================================================
# FUNCIONES DE EXTRACCIÓN DE INFORMACIÓN
# ============================================================================

def obtener_fecha_carpeta(nombre_carpeta):
    """
    Extrae fecha del nombre de carpeta.
    
    Formato esperado: UPIITA_contours_25nov.2025_YYYYMMDD_...
    
    Args:
        nombre_carpeta (str o Path): Nombre de la carpeta
    
    Returns:
        datetime: Objeto datetime con la fecha
        None: Si no se puede extraer la fecha
    """
    try:
        nombre = Path(nombre_carpeta).name
        partes = nombre.split('_')
        
        for parte in partes:
            if len(parte) == 8 and parte.isdigit():
                fecha = datetime.strptime(parte, '%Y%m%d')
                return fecha
                
    except Exception:
        pass
    
    return None


def obtener_fecha_str(nombre_carpeta, formato='%Y-%m-%d'):
    """
    Extrae fecha del nombre de carpeta y la retorna como string.
    
    Args:
        nombre_carpeta (str o Path): Nombre de la carpeta
        formato (str): Formato de salida de la fecha
    
    Returns:
        str: Fecha formateada
        None: Si no se puede extraer la fecha
    """
    fecha = obtener_fecha_carpeta(nombre_carpeta)
    if fecha:
        return fecha.strftime(formato)
    return None


def extraer_coordenadas(datos, transform):
    """
    Extrae coordenadas (x, y) de píxeles válidos.
    
    Args:
        datos (numpy.ndarray): Array de datos
        transform (rasterio.transform): Transform de la imagen
    
    Returns:
        tuple: (coordenadas_x, coordenadas_y, valores)
    """
    # Encontrar índices de píxeles válidos
    filas, cols = np.where(~np.isnan(datos))
    
    if len(filas) == 0:
        return np.array([]), np.array([]), np.array([])
    
    # Convertir índices a coordenadas geográficas
    xs = transform.c + cols * transform.a + filas * transform.b
    ys = transform.f + cols * transform.d + filas * transform.e
    
    # Valores de píxeles
    valores = datos[filas, cols]
    
    return xs, ys, valores


# ============================================================================
# FUNCIONES DE INFORMACIÓN Y VALIDACIÓN
# ============================================================================

def obtener_info_imagen(ruta_tiff):
    """
    Obtiene información completa de una imagen TIFF.
    
    Args:
        ruta_tiff (str o Path): Ruta al archivo TIFF
    
    Returns:
        dict: Información de la imagen
    """
    try:
        with rasterio.open(ruta_tiff) as src:
            return {
                'ruta': str(ruta_tiff),
                'ancho': src.width,
                'alto': src.height,
                'bandas': src.count,
                'dtype': src.dtypes[0],
                'crs': str(src.crs),
                'bounds': src.bounds,
                'transform': src.transform,
                'nodata': src.nodata
            }
    except Exception as e:
        return {'error': str(e)}


def contar_pixeles_validos(datos):
    """
    Cuenta píxeles válidos (no NaN, no inf).
    
    Args:
        datos (numpy.ndarray): Array de datos
    
    Returns:
        dict: Estadísticas de píxeles
    """
    total = datos.size
    validos = np.sum(~np.isnan(datos) & ~np.isinf(datos))
    invalidos = total - validos
    
    return {
        'total': total,
        'validos': int(validos),
        'invalidos': int(invalidos),
        'porcentaje_validos': (validos / total * 100) if total > 0 else 0
    }


def validar_enmascaramiento(ruta_tiff, ruta_shapefile=None):
    """
    Valida calidad del enmascaramiento de una imagen.
    
    Args:
        ruta_tiff (str o Path): Ruta al archivo TIFF
        ruta_shapefile (str o Path): Ruta al shapefile
    
    Returns:
        dict: Reporte de validación
    """
    try:
        # Cargar imagen sin máscara
        datos_originales = cargar_imagen(ruta_tiff)
        info_original = contar_pixeles_validos(datos_originales)
        
        # Cargar imagen con máscara
        datos_enmascarados = cargar_imagen_enmascarada(ruta_tiff, ruta_shapefile)
        info_enmascarada = contar_pixeles_validos(datos_enmascarados)
        
        # Calcular estadísticas
        pixeles_dentro_poligono = info_enmascarada['validos']
        pixeles_fuera_poligono = info_original['validos'] - info_enmascarada['validos']
        
        return {
            'archivo': Path(ruta_tiff).name,
            'total_pixeles': info_original['total'],
            'pixeles_originales_validos': info_original['validos'],
            'pixeles_dentro_poligono': pixeles_dentro_poligono,
            'pixeles_fuera_poligono': pixeles_fuera_poligono,
            'porcentaje_dentro_poligono': (pixeles_dentro_poligono / info_original['total'] * 100) if info_original['total'] > 0 else 0,
            'calidad': 'BUENA' if pixeles_dentro_poligono > 0 else 'SIN DATOS'
        }
        
    except Exception as e:
        return {
            'archivo': Path(ruta_tiff).name,
            'error': str(e),
            'calidad': 'ERROR'
        }


# ============================================================================
# FUNCIONES PARA BATCH PROCESSING
# ============================================================================

def listar_imagenes_indice(ruta_indice):
    """
    Lista todas las imágenes TIFF de un índice junto con archivos CSV de píxeles.
    
    Args:
        ruta_indice (str o Path): Ruta de la carpeta del índice
    
    Returns:
        list: Lista de diccionarios con información de cada imagen
    """
    ruta_indice = Path(ruta_indice)
    imagenes = []
    
    if not ruta_indice.exists():
        return imagenes
    
    # Recorrer carpetas de fechas
    for carpeta_fecha in sorted(ruta_indice.iterdir()):
        if not carpeta_fecha.is_dir():
            continue
        
        # Buscar archivos TIFF
        archivos_tiff = list(carpeta_fecha.glob('*.tif')) + list(carpeta_fecha.glob('*.tiff'))
        
        for archivo_tiff in archivos_tiff:
            fecha = obtener_fecha_carpeta(carpeta_fecha.name)
            
            # NOTA: Agregar ruta del CSV de píxeles si existe
            carpeta_pixeles = carpeta_fecha / "valores_pixeles"
            archivo_csv = None
            if carpeta_pixeles.exists():
                archivos_csv = list(carpeta_pixeles.glob('*.csv'))
                if archivos_csv:
                    archivo_csv = archivos_csv[0]  # Tomar el primer CSV encontrado
            
            imagenes.append({
                'ruta': archivo_tiff,
                'carpeta': carpeta_fecha.name,
                'fecha': fecha,
                'fecha_str': fecha.strftime('%Y-%m-%d') if fecha else None,
                'nombre_archivo': archivo_tiff.name,
                'csv_pixeles': archivo_csv  # Nueva propiedad
            })
    
    return imagenes


if __name__ == "__main__":
    # Prueba básica del módulo
    print("="*80)
    print("MÓDULO PROCESADOR_BASE - PRUEBA")
    print("="*80)
    
    print("\nValidando shapefile...")
    if RUTA_SHAPEFILE.exists():
        print(f"✓ Shapefile encontrado: {RUTA_SHAPEFILE}")
        
        # Leer shapefile
        gdf = gpd.read_file(RUTA_SHAPEFILE)
        print(f"  • CRS: {gdf.crs}")
        print(f"  • Geometrías: {len(gdf)}")
        print(f"  • Área total: {gdf.geometry.area.sum():.2f} unidades²")
    else:
        print(f"✗ Shapefile no encontrado: {RUTA_SHAPEFILE}")
