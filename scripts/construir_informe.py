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
def page(i,name,subtitle):
    p=h.page(DEST,f'{i:03}_{name.replace(" ","_")}',name,i)
    h.textbox(p,'Cabecera',['DATABEL | '+name,subtitle],24,20,1232,95,24,True)
    return p
def metric(p,i,name,fmt='#,0'):
    h.visual(p,'KPI '+str(i),'card',[h.field('Values',T,name,True,fmt)],24+i*312,145,296,110,name)
def chart(p,name,col,measure,x,y,w=608,height=260):
    fmt='0.00%' if measure=='Tasa de abandono' else '#,0'
    fields=[h.field('Category',T,col,False),h.field('Y',T,measure,True,fmt)]
    if measure=='Tasa de abandono':
        fields += [h.field('Tooltips',T,'Clientes'),h.field('Tooltips',T,'Bajas')]
    h.visual(p,name,'clusteredBarChart',fields,x,y,w,height,name)
p=page(0,'Resumen','Caso educativo de DataCamp · Instantánea de clientes · Sin dimensión temporal')
for i,n in enumerate(['Clientes','Bajas','Tasa de abandono','Clientes retenidos']):metric(p,i,n,'0.00%' if i==2 else '#,0')
chart(p,'Bajas por categoría','Categoria de abandono','Bajas',24,285)
chart(p,'Abandono por contrato','Contract Type','Tasa de abandono',648,285)
h.visual(p,'Filtro estado','slicer',[h.field('Values',T,'State',False)],24,575,400,90,'Estado')
h.visual(p,'Filtro edad','slicer',[h.field('Values',T,'Grupo de edad',False)],440,575,400,90,'Grupo de edad')
h.visual(p,'Filtro contrato','slicer',[h.field('Values',T,'Contract Type',False)],856,575,400,90,'Tipo de contrato')
h.textbox(p,'Criterio',['Cómo leer el diagnóstico','Tasa = bajas / clientes del segmento. Al pasar por una barra de tasa, el tooltip muestra clientes y bajas.','Los filtros de esta página se combinan. Borra sus selecciones para recuperar los totales.','Datos ficticios de DataCamp; instantánea sin dimensión temporal. Las asociaciones no prueban causalidad.'],24,690,1232,135,18)
p=page(1,'Segmentos','Comparación descriptiva · Evaluar tasas junto con el tamaño de cada segmento')
chart(p,'Abandono por edad','Grupo de edad','Tasa de abandono',24,145)
chart(p,'Clientes por edad','Grupo de edad','Clientes',648,145)
chart(p,'Abandono por estado','State','Tasa de abandono',24,425,height=260)
chart(p,'Abandono y grupos','Group','Tasa de abandono',648,425,height=260)
h.textbox(p,'Nota',['Interpretación','Los estados se ordenan por tasa. El tooltip permite contrastar cada porcentaje con clientes y bajas.','El gráfico conserva los 51 estados y territorios. Los segmentos pequeños requieren cautela.'],24,710,1232,115,18)
p=page(2,'Contratos y planes','Revisar la adecuación del plan y el tipo de contrato antes de proponer acciones')
chart(p,'Tasa por método de pago','Payment Method','Tasa de abandono',24,145)
chart(p,'Tasa por plan internacional','Intl Plan','Tasa de abandono',648,145)
chart(p,'Tasa por datos ilimitados','Unlimited Data Plan','Tasa de abandono',24,425)
chart(p,'Tasa por llamadas a servicio','Customer Service Calls','Tasa de abandono',648,425)
h.visual(p,'Actividad internacional','slicer',[h.field('Values',T,'Intl Active',False)],24,705,480,90,'Actividad internacional')
h.textbox(p,'Nota',['Cruzar actividad y plan','El filtro de actividad internacional compara usuarios que llaman al exterior y quienes no.','La tarifa mensual no representa ingresos perdidos ni ahorro potencial.'],530,705,726,120,18)
p=page(3,'Motivos y calidad','Reconciliar el total antes de interpretar por qué se produce el abandono')
metric(p,0,'Clientes');metric(p,1,'Bajas');metric(p,2,'Bajas sin motivo');metric(p,3,'IDs duplicados')
chart(p,'Motivos declarados de las bajas','Motivo de abandono','Bajas',24,285,1232,380)
h.textbox(p,'Nota',['Calidad y procedencia','Se conservan los 21 motivos, incluidos los 27 casos sin información. El detalle también está en el repositorio.','Las celdas vacías de clientes retenidos no son bajas. Se excluyó el teléfono y se ocultó el identificador de cliente.','Caso educativo de DataCamp. Consulta el README para fuentes, reproducción y estado de validación.'],24,690,1232,135,18)
cfg=h.read(DEST/'Report/config.json');cfg['activeSectionIndex']=0;h.save(DEST/'Report/config.json',cfg)
print('Modelo con',len(table['measures']),'medidas y 4 páginas construido en',DEST)
