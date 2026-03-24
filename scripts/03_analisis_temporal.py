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

ANÁLISIS CLAVE PARA TESIS
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
        print(f"\nADVERTENCIA: No se encontraron imágenes para {indice}")
        return None
    
    print(f"Encontradas {len(imagenes)} imágenes")
    print("\n" + "-"*80)
    
    # Calcular estadísticas por fecha
    datos_temporales = []
    
    for i, img_info in enumerate(imagenes, 1):
        fecha_str = img_info['fecha_str'] or img_info['carpeta']
        fecha = img_info['fecha']
        fuente_icono = "CSV" if img_info.get('csv_pixeles') else "TIFF"
        
        print(f"[{i}/{len(imagenes)}] ({fuente_icono}) {fecha_str}... ", end='', flush=True)
        
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
        print("\nERROR: No se pudieron procesar imágenes")
        return None
    
    # Crear DataFrame
    df = pd.DataFrame(datos_temporales)
    df = df.sort_values('fecha')
    
    print(f"\nProcesadas {len(df)} imágenes válidas")
    
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
    print("\n[1] Calculando tendencia lineal...")
    tendencia = calcular_tendencia_lineal(df, 'fecha', 'media')
    if tendencia:
        print(f"   • Pendiente: {tendencia['pendiente']:.8f}")
        print(f"   • R²: {tendencia['r2']:.4f}")
        print(f"   • P-valor: {tendencia['p_valor']:.6f}")
        print(f"   • Resultado: {tendencia['tendencia']}")
        print(f"   • Cambio total: {tendencia['cambio_absoluto']:.4f} ({tendencia['cambio_porcentual']:.2f}%)")
        resultados['tendencia_lineal'] = tendencia
    else:
        print("   ADVERTENCIA: No se pudo calcular tendencia")
    
    # 2. Test de Mann-Kendall
    print("\n[2] Test de Mann-Kendall...")
    mk_test = test_mann_kendall(df['media'].values)
    if mk_test:
        print(f"   • Tau de Kendall: {mk_test['tau']:.4f}")
        print(f"   • P-valor: {mk_test['p_valor']:.6f}")
        print(f"   • Resultado: {mk_test['resultado']}")
        resultados['mann_kendall'] = mk_test
    else:
        print("   ADVERTENCIA: No se pudo ejecutar test")
    
    # 3. Velocidad de cambio
    print("\n[3] Calculando velocidad de cambio...")
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
        print("   ADVERTENCIA: No se pudo calcular velocidad")
    
    # 4. Tasa de cambio mensual
    print("\n[4] Calculando tasa de cambio mensual...")
    tasa_mensual = calcular_tasa_cambio_periodo(df, 'fecha', 'media', 'M')
    if tasa_mensual is not None:
        print(f"   • Meses analizados: {len(tasa_mensual)}")
        if 'cambio_porcentual' in tasa_mensual.columns:
            cambio_prom = tasa_mensual['cambio_porcentual'].mean()
            print(f"   • Cambio promedio mensual: {cambio_prom:.2f}%")
        resultados['tasa_mensual'] = tasa_mensual
    else:
        print("   ADVERTENCIA: No se pudo calcular tasa mensual")
    
    # 5. Descomposición estacional (si hay suficientes datos)
    if len(df) >= 4:
        print("\n5️⃣  Descomposición estacional...")
        try:
            decomp = descomponer_serie_temporal(df, 'fecha', 'media')
            if decomp:
                print("   ✓ Serie descompuesta en: tendencia, estacional, residuo")
                resultados['descomposicion'] = decomp
            else:
                print("   ADVERTENCIA: No se pudo descomponer la serie")
        except Exception as e:
            print(f"   ADVERTENCIA: Error en descomposición: {e}")
    else:
        print("\n[5] Descomposición estacional...")
        print(f"   ADVERTENCIA: Omitida: se requieren al menos 4 imágenes (actual: {len(df)}).")
        print("   Recomendación: usar mínimo 5 imágenes para mayor estabilidad.")
    
    # 6. Comparación entre periodos
    print("\n[6] Comparando periodos...")
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
        print("   ADVERTENCIA: No se pudo comparar periodos")
    
    # 7. Detección de punto de quiebre
    if len(df) >= 6:
        print("\n7️⃣  Detectando punto de quiebre...")
        quiebre = detectar_punto_quiebre(df, 'fecha', 'media')
        if quiebre:
            print(f"   • Fecha de quiebre: {quiebre['fecha_quiebre'].strftime('%Y-%m-%d')}")
            print(f"   • Tipo de cambio: {quiebre['tipo_cambio']}")
            print(f"   • R² total: {quiebre['r2_total']:.4f}")
            resultados['punto_quiebre'] = quiebre
        else:
            print("   ADVERTENCIA: No se detectó punto de quiebre significativo")
    else:
        print("\n[7] Detectando punto de quiebre...")
        print(f"   ADVERTENCIA: Omitido: se requieren al menos 6 imágenes (actual: {len(df)}).")
        print("   Recomendación: usar mínimo 5 imágenes para análisis temporal más confiable.")
    
    # 8. Estadísticas mensuales
    print("\n[8] Calculando estadísticas mensuales...")
    stats_mensuales = calcular_estadisticas_por_mes(df, 'fecha', 'media')
    if stats_mensuales is not None:
        print(f"   • Meses con datos: {len(stats_mensuales)}")
        resultados['estadisticas_mensuales'] = stats_mensuales
    
    print("\n" + "="*80)
    print("\nANÁLISIS TEMPORAL COMPLETADO")
    print("="*80)
    
    return resultados


