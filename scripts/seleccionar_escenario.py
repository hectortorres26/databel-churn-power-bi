"""Selecciona escenarios guardados en los slicers PBIR para validación nativa.

Usar 'base' al terminar: elimina las selecciones de prueba. No modifica el modelo.
"""
from pathlib import Path
import argparse,json
import pandas as pd

R=Path(__file__).resolve().parents[1]
cases={
 'base':{},
 'mensual':{'Contract Type':'Month-to-Month'},
 'ca_mensual':{'Contract Type':'Month-to-Month','State':'CA'},
 'mayores':{'Grupo de edad':'65 o más'},
 'internacional':{'Intl Active':'Yes'},
}
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('escenario',choices=cases)
args=parser.parse_args();selection=cases[args.escenario]
for p in (R/'powerbi/DatabelPresentacion/Databel.Report/definition/pages').glob('*/visuals/*/visual.json'):
 v=json.loads(p.read_text(encoding='utf-8'));visual=v['visual']
 if visual['visualType']!='slicer':continue
 col=visual['query']['queryState']['Values']['projections'][0]['field']['Column']['Property']
 objects=visual.setdefault('objects',{});objects.pop('general',None)
 if col in selection:
  objects['general']=[{'properties':{'filter':{'filter':{
   'Version':2,'From':[{'Name':'d','Entity':'Databel - Data','Type':0}],
   'Where':[{'Condition':{'In':{'Expressions':[{'Column':{'Expression':{'SourceRef':{'Source':'d'}},'Property':col}}],
             'Values':[[{'Literal':{'Value':"'"+selection[col].replace("'","''")+"'"}}]]}}}]
  }}}}]
 p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
data=pd.read_csv(R/'data/Databel - Data.csv')
data['Grupo de edad']=data.Age.map(lambda a:'Menores de 30' if a<30 else '65 o más' if a>=65 else '30 a 64')
for k,value in selection.items():data=data[data[k].eq(value)]
yes=int(data['Churn Label'].eq('Yes').sum())
print(json.dumps({'escenario':args.escenario,'selecciones':selection,'clientes':len(data),'bajas':yes,'retenidos':len(data)-yes,'tasa':yes/len(data)},ensure_ascii=True))
