"""Construye una adaptación propia sobre el esquema inicial atribuido a DataCamp."""
from pathlib import Path
import json, shutil
import report_helpers as h

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'trabajo/modelo_base'
DEST=ROOT/'powerbi/Databel'
DEST.mkdir(parents=True,exist_ok=True)
# Las páginas son generadas por este script; regenerarlas evita visuales antiguos
# después de cambiar títulos. El destino se valida antes de borrar esta salida.
sections=(DEST/'Report/sections').resolve()
if not sections.is_relative_to((ROOT/'powerbi/Databel/Report').resolve()):
    raise ValueError('Destino de páginas fuera del proyecto')
if sections.exists(): shutil.rmtree(sections)
for file in BASE.iterdir():
    if file.name in ['Report','Model']: continue
    if file.is_dir(): shutil.copytree(file,DEST/file.name,dirs_exist_ok=True)
    else: shutil.copy2(file,DEST/file.name)
for name in ['config.json','report.json']:
    h.save(DEST/'Report'/name,h.read(BASE/'Report'/name))
m=h.read(BASE/'Model/database.json')
m['name']='Databel_portafolio'
table=m['model']['tables'][0]
m['model']['tables']=[table]
m['model'].pop('cultures',None)
table['columns']=[c for c in table['columns'] if c['name']!='Phone Number']
for c in table['columns']:
    if c['name']=='Customer ID':c['isHidden']=True
    if c['name']=='State':c['dataCategory']='StateOrProvince'
source='https://assets.datacamp.com/production/repositories/5993/datasets/d6a32ec1293e10bd44441b4f8b4fe60b9776e0d1/Databel%20-%20Data.csv'
m['model']['expressions']=[{'name':'FuenteCSV','kind':'m','expression':f'"{source}" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'}]
types=', '.join('{"'+c['name']+'", '+{'int64':'Int64.Type','double':'type number','string':'type text'}.get(c['dataType'],'type text')+'}' for c in table['columns'])
query=f'''let
    Archivo = if Text.StartsWith(FuenteCSV, "https://") then Web.Contents(FuenteCSV) else File.Contents(FuenteCSV),
    CSV = Csv.Document(Archivo,[Delimiter=",", Columns=29, Encoding=1252, QuoteStyle=QuoteStyle.Csv]),
    Cabeceras = Table.PromoteHeaders(CSV, [PromoteAllScalars=true]),
    SinTelefono = Table.RemoveColumns(Cabeceras, {{"Phone Number"}}),
    Tipos = Table.TransformColumnTypes(SinTelefono, {{{types}}}, "en-US"),
    Edades = Table.AddColumn(Tipos, "Grupo de edad", each if [Age] < 30 then "Menores de 30" else if [Age] >= 65 then "65 o más" else "30 a 64", type text),
    Categorias = Table.AddColumn(Edades, "Categoria de abandono", each if [Churn Label] <> "Yes" then "No aplica" else if [Churn Category] = null or Text.Trim([Churn Category]) = "" then "Sin motivo informado" else [Churn Category], type text),
    Motivos = Table.AddColumn(Categorias, "Motivo de abandono", each if [Churn Label] <> "Yes" then "No aplica" else if [Churn Reason] = null or Text.Trim([Churn Reason]) = "" then "Sin motivo informado" else [Churn Reason], type text)
in
    Motivos'''
table['partitions'][0]['source']['expression']=query.splitlines()
for col in ['Grupo de edad','Categoria de abandono','Motivo de abandono']:
    table['columns'].append({'name':col,'dataType':'string','sourceColumn':col,'summarizeBy':'none'})
t="'Databel - Data'"
defs=[
 ('Clientes',f'DISTINCTCOUNT({t}[Customer ID])','#,0'),
 ('Bajas',f'CALCULATE([Clientes], KEEPFILTERS({t}[Churn Label] = "Yes"))','#,0'),
 ('Tasa de abandono','DIVIDE([Bajas], [Clientes])','0.00%'),
 ('Clientes retenidos',f'CALCULATE([Clientes], KEEPFILTERS({t}[Churn Label] = "No"))','#,0'),
 ('Bajas sin motivo',f'CALCULATE([Bajas], KEEPFILTERS({t}[Motivo de abandono] = "Sin motivo informado"))','#,0'),
 ('Cargo mensual medio',f'AVERAGE({t}[Monthly Charge])','#,0.00'),
 ('Llamadas de servicio medias',f'AVERAGE({t}[Customer Service Calls])','0.00'),
 ('Filas',f'COUNTROWS({t})','#,0'),
 ('IDs duplicados','[Filas] - [Clientes]','#,0'),
]
table['measures']=[{'name':name,'expression':expr,'formatString':fmt,'displayFolder':'Indicadores'} for name,expr,fmt in defs]
h.save(DEST/'Model/database.json',m)
(ROOT/'docs').mkdir(exist_ok=True)
(ROOT/'docs/medidas.dax').write_text('\n\n'.join(name+' =\n'+expr for name,expr,fmt in defs)+'\n',encoding='utf-8')
(ROOT/'docs/transformaciones.pq').write_text(query+'\n',encoding='utf-8')
h.SCHEMA={table['name']:{c['name']:c['dataType'] for c in table['columns']}}
T=table['name']
from diseno_visual import build
build(DEST,T)
cfg=h.read(DEST/'Report/config.json');cfg['activeSectionIndex']=0;h.save(DEST/'Report/config.json',cfg)
print('Modelo con',len(table['measures']),'medidas y diseño actualizado en',DEST)