"""
Sistema Integrado de Análisis de Índices de Vegetación

Menú principal unificado para acceder a todos los análisis:
- Validación de datos
- Análisis exploratorio
- Análisis temporal
- Análisis espacial
- Segmentación de zonas

Autor: Sistema de Análisis de Tesis
Fecha: Enero 2026
"""

import sys
from pathlib import Path
import subprocess

# Agregar rutas
sys.path.append(str(Path(__file__).parent))

from configuracion.config import (
    obtener_indices_disponibles,
    INDICES_INFO
)


def mostrar_banner():
    """Muestra el banner del sistema."""
    print("""
================================================================================
    SISTEMA DE ANALISIS DE INDICES DE VEGETACION
    Trabajo de Tesis - UPIITA
    
    Analisis Temporal, Espacial y Predicciones
================================================================================
    """)


def mostrar_resumen_datos():
    """Muestra resumen de datos disponibles."""
    print("\n" + "="*80)
    print("DATOS DISPONIBLES")
    print("="*80)
    
    indices = obtener_indices_disponibles()
    
    if indices:
        print(f"\nIndices encontrados: {len(indices)}")
        for indice in indices:
            print(f"  - {indice:<8} {INDICES_INFO[indice]['nombre']}")
    else:
        print("\nNo se encontraron datos")
    
    return indices


def ejecutar_script(ruta_script):
    """Ejecuta un script de Python."""
    try:
        # Agregar variable de entorno para modo automático
        import os
        env = os.environ.copy()
        env['ANALISIS_AUTOMATICO'] = '1'
        
        resultado = subprocess.run(
            [sys.executable, str(ruta_script)],
            cwd=Path(__file__).parent,  # Ejecutar desde la raíz del proyecto, no desde scripts/
            capture_output=False,
            env=env
        )
        return resultado.returncode == 0
    except Exception as e:
        print(f"\n❌ Error al ejecutar script: {e}")
        return False


def ejecutar_analisis_completo(scripts_dir):
    """Ejecuta todos los análisis en secuencia."""
    print("""
================================================================================
    ANALISIS COMPLETO AUTOMATICO
================================================================================

Se ejecutaran todos los analisis en el siguiente orden:

  1. Validacion de Datos
  2. Analisis Exploratorio
  3. Analisis Temporal
  4. Analisis Espacial
  5. Segmentacion de Zonas
  6. Predicciones Futuras (Deep Learning)
  7. Generacion de Reportes PDF

ADVERTENCIA: Esto puede tomar 15-25 minutos

================================================================================
    """)
    
    confirmacion = input("Deseas continuar? (S/N): ").strip().upper()
    
    if confirmacion != 'S':
        print("\nAnalisis completo cancelado")
        return
    
    import time
    
    analisis = [
        ("[1] Validacion de Datos", "scripts/00_validacion_datos.py"),
        ("[2] Analisis Exploratorio", "scripts/01_analisis_exploratorio.py"),
        ("[3] Analisis Temporal", "scripts/03_analisis_temporal.py"),
        ("[4] Analisis Espacial", "scripts/02_analisis_espacial.py"),
        ("[5] Segmentacion de Zonas", "scripts/04_segmentacion_zonas.py"),
        ("[6] Predicciones Futuras (Deep Learning)", "scripts/05_predicciones_futuras.py"),
        ("[7] Generacion de PDFs", "scripts/99_generar_reporte_pdf.py")
    ]
    
    resultados = []
    tiempo_inicio = time.time()
    
    print("\n" + "="*80)
    print("INICIANDO ANÁLISIS COMPLETO")
    print("="*80)
    
    for i, (nombre, script) in enumerate(analisis, 1):
        print(f"\n{'='*80}")
        print(f"PASO {i}/6: {nombre}")
        print(f"{'='*80}")
        print(f"Iniciando a las {time.strftime('%H:%M:%S')}")
        
        tiempo_paso = time.time()
        exito = ejecutar_script(Path(__file__).parent / script)
        duracion_paso = time.time() - tiempo_paso
        
        resultados.append({
            'nombre': nombre,
            'exito': exito,
            'duracion': duracion_paso
        })
        
        if exito:
            print(f"\n[OK] {nombre} - COMPLETADO en {duracion_paso:.1f}s")
        else:
            print(f"\n[ADVERTENCIA] {nombre} - COMPLETADO CON ADVERTENCIAS en {duracion_paso:.1f}s")
        
        # Pausa breve entre análisis
        # NOTA: Agregué esta pausa porque si corren muy rápido uno tras otro
        # a veces había conflictos al escribir archivos
        if i < len(analisis):
            print("\nPreparando siguiente analisis...")
            time.sleep(2)
    
    # Resumen final
    duracion_total = time.time() - tiempo_inicio
    
    print("\n" + "="*80)
    print("ANALISIS COMPLETO FINALIZADO")
    print("="*80)
    
    print(f"\nTiempo total: {duracion_total/60:.1f} minutos ({duracion_total:.0f}s)")
    
    print("\nRESUMEN DE RESULTADOS:")
    print("-" * 80)
    for i, res in enumerate(resultados, 1):
        estado = "[OK]" if res['exito'] else "[ADVERTENCIA]"
        print(f"  {i}. {res['nombre']:<45} {estado:>15} ({res['duracion']:.1f}s)")
    
    print("\n" + "="*80)
    print("ARCHIVOS GENERADOS EN:")
    print("="*80)
    print(f"  Reportes CSV:      {Path('reportes').absolute()}")
    print(f"  Visualizaciones:   {Path('visualizaciones').absolute()}")
    print(f"  Datos procesados:  {Path('datos_procesados').absolute()}")
    
    print("\nPROXIMOS PASOS:")
    print("  1. Ejecuta: python ver_resultados.py")
    print("     Para ver todas las graficas generadas")
    print("  2. Revisa la carpeta 'visualizaciones'")
    print("     Contiene todas las imagenes para tu tesis")
    print("  3. Revisa la carpeta 'reportes'")
    print("     Contiene todos los CSV con resultados numericos")
    
    print("\n" + "="*80)
    
    input("\nPresiona ENTER para continuar...")
    
    return resultados


