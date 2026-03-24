"""
GENERADOR DE GUÍAS DE INTERPRETACIÓN DE COLORES

Genera archivos TXT explicativos para TODOS los índices de vegetación,
explicando qué significa cada color en las visualizaciones espaciales.

Ejecutar: python scripts/generar_guias_colores.py
"""

import sys
from pathlib import Path
from datetime import datetime

# Agregar rutas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configuracion.config import (
    RUTA_REPORTES,
    INDICES_INFO,
    obtener_indices_disponibles
)


def generar_guia_colores_indice(indice, carpeta_salida):
    """
    Genera un archivo TXT completo que explica los colores para un índice específico.
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    archivo_txt = carpeta_salida / f"GUIA_COLORES_{indice}.txt"
    
    # Obtener rangos específicos según el índice
    if indice == 'NDVI':
        rangos = [
            ("< 0", "Agua, nubes o sombras"),
            ("0 - 0.2", "Suelo desnudo, rocas o áreas urbanas"),
            ("0.2 - 0.4", "Vegetación dispersa o con estrés severo"),
            ("0.4 - 0.6", "Vegetación moderada (cultivos en crecimiento)"),
            ("0.6 - 0.8", "Vegetación densa y saludable"),
            ("> 0.8", "Vegetación muy densa (bosques, cultivos maduros)")
        ]
    elif indice == 'NDMI':
        rangos = [
            ("< -0.3", "Vegetación muy seca o suelo"),
            ("-0.3 - 0", "Bajo contenido de humedad (estrés hídrico)"),
            ("0 - 0.2", "Contenido de humedad moderado"),
            ("0.2 - 0.4", "Buen contenido de humedad"),
            ("> 0.4", "Alto contenido de humedad")
        ]
    elif indice == 'NDRE':
        rangos = [
            ("< 0.1", "Sin vegetación o vegetación muerta"),
            ("0.1 - 0.2", "Vegetación con muy bajo contenido de clorofila"),
            ("0.2 - 0.3", "Vegetación con contenido moderado de clorofila"),
            ("0.3 - 0.5", "Vegetación saludable"),
            ("> 0.5", "Vegetación muy saludable, alta clorofila")
        ]
    elif indice == 'MSAVI':
        rangos = [
            ("< 0.1", "Suelo desnudo"),
            ("0.1 - 0.25", "Vegetación muy escasa"),
            ("0.25 - 0.4", "Vegetación dispersa"),
            ("0.4 - 0.6", "Vegetación moderada"),
            ("> 0.6", "Vegetación densa")
        ]
    elif indice == 'RECI':
        rangos = [
            ("< 0.5", "Muy bajo contenido de clorofila"),
            ("0.5 - 1.0", "Bajo contenido de clorofila"),
            ("1.0 - 2.0", "Contenido moderado de clorofila"),
            ("2.0 - 3.0", "Alto contenido de clorofila"),
            ("> 3.0", "Muy alto contenido de clorofila")
        ]
    else:
        rangos = [
            ("< 0.2", "Valor muy bajo"),
            ("0.2 - 0.4", "Valor bajo"),
            ("0.4 - 0.6", "Valor moderado"),
            ("0.6 - 0.8", "Valor alto"),
            ("> 0.8", "Valor muy alto")
        ]
    
    contenido = f"""
================================================================================
          GUÍA COMPLETA DE INTERPRETACIÓN DE COLORES
================================================================================

  ÍNDICE: {indice}
  NOMBRE: {INDICES_INFO[indice]['nombre']}
  
  DESCRIPCIÓN:
  {INDICES_INFO[indice]['descripcion']}

================================================================================
  Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
================================================================================


Esta guía explica cómo interpretar los colores en TODAS las visualizaciones
generadas para el índice {indice}. Úsela como referencia rápida.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    1. MAPA DE CALOR ESPACIAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos: mapa_calor_{indice}_*.png

PALETA DE COLORES (degradado marrón → amarillo → verde):

