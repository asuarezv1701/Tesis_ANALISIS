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
    """Agrega página de separación de sección (simplificada)."""
    fig, ax = plt.subplots(figsize=(8.5, 11))
    fig.patch.set_facecolor('#F5F5F5')
    ax.set_facecolor('#F5F5F5')
    
    # Título centrado
    ax.text(0.5, 0.5, titulo,
            ha='center', va='center', fontsize=28, fontweight='bold',
            color='#2E86AB', transform=ax.transAxes)
    
    # Ocultar todos los ejes y bordes
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    ax.set_frame_on(False)
    
    plt.tight_layout()
    pdf.savefig(fig, bbox_inches='tight', facecolor='#F5F5F5')
    plt.close(fig)


def agregar_resumen_ejecutivo(pdf, indice):
    """Agrega página con resumen ejecutivo."""
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    # Título
    plt.text(0.5, 0.95, 'RESUMEN EJECUTIVO',
             ha='center', va='top', fontsize=20, fontweight='bold')
    
    # Buscar archivos de tendencia lineal (nombre correcto)
    archivos = list(RUTA_REPORTES.glob(f"03_temporal/tendencia_lineal_{indice}_*.csv"))
    
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
        
        # Buscar info de período en archivo de estadísticas exploratorias
        archivos_exp = list(RUTA_REPORTES.glob(f"01_exploratorio/analisis_exploratorio_{indice}_*.csv"))
        if archivos_exp:
            df_exp = pd.read_csv(archivos_exp[-1])
            if 'fecha' in df_exp.columns and len(df_exp) > 1:
                plt.text(0.1, y_pos, f'Período: {df_exp["fecha"].iloc[0]} a {df_exp["fecha"].iloc[-1]}',
                         ha='left', va='top', fontsize=10)
                y_pos -= 0.05
                plt.text(0.1, y_pos, f'Total de imágenes analizadas: {len(df_exp)}',
                         ha='left', va='top', fontsize=10)
                y_pos -= 0.08
        
        # Resultados de tendencia
        plt.text(0.1, y_pos, 'RESULTADOS DE TENDENCIA TEMPORAL:',
                 ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.05
        
        if 'pendiente' in df.columns:
            pendiente = df['pendiente'].iloc[0]
            r2 = df['r2'].iloc[0] if 'r2' in df.columns else df.get('r_cuadrado', [0]).iloc[0]
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
            
            # Formatear pendiente de forma legible
            if abs(pendiente) < 0.0001:
                pendiente_str = f'{pendiente:.2e}'  # Notación científica
            else:
                pendiente_str = f'{pendiente:.4f}'
            
            plt.text(0.1, y_pos, f'• Pendiente: {pendiente_str} unidades/día',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            plt.text(0.1, y_pos, f'• R² = {r2:.2f} ({r2*100:.0f}% de varianza explicada)',
                     ha='left', va='top', fontsize=10)
            y_pos -= 0.04
            
            # Formatear p-valor
            if p_valor < 0.001:
                p_valor_str = '< 0.001'
            else:
                p_valor_str = f'{p_valor:.3f}'
            
            plt.text(0.1, y_pos, f'• Significancia: {significancia} (p = {p_valor_str})',
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
            nombre_lower = img_path.stem.lower()
            
            # Para descomposición estacional: mostrar imagen completa sin texto adicional
            if 'descomposicion' in nombre_lower:
                fig = plt.figure(figsize=(8.5, 11))
                fig.patch.set_facecolor('white')
                ax = fig.add_axes([0.02, 0.02, 0.96, 0.96])
                try:
                    img = plt.imread(img_path)
                    ax.imshow(img)
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error al cargar imagen', ha='center', va='center')
                ax.axis('off')
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()
                continue
            
            # Para otras imágenes: layout con descripción
            fig, ax = plt.subplots(figsize=(8.5, 11))
            fig.patch.set_facecolor('white')
            ax.set_facecolor('white')
            
            # Título con nombre del archivo
            titulo = img_path.stem.replace('_', ' ').title()
            fig.text(0.5, 0.97, titulo,
                     ha='center', va='top', fontsize=14, fontweight='bold')
            
            # Cargar y mostrar imagen (ajustada para dejar espacio a descripción)
            try:
                img = plt.imread(img_path)
                # Reposicionar el subplot para la imagen
                ax.set_position([0.05, 0.35, 0.9, 0.58])
                ax.imshow(img)
            except Exception as e:
                ax.text(0.5, 0.5, f'Error al cargar imagen', ha='center', va='center')
            
            ax.axis('off')
            ax.set_frame_on(False)
            
            # Agregar descripción detallada según el tipo de gráfica
            descripcion = "QUÉ MUESTRA ESTA GRÁFICA:\n\n"
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


def exportar_resultados_excel(indice):
    """
    Exporta todos los resultados numéricos a archivos Excel y CSV.
    Más accesibles y fáciles de interpretar que tablas en PDF.
    """
    print(f"  • Exportando resultados numéricos a Excel/CSV...")
    
    # Crear carpeta para exportaciones
    carpeta_export = RUTA_REPORTES_PDF / "datos_exportados"
    carpeta_export.mkdir(exist_ok=True, parents=True)
    
    archivos_creados = []
    
    # Buscar CSVs de resultados
    carpetas_reportes = [
        ('01_exploratorio', 'Análisis Exploratorio'),
        ('02_espacial', 'Análisis Espacial'),
        ('03_temporal', 'Análisis Temporal'),
        ('05_predicciones', 'Predicciones')
    ]
    
    # Intentar crear archivo Excel consolidado
    try:
        archivo_excel = carpeta_export / f"Resultados_Completos_{indice}_{datetime.now().strftime('%Y%m%d')}.xlsx"
        
        with pd.ExcelWriter(archivo_excel, engine='openpyxl') as writer:
            hojas_creadas = 0
            
            for carpeta_nombre, descripcion in carpetas_reportes:
                ruta_carpeta = RUTA_REPORTES / carpeta_nombre
                
                if not ruta_carpeta.exists():
                    continue
                
                # Buscar CSVs de este índice (tomar el más reciente)
                csvs = sorted(ruta_carpeta.glob(f'*{indice}*.csv'), reverse=True)
                
                if not csvs:
                    continue
                
                # Tomar solo el más reciente de cada tipo
                tipos_procesados = set()
                
                for csv_path in csvs:
                    # Extraer tipo de análisis del nombre
                    nombre_base = csv_path.stem.split(f'_{indice}')[0]
                    
                    if nombre_base in tipos_procesados:
                        continue
                    
                    tipos_procesados.add(nombre_base)
                    
                    try:
                        df = pd.read_csv(csv_path)
                        
                        if len(df) == 0:
                            continue
                        
                        # Formatear números para mejor legibilidad
                        for col in df.columns:
                            if df[col].dtype in ['float64', 'float32']:
                                df[col] = df[col].round(4)
                        
                        # Nombre de hoja (máximo 31 caracteres para Excel)
                        nombre_hoja = nombre_base[:28].replace('_', ' ').title()
                        
                        # Evitar nombres duplicados
                        if nombre_hoja in [sheet.title for sheet in writer.book.worksheets if hasattr(writer, 'book')]:
                            nombre_hoja = f"{nombre_hoja[:25]}_{hojas_creadas}"
                        
                        df.to_excel(writer, sheet_name=nombre_hoja, index=False)
                        hojas_creadas += 1
                        
                        if hojas_creadas >= 10:  # Máximo 10 hojas
                            break
                            
                    except Exception as e:
                        continue
                
                if hojas_creadas >= 10:
                    break
            
            if hojas_creadas > 0:
                archivos_creados.append(archivo_excel)
                print(f"    ✓ Excel creado: {archivo_excel.name} ({hojas_creadas} hojas)")
    
    except Exception as e:
        print(f"    ⚠ No se pudo crear Excel (openpyxl no disponible): {e}")
        print("    → Exportando a CSV individuales...")
    
    # También crear CSVs individuales con nombres descriptivos
    for carpeta_nombre, descripcion in carpetas_reportes:
        ruta_carpeta = RUTA_REPORTES / carpeta_nombre
        
        if not ruta_carpeta.exists():
            continue
        
        csvs = sorted(ruta_carpeta.glob(f'*{indice}*.csv'), reverse=True)
        
        if csvs:
            csv_mas_reciente = csvs[0]
            try:
                df = pd.read_csv(csv_mas_reciente)
                if len(df) > 0:
                    # Guardar copia con nombre más claro
                    nombre_nuevo = f"{indice}_{descripcion.replace(' ', '_')}.csv"
                    archivo_csv = carpeta_export / nombre_nuevo
                    df.to_csv(archivo_csv, index=False)
                    archivos_creados.append(archivo_csv)
            except Exception:
                continue
    
    return archivos_creados


def agregar_tabla_resultados(pdf, indice):
    """
    Agrega página informativa sobre los resultados numéricos exportados.
    Los datos detallados se exportan a Excel/CSV para mejor accesibilidad.
    """
    agregar_seccion(pdf, 'RESULTADOS NUMÉRICOS')
    
    # Exportar resultados a Excel/CSV
    archivos_exportados = exportar_resultados_excel(indice)
    
    # Crear página informativa en el PDF
    fig = plt.figure(figsize=(8.5, 11))
    fig.patch.set_facecolor('white')
    
    y_pos = 0.92
    
    # Título
    plt.text(0.5, y_pos, 'DATOS NUMÉRICOS EXPORTADOS',
             ha='center', va='top', fontsize=18, fontweight='bold')
    y_pos -= 0.08
    
    # Explicación
    explicacion = """Los resultados numéricos detallados se han exportado a archivos 
Excel y CSV para facilitar su análisis y uso en otras aplicaciones.

Estos archivos contienen:"""
    
    plt.text(0.1, y_pos, explicacion, ha='left', va='top', fontsize=11,
             wrap=True, linespacing=1.5)
    y_pos -= 0.15
    
    # Lista de contenidos
    contenidos = [
        ("📊 Análisis Exploratorio", "Estadísticas descriptivas por fecha"),
        ("🗺️ Análisis Espacial", "Hotspots, clustering, autocorrelación"),
        ("📈 Análisis Temporal", "Tendencias, velocidad de cambio, estacionalidad"),
        ("🔮 Predicciones", "Proyecciones futuras basadas en patrones históricos")
    ]
    
    for titulo, desc in contenidos:
        plt.text(0.12, y_pos, titulo, ha='left', va='top', fontsize=12, fontweight='bold')
        y_pos -= 0.03
        plt.text(0.15, y_pos, desc, ha='left', va='top', fontsize=10, color='#555555')
        y_pos -= 0.05
    
    y_pos -= 0.05
    
    # Ubicación de archivos
    plt.text(0.1, y_pos, 'UBICACIÓN DE ARCHIVOS:', ha='left', va='top',
             fontsize=12, fontweight='bold', color='#2E86AB')
    y_pos -= 0.05
    
    ruta_export = RUTA_REPORTES_PDF / "datos_exportados"
    plt.text(0.12, y_pos, str(ruta_export), ha='left', va='top',
             fontsize=9, family='monospace', color='#333333',
             bbox=dict(boxstyle='round', facecolor='#F0F0F0', alpha=0.8))
    y_pos -= 0.08
    
    # Lista de archivos creados
    if archivos_exportados:
        plt.text(0.1, y_pos, 'Archivos generados:', ha='left', va='top',
                 fontsize=11, fontweight='bold')
        y_pos -= 0.04
        
        for archivo in archivos_exportados[:6]:  # Máximo 6
            nombre = archivo.name if hasattr(archivo, 'name') else str(archivo)
            plt.text(0.12, y_pos, f"• {nombre}", ha='left', va='top', fontsize=9)
            y_pos -= 0.03
    
    y_pos -= 0.05
    
    # Nota sobre cómo usar
    nota = """CÓMO USAR ESTOS ARCHIVOS:

• Excel (.xlsx): Abrir con Microsoft Excel, Google Sheets o LibreOffice Calc
• CSV (.csv): Importar en cualquier programa de análisis de datos

Los archivos CSV pueden abrirse directamente en Excel haciendo doble clic."""
    
    plt.text(0.1, y_pos, nota, ha='left', va='top', fontsize=10,
             bbox=dict(boxstyle='round', facecolor='#E8F5E9', alpha=0.8, pad=0.5),
             linespacing=1.4)
    
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close()
    
    # Ya no agregar tablas embebidas - los datos están en Excel/CSV
    return


def _agregar_tabla_resultados_legacy(pdf, indice):
    """Versión anterior - Ya no se usa, los datos se exportan a Excel."""
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
                
                # Convertir DataFrame a texto formateado (mejor legibilidad)
                cell_text = []
                for idx, row in df_mostrar.iterrows():
                    row_text = []
                    for col_name, val in zip(df_mostrar.columns, row):
                        if pd.isna(val):
                            row_text.append('-')
                        elif isinstance(val, (int, np.integer)):
                            row_text.append(f'{val:,}')
                        elif isinstance(val, (float, np.floating)):
                            # Formateo inteligente según el valor y tipo de columna
                            col_lower = col_name.lower()
                            abs_val = abs(val)
                            
                            # Porcentajes
                            if 'porcent' in col_lower or '%' in col_lower or 'cv' in col_lower:
                                row_text.append(f'{val:.1f}%')
                            # P-valores
                            elif 'p_valor' in col_lower or 'p-value' in col_lower:
                                if val < 0.001:
                                    row_text.append('< 0.001')
                                else:
                                    row_text.append(f'{val:.3f}')
                            # R² o correlaciones
                            elif 'r_cuadrado' in col_lower or 'r2' in col_lower or 'correlacion' in col_lower:
                                row_text.append(f'{val:.3f}')
                            # Valores muy pequeños (usa notación científica)
                            elif abs_val < 0.0001 and abs_val > 0:
                                row_text.append(f'{val:.2e}')
                            # Valores índice típicos (-1 a 1)
                            elif -1 <= val <= 1:
                                row_text.append(f'{val:.3f}')
                            # Valores mayores
                            elif abs_val >= 1000:
                                row_text.append(f'{val:,.0f}')
                            elif abs_val >= 100:
                                row_text.append(f'{val:.1f}')
                            else:
                                row_text.append(f'{val:.2f}')
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
                print(f"ADVERTENCIA: Error al procesar {csv_path.name}: {e}")
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
    
    print(f"\nCreando PDF: {archivo_pdf.name}")
    
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
    
    print(f"\nPDF generado exitosamente")
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
        print("\nERROR: No se encontraron índices con datos.")
        sys.exit(1)
    
    # Detectar modo automático
    import os
    modo_automatico = os.environ.get('ANALISIS_AUTOMATICO') == '1'
    
    if modo_automatico:
        # Generar PDFs para todos
        print("\nModo automático: generando PDFs para todos los índices\n")
        
        for indice in indices_disponibles:
            try:
                generar_reporte_pdf(indice)
            except Exception as e:
                print(f"ADVERTENCIA: Error al generar PDF para {indice}: {e}")
    
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
    print(f"\nLos PDFs están en: {RUTA_REPORTES_PDF.absolute()}")
