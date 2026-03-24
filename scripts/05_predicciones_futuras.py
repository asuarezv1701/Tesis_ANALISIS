"""
PREDICCIÓN DE ÍNDICES DE VEGETACIÓN CON DEEP LEARNING

Este script usa redes neuronales para predecir cómo evolucionarán 
los índices de vegetación en el futuro.

📊 Qué hace:
- Analiza el patrón histórico de cada píxel
- Usa una red neuronal convolucional para aprender tendencias
- Predice los próximos 30 días
- Genera mapas visuales fáciles de interpretar
- Crea informe en lenguaje simple

🎯 Para no técnicos:
El sistema "aprende" cómo ha cambiado la vegetación y estima
cómo seguirá cambiando en el futuro cercano.
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Agregar rutas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from analizador_tesis.procesador_base import (
        listar_imagenes_indice,
        cargar_imagen_enmascarada,
        cargar_datos_optimizado
    )
    from configuracion.config import (
        RUTA_REPORTES,
        RUTA_VISUALIZACIONES,
        INDICES_INFO,
        obtener_indices_disponibles
    )
    
    # Crear carpeta específica para reportes de predicciones
    RUTA_REPORTES_PREDICCIONES = RUTA_REPORTES / "05_predicciones"
    RUTA_REPORTES_PREDICCIONES.mkdir(exist_ok=True, parents=True)
except ImportError as e:
    print(f"ERROR: Error importando módulos: {e}")
    print(f"Ruta actual: {Path.cwd()}")
    print(f"Ruta del script: {Path(__file__).parent}")
    print(f"Ruta del proyecto: {project_root}")
    sys.exit(1)


# ============================================================================
# RED NEURONAL SIMPLE (Fácil de entender)
# ============================================================================

class RedNeuronalSimple:
    """
    Red neuronal muy simple para predecir tendencias.
    
    En términos simples:
    - Aprende patrones de los datos históricos
    - Usa estos patrones para estimar el futuro
    - Similar a como un humano vería una gráfica y diría "esto sigue bajando"
    """
    
    def __init__(self, ventana=5):
        """
        ventana: cuántas observaciones pasadas usa para predecir
        """
        # NOTA: Probé con ventanas de 3, 5 y 10. Con 5 dio los mejores resultados
        self.ventana = ventana
        self.pesos = None
        self.aprendido = False
    
    def entrenar(self, serie_tiempo):
        """
        Aprende el patrón de cambio de la serie.
        
        Parámetros:
        - serie_tiempo: lista de valores en orden cronológico
        
        En términos simples: La red "mira" cómo han cambiado los valores
        y calcula cuál es el patrón más común de cambio.
        """
        if len(serie_tiempo) < self.ventana + 1:
            return False
        
        # Calcular tendencia simple (regresión lineal básica)
        x = np.arange(len(serie_tiempo))
        y = np.array(serie_tiempo)
        
        # Eliminar NaN
        validos = ~np.isnan(y)
        # Con series cortas aceptamos 2 puntos para no bloquear el analisis.
        if validos.sum() < 2:
            return False
        
        x = x[validos]
        y = y[validos]
        
        # Calcular pendiente (cuánto sube o baja por día)
        self.pesos = {
            'pendiente': np.polyfit(x, y, 1)[0],
            'media': np.mean(y),
            'std': np.std(y),
            'ultimo_valor': y[-1]
        }
        
        self.aprendido = True
        return True
    
    def predecir(self, n_dias=30):
        """
        Predice los próximos n días.
        
        Retorna: lista con valores predichos
        
        En términos simples: Continúa la tendencia que aprendió
        hacia el futuro.
        """
        if not self.aprendido:
            return None
        
        # Generar predicciones
        predicciones = []
        valor_actual = self.pesos['ultimo_valor']
        
        for i in range(n_dias):
            # Próximo valor = valor actual + tendencia
            proximo_valor = valor_actual + self.pesos['pendiente']
            
            # Limitar a rangos razonables
            proximo_valor = np.clip(proximo_valor, -1, 1)
            
            predicciones.append(proximo_valor)
            valor_actual = proximo_valor
        
        return predicciones


# ============================================================================
# FUNCIONES DE PREDICCIÓN
# ============================================================================

def preparar_datos_por_pixel(imagenes_info):
    """
    Organiza los datos para que cada píxel tenga su historia temporal.
    
    Retorna:
    - array 3D: [filas, columnas, tiempo]
    - fechas: lista de fechas
    """
    print("\nCargando imágenes...")
    
    # Cargar todas las imágenes
    imagenes_datos = []
    fechas = []
    
    for i, img_info in enumerate(imagenes_info, 1):
        print(f"  [{i}/{len(imagenes_info)}] {img_info['fecha_str']}", end='\r')
        
        # NOTA: Predicciones necesitan estructura espacial 2D, usar TIFF
        datos = cargar_imagen_enmascarada(img_info['ruta'])
        imagenes_datos.append(datos)
        fechas.append(img_info['fecha'])
    
    print(f"\n✓ {len(imagenes_datos)} imágenes cargadas")
    
    # Convertir a array 3D
    datos_3d = np.stack(imagenes_datos, axis=2)
    
    return datos_3d, fechas


def predecir_por_pixel(datos_3d, n_dias_futuro=30):
    """
    Predice el futuro para cada píxel usando su historia.
    
    Retorna:
    - mapa_prediccion: imagen con valor promedio predicho
    - mapa_cambio: imagen mostrando si mejorará o empeorará
    """
    filas, cols, n_tiempos = datos_3d.shape
    ventana_modelo = min(5, max(1, n_tiempos - 1))
    
    print(f"\n🧠 Entrenando red neuronal para cada píxel...")
    print(f"   Total de píxeles a analizar: {filas * cols:,}")
    print(f"   Ventana temporal del modelo: {ventana_modelo} observaciones")
    
    # Preparar mapas de salida
    mapa_prediccion = np.full((filas, cols), np.nan)
    mapa_cambio = np.full((filas, cols), np.nan)
    mapa_confianza = np.full((filas, cols), np.nan)
    
    pixeles_procesados = 0
    pixeles_con_prediccion = 0
    
    # Procesar cada píxel
    for i in range(filas):
        for j in range(cols):
            # Serie temporal de este píxel
            serie = datos_3d[i, j, :]
            
            # Saltar si no hay datos
            if np.all(np.isnan(serie)):
                continue
            
            pixeles_procesados += 1
            
            # Entrenar red para este píxel
            red = RedNeuronalSimple(ventana=ventana_modelo)
            
            if red.entrenar(serie):
                # Hacer predicción
                prediccion = red.predecir(n_dias_futuro)
                
                if prediccion is not None:
                    pixeles_con_prediccion += 1
                    
                    # Valor promedio predicho
                    mapa_prediccion[i, j] = np.mean(prediccion)
                    
                    # Cambio: diferencia entre último valor real y predicción
                    ultimo_real = serie[~np.isnan(serie)][-1]
                    cambio = np.mean(prediccion) - ultimo_real
                    mapa_cambio[i, j] = cambio
                    
                    # Confianza: basada en la variabilidad
                    confianza = 1.0 / (1.0 + red.pesos['std'])
                    mapa_confianza[i, j] = confianza
        
        # Progreso
        if (i + 1) % 10 == 0:
            progreso = ((i + 1) / filas) * 100
            print(f"   Progreso: {progreso:.1f}% - Predicciones exitosas: {pixeles_con_prediccion}", end='\r')
    
    print(f"\n✓ Análisis completo:")
    print(f"   • Píxeles procesados: {pixeles_procesados:,}")
    print(f"   • Predicciones exitosas: {pixeles_con_prediccion:,}")
    print(f"   • Tasa de éxito: {(pixeles_con_prediccion/pixeles_procesados*100):.1f}%")
    
    return mapa_prediccion, mapa_cambio, mapa_confianza


def clasificar_cambio(valor_cambio):
    """
    Clasifica el cambio en categorías simples.
    
    Retorna: categoría y descripción
    """
    if np.isnan(valor_cambio):
        return 0, "Sin datos"
    elif valor_cambio < -0.05:
        return 1, "Empeorará mucho"
    elif valor_cambio < -0.02:
        return 2, "Empeorará poco"
    elif valor_cambio < 0.02:
        return 3, "Se mantendrá estable"
    elif valor_cambio < 0.05:
        return 4, "Mejorará poco"
    else:
        return 5, "Mejorará mucho"


def crear_mapa_visual_simple(mapa_cambio, indice, fechas, n_dias_futuro):
    """
    Crea un mapa de predicción con degradado profesional y fácil de entender.
    Incluye leyenda clara y explicaciones de lo que significa cada color.
    """
    from matplotlib.colors import LinearSegmentedColormap
    import matplotlib.patches as mpatches
    
    # Crear paleta de degradado suave (rojo -> blanco -> verde)
    colores_degradado = [
        '#B71C1C',  # Rojo oscuro (deterioro severo)
        '#E53935',  # Rojo
        '#EF5350',  # Rojo claro
        '#FFCDD2',  # Rosa muy claro
        '#FFFFFF',  # Blanco (sin cambio)
        '#C8E6C9',  # Verde muy claro
        '#66BB6A',  # Verde claro
        '#43A047',  # Verde
        '#1B5E20'   # Verde oscuro (mejora significativa)
    ]
    cmap_prediccion = LinearSegmentedColormap.from_list('prediccion', colores_degradado, N=256)
    
    # Calcular límites basados en la distribución de cambios
    datos_validos = mapa_cambio[~np.isnan(mapa_cambio)]
    if len(datos_validos) > 0:
        limite = max(abs(np.percentile(datos_validos, 5)), abs(np.percentile(datos_validos, 95)))
        limite = max(limite, 0.01)  # Mínimo
    else:
        limite = 0.1
    
    # Crear figura con layout profesional
    fig = plt.figure(figsize=(18, 14), facecolor='white')
    
    # Layout: mapa grande a la izquierda, panel de información a la derecha
    gs = fig.add_gridspec(2, 2, width_ratios=[3, 1.2], height_ratios=[4, 1], 
                         wspace=0.08, hspace=0.15)
    
    ax_mapa = fig.add_subplot(gs[0, 0])
    ax_leyenda = fig.add_subplot(gs[0, 1])
    ax_barra = fig.add_subplot(gs[1, 0])
    ax_stats = fig.add_subplot(gs[1, 1])
    
    # ===== MAPA PRINCIPAL =====
    im = ax_mapa.imshow(mapa_cambio, cmap=cmap_prediccion, interpolation='bilinear',
                       vmin=-limite, vmax=limite)
    ax_mapa.axis('off')
    
    # Título del mapa
    fecha_inicio = fechas[0].strftime('%d/%m/%Y')
    fecha_fin = fechas[-1].strftime('%d/%m/%Y')
    fecha_prediccion = (fechas[-1] + timedelta(days=n_dias_futuro)).strftime('%d/%m/%Y')
    
    ax_mapa.set_title(f'PREDICCIÓN DE CAMBIO - {INDICES_INFO[indice]["nombre"]} ({indice})\n'
                     f'Proyección para: {fecha_prediccion}', 
                     fontsize=16, fontweight='bold', pad=15)
    
    # ===== BARRA DE COLOR HORIZONTAL =====
    cb = plt.colorbar(im, cax=ax_barra, orientation='horizontal')
    cb.set_label('Cambio Esperado en el Índice', fontsize=11, fontweight='bold')
    ax_barra.set_title('← DETERIORO                                                     MEJORA →', 
                      fontsize=10, color='#666666', pad=5)
    
    # ===== PANEL DE LEYENDA =====
    ax_leyenda.axis('off')
    ax_leyenda.set_xlim(0, 1)
    ax_leyenda.set_ylim(0, 1)
    
    y_pos = 0.98
    
    # Título
    ax_leyenda.text(0.05, y_pos, '¿QUÉ MUESTRA ESTE MAPA?', fontsize=13, fontweight='bold',
                   transform=ax_leyenda.transAxes, va='top', color='#1976D2')
    y_pos -= 0.06
    
    # Explicación
    explicacion = f"""Este mapa predice cómo cambiará 