"""
    
    # Agregar rangos específicos del índice
    contenido += f"  {'VALOR':<15} {'SIGNIFICADO':<50}\n"
    contenido += f"  {'─'*15} {'─'*50}\n"
    for rango, significado in rangos:
        contenido += f"  {rango:<15} {significado}\n"
    
    contenido += f"""

COLORES EN EL MAPA:
  🟤 MARRÓN OSCURO  →  Valores más bajos (vegetación escasa/suelo)
  🟤 MARRÓN CLARO   →  Valores bajos
  🟡 AMARILLO       →  Valores medios (transición)
  🟢 VERDE CLARO    →  Valores moderados-altos
  🟢 VERDE OSCURO   →  Valores más altos (vegetación saludable)

¿QUÉ BUSCAR?
  • Zonas uniformes del mismo color = áreas homogéneas
  • Gradientes de color = transiciones entre tipos de cobertura
  • Manchas aisladas = posibles anomalías a investigar


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    2. MAPA DE HOTSPOTS Y COLDSPOTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos: hotspots_{indice}_*.png

Este mapa identifica zonas ESTADÍSTICAMENTE DIFERENTES al promedio:

  COLOR         NOMBRE      QUÉ SIGNIFICA
  ─────────────────────────────────────────────────────────────────────────
  🟠 NARANJA    HOTSPOT     Valores EXCEPCIONALMENTE ALTOS
                            • Vegetación inusualmente saludable
                            • Posiblemente: mejor riego, microclima favorable
                            • ACCIÓN: Investigar qué hace diferente esta zona
  
  🔵 AZUL      COLDSPOT    Valores EXCEPCIONALMENTE BAJOS  ⚠️ ATENCIÓN
                            • Vegetación con problemas potenciales
                            • Posiblemente: estrés, enfermedad, plagas, daño
                            • ACCIÓN: Inspección prioritaria en campo
  
  ⬜ GRIS      NORMAL       Valores dentro del rango esperado
                            • Sin anomalías estadísticas
                            • Comportamiento típico para el área

