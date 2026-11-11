"""Convierte la adaptación de PbixProj a un proyecto nativo PBIP/PBIR.

Requiere el esqueleto creado con el CLI oficial de Microsoft (ver documentación).
Reutiliza el modelo validado; no reconstruye ni altera los datos.
"""
from pathlib import Path
import copy
import json
import shutil

R=Path(__file__).resolve().parents[1]
source=R/'powerbi/Databel'
target=R/'powerbi/DatabelPresentacion'
report=target/'Databel.Report'
model=target/'Databel.SemanticModel'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,value):
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Desktop puede convertir BIM a TMDL al guardar. Conservar ese modelo en una
# regeneración exclusivamente visual evita mezclar dos formatos en la carpeta.
if not (model/'definition/model.tmdl').exists():
    save(model/'model.bim',read(source/'Model/database.json'))
    save(model/'definition.pbism',{'version':'1.0','settings':{}})
report_config=read(report/'definition/report.json')
report_config['objects']={'outspacePane':[{'properties':{'visible':{'expr':{'Literal':{'Value':'false'}}},'expanded':{'expr':{'Literal':{'Value':'false'}}}}}]}
save(report/'definition/report.json',report_config)
page_ids=[]
total_visuals=0
for page_path in sorted((source/'Report/sections').glob('*/section.json')):
    old=read(page_path);pid=old['name'];page_ids.append(pid)
    page={k:old[k] for k in ('name','displayName','height','width')}
    page.update({'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json','displayOption':'FitToPage','objects':read(page_path.parent/'config.json')['objects']})
    data_visuals=[]
    paths=list(page_path.parent.glob('visualContainers/*/config.json'))
    paths.sort(key=lambda p:(read(p.parent/'visualContainer.json')['y'],read(p.parent/'visualContainer.json')['x']))
    visual_ids={read(path)['name'] for path in paths}
    visual_root=(report/'definition/pages'/pid/'visuals').resolve()
    assert visual_root.is_relative_to(report.resolve())
    if visual_root.exists():
        for old_folder in visual_root.iterdir():
            if old_folder.is_dir() and old_folder.name not in visual_ids:
                shutil.rmtree(old_folder)
    total_visuals+=len(paths)
    for order,path in enumerate(paths):
        cfg=read(path);old_visual=cfg['singleVisual'];kind=old_visual['visualType']
        pos=read(path.parent/'visualContainer.json');pos['tabOrder']=order
        visual={'visualType':kind,'objects':old_visual.get('objects',{}),'visualContainerObjects':old_visual.get('vcObjects',{}),'drillFilterOtherVisuals':True}
        if 'prototypeQuery' in old_visual:
            data_visuals.append((cfg['name'],kind))
            query=old_visual['prototypeQuery'];aliases={v['Name']:v['Entity'] for v in query['From']}
            fields={}
            for select in query['Select']:
                field={k:copy.deepcopy(v) for k,v in select.items() if k!='Name'}
                typ=next(iter(field));ref=field[typ]['Expression']['SourceRef']
                field[typ]['Expression']['SourceRef']={'Entity':aliases[ref['Source']]}
                fields[select['Name']]=field
            state={}
            for role,projections in old_visual['projections'].items():
                state[role]={'projections':[{'field':fields[p['queryRef']],'nativeQueryRef':next(iter(fields[p['queryRef']].values()))['Property'],**p} for p in projections]}
            visual['query']={'queryState':state}
            if kind=='tableEx':
                for projection in state['Values']['projections']:
                    field_name=projection['nativeQueryRef']
                    if field_name=='State':projection['displayName']='Estado'
            if 'OrderBy' in query:
                expr=query['OrderBy'][0]['Expression'];typ=next(iter(expr));field=copy.deepcopy(expr)
                ref=field[typ]['Expression']['SourceRef'];field[typ]['Expression']['SourceRef']={'Entity':aliases[ref['Source']]}
                visual['query']['sortDefinition']={'sort':[{'field':field,'direction':'Descending' if query['OrderBy'][0]['Direction']==2 else 'Ascending'}],'isDefaultSort':False}
        v={'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definition/visualContainer/2.9.0/schema.json','name':cfg['name'],'position':pos,'visual':visual}
        save(report/'definition/pages'/pid/'visuals'/cfg['name']/'visual.json',v)
    # Selecciones de gráficos y segmentadores filtran los indicadores de su página.
    page['visualInteractions']=[{'source':a,'target':b,'type':'DataFilter'} for a,kind in data_visuals if kind!='card' for b,_ in data_visuals if a!=b]
    save(report/'definition/pages'/pid/'page.json',page)
pages_path=report/'definition/pages/pages.json'
pages=read(pages_path);pages['pageOrder']=page_ids;pages['activePageName']=page_ids[0];save(pages_path,pages)
# Quita únicamente la página vacía del scaffold; conserva cualquier página ajena.
for p in (report/'definition/pages').glob('*/page.json'):
    if p.parent.name not in page_ids and not (p.parent/'visuals').exists():
        p.unlink();p.parent.rmdir()
print(f'PBIP creado con {len(page_ids)} páginas, {total_visuals} objetos y el modelo validado.')
