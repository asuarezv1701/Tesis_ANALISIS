"""
GENERADOR DE REPORTES PDF PROFESIONALES

Crea reportes en PDF con:
- Resumen ejecutivo
- Gráficas principales
- Tablas con resultados
- Interpretación de resultados

Formato profesional listo para incluir en tesis.
"""

import sys
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Agregar rutas
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from configuracion.config import (
    RUTA_REPORTES,
    RUTA_VISUALIZACIONES,
    RUTA_REPORTES_PDF,
    INDICES_INFO,
    obtener_indices_disponibles
)


def crear_portada(pdf, indice):
    """Crea portada del reporte."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Título principal
    plt.text(0.5, 0.7, 'REPORTE DE ANÁLISIS', 
             ha='center', va='center', fontsize=32, fontweight='bold')
    
    plt.text(0.5, 0.62, f'{INDICES_INFO[indice]["nombre"]}',
             ha='center', va='center', fontsize=24, color='#2E86AB')
    
    plt.text(0.5, 0.55, f'({indice})',
             ha='center', va='center', fontsize=18, color='gray')
    
    # Información
    plt.text(0.5, 0.4, 'Análisis Espacial y Temporal de Vegetación',
             ha='center', va='center', fontsize=14)
    
    plt.text(0.5, 0.35, 'UPIITA - Instituto Politécnico Nacional',
             ha='center', va='center', fontsize=12, style='italic')
    
    # Fecha
    plt.text(0.5, 0.2, f'Generado: {datetime.now().strftime("%d de %B de %Y")}',
             ha='center', va='center', fontsize=10, color='gray')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_seccion(pdf, titulo):
    """Agrega página de separación de sección."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('#F5F5F5')
    
    plt.text(0.5, 0.5, titulo,
             ha='center', va='center', fontsize=28, fontweight='bold',
             color='#2E86AB')
    
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_resumen_ejecutivo(pdf, indice):
    """Agrega página con resumen ejecutivo."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Título
    plt.text(0.5, 0.95, 'RESUMEN EJECUTIVO',
             ha='center', va='top', fontsize=20, fontweight='bold')
    
    # Buscar archivos de tendencias temporales
    archivo_tendencias = RUTA_REPORTES / "03_temporal" / f"tendencias_{indice}_{datetime.now().strftime('%Y%m%d')}*.csv"
    archivos = list(RUTA_REPORTES.glob(f"03_temporal/tendencias_{indice}_*.csv"))
    
    if archivos:
        df = pd.read_csv(archivos[-1])  # Más reciente
        
        y_pos = 0.85
        
        # Información general
        plt.text(0.1, y_pos, f'Índice analizado: {INDICES_INFO[indice]["nombre"]}',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        plt.text(0.1, y_pos, f'Total de imágenes: {len(df)}',
                 ha='left', va='top', fontsize=10)
        y_pos -= 0.05
        
        if 'fecha_inicio' in df.columns:
            plt.text(0.1, y_pos, f'Período: {df["fecha_inicio"].iloc[0]} a {df["fecha_fin"].iloc[0]}',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.08
        
        # Resultados de tendencia
        plt.text(0.1, y_pos, 'RESULTADOS DE TENDENCIA TEMPORAL:',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        if 'pendiente' in df.columns:
            pendiente = df['pendiente'].iloc[0]
            r2 = df['r_cuadrado'].iloc[0]
            p_valor = df['p_valor'].iloc[0]
            
            # Interpretación
            if p_valor < 0.05:
                significancia = "SIGNIFICATIVA ✓"
                color_sig = 'green'
            else:
                significancia = "No significativa"
                color_sig = 'orange'
            
            if pendiente > 0:
                tendencia = "CRECIENTE (Mejorando)"
                color_tend = 'green'
            else:
                tendencia = "DECRECIENTE (Deteriorando)"
                color_tend = 'red'
            
            plt.text(0.1, y_pos, f'• Tendencia: {tendencia}',
                     ha='left', va='top', fontsize=11, color=color_tend, fontweight='bold')
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• Pendiente: {pendiente:.6f} unidades/día',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• R² = {r2:.3f} (Fuerza de tendencia)',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• Significancia: {significancia} (p={p_valor:.4f})',
                     ha='left', va='top', fontsize=10, color=color_sig, fontweight='bold')
            y_pos -= 0.06
        
        # Interpretación
        plt.text(0.1, y_pos, '¿QUÉ SIGNIFICA?',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.04
        
        explicacion = f"""