MÉTODO DE DETECCIÓN:
  Se identifican píxeles fuera de 2 desviaciones estándar del promedio.
  Esto significa que son estadísticamente inusuales (< 5% de probabilidad).


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    3. MAPA DE SEGMENTACIÓN (CLUSTERING K-MEANS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos: clustering_{indice}_*.png

⚠️  IMPORTANTE: En este mapa, los colores NO indican calidad directamente.
    Los colores identifican GRUPOS de zonas con valores similares.

COLORES USADOS:
  🔴 ROJO      →  Zona/Grupo 1
  🟠 NARANJA   →  Zona/Grupo 2
  🟡 AMARILLO  →  Zona/Grupo 3
  🟢 VERDE     →  Zona/Grupo 4
  🔵 AZUL      →  Zona/Grupo 5

CÓMO INTERPRETAR CORRECTAMENTE:

  1. Cada color representa un GRUPO de píxeles similares entre sí
  2. Para saber qué significa cada grupo, debe revisar el archivo CSV:
     → clustering_{indice}_*.csv
  3. En el CSV encontrará el VALOR MEDIO de cada zona
  4. Ordene los grupos por valor medio para entender cuál es mejor/peor

EJEMPLO PRÁCTICO:
  Si el CSV muestra:
    Zona 1 (Rojo):    media = 0.28  → Vegetación escasa
    Zona 2 (Naranja): media = 0.41  → Vegetación moderada-baja
    Zona 3 (Amarillo): media = 0.52 → Vegetación moderada
    Zona 4 (Verde):   media = 0.65  → Vegetación saludable
    Zona 5 (Azul):    media = 0.78  → Vegetación muy saludable

  → En este caso, AZUL = mejor vegetación, ROJO = peor vegetación
  → Pero esto puede cambiar en otro análisis


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    4. MAPA DE DIFERENCIAS TEMPORALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos: diferencia_{indice}_*.png

Muestra CAMBIOS entre dos fechas consecutivas:

  COLOR              CAMBIO              QUÉ SIGNIFICA
  ─────────────────────────────────────────────────────────────────────────
  🔴 ROJO OSCURO    Muy negativo        Deterioro severo de vegetación
                                        • Pérdida significativa
                                        • Posible: cosecha, incendio, sequía
  
  🔴 ROJO CLARO    Ligeramente neg.     Disminución leve
                                        • Defoliación normal o estrés leve
  
  ⬜ BLANCO/GRIS   Sin cambio           Área estable
                                        • Condiciones mantenidas
  
  🟢 VERDE CLARO   Ligeramente pos.     Mejora leve
                                        • Crecimiento gradual
  
  🟢 VERDE OSCURO  Muy positivo         Mejora significativa
                                        • Recuperación o crecimiento rápido
                                        • Posible: lluvias, fertilización


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    5. MAPA DE PREDICCIÓN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Archivos: {indice}_prediccion_*.png

Proyección de cambios FUTUROS basada en patrones históricos:

  COLOR              PREDICCIÓN          ACCIÓN RECOMENDADA
  ─────────────────────────────────────────────────────────────────────────
  🔴 ROJO OSCURO    Empeorará mucho     ⚠️ Planificar intervención urgente
                    (< -5%)
  
  🔴 ROJO          Empeorará            Monitorear de cerca
                    (-2% a -5%)
  
  🟡 AMARILLO      Estable              Mantener prácticas actuales
                    (-2% a +2%)
  
  🟢 VERDE         Mejorará             Condiciones favorables
                    (+2% a +5%)
  
  🟢 VERDE OSCURO  Mejorará mucho       Ninguna acción necesaria
                    (> +5%)

NOTA: Las predicciones tienen incertidumbre. Use como guía, no como certeza.


================================================================================
                         RESUMEN RÁPIDO
================================================================================

  MAPA           COLORES                    SIGNIFICADO
  ──────────────────────────────────────────────────────────────────────────
  Calor          Marrón→Amarillo→Verde      Bajo→Medio→Alto valor de {indice}
  Hotspots       Naranja/Azul/Gris          Alto/Bajo/Normal (anomalías)
  Clustering     Rojo/Naranja/Amarillo/     Grupos (ver CSV para valores)
                 Verde/Azul
  Diferencias    Rojo→Blanco→Verde          Empeoró→Igual→Mejoró
  Predicción     Rojo→Amarillo→Verde        Empeorará→Estable→Mejorará


================================================================================
Para más detalles, consulte los archivos CSV en la carpeta de reportes.
================================================================================
"""
    
    # Guardar archivo
    with open(archivo_txt, 'w', encoding='utf-8') as f:
        f.write(contenido)
    
    return archivo_txt


def generar_todas_las_guias():
    """
    Genera guías de colores para TODOS los índices disponibles.
    """
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║           GENERADOR DE GUÍAS DE INTERPRETACIÓN DE COLORES                 ║
║                                                                           ║
║  Crea archivos TXT explicativos para cada índice de vegetación           ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Obtener índices disponibles
    indices = obtener_indices_disponibles()
    
    if not indices:
        print("No se encontraron índices con datos.")
        return []
    
    print(f"Índices detectados: {', '.join(indices)}\n")
    
    # Carpeta de salida
    carpeta_guias = RUTA_REPORTES / "GUIAS_INTERPRETACION"
    carpeta_guias.mkdir(exist_ok=True, parents=True)
    
    archivos_creados = []
    
    for indice in indices:
        print(f"Generando guía para {indice}...", end=" ")
        try:
            archivo = generar_guia_colores_indice(indice, carpeta_guias)
            archivos_creados.append(archivo)
            print(f"✓ {archivo.name}")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print(f"\n{'='*80}")
    print(f"✓ Generadas {len(archivos_creados)} guías de interpretación")
    print(f"  Ubicación: {carpeta_guias}")
    print(f"{'='*80}")
    
    return archivos_creados


if __name__ == "__main__":
    generar_todas_las_guias()