def menu_principal():
    """Menú principal del sistema."""
    mostrar_banner()
    
    # Verificar datos
    indices = mostrar_resumen_datos()
    
    if not indices:
        print("\n❌ No hay datos para analizar. Ejecuta primero el descargador.")
        return
    
    scripts_dir = Path(__file__).parent / "scripts"
    
    while True:
        print("\n" + "="*80)
        print("MENÚ PRINCIPAL")
        print("="*80)
        
        print("""
ANALISIS DISPONIBLES:

  [1] Validacion de Datos
      Verifica que el shapefile funcione correctamente

  [2] Analisis Exploratorio
      Estadisticas basicas, distribuciones, calidad de datos

  [3] Analisis Temporal
      Tendencias, velocidades de cambio, comparacion de periodos

  [4] Analisis Espacial
      Mapas de calor, hotspots, clustering, autocorrelacion

  [5] Segmentacion de Zonas
      Dividir area en zonas y analizar evolucion de cada una

  [6] Predicciones Futuras (DEEP LEARNING)
      Predice evolucion con redes neuronales + mapa visual

  [7] Generar Reportes PDF
      Crea PDFs profesionales con todas las graficas

  [8] Ayuda
      Explica que hace cada analisis

  ------------------------------------------------------------------------

  [T] EJECUTAR TODO
      Ejecuta todos los analisis (1-7) + genera PDFs automaticamente

  [0] Salir

        """)
        
        opcion = input("Selecciona una opción: ").strip().upper()
        
        if opcion == '0':
            print("\nSaliendo del sistema...")
            break
        
        elif opcion == '1':
            print("\n" + "="*80)
            print("EJECUTANDO: Validación de Datos")
            print("="*80)
            ejecutar_script(scripts_dir / "00_validacion_datos.py")
        
        elif opcion == '2':
            print("\n" + "="*80)
            print("EJECUTANDO: Análisis Exploratorio")
            print("="*80)
            ejecutar_script(scripts_dir / "01_analisis_exploratorio.py")
        
        elif opcion == '3':
            print("\n" + "="*80)
            print("EJECUTANDO: Análisis Temporal")
            print("="*80)
            ejecutar_script(scripts_dir / "03_analisis_temporal.py")
        
        elif opcion == '4':
            print("\n" + "="*80)
            print("EJECUTANDO: Análisis Espacial")
            print("="*80)
            ejecutar_script(scripts_dir / "02_analisis_espacial.py")
        
        elif opcion == '5':
            print("\n" + "="*80)
            print("EJECUTANDO: Segmentación de Zonas")
            print("="*80)
            ejecutar_script(scripts_dir / "04_segmentacion_zonas.py")
        
        elif opcion == '6':
            print("\n" + "="*80)
            print("EJECUTANDO: Predicciones Futuras con Deep Learning")
            print("="*80)
            ejecutar_script(scripts_dir / "05_predicciones_futuras.py")
        
        elif opcion == '7':
            print("\n" + "="*80)
            print("EJECUTANDO: Generador de Reportes PDF")
            print("="*80)
            ejecutar_script(scripts_dir / "99_generar_reporte_pdf.py")
        
        elif opcion == '8':
            mostrar_ayuda()
        
        elif opcion == 'T':
            ejecutar_analisis_completo(scripts_dir)
        
        else:
            print("\nOpcion no valida. Intenta de nuevo.")
    
    print("\n" + "="*80)
    print("SISTEMA CERRADO")
    print("="*80)