El índice {indice} ({INDICES_INFO[indice]['nombre']}) mide: {INDICES_INFO[indice]['descripcion']}

Durante el período analizado, se observa una tendencia {tendencia.lower()}.
"""
        
        for linea in explicacion.strip().split('\n'):
            plt.text(0.1, y_pos, linea.strip(), ha='left', va='top', fontsize=9, wrap=True)
            y_pos -= 0.03
    
    else:
        plt.text(0.5, 0.5, 'No se encontraron datos de análisis temporal',
                 ha='center', va='center', fontsize=12, color='gray')
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()


def agregar_graficas(pdf, indice):
    """Agrega las gráficas principales al PDF con descripciones detalladas."""
    carpeta_vis = RUTA_VISUALIZACIONES / indice
    
    # Diccionario de descripciones detalladas por tipo de gráfica
    descripciones = {
        'serie_temporal': f"""
INTERPRETACIÓN: Esta gráfica muestra cómo ha cambiado el valor promedio del índice {indice} 
a lo largo del tiempo. Cada punto representa una imagen satelital capturada en una fecha específica.

QUÉ BUSCAR:
• Tendencia general: ¿La línea sube (mejora) o baja (deterioro) con el tiempo?
• Variabilidad: ¿Hay picos o caídas bruscas? Pueden indicar eventos climáticos o cambios estacionales
• Patrón estacional: ¿Se repiten ciclos de subida/bajada? Es normal en vegetación por estaciones
""",
        'histograma': f"""
INTERPRETACIÓN: Este histograma muestra cómo se distribuyen los valores del índice {indice}
en toda el área de estudio. El eje vertical indica cuántos píxeles tienen cada valor.

QUÉ BUSCAR:
• Forma de la distribución: ¿Es una campana simétrica o tiene colas largas?
• Picos múltiples: Pueden indicar diferentes tipos de vegetación o zonas en el área
• Líneas de media/mediana: Si están juntas, la distribución es simétrica
""",
        'boxplot': f"""
INTERPRETACIÓN: Los boxplots muestran el rango de valores para cada fecha. La caja representa
el 50% central de los datos, y los bigotes muestran el rango completo (excluyendo valores atípicos).

QUÉ BUSCAR:
• Altura de las cajas: Mayor altura = mayor variabilidad en esa fecha
• Posición vertical: Cajas más arriba = valores más altos de {indice}
• Puntos aislados: Son valores extremos que se salen del patrón normal
""",
        'mapa_calor': f"""
INTERPRETACIÓN: Este mapa muestra la distribución espacial del índice {indice} en el área de estudio.
Los colores cálidos (rojos) y fríos (verdes/azules) representan diferentes niveles de vegetación.

QUÉ BUSCAR:
• Zonas homogéneas: Áreas grandes del mismo color indican uniformidad
• Patrones espaciales: ¿Hay gradientes? ¿Zonas claramente diferentes?
• Hotspots/Coldspots: Puntos muy diferentes al entorno pueden ser áreas de interés
""",
        'tendencia': f"""
INTERPRETACIÓN: Esta gráfica incluye una línea de tendencia (regresión lineal) que resume
la dirección general del cambio en el tiempo.

QUÉ BUSCAR:
• Pendiente: Si la línea sube, hay mejora; si baja, hay deterioro
• R² (coeficiente de determinación): Valores cercanos a 1.0 indican tendencia fuerte
• Dispersión: Puntos muy alejados de la línea indican mucha variabilidad
""",
        'prediccion': f"""