def guardar_reportes_temporales(resultados, indice):
    """
    Guarda todos los reportes del análisis temporal.
    """
    print("\nGuardando reportes...")
    
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
    print("\nGenerando visualizaciones...")
    
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
        print(f"ADVERTENCIA: Error al generar visualizaciones: {e}")


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
    """
    Gráfica de descomposición estacional con layout de 2 columnas:
    - Izquierda: Las 4 gráficas de descomposición
    - Derecha: Panel de interpretación
    """
    import matplotlib.pyplot as plt
    from configuracion.config import INDICES_INFO
    
    # Figura más ancha para acomodar panel de interpretación
    fig = plt.figure(figsize=(18, 14))
    
    # Layout: gráficas (75%) | interpretación (25%)
    gs = fig.add_gridspec(4, 2, width_ratios=[3, 1], hspace=0.35, wspace=0.08)
    
    # Colores profesionales
    colores = {
        'original': '#2196F3',  # Azul
        'tendencia': '#E53935',  # Rojo
        'estacional': '#43A047',  # Verde
        'residuo': '#FF9800'  # Naranja
    }
    
    componentes = [
        ('original', 'SERIE ORIGINAL', indice),
        ('tendencia', 'TENDENCIA', indice),
        ('estacional', 'COMPONENTE ESTACIONAL', 'Variación'),
        ('residuo', 'RESIDUOS', 'Residuo')
    ]
    
    # Dibujar las 4 gráficas en la columna izquierda
    for idx, (key, titulo, ylabel) in enumerate(componentes):
        ax = fig.add_subplot(gs[idx, 0])
        
        datos = decomp[key]
        if datos is not None and not datos.isna().all():
            ax.plot(datos.index, datos.values, color=colores[key], linewidth=1.5)
            ax.fill_between(datos.index, datos.values, alpha=0.2, color=colores[key])
        
        ax.set_title(f'{titulo}', fontsize=11, fontweight='bold', 
                    color=colores[key], loc='left', pad=8)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.tick_params(axis='both', labelsize=8)
        
        if idx == 3:
            ax.set_xlabel('Fecha', fontsize=9)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
        else:
            ax.set_xticklabels([])
    
    # Panel de interpretación en la columna derecha (ocupa las 4 filas)
    ax_interp = fig.add_subplot(gs[:, 1])
    ax_interp.axis('off')
    
    # Título del panel
    ax_interp.text(0.05, 0.98, '¿CÓMO INTERPRETAR?', fontsize=13, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#1565C0')
    
    # Calcular estadísticas para interpretación
    tendencia_datos = decomp['tendencia']
    estacional_datos = decomp['estacional']
    
    if tendencia_datos is not None and len(tendencia_datos) > 1:
        cambio_tendencia = tendencia_datos.iloc[-1] - tendencia_datos.iloc[0]
        if cambio_tendencia > 0.01:
            direccion = "CRECIENTE ↑"
            color_dir = '#2E7D32'
            significado = "La vegetación está mejorando"
        elif cambio_tendencia < -0.01:
            direccion = "DECRECIENTE ↓"
            color_dir = '#C62828'
            significado = "La vegetación está deteriorándose"
        else:
            direccion = "ESTABLE →"
            color_dir = '#F57C00'
            significado = "Sin cambios significativos"
    else:
        direccion = "No determinada"
        color_dir = '#666666'
        significado = ""
    
    # Contenido de interpretación
    y_pos = 0.88
    
    # 1. Serie Original
    ax_interp.text(0.05, y_pos, '1. SERIE ORIGINAL', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#2196F3')
    y_pos -= 0.03
    ax_interp.text(0.05, y_pos, f'Valores de {indice} observados\nen cada fecha. Muestra la\nvariabilidad total de los datos.',
                  fontsize=9, transform=ax_interp.transAxes, va='top', color='#444444')
    y_pos -= 0.12
    
    # 2. Tendencia
    ax_interp.text(0.05, y_pos, '2. TENDENCIA', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#E53935')
    y_pos -= 0.03
    ax_interp.text(0.05, y_pos, f'Dirección: {direccion}', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color=color_dir)
    y_pos -= 0.03
    ax_interp.text(0.05, y_pos, f'{significado}\na largo plazo.',
                  fontsize=9, transform=ax_interp.transAxes, va='top', color='#444444')
    y_pos -= 0.10
    
    # 3. Componente Estacional
    ax_interp.text(0.05, y_pos, '3. ESTACIONALIDAD', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#43A047')
    y_pos -= 0.03
    if estacional_datos is not None:
        amp_estacional = estacional_datos.max() - estacional_datos.min()
        if amp_estacional > 0.05:
            patron = "Patrón estacional FUERTE"
        elif amp_estacional > 0.02:
            patron = "Patrón estacional MODERADO"
        else:
            patron = "Patrón estacional DÉBIL"
    else:
        patron = "No determinado"
    ax_interp.text(0.05, y_pos, f'{patron}\nCiclos que se repiten cada\naño (lluvias, sequía, etc.).',
                  fontsize=9, transform=ax_interp.transAxes, va='top', color='#444444')
    y_pos -= 0.12
    
    # 4. Residuos
    ax_interp.text(0.05, y_pos, '4. RESIDUOS', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#FF9800')
    y_pos -= 0.03
    ax_interp.text(0.05, y_pos, 'Variación aleatoria no\nexplicada. Valores cercanos\na cero = buen modelo.',
                  fontsize=9, transform=ax_interp.transAxes, va='top', color='#444444')
    y_pos -= 0.12
    
    # Resumen
    ax_interp.text(0.05, y_pos, '━━━━━━━━━━━━━━━━━', fontsize=8,
                  transform=ax_interp.transAxes, va='top', color='#CCCCCC')
    y_pos -= 0.03
    ax_interp.text(0.05, y_pos, 'RESUMEN:', fontsize=10, fontweight='bold',
                  transform=ax_interp.transAxes, va='top', color='#333333')
    y_pos -= 0.04
    
    resumen = f'El índice {indice} muestra una\ntendencia {direccion.lower()}.'
    if amp_estacional > 0.02 if estacional_datos is not None else False:
        resumen += f'\n\nSe detecta estacionalidad,\nlo cual es normal para\nvegetación.'
    
    ax_interp.text(0.05, y_pos, resumen,
                  fontsize=9, transform=ax_interp.transAxes, va='top', color='#444444',
                  bbox=dict(boxstyle='round', facecolor='#F5F5F5', alpha=0.8))
    
    # Título principal
    fig.suptitle(f'{indice} - DESCOMPOSICIÓN DE SERIE TEMPORAL\n{INDICES_INFO[indice]["nombre"]}', 
                fontsize=14, fontweight='bold', y=0.98)
    
    plt.savefig(archivo_salida, dpi=150, bbox_inches='tight', facecolor='white')
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
                analizar_temporal_indice(indice)
        elif opcion.isdigit():
            num = int(opcion) - 1
            if 0 <= num < len(indices_disponibles):
                analizar_temporal_indice(indices_disponibles[num])


if __name__ == "__main__":
    import os
    if os.environ.get('ANALISIS_AUTOMATICO') == '1':
        # Modo automático: analizar todos los índices sin menú
        print("\nModo automático: analizando TODOS los índices\n")
        indices_disponibles = obtener_indices_disponibles()
        for indice in indices_disponibles:
            analizar_temporal_indice(indice)
    else:
        # Modo manual: mostrar menú
        menu_principal()
    
    print("\n" + "="*80)
    print("ANÁLISIS TEMPORAL COMPLETADO")
    print("="*80)
    print("\nReportes en: reportes/03_temporal/")
    print("Visualizaciones en: visualizaciones/[INDICE]/temporal/")