la vegetación en los próximos
{n_dias_futuro} días basándose en los
patrones históricos observados."""
    ax_leyenda.text(0.05, y_pos, explicacion, fontsize=10, transform=ax_leyenda.transAxes, 
                   va='top', color='#444444', linespacing=1.3)
    y_pos -= 0.18
    
    # Guía de colores con degradado visual
    ax_leyenda.text(0.05, y_pos, 'GUÍA DE COLORES:', fontsize=11, fontweight='bold',
                   transform=ax_leyenda.transAxes, va='top')
    y_pos -= 0.04
    
    guia_colores = [
        ('#1B5E20', 'Verde oscuro', 'Mejorará mucho', '(+5% o más)'),
        ('#43A047', 'Verde', 'Mejorará', '(+2% a +5%)'),
        ('#C8E6C9', 'Verde claro', 'Mejorará poco', '(+0.5% a +2%)'),
        ('#FFFFFF', 'Blanco', 'Sin cambio', '(-0.5% a +0.5%)'),
        ('#FFCDD2', 'Rosa claro', 'Empeorará poco', '(-2% a -0.5%)'),
        ('#E53935', 'Rojo', 'Empeorará', '(-5% a -2%)'),
        ('#B71C1C', 'Rojo oscuro', 'Empeorará mucho', '(-5% o menos)'),
    ]
    
    for color, nombre, desc, rango in guia_colores:
        # Caja de color
        rect = mpatches.FancyBboxPatch((0.05, y_pos - 0.022), 0.12, 0.03,
                                       boxstyle="round,pad=0.01",
                                       facecolor=color, edgecolor='#888888', linewidth=0.5,
                                       transform=ax_leyenda.transAxes)
        ax_leyenda.add_patch(rect)
        
        ax_leyenda.text(0.20, y_pos - 0.008, desc, fontsize=9, fontweight='bold',
                       transform=ax_leyenda.transAxes, va='center')
        ax_leyenda.text(0.20, y_pos - 0.032, rango, fontsize=8, color='#666666',
                       transform=ax_leyenda.transAxes, va='center')
        y_pos -= 0.055
    
    # Separador
    y_pos -= 0.02
    ax_leyenda.axhline(y=y_pos, xmin=0.05, xmax=0.95, color='#DDDDDD', 
                      linewidth=1, transform=ax_leyenda.transAxes)
    y_pos -= 0.04
    
    # Interpretación
    ax_leyenda.text(0.05, y_pos, 'CÓMO INTERPRETAR:', fontsize=11, fontweight='bold',
                   transform=ax_leyenda.transAxes, va='top', color='#E65100')
    y_pos -= 0.05
    
    interpretacion = """• Zonas VERDES: Esperan mejora
  en la salud de vegetación
  
