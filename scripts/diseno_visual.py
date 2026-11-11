"""Diseño editorial de Databel. Modifica el informe, no los cálculos del modelo."""
from pathlib import Path
import shutil
import report_helpers as h

WIDTH, HEIGHT = 1440, 900

def text(page, name, lines, box, sizes, background, foreground, bold_first=True):
    x,y,w,height=box
    pos={'x':x,'y':y,'width':w,'height':height,'z':0}
    paragraphs=[]
    for i,line in enumerate(lines):
        paragraphs.append({'textRuns':[{'value':line,'textStyle':{
            'fontFamily':'Segoe UI','fontSize':f'{sizes[min(i,len(sizes)-1)]}pt',
            'fontWeight':'bold' if (i==0 and bold_first) else 'normal',
            'color':foreground[min(i,len(foreground)-1)]}}]})
    cfg={'name':h.uid(str(page)+name),'layouts':[{'id':0,'position':pos}],
         'singleVisual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':paragraphs}}]},
          'vcObjects':{'background':[{'properties':{'show':h.lit('true'),'color':h.color(background),'transparency':h.lit('0D')}}]}}}
    d=page/'visualContainers'/('p_'+name)
    h.save(d/'config.json',cfg);h.save(d/'visualContainer.json',pos)

def build(dest, table):
    dest=Path(dest).resolve()
    sections=(dest/'Report/sections').resolve()
    assert sections.is_relative_to(dest/'Report')
    if sections.exists():shutil.rmtree(sections)
    def page(i,name,title,subtitle):
        p=h.page(dest,f'{i:03}_{name.replace(" ","_")}',name,i)
        spec=h.read(p/'section.json');spec.update(width=WIDTH,height=HEIGHT);h.save(p/'section.json',spec)
        config=h.read(p/'config.json');config['objects']['background'][0]['properties']['color']=h.color(h.PAPER);h.save(p/'config.json',config)
        text(p,'Cabecera',[f'DATABEL   /   {i+1:02d}   {name.upper()}',title,subtitle],(32,20,1376,112),[11,28,12],h.INK,['#89D4CA','#FFFFFF','#CFDDE5'])
        text(p,'Pie',['Hector Americo Torres Huamani  ·  Caso educativo de DataCamp  ·  Datos ficticios, sin dimensión temporal'],(32,860,1376,34),[10],h.PAPER,[h.MUTED],False)
        return p
    def card(p,name,x,y,w=326,height=112,caption=None,accent=None):
        fmt='0.00%' if name=='Tasa de abandono' else '0.00' if name=='Llamadas de servicio medias' else '#,0.00' if name=='Cargo mensual medio' else '#,0'
        h.visual(p,'KPI '+name,'card',[h.field('Values',table,name,True,fmt)],x,y,w,height,caption or name,accent)
    def chart(p,name,col,measure,box,kind='clusteredBarChart',ascending=False):
        rate=measure=='Tasa de abandono';fmt='0.00%' if rate else '#,0'
        fields=[h.field('Category',table,col,False),h.field('Y',table,measure,True,fmt)]
        if rate:fields += [h.field('Tooltips',table,'Clientes'),h.field('Tooltips',table,'Bajas')]
        h.visual(p,name,kind,fields,*box,name,h.CHURN if rate else h.VOLUME)
        if ascending:
            folder=p/'visualContainers'/('p_'+name)
            cfg=h.read(folder/'config.json');q=cfg['singleVisual']['prototypeQuery']
            q['OrderBy']=[{'Direction':1,'Expression':{k:v for k,v in q['Select'][0].items() if k!='Name'}}]
            h.save(folder/'config.json',cfg)
            query=h.read(folder/'query.json');query['Commands'][0]['SemanticQueryDataShapeCommand']['Query']=q;h.save(folder/'query.json',query)
    def slicer(p,name,col,box):
        h.visual(p,'Filtro '+name,'slicer',[h.field('Values',table,col,False)],*box,name)
    def detail(p,name,col,measures,box):
        fields=[h.field('Values',table,col,False)]+[h.field('Values',table,m,True,'0.00%' if m=='Tasa de abandono' else '#,0') for m in measures]
        h.visual(p,name,'tableEx',fields,*box,name)
        folder=p/'visualContainers'/('p_'+name)
        cfg=h.read(folder/'config.json');q=cfg['singleVisual']['prototypeQuery']
        q['OrderBy']=[{'Direction':2,'Expression':{k:v for k,v in q['Select'][-1].items() if k!='Name'}}]
        h.save(folder/'config.json',cfg)
        query=h.read(folder/'query.json');query['Commands'][0]['SemanticQueryDataShapeCommand']['Query']=q;h.save(folder/'query.json',query)
    def note(p,name,title,body,box):
        text(p,name,[title,*body],box,[14,12], '#E8EEEF',[h.INK,h.MUTED])

    p=page(0,'Resumen','Abandono de clientes','Una lectura del volumen, la tasa y los principales segmentos de abandono.')
    slicer(p,'Estado','State',(32,152,440,90))
    slicer(p,'Grupo de edad','Grupo de edad',(500,152,440,90))
    slicer(p,'Contrato','Contract Type',(968,152,440,90))
    for x,name,caption,accent in [(32,'Clientes','CLIENTES ANALIZADOS',h.INK),(382,'Bajas','BAJAS',h.CHURN),(732,'Tasa de abandono','TASA DE ABANDONO',h.CHURN),(1082,'Clientes retenidos','CLIENTES RETENIDOS',h.RETAINED)]:
        card(p,name,x,258,height=112,caption=caption,accent=accent)
    chart(p,'Abandono por contrato','Contract Type','Tasa de abandono',(32,386,676,350))
    chart(p,'Bajas por categoría','Categoria de abandono','Bajas',(732,386,676,350))
    note(p,'Lectura de tasas','TASAS Y VOLUMEN RESPONDEN PREGUNTAS DISTINTAS',['Naranja: proporción que abandona dentro de cada segmento.','Azul: número de clientes o bajas. Verde: clientes retenidos.'],(32,760,676,82))
    note(p,'Uso de filtros','EXPLORACIÓN POR SEGMENTO',['Los tres filtros se combinan y actualizan esta página.','Quitar sus selecciones recupera el total de la muestra.'],(732,760,676,82))

    p=page(1,'Segmentos','¿Dónde se concentra el abandono?','Comparar la tasa junto con el tamaño del segmento evita conclusiones por porcentajes aislados.')
    for x,name,accent in [(32,'Clientes',h.INK),(382,'Bajas',h.CHURN),(732,'Tasa de abandono',h.CHURN),(1082,'Clientes retenidos',h.RETAINED)]:card(p,name,x,152,accent=accent)
    chart(p,'Abandono por edad','Grupo de edad','Tasa de abandono',(32,288,444,246))
    chart(p,'Clientes por edad','Grupo de edad','Clientes',(498,288,444,246))
    chart(p,'Abandono según pertenencia a grupo','Group','Tasa de abandono',(964,288,444,246))
    detail(p,'Estado · tasa y tamaño del segmento','State',['Clientes','Bajas','Tasa de abandono'],(32,558,910,282))
    note(p,'Nota geográfica','UN PORCENTAJE NECESITA SU DENOMINADOR',['La tabla conserva 51 estados y territorios.','Incluye clientes, bajas y tasa en la misma fila.','Los segmentos pequeños requieren cautela.'],(964,558,444,132))
    slicer(p,'Estado','State',(964,712,444,90))
    text(p,'Ayuda geográfica',['Desplazar la tabla permite consultar todos los estados.'],(964,808,444,34),[11],h.PAPER,[h.MUTED],False)

    p=page(2,'Contratos y planes','Planes, pagos y atención al cliente','Cruzar actividad internacional y plan permite comparar perfiles de uso más concretos.')
    slicer(p,'Actividad internacional','Intl Active',(32,152,430,90))
    card(p,'Clientes',486,152,290,112,'CLIENTES DEL CONTEXTO',h.INK)
    card(p,'Tasa de abandono',800,152,290,112,'TASA DE ABANDONO',h.CHURN)
    card(p,'Llamadas de servicio medias',1114,152,294,112,'LLAMADAS · MEDIA',h.VOLUME)
    chart(p,'Abandono por método de pago','Payment Method','Tasa de abandono',(32,288,676,252))
    chart(p,'Abandono por plan internacional','Intl Plan','Tasa de abandono',(732,288,676,252))
    chart(p,'Abandono por datos ilimitados','Unlimited Data Plan','Tasa de abandono',(32,564,676,252))
    chart(p,'Abandono por llamadas a soporte','Customer Service Calls','Tasa de abandono',(732,564,676,252),'clusteredColumnChart',True)
    text(p,'Nota de lectura',['Las tasas parten de cero y usan la misma escala. Las llamadas se ordenan de 0 a 5; describen una asociación, no una causa.'],(32,822,1376,34),[11],h.PAPER,[h.MUTED],False)

    p=page(3,'Motivos y calidad','Motivos declarados y calidad del dato','Mantener los casos sin información permite reconciliar el diagnóstico con el total de bajas.')
    for x,name,caption,accent in [(32,'Bajas','BAJAS TOTALES',h.CHURN),(382,'Bajas sin motivo','BAJAS SIN MOTIVO',h.CHURN),(732,'IDs duplicados','IDS DUPLICADOS',h.RETAINED),(1082,'Clientes','CLIENTES ANALIZADOS',h.INK)]:card(p,name,x,152,caption=caption,accent=accent)
    chart(p,'Bajas por categoría','Categoria de abandono','Bajas',(32,288,480,480))
    detail(p,'Detalle completo de motivos','Motivo de abandono',['Bajas'],(536,288,872,550))
    note(p,'Calidad','CRITERIO DE CALIDAD',['«Sin motivo informado» conserva las bajas sin respuesta.','«No aplica» corresponde a clientes que permanecen.'],(32,790,480,70))
    print('Rediseño construido: 1440 × 900; cuatro páginas, tablas de detalle y colores semánticos.')

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]
    dest=root/'powerbi/Databel'
    model=h.read(dest/'Model/database.json');table=model['model']['tables'][0]
    h.SCHEMA={table['name']:{c['name']:c['dataType'] for c in table['columns']}}
    build(dest,table['name'])
