"""
Análisis Temporal de Índices de Vegetación
Autor: Tesis UPIITA
Fecha: Enero 2026
Versión: 2.0

NOTA: Este análisis es el corazón de mi tesis. Los resultados de las tendencias
son los que usaré para las conclusiones principales.

DUDA RESUELTA: ¿Usar Mann-Kendall o solo regresión lineal? Decidí usar ambos
porque Mann-Kendall no asume normalidad en los datos.
Este script realiza análisis temporal completo:
1. Tendencias (regresión lineal + Mann-Kendall)
2. Velocidad de cambio semanal/mensual
3. Descomposición estacional
4. Comparación entre periodos
5. Detección de puntos de quiebre
6. Visualizaciones temporales completas

⭐ ANÁLISIS CLAVE PARA TESIS
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
from analizador_tesis.temporal import (
    preparar_serie_temporal,
    calcular_tendencia_lineal,
    test_mann_kendall,
    calcular_velocidad_cambio,
    calcular_tasa_cambio_periodo,
    descomponer_serie_temporal,
    comparar_periodos,
    detectar_punto_quiebre,
    calcular_estadisticas_por_mes
)
from analizador_tesis.estadisticas import calcular_estadisticas_basicas
from configuracion.config import (
    RUTA_DESCARGAS,
    RUTA_SHAPEFILE,
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    INDICES_INFO,
    obtener_indices_disponibles
)

# Crear carpeta específica para reportes temporales
RUTA_REPORTES_TEMPORAL = RUTA_REPORTES / "03_temporal"
RUTA_REPORTES_TEMPORAL.mkdir(exist_ok=True, parents=True)

warnings.filterwarnings('ignore')


# ============================================================================
# FUNCIONES DE ANÁLISIS
# ============================================================================

def analizar_temporal_indice(indice):
    """
    Realiza análisis temporal completo de un índice.
    """
    print(f"\n{'#'*80}")
    print(f"# ANÁLISIS TEMPORAL: {indice}")
    print(f"{'#'*80}")
    
    print(f"\nÍndice: {indice} - {INDICES_INFO[indice]['nombre']}")
    
    # Listar imágenes
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes = listar_imagenes_indice(ruta_indice)
    
    if not imagenes:
        print(f"\n⚠️  No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes")
    print("\n" + "-"*80)
    
    # Calcular estadísticas por fecha
    datos_temporales = []
    
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        fecha = img_info['fecha']
        fuente_icono = "\ud83d\udcc4" if img_info.get('csv_pixeles') else "\ud83d\uddbc\ufe0f"
        
        print(f"[{i}/{len(imagenes)}] {fuente_icono} {fecha_str}... ", end='', flush=True)
        
        try:
            # Cargar datos de forma optimizada (CSV si existe, sino TIFF)
            datos, fuente = cargar_datos_optimizado(img_info, usar_csv=True)
            
            # Calcular estadísticas
            stats = calcular_estadisticas_basicas(datos, incluir_percentiles=True)
            
            if stats['n'] > 0:
                datos_temporales.append({
                    'fecha': fecha,
                    'fecha_str': fecha_str,
                    'pixeles': stats['n'],
                    'media': stats['media'],
                    'mediana': stats['mediana'],
                    'std': stats['std'],
                    'min': stats['min'],
                    'max': stats['max'],
                    'p05': stats['p05'],
                    'p25': stats['p25'],
                    'p75': stats['p75'],
                    'p95': stats['p95']
                })
                print(f"[OK] [{fuente.upper()}] Media: {stats['media']:.4f}")
            else:
                print("[ADVERTENCIA] Sin datos válidos")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    if not datos_temporales:
        print("\n❌ No se pudieron procesar imágenes")
        return None
    
    # Crear DataFrame
    df = pd.DataFrame(datos_temporales)
    df = df.sort_values('fecha')
    
    print(f"\n✅ Procesadas {len(df)} imágenes válidas")
    
    # Realizar análisis temporales
    resultados = realizar_analisis_temporal(df, indice)
    
    # Guardar reportes
    guardar_reportes_temporales(resultados, indice)
    
    # Generar visualizaciones
    generar_visualizaciones_temporales(resultados, indice)
    
    return resultados


def realizar_analisis_temporal(df, indice):
    """
    Ejecuta todos los análisis temporales.
    """
    print("\n" + "="*80)
    print("EJECUTANDO ANÁLISIS TEMPORALES")
    print("="*80)
    
    resultados = {
        'indice': indice,
        'df_completo': df,
        'n_imagenes': len(df),
        'fecha_inicio': df['fecha'].min(),
        'fecha_fin': df['fecha'].max(),
        'dias_total': (df['fecha'].max() - df['fecha'].min()).days
    }
    
    # 1. Tendencia lineal
    print("\n1️⃣  Calculando tendencia lineal...")
    tendencia = calcular_tendencia_lineal(df, 'fecha', 'media')
    if tendencia:
        print(f"   • Pendiente: {tendencia['pendiente']:.8f}")
        print(f"   • R²: {tendencia['r2']:.4f}")
        print(f"   • P-valor: {tendencia['p_valor']:.6f}")
        print(f"   • Resultado: {tendencia['tendencia']}")
        print(f"   • Cambio total: {tendencia['cambio_absoluto']:.4f} ({tendencia['cambio_porcentual']:.2f}%)")
        resultados['tendencia_lineal'] = tendencia
    else:
        print("   ⚠️  No se pudo calcular tendencia")
    
    # 2. Test de Mann-Kendall
    print("\n2️⃣  Test de Mann-Kendall...")
    mk_test = test_mann_kendall(df['media'].values)
    if mk_test:
        print(f"   • Tau de Kendall: {mk_test['tau']:.4f}")
        print(f"   • P-valor: {mk_test['p_valor']:.6f}")
        print(f"   • Resultado: {mk_test['resultado']}")
        resultados['mann_kendall'] = mk_test
    else:
        print("   ⚠️  No se pudo ejecutar test")
    
    # 3. Velocidad de cambio
    print("\n3️⃣  Calculando velocidad de cambio...")
    velocidad_df = calcular_velocidad_cambio(df, 'fecha', 'media')
    if velocidad_df is not None and len(velocidad_df) > 0:
        vel_promedio = velocidad_df['velocidad_por_dia'].mean()
        vel_max = velocidad_df['velocidad_por_dia'].max()
        vel_min = velocidad_df['velocidad_por_dia'].min()
        print(f"   • Velocidad promedio: {vel_promedio:.6f} unidades/día")
        print(f"   • Velocidad máxima: {vel_max:.6f} unidades/día")
        print(f"   • Velocidad mínima: {vel_min:.6f} unidades/día")
        resultados['velocidad_cambio'] = velocidad_df
    else:
        print("   ⚠️  No se pudo calcular velocidad")
    
    # 4. Tasa de cambio mensual
    print("\n4️⃣  Calculando tasa de cambio mensual...")
    tasa_mensual = calcular_tasa_cambio_periodo(df, 'fecha', 'media', 'M')
    if tasa_mensual is not None:
        print(f"   • Meses analizados: {len(tasa_mensual)}")
        if 'cambio_porcentual' in tasa_mensual.columns:
            cambio_prom = tasa_mensual['cambio_porcentual'].mean()
            print(f"   • Cambio promedio mensual: {cambio_prom:.2f}%")
        resultados['tasa_mensual'] = tasa_mensual
    else:
        print("   ⚠️  No se pudo calcular tasa mensual")
    
    # 5. Descomposición estacional (si hay suficientes datos)
    if len(df) >= 12:
        print("\n5️⃣  Descomposición estacional...")
        try:
            decomp = descomponer_serie_temporal(df, 'fecha', 'media')
            if decomp:
                print("   ✓ Serie descompuesta en: tendencia, estacional, residuo")
                resultados['descomposicion'] = decomp
            else:
                print("   ⚠️  No se pudo descomponer la serie")
        except Exception as e:
            print(f"   ⚠️  Error en descomposición: {e}")
    
    # 6. Comparación entre periodos
    print("\n6️⃣  Comparando periodos...")
    comparacion = comparar_periodos(df, 'fecha', 'media')
    if comparacion:
        print(f"   • Periodo 1: {comparacion['periodo1']['n']} imágenes, "
              f"Media = {comparacion['periodo1']['media']:.4f}")
        print(f"   • Periodo 2: {comparacion['periodo2']['n']} imágenes, "
              f"Media = {comparacion['periodo2']['media']:.4f}")
        print(f"   • Cambio: {comparacion['cambio_absoluto']:.4f} "
              f"({comparacion['cambio_porcentual']:.2f}%)")
        print(f"   • {comparacion['interpretacion']}")
        resultados['comparacion_periodos'] = comparacion
    else:
        print("   ⚠️  No se pudo comparar periodos")
    
    # 7. Detección de punto de quiebre
    if len(df) >= 10:
        print("\n7️⃣  Detectando punto de quiebre...")
        quiebre = detectar_punto_quiebre(df, 'fecha', 'media')
        if quiebre:
            print(f"   • Fecha de quiebre: {quiebre['fecha_quiebre'].strftime('%Y-%m-%d')}")
            print(f"   • Tipo de cambio: {quiebre['tipo_cambio']}")
            print(f"   • R² total: {quiebre['r2_total']:.4f}")
            resultados['punto_quiebre'] = quiebre
        else:
            print("   ⚠️  No se detectó punto de quiebre significativo")
    
    # 8. Estadísticas mensuales
    print("\n8️⃣  Calculando estadísticas mensuales...")
    stats_mensuales = calcular_estadisticas_por_mes(df, 'fecha', 'media')
    if stats_mensuales is not None:
        print(f"   • Meses con datos: {len(stats_mensuales)}")
        resultados['estadisticas_mensuales'] = stats_mensuales
    
    print("\n" + "="*80)
    print("✅ ANÁLISIS TEMPORAL COMPLETADO")
    print("="*80)
    
    return resultados


def guardar_reportes_temporales(resultados, indice):
    """
    Guarda todos los reportes del análisis temporal.
    """
    print("\n📊 Guardando reportes...")
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_reportes = RUTA_REPORTES_TEMPORAL
    carpeta_reportes.mkdir(exist_ok=True, parents=True)
    
    archivos_guardados = []
    
    # 1. Datos completos
    archivo = carpeta_reportes / f"serie_temporal_{indice}_{timestamp}.csv"
    resultados['df_completo'].to_csv(archivo, index=False)
    archivos_guardados.append(archivo.name)
    
    # 2. Tendencia lineal
    if 'tendencia_lineal' in resultados:
        df_tend = pd.DataFrame([resultados['tendencia_lineal']])
        archivo = carpeta_reportes / f"tendencia_lineal_{indice}_{timestamp}.csv"
        df_tend.to_csv(archivo, index=False)
        archivos_guardados.append(archivo.name)
    
    # 3. Velocidad de cambio
    if 'velocidad_cambio' in resultados:
        archivo = carpeta_reportes / f"velocidad_cambio_{indice}_{timestamp}.csv"
        resultados['velocidad_cambio'].to_csv(archivo, index=False)
        archivos_guardados.append(archivo.name)
    
    # 4. Tasa mensual
    if 'tasa_mensual' in resultados:
        archivo = carpeta_reportes / f"tasa_mensual_{indice}_{timestamp}.csv"
        resultados['tasa_mensual'].to_csv(archivo, index=False)
        archivos_guardados.append(archivo.name)
    
    # 5. Comparación de periodos
    if 'comparacion_periodos' in resultados:
        df_comp = pd.DataFrame([resultados['comparacion_periodos']])
        archivo = carpeta_reportes / f"comparacion_periodos_{indice}_{timestamp}.csv"
        df_comp.to_csv(archivo, index=False)
        archivos_guardados.append(archivo.name)
    
    # 6. Estadísticas mensuales
    if 'estadisticas_mensuales' in resultados:
        archivo = carpeta_reportes / f"estadisticas_mensuales_{indice}_{timestamp}.csv"
        resultados['estadisticas_mensuales'].to_csv(archivo, index=False)
        archivos_guardados.append(archivo.name)
    
    print(f"✓ Guardados {len(archivos_guardados)} reportes en: {carpeta_reportes}")
    for nombre in archivos_guardados:
        print(f"  • {nombre}")


def generar_visualizaciones_temporales(resultados, indice):
    """
    Genera todas las visualizaciones del análisis temporal.
    """
    print("\n📈 Generando visualizaciones...")
    
    from analizador_tesis import visualizador
    import matplotlib.pyplot as plt
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    carpeta_vis = RUTA_VISUALIZACIONES / indice / "temporal"
    carpeta_vis.mkdir(exist_ok=True, parents=True)
    
    df = resultados['df_completo']
    
    visualizaciones_creadas = []
    
    try:
        # 1. Serie temporal con bandas de confianza
        archivo = carpeta_vis / f"serie_temporal_{indice}_{timestamp}.png"
        visualizador.graficar_serie_temporal(
            df, 'fecha', 'media',
            f'{indice} - Evolución Temporal',
            archivo, con_bandas=True
        )
        visualizaciones_creadas.append(archivo.name)
        
        # 2. Tendencia lineal
        if 'tendencia_lineal' in resultados:
            archivo = carpeta_vis / f"tendencia_lineal_{indice}_{timestamp}.png"
            graficar_tendencia_lineal(df, resultados['tendencia_lineal'], indice, archivo)
            visualizaciones_creadas.append(archivo.name)
        
        # 3. Velocidad de cambio
        if 'velocidad_cambio' in resultados:
            archivo = carpeta_vis / f"velocidad_cambio_{indice}_{timestamp}.png"
            graficar_velocidad_cambio(resultados['velocidad_cambio'], indice, archivo)
            visualizaciones_creadas.append(archivo.name)
        
        # 4. Comparación de periodos
        if 'comparacion_periodos' in resultados:
            archivo = carpeta_vis / f"comparacion_periodos_{indice}_{timestamp}.png"
            graficar_comparacion_periodos(df, resultados['comparacion_periodos'], indice, archivo)
            visualizaciones_creadas.append(archivo.name)
        
        # 5. Descomposición estacional
        if 'descomposicion' in resultados:
            archivo = carpeta_vis / f"descomposicion_estacional_{indice}_{timestamp}.png"
            graficar_descomposicion(resultados['descomposicion'], indice, archivo)
            visualizaciones_creadas.append(archivo.name)
        
        print(f"✓ Generadas {len(visualizaciones_creadas)} visualizaciones")
        for nombre in visualizaciones_creadas:
            print(f"  • {nombre}")
        
    except Exception as e:
        print(f"⚠️  Error al generar visualizaciones: {e}")


# ============================================================================
# FUNCIONES DE VISUALIZACIÓN ESPECÍFICAS
# ============================================================================

def graficar_tendencia_lineal(df, tendencia, indice, archivo_salida):
    """Gráfica de tendencia lineal con regresión."""
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Datos originales
    ax.scatter(df['fecha'], df['media'], alpha=0.6, s=50, label='Datos observados')
    
    # Línea de tendencia
    fecha_inicial = df['fecha'].min()
    dias = (df['fecha'] - fecha_inicial).dt.days
    y_pred = tendencia['intercepto'] + tendencia['pendiente'] * dias
    
    ax.plot(df['fecha'], y_pred, 'r-', linewidth=2, label='Tendencia lineal')
    
    # Información
    texto = (f"Tendencia: {tendencia['tendencia']}\n"
             f"Pendiente: {tendencia['pendiente']:.8f}\n"
             f"R² = {tendencia['r2']:.4f}\n"
             f"p-valor = {tendencia['p_valor']:.6f}")
    
    ax.text(0.02, 0.98, texto, transform=ax.transAxes,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    ax.set_xlabel('Fecha')
    ax.set_ylabel(f'{indice}')
    ax.set_title(f'{indice} - Análisis de Tendencia Lineal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.close()


def graficar_velocidad_cambio(df_vel, indice, archivo_salida):
    """Gráfica de velocidad de cambio."""
    import matplotlib.pyplot as plt
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    ax.bar(range(len(df_vel)), df_vel['velocidad_por_dia'], 
           color=['green' if v > 0 else 'red' for v in df_vel['velocidad_por_dia']],
           alpha=0.7)
    
    ax.axhline(0, color='black', linestyle='-', linewidth=0.5)
    ax.axhline(df_vel['velocidad_por_dia'].mean(), color='blue', linestyle='--', 
               linewidth=2, label=f"Promedio: {df_vel['velocidad_por_dia'].mean():.6f}")
    
    ax.set_xlabel('Intervalo')
    ax.set_ylabel('Velocidad de Cambio (unidades/día)')
    ax.set_title(f'{indice} - Velocidad de Cambio entre Fechas')
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.close()


def graficar_comparacion_periodos(df, comparacion, indice, archivo_salida):
    """Gráfica de comparación entre periodos."""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Dividir datos
    fecha_corte = comparacion['fecha_corte']
    periodo1 = df[df['fecha'] < fecha_corte]
    periodo2 = df[df['fecha'] >= fecha_corte]
    
    # Serie temporal con división
    ax = axes[0]
    ax.plot(periodo1['fecha'], periodo1['media'], 'o-', color='blue', label='Periodo 1')
    ax.plot(periodo2['fecha'], periodo2['media'], 'o-', color='red', label='Periodo 2')
    ax.axvline(fecha_corte, color='black', linestyle='--', linewidth=2, label='Fecha de corte')
    ax.set_xlabel('Fecha')
    ax.set_ylabel(f'{indice}')
    ax.set_title('Serie Temporal por Periodos')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Boxplot comparativo
    ax = axes[1]
    bp = ax.boxplot([periodo1['media'], periodo2['media']],
                    labels=[comparacion['etiqueta_periodo1'], comparacion['etiqueta_periodo2']],
                    patch_artist=True)
    bp['boxes'][0].set_facecolor('blue')
    bp['boxes'][1].set_facecolor('red')
    
    ax.set_ylabel(f'{indice}')
    ax.set_title(f'Comparación Estadística\n{comparacion["interpretacion"]}')
    ax.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.close()


def graficar_descomposicion(decomp, indice, archivo_salida):
    """Gráfica de descomposición estacional."""
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(4, 1, figsize=(12, 10))
    
    # Original
    decomp['original'].plot(ax=axes[0], title='Serie Original')
    axes[0].set_ylabel(indice)
    
    # Tendencia
    decomp['tendencia'].plot(ax=axes[1], title='Tendencia', color='red')
    axes[1].set_ylabel(indice)
    
    # Estacional
    decomp['estacional'].plot(ax=axes[2], title='Componente Estacional', color='green')
    axes[2].set_ylabel('Estacional')
    
    # Residuo
    decomp['residuo'].plot(ax=axes[3], title='Residuos', color='orange')
    axes[3].set_ylabel('Residuo')
    axes[3].set_xlabel('Fecha')
    
    for ax in axes:
        ax.grid(True, alpha=0.3)
    
    plt.suptitle(f'{indice} - Descomposición de Serie Temporal', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
    plt.close()


# ============================================================================
# MENÚ PRINCIPAL
# ============================================================================

def menu_principal():
    """Menú interactivo."""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║                    ANÁLISIS TEMPORAL DE ÍNDICES                           ║
║                   (Tendencias, Estacionalidad, Cambios)                   ║
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
        print("  A. Analizar TODOS los índices")
        print("  0. Salir")
        
        opcion = input("\nSelecciona una opción: ").strip().upper()
        
        if opcion == '0':
            break
        elif opcion == 'A':
            for indice in indices_disponibles:
                analizar_temporal_indice(indice)
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                analizar_temporal_indice(indices_disponibles[num])


if __name__ == "__main__":
    menu_principal()
    
    print("\n" + "="*80)
    print("ANÁLISIS TEMPORAL COMPLETADO")
    print("="*80)
    print("\nReportes en: reportes/temporal/")
    print("Visualizaciones en: visualizaciones/[INDICE]/temporal/")
