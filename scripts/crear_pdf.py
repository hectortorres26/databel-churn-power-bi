"""Reporte de resultados y guía de lectura; requiere reportlab."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Preformatted
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4

R=Path(__file__).resolve().parents[1]
stats=json.loads((R/'output/metricas.json').read_text(encoding='utf-8'))
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='Portada',fontName='Helvetica-Bold',fontSize=27,leading=32,textColor=colors.HexColor('#102D42'),spaceAfter=20))
styles['BodyText'].leading=15
styles['BodyText'].spaceAfter=10
styles['Heading1'].textColor=colors.HexColor('#087F8C')
story=[]
def p(text,style='BodyText'):story.append(Paragraph(escape(text),styles[style]))
def table(rows):
    data=[[Paragraph(escape(str(c)),styles['BodyText']) for c in row] for row in rows]
    t=Table(data,colWidths=[265,240],repeatRows=1)
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF2F5')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),1,colors.HexColor('#087F8C')),('BOTTOMPADDING',(0,0),(-1,-1),9)]))
    story.append(t)

p('Databel: diagnóstico del abandono de clientes','Portada')
p('Reporte del análisis y guía de Power Query y DAX')
p('Hector Americo Torres Huamani | 11 de noviembre de 2026')
p('Adaptación de un caso educativo de DataCamp. Datos ficticios de telecomunicaciones; análisis descriptivo de una instantánea.')
table([['Indicador','Resultado'],['Clientes',f"{stats['rows']:,}".replace(',', ' ')],['Bajas',f"{stats['churned']:,}".replace(',', ' ')],['Tasa de abandono',f"{stats['churn_rate']*100:.2f}".replace('.', ',')+' %'],['Bajas sin motivo',stats['churned_missing_reason']]])
p('Estado de la entrega','Heading1')
p('El proyecto nativo PBIP cargó correctamente en Power BI Desktop. Sus nueve medidas coinciden con Python en 13 contextos de filtro y 14 agregaciones de gráficos. Revisé las cuatro páginas mediante la herramienta oficial de Microsoft y comprobé cuatro selecciones guardadas de los segmentadores, incluida una combinación, y la recuperación del total. El PDF de presentación conserva las vistas reales del informe. No se ensayaron clics ni hover de tooltips.')
p('DataCamp mostraba los tres capítulos completados antes de esta adaptación. Esa evidencia no constituye una aprobación nueva del archivo de portafolio.')
story.append(PageBreak())
p('1. Contexto, datos y proceso','Heading1')
p('El objetivo es describir dónde se concentra el abandono y proponer preguntas para una investigación de retención. El CSV tiene 6 687 filas y 29 columnas originales, con una fila por cliente. Incluye contrato, edad, estado, planes, consumo, cargos y motivo de baja.')
p('Primera prueba: revisé etiquetas e identificadores y calculé la tasa global y las tasas por contrato. No encontré filas duplicadas ni IDs repetidos. La revisión de nulos mostró 4 918 celdas vacías en categoría y motivo: 4 891 corresponden a clientes que permanecen y 27 a clientes que abandonaron.')
p('Mejora: separé los motivos no aplicables de los no informados. Conservar las 27 bajas evita cambiar silenciosamente el denominador de la distribución. Añadí una comprobación con csv.DictReader, reconciliaciones de totales por segmento y un cruce entre actividad y plan internacional.')
p('La comprobación posterior en Edge detectó cadenas vacías en el modelo inicial: ISBLANK no las contabilizaba. El filtro DAX de motivo igual a texto vacío confirmó las 27 bajas sin información. La transformación Power Query de la plantilla contempla nulos y texto vacío.')
p('El informe tiene cuatro páginas: Resumen; Segmentos; Contratos y planes; Motivos y calidad. La plantilla no incorpora los datos: se cargan desde la fuente original o una ruta local configurable.')
p('2. Resultados y lectura','Heading1')
table([['Segmento','Bajas / clientes; tasa'],['Mensual','1 579 / 3 411; 46,29 %'],['Un año','167 / 1 479; 11,29 %'],['Dos años','50 / 1 797; 2,78 %'],['Competencia como categoría','805 / 1 796 bajas; 44,82 %'],['Motivo sin informar','27 / 1 796 bajas; 1,50 %']])
p('La tasa de contrato responde qué proporción de clientes del segmento abandonó. El porcentaje de motivos responde cómo se distribuyen las bajas. Sus denominadores son distintos y no deben intercambiarse.')
story.append(PageBreak())
p('3. Guía de Power Query','Heading1')
p('FuenteCSV permite elegir la URL oficial o una ruta local. La consulta lee el CSV, promueve encabezados y aplica tipos. El teléfono se elimina porque no es necesario para el análisis; el identificador queda oculto en el modelo para usarlo en recuentos.')
p('Grupo de edad clasifica a los clientes en menores de 30, de 30 a 64 y de 65 o más. Las columnas Categoria de abandono y Motivo de abandono asignan No aplica a clientes retenidos y Sin motivo informado a bajas sin ese dato. El CSV original permanece intacto.')
p('4. Guía de medidas DAX','Heading1')
for name,formula,explanation in [
('Clientes',"DISTINCTCOUNT('Databel - Data'[Customer ID])",'Cuenta clientes distintos dentro de los filtros vigentes. El dato original ya es único, pero la medida explicita la unidad.'),
('Bajas',"CALCULATE([Clientes],\n  KEEPFILTERS('Databel - Data'[Churn Label] = \"Yes\"))",'Restringe el conteo a clientes que abandonaron y conserva los demás filtros. KEEPFILTERS evita sustituir una selección explícita de etiqueta.'),
('Tasa de abandono','DIVIDE([Bajas], [Clientes])','Calcula el cociente en cada contexto y evita dividir directamente entre cero. Se formatea como porcentaje, sin multiplicar otra vez por cien.'),
('Bajas sin motivo',"CALCULATE([Bajas],\n  KEEPFILTERS('Databel - Data'[Motivo de abandono]\n    = \"Sin motivo informado\"))",'Cuantifica la falta de información entre las bajas. El total sin filtros es 27.'),
('IDs duplicados','[Filas] - [Clientes]','Compara filas y clientes únicos. Su valor esperado es cero en este conjunto.')]:
    p(name,'Heading2'); story.append(Preformatted(formula,styles['Code']));p(explanation)
story.append(PageBreak())
p('5. Cómo estudiar y comprobar el informe','Heading1')
p('1. Abrir powerbi/DatabelPresentacion/Databel.pbip, conservando sus carpetas Report y SemanticModel, y actualizar el CSV con FuenteCSV. Como alternativa, abrir entregables/Databel_abandono.pbit. 2. Comprobar 6 687 clientes, 1 796 bajas y 26,86 %. 3. Filtrar un contrato o grupo y comparar con las tablas output. 4. Quitar las selecciones y recuperar los totales. 5. Revisar que los motivos suman 1 796, incluidos 27 sin información.')
p('El notebook valida los recuentos sin depender del motor DAX. Además, Power BI mostró correctamente las selecciones mensual (3 411 clientes; 46,29 %), California y mensual (33; 78,79 %), 65 o más (1 256; 38,46 %) y actividad internacional. Las selecciones se cargaron desde el formato PBIR, sin automatizar el ratón. El detalle está en docs/validacion_dashboard.md y output/validacion_nativa.json.')
p('6. Conclusiones y límites','Heading1')
p('Investigaría la adecuación de los planes internacionales y los contratos mensuales. Entre clientes con actividad internacional, quienes no tienen plan presentan 846 bajas de 2 097 clientes (40,34 %); quienes tienen plan, 36 de 474 (7,59 %). Hay diferencias de composición que este análisis no controla.')
p('No hay dimensión temporal: la antigüedad no permite reconstruir bajas mensuales. Los motivos se conocen después de abandonar y no serían predictores válidos disponibles de antemano. No se entrenó un modelo ni se estimaron ahorros. Los datos son ficticios y las asociaciones no demuestran causalidad.')
p('7. Procedencia y reproducción','Heading1')
p('Fuente: DataCamp, Case Study: Analyzing Customer Churn in Power BI. Los materiales originales y soluciones se conservaron aparte. La plantilla adapta el esquema inicial y añade medidas en español, páginas propias y tratamiento de nulos.')
p('SHA-256 del CSV: '+stats['sha256'])
p('Python: ejecutar scripts/analizar.py con el CSV indicado en data/README.md. Power BI: abrir entregables/Databel_abandono.pbit. Consultar README.md para el estado de validación y las dependencias.')
def footer(canvas,doc):
    canvas.setFont('Helvetica',8);canvas.setFillColor(colors.HexColor('#607483'))
    canvas.drawString(44,26,'Databel | Caso educativo basado en DataCamp')
    canvas.drawRightString(A4[0]-44,26,str(doc.page))
target=R/'docs/Reporte_y_guia_Databel.pdf'
SimpleDocTemplate(str(target),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=42,bottomMargin=46,title='Databel: reporte y guía',author='Hector Americo Torres Huamani').build(story,onFirstPage=footer,onLaterPages=footer)
print(target)