INTERPRETACIÓN: Este gráfico muestra los valores históricos (datos reales) y la proyección
hacia el futuro basada en patrones identificados por el modelo de inteligencia artificial.

QUÉ BUSCAR:
• Zona sombreada: Representa el intervalo de confianza (incertidumbre de la predicción)
• Continuidad: ¿La predicción sigue el patrón histórico o cambia bruscamente?
• Divergencia: Bandas de confianza que se amplían indican mayor incertidumbre a futuro
"""
    }
    
    # Buscar gráficas por tipo
    tipos_analisis = ['exploratorio', 'temporal', 'espacial', 'prediccion']
    
    for tipo in tipos_analisis:
        carpeta_tipo = carpeta_vis / tipo
        
        if not carpeta_tipo.exists():
            continue
        
        # Agregar sección
        agregar_seccion(pdf, f'ANÁLISIS {tipo.upper()}')
        
        # Buscar imágenes PNG
        imagenes = sorted(carpeta_tipo.glob('*.png'))
        
        for img_path in imagenes[:10]:  # Máximo 10 imágenes por tipo
            fig = plt.figure(figsize=(8.5, 11))
            fig.patch.set_facecolor('white')
            
            # Título con nombre del archivo
            titulo = img_path.stem.replace('_', ' ').title()
            plt.text(0.5, 0.97, titulo,
                     ha='center', va='top', fontsize=14, fontweight='bold',
                     transform=fig.transFigure)
            
            # Cargar y mostrar imagen (ajustada para dejar espacio a descripción)
            img = plt.imread(img_path)
            ax = plt.axes([0.05, 0.35, 0.9, 0.6])
            ax.imshow(img)
            ax.axis('off')
            
            # Agregar descripción detallada según el tipo de gráfica
            descripcion = "QUÉ MUESTRA ESTA GRÁFICA:\n\n"
            
            # Identificar tipo de gráfica por nombre de archivo
            nombre_lower = img_path.stem.lower()
            if 'serie' in nombre_lower or 'temporal' in nombre_lower:
                descripcion += descripciones['serie_temporal']
            elif 'histograma' in nombre_lower or 'distribucion' in nombre_lower:
                descripcion += descripciones['histograma']
            elif 'boxplot' in nombre_lower or 'box' in nombre_lower:
                descripcion += descripciones['boxplot']
            elif 'mapa' in nombre_lower or 'espacial' in nombre_lower or 'hotspot' in nombre_lower:
                descripcion += descripciones['mapa_calor']
            elif 'tendencia' in nombre_lower or 'regresion' in nombre_lower:
                descripcion += descripciones['tendencia']
            elif 'prediccion' in nombre_lower or 'forecast' in nombre_lower:
                descripcion += descripciones['prediccion']
            else:
                descripcion += f"""Esta visualización forma parte del análisis {tipo} del índice {indice}.