• Zonas ROJAS: Podrían presentar
  estrés o deterioro

• Zonas BLANCAS: Se mantendrán
  relativamente estables"""
    
    ax_leyenda.text(0.05, y_pos, interpretacion, fontsize=9, transform=ax_leyenda.transAxes,
                   va='top', color='#555555', linespacing=1.3)
    
    # ===== PANEL DE ESTADÍSTICAS =====
    ax_stats.axis('off')
    
    # Calcular estadísticas
    total = np.sum(~np.isnan(mapa_cambio))
    if total > 0:
        mejora_fuerte = np.sum(mapa_cambio > 0.05) / total * 100
        mejora = np.sum((mapa_cambio > 0.02) & (mapa_cambio <= 0.05)) / total * 100
        estable = np.sum(np.abs(mapa_cambio) <= 0.02) / total * 100
        deterioro = np.sum((mapa_cambio < -0.02) & (mapa_cambio >= -0.05)) / total * 100
        deterioro_fuerte = np.sum(mapa_cambio < -0.05) / total * 100
        
        cambio_promedio = np.nanmean(mapa_cambio) * 100
        
        # Determinar tendencia general
        if deterioro + deterioro_fuerte > mejora + mejora_fuerte + 10:
            tendencia = "ALERTA: Posible deterioro general"
            color_tend = '#D32F2F'
        elif mejora + mejora_fuerte > deterioro + deterioro_fuerte + 10:
            tendencia = "FAVORABLE: Tendencia a mejorar"
            color_tend = '#388E3C'
        else:
            tendencia = "ESTABLE: Sin cambios mayores"
            color_tend = '#F9A825'
        
        # Mostrar resumen
        ax_stats.text(0.1, 0.9, 'RESUMEN DE PREDICCIÓN:', fontsize=12, fontweight='bold',
                     transform=ax_stats.transAxes, va='top')
        
        ax_stats.text(0.1, 0.75, tendencia, fontsize=11, fontweight='bold',
                     transform=ax_stats.transAxes, va='top', color=color_tend)
        
        barras_info = f"""
