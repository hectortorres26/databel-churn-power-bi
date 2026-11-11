"""Genera el notebook y el reporte a partir de agregaciones ya verificadas."""
from pathlib import Path
import json
import nbformat
from nbclient import NotebookClient

R=Path(__file__).resolve().parents[1]
nb=nbformat.v4.new_notebook()
nb.cells=[
nbformat.v4.new_markdown_cell('# Databel: validación independiente\n\nEste notebook complementa la plantilla de Power BI. Datos ficticios del caso educativo de DataCamp. Evalúa una instantánea, no una serie temporal.'),
nbformat.v4.new_code_cell("from pathlib import Path\nimport pandas as pd\nroot = Path.cwd()\narchivo = root / 'data/Databel - Data.csv'\ndf = pd.read_csv(archivo)\nassert df['Customer ID'].is_unique\nassert set(df['Churn Label']) == {'Yes', 'No'}\ndf.shape"),
nbformat.v4.new_markdown_cell('## Indicadores\nLa tasa se calcula sobre todos los clientes del contexto. No es una tasa mensual.'),
nbformat.v4.new_code_cell("clientes = len(df)\nbajas = int(df['Churn Label'].eq('Yes').sum())\npd.Series({'Clientes': clientes, 'Bajas': bajas, 'Tasa de abandono': bajas/clientes})"),
nbformat.v4.new_markdown_cell('## Contratos\nUna tasa alta y un volumen alto son señales distintas. La comparación es descriptiva.'),
nbformat.v4.new_code_cell("resumen = df.assign(baja=df['Churn Label'].eq('Yes')).groupby('Contract Type')['baja'].agg(clientes='size', bajas='sum')\nresumen['tasa'] = resumen['bajas']/resumen['clientes']\nassert resumen['clientes'].sum() == clientes\nassert resumen['bajas'].sum() == bajas\nresumen"),
nbformat.v4.new_markdown_cell('## Motivos ausentes\nSe conservan 27 bajas sin motivo. El denominador de los porcentajes es el total de bajas.'),
nbformat.v4.new_code_cell("perdidos = df.loc[df['Churn Label'].eq('Yes')]\nmotivos = perdidos['Churn Category'].fillna('Sin motivo informado').value_counts().to_frame('bajas')\nmotivos['porcentaje_de_bajas'] = motivos['bajas']/bajas\nassert motivos['bajas'].sum() == bajas\nmotivos"),
nbformat.v4.new_markdown_cell('## Plan internacional\nCruzo actividad y suscripción para evitar atribuir al plan la composición de sus usuarios.'),
nbformat.v4.new_code_cell("cruce = df.assign(baja=df['Churn Label'].eq('Yes')).groupby(['Intl Active','Intl Plan'])['baja'].agg(clientes='size', bajas='sum')\ncruce['tasa'] = cruce['bajas']/cruce['clientes']\ncruce"),
nbformat.v4.new_markdown_cell('## Comprobación del modelo propio\nLa plantilla cargó en Power BI Desktop. Las consultas DAX se contrastaron con pandas en 13 contextos de filtro y para las 11 combinaciones de dimensiones y medidas de los gráficos. Esta celda resume la evidencia guardada; no vuelve a conectarse a Power BI. Las nueve medidas y Power Query coinciden con la fuente publicada.'),
nbformat.v4.new_code_cell("import json\nvalidacion = json.loads((root / 'output/validacion_motor.json').read_text(encoding='utf-8-sig'))\nassert validacion['status'] == 'OK'\nassert validacion['source_matches_loaded_model']\npd.Series({'Pruebas de filtros': len(validacion['filter_cases']), 'Combinaciones de gráficos': len(validacion['visual_cases']), 'Medidas comprobadas': validacion['measures'], 'Fallos': len(validacion['failures'])})"),
nbformat.v4.new_markdown_cell('## Conclusión\nLos contratos mensuales concentran 1 579 bajas y una tasa del 46,29 %. La competencia representa el 44,82 % de todas las bajas. Estas asociaciones orientan una investigación, pero no prueban causalidad.\n\nLa revisión conserva 51 estados y territorios y 21 motivos, añade un filtro de contrato y contextualiza las tasas con clientes y bajas. El cálculo del modelo propio está validado. Sigue pendiente comprobar con clics los filtros, tooltips y páginas en Power BI: las consultas no sustituyen esa revisión visual. El procedimiento y sus límites están en docs/validacion_dashboard.md.')
]
nb.metadata['kernelspec']={'name':'python3','display_name':'Python 3','language':'python'}
client=NotebookClient(nb,timeout=120,kernel_name='python3',resources={'metadata':{'path':str(R)}})
client.execute()
nbformat.write(nb,R/'Validacion_Databel.ipynb')
print('Notebook ejecutado sin errores.')