def mostrar_ayuda():
    """Muestra ayuda detallada sobre cada análisis."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                        GUÍA DE ANÁLISIS                                   ║
╚═══════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────────────┐
│ 1️⃣  VALIDACIÓN DE DATOS                                                 │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Verifica que el shapefile elimine correctamente píxeles fuera del     │
│   área de interés                                                       │
│ • Muestra cuántos píxeles quedan dentro y fuera del polígono           │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Primera vez que usas el sistema                                      │
│ • Para verificar que el enmascaramiento funciona                       │
│                                                                         │
│ RESULTADOS:                                                             │
│ • Confirmación de que solo se analizan píxeles dentro del área         │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 2️⃣  ANÁLISIS EXPLORATORIO                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Calcula estadísticas básicas de cada imagen (media, mediana, desv.)  │
│ • Analiza la distribución de valores (histogramas)                     │
│ • Detecta valores atípicos (outliers)                                  │
│ • Clasifica calidad de las imágenes                                    │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Para conocer tus datos por primera vez                               │
│ • Identificar imágenes con problemas de calidad                        │
│                                                                         │
│ RESULTADOS CLAVE:                                                       │
│ • Media: Valor promedio del índice en el área                          │
│ • CV (Coeficiente de Variación): Qué tan heterogénea es el área       │
│   - CV bajo (<20%): Área homogénea                                     │
│   - CV alto (>30%): Área muy variable                                  │
│ • Outliers: Píxeles con valores muy diferentes al resto                │
│                                                                         │
│ 📊 GENERA:                                                              │
│ • 4 gráficas por índice: distribución, boxplot, Q-Q plot, serie tempo  │
│ • CSV con estadísticas de todas las fechas                             │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 3️⃣  ANÁLISIS TEMPORAL ⭐ MÁS IMPORTANTE PARA TESIS                      │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Analiza cómo cambia el índice a lo largo del tiempo                  │
│ • Detecta tendencias (¿está mejorando o empeorando la vegetación?)    │
│ • Calcula velocidad de cambio (qué tan rápido cambia)                 │
│ • Compara diferentes períodos de tiempo                                │
│ • Detecta puntos de quiebre (cambios bruscos)                          │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Para responder: ¿La vegetación está mejorando o deteriorándose?     │
│ • Para detectar estacionalidad (patrones que se repiten)               │
│                                                                         │
│ RESULTADOS CLAVE:                                                       │
│ • Pendiente: Cambio por día                                            │
│   - Positiva: Vegetación mejorando                                     │
│   - Negativa: Vegetación deteriorándose                                │
│   - Ejemplo: -0.00155 = pierde 0.00155 unidades por día               │
│                                                                         │
│ • R² (0 a 1): Qué tan fuerte es la tendencia                          │
│   - R² > 0.7: Tendencia MUY clara                                     │
│   - R² 0.3-0.7: Tendencia moderada                                    │
│   - R² < 0.3: Tendencia débil o sin tendencia                         │
│                                                                         │
│ • P-valor: Confiabilidad estadística                                   │
│   - p < 0.05: Tendencia SIGNIFICATIVA (confiable)                     │
│   - p > 0.05: No significativa (puede ser azar)                       │
│                                                                         │
│ • Tau de Kendall (-1 a 1): Otra forma de medir tendencia              │
│   - Cerca de -1: Fuerte tendencia decreciente                         │
│   - Cerca de +1: Fuerte tendencia creciente                           │
│   - Cerca de 0: Sin tendencia                                         │
│                                                                         │
│ • Cambio porcentual: Cuánto cambió en total                           │
│   - Ejemplo: -32.70% = perdió casi un tercio de su valor              │
│                                                                         │
│ 📊 GENERA:                                                              │
│ • Series temporales con líneas de tendencia                            │
│ • Gráficas de velocidad de cambio                                      │
│ • Comparación entre períodos                                           │
│ • 6 CSV con tendencias, velocidades, cambios mensuales, etc.           │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 4️⃣  ANÁLISIS ESPACIAL                                                   │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Identifica DÓNDE están las zonas con valores altos/bajos            │
│ • Detecta hotspots (zonas críticas) y coldspots                        │
│ • Agrupa píxeles similares (clustering)                                │
│ • Analiza si hay patrones espaciales (agrupamiento)                    │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Para responder: ¿Dónde están las zonas problemáticas?               │
│ • Para encontrar patrones espaciales                                   │
│                                                                         │
│ RESULTADOS CLAVE:                                                       │
│ • Hotspots: Zonas con valores MUY altos                                │
│   - Porcentaje: Qué % del área son hotspots                           │
│   - Media hotspots: Valor promedio en esas zonas                      │
│                                                                         │
│ • Coldspots: Zonas con valores MUY bajos (problemáticas)               │
│                                                                         │
│ • Clusters: Grupos de píxeles similares                                │
│   - 5 clusters = dividir área en 5 grupos según similitud             │
│   - Cada cluster tiene su media, tamaño, etc.                         │
│                                                                         │
│ • I de Moran (-1 a 1): Autocorrelación espacial                       │
│   - Positivo: Píxeles similares están juntos (agrupados)              │
│   - Negativo: Patrón de tablero de ajedrez                            │
│   - Cerca de 0: Distribución aleatoria                                │
│                                                                         │
│ 📊 GENERA:                                                              │
│ • Mapas de calor (colores muestran valores)                            │
│ • Mapas de hotspots/coldspots                                          │
│ • Mapas de clustering                                                   │
│ • Mapas de diferencias entre fechas                                    │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 5️⃣  SEGMENTACIÓN DE ZONAS                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Divide el área en zonas más pequeñas                                 │
│ • Analiza la evolución temporal de cada zona por separado             │
│ • Compara cómo evolucionan las diferentes zonas                        │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Para análisis más detallado por secciones                            │
│ • Cuando quieres comparar diferentes partes del área                   │
│                                                                         │
│ RESULTADOS:                                                             │
│ • Tendencia de cada zona individual                                    │
│ • Comparación entre zonas                                              │
│ • Zonas con mejor/peor evolución                                       │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 6️⃣  PREDICCIONES FUTURAS (DEEP LEARNING) ⭐ NUEVO                      │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Usa redes neuronales para PREDECIR cómo evolucionará la vegetación  │
│ • Analiza el patrón histórico de cada píxel                            │
│ • Genera predicción para los próximos 30 días                          │
│ • Crea mapas visuales MUY fáciles de entender                          │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Cuando quieres saber QUÉ PASARÁ en el futuro                         │
│ • Para planificar intervenciones preventivas                           │
│ • Para demostrar capacidades de IA en tu tesis                         │
│                                                                         │
│ RESULTADOS CLAVE (Muy fáciles de entender):                            │
│                                                                         │
│ • Mapa de predicción con 5 colores:                                    │
│   🟥 Rojo oscuro = Empeorará MUCHO (requiere atención urgente)         │
│   🟧 Rojo claro = Empeorará un poco                                    │
│   🟨 Amarillo = Se mantendrá estable                                   │
│   🟩 Verde claro = Mejorará un poco                                    │
│   🟩 Verde oscuro = Mejorará MUCHO                                     │
│                                                                         │
│ • Informe en lenguaje simple que incluye:                              │
│   - Tendencia general (MEJORA / DETERIORO / ESTABLE)                  │
│   - Porcentajes del área en cada categoría                            │
│   - Explicación de qué significa                                       │
│   - Recomendaciones prácticas                                          │
│                                                                         │
│ ¿CÓMO FUNCIONA?                                                         │
│ La red neuronal "aprende" cómo ha cambiado cada píxel en el pasado,   │
│ identifica patrones, y continúa esos patrones hacia el futuro.        │
│ Es como cuando ves una gráfica bajando y dices "esto seguirá          │
│ bajando", pero la IA lo hace matemáticamente para cada píxel.         │
│                                                                         │
│ 📊 GENERA:                                                              │
│ • Mapa visual con colores (PNG de alta resolución)                     │
│ • Informe completo en texto simple (TXT)                               │
│ • Todo listo para incluir en presentación o tesis                      │
│                                                                         │
│ 💡 PERFECTO PARA:                                                       │
│ • Presentaciones a no técnicos (los colores hablan por sí solos)      │
│ • Tomar decisiones de manejo                                           │
│ • Demostrar que usaste IA/Machine Learning en tu tesis                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ 5️⃣  SEGMENTACIÓN DE ZONAS                                               │
├─────────────────────────────────────────────────────────────────────────┤
│ ¿QUÉ HACE?                                                              │
│ • Divide el área en ZONAS (como regiones geográficas)                  │
│ • Analiza la evolución temporal DE CADA ZONA por separado              │
│ • Compara zonas entre sí (¿cuál está mejor/peor?)                     │
│                                                                         │
│ 3 MÉTODOS:                                                              │
│ • Clustering: Agrupa píxeles similares                                 │
│ • Cuadrantes: Divide en cuadrícula (Norte, Sur, Este, Oeste, etc.)    │
│ • Percentiles: Por rangos de valores (muy bajo, bajo, medio, etc.)    │
│                                                                         │
│ ¿CUÁNDO USARLO?                                                         │
│ • Para identificar si algunas zonas se deterioran más que otras        │
│ • Para análisis detallado por región                                   │
│                                                                         │
│ RESULTADOS CLAVE:                                                       │
│ • Cada zona tiene su propia tendencia temporal                         │
│ • Puedes ver qué zonas mejoran y cuáles empeoran                       │
│ • Identificas zona mejor y zona peor                                   │
│                                                                         │
│ 📊 GENERA:                                                              │
│ • Mapa de zonas identificadas                                          │
│ • Serie temporal de cada zona                                          │
│ • Comparación de tendencias entre zonas                                │
│ • CSV con evolución de cada zona                                       │
└─────────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════╗
║                    EJEMPLO PRÁCTICO DE INTERPRETACIÓN                     ║
╚═══════════════════════════════════════════════════════════════════════════╝

Supongamos que analizas MSAVI y obtienes:

📈 ANÁLISIS TEMPORAL:
   • Pendiente: -0.00155079
   • R²: 0.2002
   • P-valor: 0.047934
   • Cambio total: -32.70%
   
   ✅ INTERPRETACIÓN:
   "El índice MSAVI muestra una tendencia DECRECIENTE significativa (p<0.05).
   La vegetación está perdiendo 0.00155 unidades por día, lo que representa
   una pérdida del 32.7% en el período analizado. La R² de 0.20 indica que
   la tendencia es moderada, sugiriendo que hay variabilidad pero la 
   dirección del cambio es clara."

🗺️  ANÁLISIS ESPACIAL:
   • Hotspots: 8.5% del área
   • Coldspots: 12.3% del área
   • I de Moran: 0.65 (p<0.001)
   
   ✅ INTERPRETACIÓN:
   "Se identificaron zonas críticas (coldspots) que representan el 12.3%
   del área total. El índice de Moran positivo (0.65) indica que existe
   agrupamiento espacial significativo, es decir, las zonas problemáticas
   tienden a estar juntas geográficamente."

🎯 SEGMENTACIÓN:
   • Zona 0: Tendencia -0.008, R²=0.75 (peor zona)
   • Zona 4: Tendencia +0.002, R²=0.45 (mejor zona)
   
   ✅ INTERPRETACIÓN:
   "Existe heterogeneidad espacial significativa. La Zona 0 muestra un
   deterioro acelerado (-0.008/día, R²=0.75) mientras que la Zona 4
   presenta ligera recuperación. Esto sugiere que diferentes áreas
   requieren intervenciones específicas."

╔═══════════════════════════════════════════════════════════════════════════╗
║                         ORDEN RECOMENDADO                                 ║
╚═══════════════════════════════════════════════════════════════════════════╝

Para tu tesis, te recomiendo este orden:

1. Validación de datos (1 vez, al inicio)
2. Análisis exploratorio (conocer tus datos)
3. Análisis temporal (⭐ MÁS IMPORTANTE - tendencias)
4. Análisis espacial (identificar dónde están los problemas)
5. Segmentación de zonas (análisis detallado por región)

Presiona ENTER para continuar...
    """)
    input()


if __name__ == "__main__":
    try:
        menu_principal()
    except KeyboardInterrupt:
        print("\n\n👋 Sistema interrumpido por el usuario")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