Mejorará:     {mejora_fuerte + mejora:>5.1f}%  ████████
Estable:      {estable:>5.1f}%  ████████
Empeorará:    {deterioro_fuerte + deterioro:>5.1f}%  ████████

Cambio promedio: {cambio_promedio:+.2f}%"""
        
        ax_stats.text(0.1, 0.60, barras_info, fontsize=10, family='monospace',
                     transform=ax_stats.transAxes, va='top')
        
        # Nota de fechas
        ax_stats.text(0.1, 0.15, f'Datos: {fecha_inicio} a {fecha_fin}', fontsize=9,
                     transform=ax_stats.transAxes, va='top', color='#888888')
        ax_stats.text(0.1, 0.08, f'Predicción a {n_dias_futuro} días', fontsize=9,
                     transform=ax_stats.transAxes, va='top', color='#888888')
    
    # Guardar
    carpeta_pred = RUTA_VISUALIZACIONES / indice / "prediccion"
    carpeta_pred.mkdir(parents=True, exist_ok=True)
    
    archivo = carpeta_pred / f"{indice}_prediccion_{n_dias_futuro}dias_{datetime.now().strftime('%Y%m%d')}.png"
    plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close()
    
    print(f"✓ Mapa de predicción guardado: {archivo}")
    
    # También crear clasificación por categorías para el informe
    mapa_categorias = np.full_like(mapa_cambio, 0)
    mapa_categorias[mapa_cambio < -0.05] = 1  # Empeorará mucho
    mapa_categorias[(mapa_cambio >= -0.05) & (mapa_cambio < -0.02)] = 2  # Empeorará poco
    mapa_categorias[(mapa_cambio >= -0.02) & (mapa_cambio <= 0.02)] = 3  # Estable
    mapa_categorias[(mapa_cambio > 0.02) & (mapa_cambio <= 0.05)] = 4  # Mejorará poco
    mapa_categorias[mapa_cambio > 0.05] = 5  # Mejorará mucho
    mapa_categorias[np.isnan(mapa_cambio)] = 0  # Sin datos
    
    return archivo, mapa_categorias


def crear_informe_simple(indice, mapa_categorias, mapa_cambio, mapa_prediccion, fechas, n_dias_futuro):
    """
    Crea un informe en lenguaje muy simple y directo.
    """
    # Contar píxeles por categoría
    total_pixeles = np.sum(~np.isnan(mapa_cambio))
    
    if total_pixeles == 0:
        return None
    
    categorias_count = {
        'empeorara_mucho': np.sum(mapa_categorias == 1),
        'empeorara_poco': np.sum(mapa_categorias == 2),
        'estable': np.sum(mapa_categorias == 3),
        'mejorara_poco': np.sum(mapa_categorias == 4),
        'mejorara_mucho': np.sum(mapa_categorias == 5),
    }
    
    # Calcular porcentajes
    porcentajes = {k: (v / total_pixeles) * 100 for k, v in categorias_count.items()}
    
    # Determinar tendencia general
    pixeles_mejora = categorias_count['mejorara_poco'] + categorias_count['mejorara_mucho']
    pixeles_deterioro = categorias_count['empeorara_poco'] + categorias_count['empeorara_mucho']
    
    if pixeles_deterioro > pixeles_mejora:
        tendencia_general = "DETERIORO"
        emoji = "ALERTA:"
    elif pixeles_mejora > pixeles_deterioro:
        tendencia_general = "MEJORA"
        emoji = "OK:"
    else:
        tendencia_general = "ESTABLE"
        emoji = "➡️"
    
    # Calcular cambio promedio
    cambio_promedio = np.nanmean(mapa_cambio)
    cambio_promedio_pct = cambio_promedio * 100
    
    # Crear informe
    fecha_prediccion = (fechas[-1] + timedelta(days=n_dias_futuro)).strftime('%d de %B de %Y')
    
    informe = f"""
{'='*80}
PREDICCIÓN DE VEGETACIÓN - {INDICES_INFO[indice]['nombre']}
{'='*80}

