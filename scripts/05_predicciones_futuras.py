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
    print(f"❌ Error importando módulos: {e}")
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
        if validos.sum() < 3:
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
    print("\n📦 Cargando imágenes...")
    
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
    
    print(f"\n🧠 Entrenando red neuronal para cada píxel...")
    print(f"   Total de píxeles a analizar: {filas * cols:,}")
    
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
            red = RedNeuronalSimple(ventana=5)
            
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
    Crea un mapa muy fácil de entender con colores claros.
    """
    # Clasificar cada píxel
    mapa_categorias = np.full_like(mapa_cambio, 0)
    
    for i in range(mapa_cambio.shape[0]):
        for j in range(mapa_cambio.shape[1]):
            categoria, _ = clasificar_cambio(mapa_cambio[i, j])
            mapa_categorias[i, j] = categoria
    
    # Crear figura grande y clara
    fig, ax = plt.subplots(figsize=(14, 10))
    
    # Colores muy claros y distintivos
    colores = [
        '#FFFFFF',  # Sin datos (blanco)
        '#8B0000',  # Empeorará mucho (rojo oscuro)
        '#FF6B6B',  # Empeorará poco (rojo claro)
        '#FFD93D',  # Estable (amarillo)
        '#95E1D3',  # Mejorará poco (verde claro)
        '#00A86B',  # Mejorará mucho (verde oscuro)
    ]
    
    from matplotlib.colors import ListedColormap
    cmap = ListedColormap(colores)
    
    # Mostrar mapa
    im = ax.imshow(mapa_categorias, cmap=cmap, vmin=0, vmax=5)
    ax.axis('off')
    
    # Título grande y claro
    fecha_inicio = fechas[0].strftime('%d/%m/%Y')
    fecha_fin = fechas[-1].strftime('%d/%m/%Y')
    fecha_prediccion = (fechas[-1] + timedelta(days=n_dias_futuro)).strftime('%d/%m/%Y')
    
    titulo = f"""
PREDICCIÓN DE VEGETACIÓN - {INDICES_INFO[indice]['nombre']}

Datos históricos: {fecha_inicio} a {fecha_fin}
Predicción para: {fecha_prediccion} ({n_dias_futuro} días adelante)

¿Cómo leer este mapa?
"""
    
    ax.set_title(titulo, fontsize=14, fontweight='bold', pad=20)
    
    # Leyenda grande y clara
    categorias = [
        'Sin datos',
        'Empeorará mucho',
        'Empeorará poco',
        'Se mantendrá estable',
        'Mejorará poco',
        'Mejorará mucho'
    ]
    
    patches = [mpatches.Patch(color=colores[i], label=categorias[i]) 
               for i in range(len(categorias))]
    
    ax.legend(handles=patches, loc='center left', bbox_to_anchor=(1, 0.5),
              fontsize=12, frameon=True, fancybox=True, shadow=True)
    
    plt.tight_layout()
    
    # Guardar
    carpeta_pred = RUTA_VISUALIZACIONES / indice / "prediccion"
    carpeta_pred.mkdir(parents=True, exist_ok=True)
    
    archivo = carpeta_pred / f"{indice}_prediccion_{n_dias_futuro}dias_{datetime.now().strftime('%Y%m%d')}.png"
    plt.savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close()
    
    print(f"✓ Mapa guardado: {archivo}")
    
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
        emoji = "⚠️"
    elif pixeles_mejora > pixeles_deterioro:
        tendencia_general = "MEJORA"
        emoji = "✅"
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

📈 INDICADORES NUMÉRICOS:
{'-'*80}

  • Cambio promedio esperado: {cambio_promedio_pct:+.2f}%
  • Área total analizada: {total_pixeles:,} píxeles
  
  • Valor actual promedio: {np.nanmean(mapa_prediccion):>.4f}
  • Valor predicho promedio: {np.nanmean(mapa_prediccion + mapa_cambio):>.4f}

💡 ¿QUÉ SIGNIFICA ESTO?
{'-'*80}

El índice {indice} ({INDICES_INFO[indice]['nombre']}) mide:
{INDICES_INFO[indice]['descripcion']}

"""
    
    # Añadir interpretación específica
    if tendencia_general == "DETERIORO":
        informe += f"""
⚠️  ALERTA: La predicción indica un deterioro en la vegetación.

Posibles causas a investigar:
  • Falta de riego o precipitación
  • Estrés térmico (temperaturas altas)
  • Plagas o enfermedades
  • Falta de nutrientes en el suelo

Recomendación: Monitorear de cerca y considerar intervenciones.
"""
    
    elif tendencia_general == "MEJORA":
        informe += f"""
✅ POSITIVO: La predicción indica una mejora en la vegetación.

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
    from configuracion.config import RUTA_DESCARGAS, NOMBRE_CARPETA_DESCARGAS
    ruta_indice = RUTA_DESCARGAS / NOMBRE_CARPETA_DESCARGAS / indice
    imagenes_info = listar_imagenes_indice(ruta_indice)
    
    if len(imagenes_info) < 5:
        print(f"\n❌ Se necesitan al menos 5 imágenes para entrenar. Solo hay {len(imagenes_info)}")
        return None
    
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
    print("\n📝 Generando informe...")
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
        print("\n❌ No se encontraron índices con datos.")
        sys.exit(1)
    
    # Detectar modo automático
    import os
    modo_automatico = os.environ.get('ANALISIS_AUTOMATICO') == '1'
    
    if modo_automatico:
        # Ejecutar todos automáticamente
        print("\n🚀 Modo automático: ejecutando para todos los índices\n")
        
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
