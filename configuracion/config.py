"""
Configuración centralizada del proyecto de análisis de tesis.
Todas las rutas, parámetros y constantes se definen aquí.
"""

import os
from pathlib import Path

# ============================================================================
# RUTAS BASE DEL PROYECTO
# ============================================================================

# Ruta base del proyecto de análisis
RUTA_PROYECTO = Path(__file__).parent.parent.absolute()

# Ruta de datos de entrada (desde Tesis_DESCARGAS)
NOMBRE_CARPETA_DESCARGAS = "UPIITA_contours_25nov.2025"
RUTA_DESCARGAS = RUTA_PROYECTO.parent / "Tesis_DESCARGAS" / "descargas" / NOMBRE_CARPETA_DESCARGAS

# Ruta del shapefile para enmascaramiento
RUTA_SHAPEFILE = RUTA_PROYECTO.parent / "Tesis_DESCARGAS" / "shapefiles" / "UPIITA_contours_25nov.2025" / "UPIITA_contours_25Nov2025.shp"

# ============================================================================
# RUTAS DE SALIDA
# ============================================================================

# NOTA: Todas las salidas se guardan en una carpeta "resultados" para mantener orden
RUTA_RESULTADOS = RUTA_PROYECTO / "resultados"

RUTA_REPORTES = RUTA_RESULTADOS / "reportes"
RUTA_VISUALIZACIONES = RUTA_RESULTADOS / "visualizaciones"
RUTA_DATOS_PROCESADOS = RUTA_RESULTADOS / "datos_procesados"
RUTA_REPORTES_PDF = RUTA_RESULTADOS / "reportes_pdf"

# Crear carpetas si no existen
for ruta in [RUTA_REPORTES, RUTA_VISUALIZACIONES, RUTA_DATOS_PROCESADOS, RUTA_REPORTES_PDF]:
    ruta.mkdir(exist_ok=True, parents=True)

# ============================================================================
# ÍNDICES DE VEGETACIÓN DISPONIBLES
# ============================================================================

INDICES_INFO = {
    "NDVI": {
        "nombre": "Normalized Difference Vegetation Index",
        "descripcion": "Índice de Vegetación Normalizado",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "< 0": "Agua, nubes, nieve",
            "0-0.2": "Suelo desnudo, rocas, construcciones",
            "0.2-0.5": "Vegetación escasa o estresada",
            "0.5-0.8": "Vegetación moderada a densa",
            "> 0.8": "Vegetación muy densa y saludable"
        }
    },
    "NDRE": {
        "nombre": "Normalized Difference Red Edge",
        "descripcion": "Red Edge Normalizado",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Bajo contenido de clorofila",
            "alto": "Alto contenido de clorofila, detecta estrés temprano"
        }
    },
    "MSAVI": {
        "nombre": "Modified Soil-Adjusted Vegetation Index",
        "descripcion": "Índice Ajustado de Vegetación",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Poca cobertura vegetal",
            "alto": "Mayor cobertura vegetal, minimiza efecto del suelo"
        }
    },
    "RECI": {
        "nombre": "Red Edge Chlorophyll Index",
        "descripcion": "Índice de Clorofila Red Edge",
        "rango_teorico": (0, 20),
        "interpretacion": {
            "0-5": "Bajo contenido de clorofila",
            "5-10": "Contenido moderado de clorofila",
            "> 10": "Alto contenido de clorofila"
        }
    },
    "NDMI": {
        "nombre": "Normalized Difference Moisture Index",
        "descripcion": "Índice de Humedad",
        "rango_teorico": (-1, 1),
        "interpretacion": {
            "bajo": "Baja humedad, estrés hídrico",
            "alto": "Alta humedad en vegetación"
        }
    }
}

# ============================================================================
# PARÁMETROS DE ANÁLISIS
# ============================================================================

# Parámetros de filtrado
PERCENTILES_DEFAULT = [1, 5, 25, 50, 75, 95, 99]

# Valores inválidos a considerar como NaN
VALORES_INVALIDOS = [0, -9999, -3.40282e+38]  # Común en datos satelitales

# Parámetros de visualización
DPI_GRAFICAS = 150
FIGSIZE_DEFAULT = (12, 6)
FIGSIZE_GRANDE = (14, 8)

# Parámetros de clustering
N_CLUSTERS_DEFAULT = 5

# Parámetros de análisis temporal
VENTANA_TEMPORAL_DIAS = 7  # Para cálculo de velocidad de cambio

# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

NIVEL_LOG = "INFO"  # DEBUG, INFO, WARNING, ERROR

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================

def validar_configuracion():
    """
    Valida que las rutas principales existan.
    """
    errores = []
    
    if not RUTA_DESCARGAS.exists():
        errores.append(f"No se encontró carpeta de descargas: {RUTA_DESCARGAS}")
    
    if not RUTA_SHAPEFILE.exists():
        errores.append(f"No se encontró shapefile: {RUTA_SHAPEFILE}")
    
    return errores


def obtener_ruta_indice(indice):
    """
    Retorna la ruta completa de un índice específico.
    """
    return RUTA_DESCARGAS / indice


def obtener_indices_disponibles():
    """
    Retorna lista de índices que tienen datos disponibles.
    """
    if not RUTA_DESCARGAS.exists():
        return []
    
    indices_disponibles = []
    for item in RUTA_DESCARGAS.iterdir():
        if item.is_dir() and item.name in INDICES_INFO:
            # Verificar que tenga carpetas de fechas
            carpetas = [d for d in item.iterdir() if d.is_dir()]
            if carpetas:
                indices_disponibles.append(item.name)
    
    return sorted(indices_disponibles)


if __name__ == "__main__":
    # Validar configuración al ejecutar este archivo
    print("="*80)
    print("VALIDACIÓN DE CONFIGURACIÓN")
    print("="*80)
    
    print(f"\nRuta del proyecto: {RUTA_PROYECTO}")
    print(f"Ruta de descargas: {RUTA_DESCARGAS}")
    print(f"Ruta de shapefile: {RUTA_SHAPEFILE}")
    
    errores = validar_configuracion()
    
    if errores:
        print("\nERRORES ENCONTRADOS:")
        for error in errores:
            print(f"  • {error}")
    else:
        print("\nConfiguración válida")
        
        indices = obtener_indices_disponibles()
        if indices:
            print(f"\nÍndices disponibles: {', '.join(indices)}")
        else:
            print("\nADVERTENCIA: No se encontraron índices con datos")