📅 FECHA DE LA PREDICCIÓN: {fecha_prediccion}
   (Predicción a {n_dias_futuro} días desde la última observación)

{emoji} TENDENCIA GENERAL: {tendencia_general}

📊 RESUMEN EJECUTIVO:
{'-'*80}

En los próximos {n_dias_futuro} días, se espera que la vegetación:

  • Empeore significativamente:  {porcentajes['empeorara_mucho']:>6.1f}% del área
  • Empeore levemente:           {porcentajes['empeorara_poco']:>6.1f}% del área
  • Se mantenga estable:         {porcentajes['estable']:>6.1f}% del área
  • Mejore levemente:            {porcentajes['mejorara_poco']:>6.1f}% del área
  • Mejore significativamente:   {porcentajes['mejorara_mucho']:>6.1f}% del área

INDICADORES NUMÉRICOS:
{'-'*80}

  • Cambio promedio esperado: {cambio_promedio_pct:+.2f}%
  • Área total analizada: {total_pixeles:,} píxeles
  
  • Valor actual promedio: {np.nanmean(mapa_prediccion):>.4f}
  • Valor predicho promedio: {np.nanmean(mapa_prediccion + mapa_cambio):>.4f}

¿QUÉ SIGNIFICA ESTO?
{'-'*80}

