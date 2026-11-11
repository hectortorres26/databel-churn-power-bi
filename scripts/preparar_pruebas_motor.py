"""Prepara casos de filtro y agregaciones esperadas desde el CSV independiente."""
from pathlib import Path
import json
import pandas as pd

R = Path(__file__).resolve().parents[1]
df = pd.read_csv(R / 'data/Databel - Data.csv')
df['Grupo de edad'] = df['Age'].map(lambda age: 'Menores de 30' if age < 30 else '65 o más' if age >= 65 else '30 a 64')
for original, derived in [('Churn Category', 'Categoria de abandono'), ('Churn Reason', 'Motivo de abandono')]:
    df[derived] = df[original].fillna('Sin motivo informado').where(df['Churn Label'].eq('Yes'), 'No aplica')

def measures(data):
    n = len(data)
    yes = data['Churn Label'].eq('Yes')
    no = data['Churn Label'].eq('No')
    # DISTINCTCOUNT/COUNTROWS devuelve BLANK sobre un conjunto vacío.
    bajas = int(yes.sum()) or None
    return {'Clientes': n or None, 'Bajas': bajas,
            'Tasa de abandono': bajas / n if bajas and n else None,
            'Clientes retenidos': int(no.sum()) or None,
            'Bajas sin motivo': int((yes & data['Motivo de abandono'].eq('Sin motivo informado')).sum()) or None,
            'Cargo mensual medio': float(data['Monthly Charge'].mean()) if n else None,
            'Llamadas de servicio medias': float(data['Customer Service Calls'].mean()) if n else None,
            'Filas': n or None, 'IDs duplicados': 0 if n else None}

specs = [('Total', {}), ('Contrato mensual', {'Contract Type':'Month-to-Month'}),
         ('Contrato anual', {'Contract Type':'One Year'}), ('Contrato dos años', {'Contract Type':'Two Year'}),
         ('Edad menor de 30', {'Grupo de edad':'Menores de 30'}), ('Edad 65 o más', {'Grupo de edad':'65 o más'}),
         ('Estado CA', {'State':'CA'}), ('CA y mensual', {'State':'CA', 'Contract Type':'Month-to-Month'}),
         ('Actividad internacional sin plan', {'Intl Active':'Yes', 'Intl Plan':'no'}),
         ('Actividad internacional con plan', {'Intl Active':'Yes', 'Intl Plan':'yes'}),
         ('Solo clientes retenidos', {'Churn Label':'No'}),
         ('Sin registros', {'State':'__SIN_ESTADO__'}), ('Total restablecido', {})]
tests=[]
for name, filters in specs:
    data=df
    for field,value in filters.items(): data=data[data[field].eq(value)]
    tests.append({'name':name, 'filters':filters, 'expected':measures(data)})

visuals=[]
for path in (R/'powerbi/Databel/Report/sections').glob('*/visualContainers/*/config.json'):
    sv=json.loads(path.read_text(encoding='utf-8'))['singleVisual']
    if sv['visualType'] not in ('clusteredBarChart','clusteredColumnChart','tableEx'): continue
    fields=sv['prototypeQuery']['Select']
    column=fields[0]['Column']['Property']
    measured_fields=fields[1:] if sv['visualType']=='tableEx' else fields[1:2]
    for measured in measured_fields:
        measure=measured['Measure']['Property']
        groups=[]
        for category, data in df.groupby(column, dropna=False):
            value=measures(data)[measure]
            if value is not None: groups.append({'category':str(category), 'value':value})
        name=path.parent.name[2:]+(' / '+measure if sv['visualType']=='tableEx' else '')
        visuals.append({'name':name, 'column':column, 'measure':measure, 'expected':groups})
out={'filter_cases':tests, 'visual_cases':visuals}
(R/'output/pruebas_motor_esperadas.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'{len(tests)} casos de filtro; {len(visuals)} combinaciones de gráficos.')