Revise los valores, patrones y tendencias mostradas en la gráfica para identificar
características importantes de la vegetación en el área de estudio."""
            
            # Agregar descripción en la parte inferior
            plt.text(0.05, 0.32, descripcion,
                     ha='left', va='top', fontsize=8,
                     transform=fig.transFigure,
                     wrap=True, family='sans-serif',
                     bbox=dict(boxstyle='round', facecolor='#F8F9FA', alpha=0.8, pad=10))
            
            pdf.savefig(fig, bbox_inches='tight')
            plt.close()


def agregar_tabla_resultados(pdf, indice):
    """Agrega tablas con resultados numéricos mejoradas."""
    agregar_seccion(pdf, 'RESULTADOS NUMÉRICOS')
    
    # Buscar CSVs de resultados
    carpetas_reportes = ['03_temporal', '02_espacial', '01_exploratorio']
    
    for carpeta in carpetas_reportes:
        ruta_carpeta = RUTA_REPORTES / carpeta
        
        if not ruta_carpeta.exists():
            continue
        
        # Buscar CSVs de este índice
        csvs = sorted(ruta_carpeta.glob(f'*{indice}*.csv'))
        
        for csv_path in csvs[:5]:  # Máximo 5 tablas por tipo
            try:
                df = pd.read_csv(csv_path)
                
                # Si está vacío, saltar
                if len(df) == 0:
                    continue
                
                # Formatear números para mejor legibilidad
                for col in df.columns:
                    if df[col].dtype in ['float64', 'float32']:
                        # Redondear números flotantes a 4 decimales
                        df[col] = df[col].round(4)
                
                # Limitar columnas para que quepa (máximo 7 para buen espaciado)
                columnas_mostrar = df.columns[:7]
                df_mostrar = df[columnas_mostrar].copy()
                
                # Limitar filas (máximo 25 para evitar tablas muy largas)
                if len(df_mostrar) > 25:
                    df_mostrar = df_mostrar.head(25)
                    nota_truncada = f"(Mostrando primeras 25 de {len(df)} filas)"
                else:
                    nota_truncada = ""
                
                # Acortar nombres de columnas si son muy largos
                df_mostrar.columns = [col[:20] + '...' if len(col) > 20 else col 
                                     for col in df_mostrar.columns]
                
                # Crear figura con más espacio
                fig, ax = plt.subplots(figsize=(8.5, 11))
                ax.axis('tight')
                ax.axis('off')
                
                # Título
                titulo = csv_path.stem.replace('_', ' ').title()
                titulo_y = 0.98 if not nota_truncada else 0.97
                plt.text(0.5, titulo_y, titulo, ha='center', va='top',
                         fontsize=13, fontweight='bold', transform=fig.transFigure)
                
                if nota_truncada:
                    plt.text(0.5, 0.94, nota_truncada, ha='center', va='top',
                             fontsize=9, style='italic', color='gray',
                             transform=fig.transFigure)
                
                # Convertir DataFrame a texto formateado
                cell_text = []
                for idx, row in df_mostrar.iterrows():
                    row_text = []
                    for val in row:
                        if pd.isna(val):
                            row_text.append('-')
                        elif isinstance(val, (int, np.integer)):
                            row_text.append(f'{val:,}')
                        elif isinstance(val, (float, np.floating)):
                            row_text.append(f'{val:.4f}')
                        else:
                            # Acortar texto si es muy largo
                            val_str = str(val)
                            row_text.append(val_str[:25] + '...' if len(val_str) > 25 else val_str)
                    cell_text.append(row_text)
                
                # Crear tabla con mejor formato
                tabla = ax.table(cellText=cell_text,
                                colLabels=df_mostrar.columns,
                                cellLoc='center',
                                loc='center',
                                bbox=[0.05, 0.05, 0.9, 0.85])
                
                # Configuración de fuente y tamaño
                tabla.auto_set_font_size(False)
                tabla.set_fontsize(9)
                
                # Ajustar altura de filas para mejor legibilidad
                tabla.scale(1, 2.0)
                
                # Estilo mejorado
                for (i, j), cell in tabla.get_celld().items():
                    # Encabezado
                    if i == 0:
                        cell.set_facecolor('#2E86AB')
                        cell.set_text_props(weight='bold', color='white', fontsize=10)
                        cell.set_height(0.08)
                    else:
                        # Filas alternas
                        if i % 2 == 0:
                            cell.set_facecolor('#F8F9FA')
                        else:
                            cell.set_facecolor('white')
                        
                        # Bordes suaves
                        cell.set_edgecolor('#E0E0E0')
                        cell.set_linewidth(0.5)
                
                # Descripción de la tabla
                descripcion_tabla = f"""Fuente: {carpeta.replace('_', ' ').title()} | Archivo: {csv_path.name}"""
                plt.text(0.5, 0.01, descripcion_tabla, ha='center', va='bottom',
                         fontsize=7, style='italic', color='gray',
                         transform=fig.transFigure)
                
                pdf.savefig(fig, bbox_inches='tight', dpi=150)
                plt.close()
                
            except Exception as e:
                print(f"⚠️  Error al procesar {csv_path.name}: {e}")
                continue


def generar_reporte_pdf(indice):
    """
    Genera reporte PDF completo para un índice.
    """
    print(f"\n{'='*80}")
    print(f"GENERANDO REPORTE PDF: {indice}")
    print(f"{'='*80}")
    
    # Crear carpeta de PDFs
    RUTA_REPORTES_PDF.mkdir(exist_ok=True, parents=True)
    
    # Nombre del archivo
    archivo_pdf = RUTA_REPORTES_PDF / f"Reporte_{indice}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    
    print(f"\n📄 Creando PDF: {archivo_pdf.name}")
    
    # Crear PDF
    with PdfPages(archivo_pdf) as pdf:
        # 1. Portada
        print("  • Portada")
        crear_portada(pdf, indice)
        
        # 2. Resumen ejecutivo
        print("  • Resumen ejecutivo")
        agregar_resumen_ejecutivo(pdf, indice)
        
        # 3. Gráficas
        print("  • Gráficas de análisis")
        agregar_graficas(pdf, indice)
        
        # 4. Tablas
        print("  • Tablas de resultados")
        agregar_tabla_resultados(pdf, indice)
        
        # Metadata del PDF
        d = pdf.infodict()
        d['Title'] = f'Reporte de Análisis - {indice}'
        d['Author'] = 'Sistema de Análisis de Vegetación - UPIITA'
        d['Subject'] = f'Análisis de {INDICES_INFO[indice]["nombre"]}'
        d['Keywords'] = f'{indice}, vegetación, análisis temporal, análisis espacial'
        d['CreationDate'] = datetime.now()
    
    print(f"\n✅ PDF generado exitosamente")
    print(f"   Ubicación: {archivo_pdf}")
    print(f"   Tamaño: {archivo_pdf.stat().st_size / 1024:.1f} KB")
    
    return archivo_pdf


# ============================================================================
# EJECUCIÓN PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║              GENERADOR DE REPORTES PDF PROFESIONALES                      ║
║                                                                           ║
║  Crea reportes completos en PDF con gráficas y resultados                ║
║  listos para incluir en tu tesis o presentación.                         ║
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
        # Generar PDFs para todos
        print("\n🚀 Modo automático: generando PDFs para todos los índices\n")
        
        for indice in indices_disponibles:
            try:
                generar_reporte_pdf(indice)
            except Exception as e:
                print(f"⚠️  Error al generar PDF para {indice}: {e}")
    
    else:
        # Modo interactivo
        while True:
            print("\n" + "="*80)
            print("MENÚ DE GENERACIÓN DE PDFs")
            print("="*80)
            
            print("\nÍNDICES DISPONIBLES:")
            for i, indice in enumerate(indices_disponibles, 1):
                print(f"  {i}. {indice} - {INDICES_INFO[indice]['nombre']}")
            
            print("\nOPCIONES:")
            print("  A. Generar PDFs de TODOS los índices")
            print("  0. Salir")
            
            opcion = input("\nSelecciona una opción: ").strip().upper()
            
            if opcion == '0':
                break
            
            elif opcion == 'A':
                for indice in indices_disponibles:
                    try:
                        generar_reporte_pdf(indice)
                    except Exception as e:
                        print(f"⚠️  Error: {e}")
            
            elif opcion.isdigit():
                num = int(opcion) - 1
                if 0 <= num < len(indices_disponibles):
                    try:
                        generar_reporte_pdf(indices_disponibles[num])
                    except Exception as e:
                        print(f"⚠️  Error: {e}")
    
    print("\n✓ Proceso completado")
    print(f"\n📁 Los PDFs están en: {RUTA_REPORTES_PDF.absolute()}")