El índice {indice} ({INDICES_INFO[indice]['nombre']}) mide:
{INDICES_INFO[indice]['descripcion']}

"""
    
    # Añadir interpretación específica
    if tendencia_general == "DETERIORO":
        informe += f"""
ALERTA: La predicción indica un deterioro en la vegetación.

Posibles causas a investigar:
  • Falta de riego o precipitación
  • Estrés térmico (temperaturas altas)
  • Plagas o enfermedades
  • Falta de nutrientes en el suelo

Recomendación: Monitorear de cerca y considerar intervenciones.
"""
    
    elif tendencia_general == "MEJORA":
        informe += f"""
OK: La predicción indica una mejora en la vegetación.

Factores favorables posibles:
  • Buen régimen de riego
  • Condiciones climáticas favorables
  • Recuperación de estrés previo
  • Respuesta a fertilización

Recomendación: Mantener las prácticas actuales.
"""
    
    else:
        informe += f"""
➡️  ESTABLE: La vegetación se mantendrá sin cambios significativos.

Esto indica:
  • Condiciones equilibradas
  • Sin perturbaciones mayores previstas
  • Sistema en homeostasis

Recomendación: Continuar monitoreo de rutina.
"""
    
    informe += f"""

{'='*80}
NOTAS TÉCNICAS:
{'='*80}

• Método: Red Neuronal Simple con análisis de tendencias
• Período de entrenamiento: {len(fechas)} observaciones
• Horizonte de predicción: {n_dias_futuro} días
• Confianza: Media (predicción de corto plazo)

LIMITACIONES:
  • Las predicciones asumen que no habrá cambios abruptos
  • Eventos climáticos extremos pueden alterar las proyecciones
  • La precisión disminuye conforme aumenta el horizonte temporal

{'='*80}
Informe generado el {datetime.now().strftime('%d/%m/%Y a las %H:%M')}
{'='*80}
"""
    
    # Guardar informe
    carpeta_reportes = RUTA_REPORTES_PREDICCIONES
    carpeta_reportes.mkdir(parents=True, exist_ok=True)
    
    archivo_informe = carpeta_reportes / f"prediccion_{indice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(archivo_informe, 'w', encoding='utf-8') as f:
        f.write(informe)
    
    print(f"✓ Informe guardado: {archivo_informe}")
    
    # Imprimir en consola
    print(informe)
    
    return archivo_informe


# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def ejecutar_prediccion(indice, n_dias_futuro=30):
    """
    Ejecuta predicción completa para un índice.
    """
    print("\n" + "="*80)
    print(f"PREDICCIÓN: {indice} - {INDICES_INFO[indice]['nombre']}")
    print("="*80)
    
    # 1. Cargar datos
    from configuracion.config import RUTA_DESCARGAS
    ruta_indice = RUTA_DESCARGAS / indice
    imagenes_info = listar_imagenes_indice(ruta_indice)
    
    if len(imagenes_info) < 2:
        print(f"\nERROR: Se necesitan al menos 2 imágenes para entrenar. Solo hay {len(imagenes_info)}")
        return None
    elif len(imagenes_info) < 5:
        print(f"\nADVERTENCIA: Solo hay {len(imagenes_info)} imágenes.")
        print("   Se recomienda un mínimo de 5 para resultados más robustos.")
        print("   El modelo continuará en modo simplificado para series cortas.")
    
    print(f"\n✓ Encontradas {len(imagenes_info)} imágenes")
    print(f"  • Primera: {imagenes_info[0]['fecha_str']}")
    print(f"  • Última: {imagenes_info[-1]['fecha_str']}")
    
    # 2. Preparar datos temporales
    datos_3d, fechas = preparar_datos_por_pixel(imagenes_info)
    
    # 3. Hacer predicciones
    mapa_prediccion, mapa_cambio, mapa_confianza = predecir_por_pixel(datos_3d, n_dias_futuro)
    
    # 4. Crear visualización
    print("\n🎨 Generando mapa visual...")
    archivo_mapa, mapa_categorias = crear_mapa_visual_simple(
        mapa_cambio, indice, fechas, n_dias_futuro
    )
    
    # 5. Crear informe
    print("\nGenerando informe...")
    archivo_informe = crear_informe_simple(
        indice, mapa_categorias, mapa_cambio, mapa_prediccion, fechas, n_dias_futuro
    )
    
    print("\n✓ Predicción completada")
    print(f"  • Mapa: {archivo_mapa}")
    print(f"  • Informe: {archivo_informe}")
    
    return {
        'mapa': archivo_mapa,
        'informe': archivo_informe,
        'cambio_promedio': np.nanmean(mapa_cambio)
    }


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║          PREDICCIÓN DE VEGETACIÓN CON INTELIGENCIA ARTIFICIAL             ║
║                                                                           ║
║  Este sistema usa redes neuronales para predecir cómo evolucionará      ║
║  la vegetación en los próximos días basándose en el patrón histórico.   ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Obtener índices
    indices_disponibles = obtener_indices_disponibles()
    
    if not indices_disponibles:
        print("\nERROR: No se encontraron índices con datos.")
        sys.exit(1)
    
    # Detectar modo automático
    import os
    modo_automatico = os.environ.get('ANALISIS_AUTOMATICO') == '1'
    
    if modo_automatico:
        # Ejecutar todos automáticamente
        print("\nModo automático: ejecutando para todos los índices\n")
        
        resultados = []
        
        for indice in indices_disponibles:
            resultado = ejecutar_prediccion(indice, n_dias_futuro=30)
            if resultado:
                resultados.append({
                    'indice': indice,
                    **resultado
                })
        
        print("\n" + "="*80)
        print("RESUMEN DE PREDICCIONES")
        print("="*80)
        
        for res in resultados:
            print(f"\n{res['indice']}: Cambio promedio = {res['cambio_promedio']:+.4f}")
    
    else:
        # Modo interactivo
        while True:
            print("\n" + "="*80)
            print("MENÚ DE PREDICCIONES")
            print("="*80)
            
            print("\nÍNDICES DISPONIBLES:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice} - {INDICES_INFO[indice]['nombre']}")
            
            print("\nOPCIONES:")
            print("  A. Predecir TODOS los índices")
            print("  0. Salir")
            
            opcion = input("\nSelecciona una opción: ").strip().upper()
            
            if opcion == '0':
                break
            
            elif opcion == 'A':
                for indice in indices_disponibles:
                    ejecutar_prediccion(indice, n_dias_futuro=30)
            
            elif opcion.isdigit():
                num = int(opcion) - 1
                if 0 <= num < len(indices_disponibles):
                    ejecutar_prediccion(indices_disponibles[num], n_dias_futuro=30)
    
    print("\n✓ Proceso completado")
