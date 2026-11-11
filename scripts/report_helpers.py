from pathlib import Path
import json,uuid,copy
SCHEMA={}

def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))

def save(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

def lit(v):return {'expr':{'Literal':{'Value':str(v)}}}

def string(s):return lit("'"+s.replace("'","''")+"'")

def color(c):return {'solid':{'color':string(c)}}

def uid(s):return uuid.uuid5(uuid.NAMESPACE_URL,s).hex[:20]

def title(text):return [{'properties':{'show':lit('true'),'text':string(text),'fontColor':color('#18354A'),'fontSize':lit('12D'),'fontFamily':string('Segoe UI'),'alignment':string('left')}}]

def visual(page,name,kind,fields,x,y,width,height,caption=None):
 """fields=(role,table,field,is_measure,format); generates matching query and bindings."""
 ident=uid(str(page)+name);pos={'x':x,'y':y,'width':width,'height':height,'z':1000}
 vc={'name':ident,'layouts':[{'id':0,'position':pos}], 'singleVisual':{'visualType':kind,'drillFilterOtherVisuals':True}}
 sv=vc['singleVisual'];sv['vcObjects']={'background':[{'properties':{'show':lit('true'),'color':color('#FFFFFF'),'transparency':lit('0D')}}],'title':title(caption or name),'border':[{'properties':{'show':lit('true'),'color':color('#DFE7EE'),'radius':lit('8D')}}]}
 if kind=='card':
  fmt=fields[0][4] or '#,0';precision=len(fmt.split('.',1)[1].replace('%','')) if '.' in fmt else 0
  sv['objects']={'labels':[{'properties':{'fontSize':lit('29D'),'color':color('#087F8C'),'labelDisplayUnits':lit('1D'),'labelPrecision':lit(str(precision)+'L')}}],'categoryLabels':[{'properties':{'show':lit('false')}}]}
 if kind=='slicer':
  sv['objects']={'data':[{'properties':{'mode':string('Dropdown')}}]}
  sv['vcObjects']['title']=[{'properties':{'show':lit('false')}}]
 if kind in ['clusteredBarChart','clusteredColumnChart','lineChart']:
  sv['objects']={'dataPoint':[{'properties':{'defaultColor':color('#087F8C')}}],'categoryAxis':[{'properties':{'show':lit('true'),'fontSize':lit('10D'),'labelColor':color('#40576A')}}],'valueAxis':[{'properties':{'show':lit('true'),'fontSize':lit('10D')}}],'legend':[{'properties':{'show':lit('false')}}]}
 refs=[];sels=[];sources=[];projections={};ordering={};selects=[];metas=[]
 for i,(role,t,f,measure,fmt) in enumerate(fields):
  alias='t'+str(next((j for j,a in enumerate(sources) if a['Entity']==t),len(sources)))
  if not any(a['Entity']==t for a in sources):sources.append({'Name':alias,'Entity':t,'Type':0})
  typ='Measure' if measure else 'Column';expr={typ:{'Expression':{'SourceRef':{'Source':alias}},'Property':f}};ref=t+'.'+f
  sels.append({**expr,'Name':ref});refs.append(ref);projections.setdefault(role,[]).append({'queryRef':ref,**({} if measure else {'active':True})});ordering.setdefault(role,[]).append(i)
  expr2=copy.deepcopy(expr);expr2[typ]['Expression']['SourceRef']={'Entity':t}
  dtype=SCHEMA.get(t,{}).get(f,'string');underlying=259 if measure else {'string':1,'int64':260,'double':259,'dateTime':7}.get(dtype,1)
  selects.append({'displayName':f,'queryName':ref,'roles':{role:True},'type':{'category':None,'underlyingType':underlying},'expr':expr2,**({'format':fmt} if fmt else {})})
  metas.append({'Restatement':f,'Name':ref,'Type':1 if measure else 2048,**({'Format':fmt} if fmt else {})})
 query={'Version':2,'From':sources,'Select':sels}
 if len(sels)==2 and kind!='slicer':query['OrderBy']=[{'Direction':2,'Expression':{k:v for k,v in sels[1].items() if k!='Name'}}]
 if kind=='lineChart':query['OrderBy']=[{'Direction':1,'Expression':{k:v for k,v in sels[0].items() if k!='Name'}}]
 sv['projections']=projections;sv['prototypeQuery']=query
 folder=page/'visualContainers'/('p_'+name);save(folder/'config.json',vc);save(folder/'visualContainer.json',pos);save(folder/'filters.json',[])
 binding={'Primary':{'Groupings':[{'Projections':list(range(len(sels)))}]},'DataReduction':{'DataVolume':3,'Primary':{'Top':{'Count':1000 if kind=='lineChart' else 20} if kind!='slicer' else {}}},'Version':1}
 save(folder/'query.json',{'Commands':[{'SemanticQueryDataShapeCommand':{'Query':query,'Binding':binding,'ExecutionMetricsKind':1}}]})
 save(folder/'dataTransforms.json',{'projectionOrdering':ordering,'queryMetadata':{'Select':metas},'visualElements':[{'DataRoles':[{'Name':f[0],'Projection':i,'isActive':not f[3]} for i,f in enumerate(fields)]}],'selects':selects})

def textbox(page,name,lines,x,y,w,h,size=14,dark=False):
 # The screenshot shows the two-line header overflowing vertically at 25/18 pt.
 if dark:size=24
 pos={'x':x,'y':y,'width':w,'height':h,'z':0};cfg={'name':uid(str(page)+name),'layouts':[{'id':0,'position':pos}],'singleVisual':{'visualType':'textbox','objects':{'general':[{'properties':{'paragraphs':[{'textRuns':[{'value':line,'textStyle':{'fontFamily':'Segoe UI','fontSize':str(size if i==0 else max(11,size-7))+'pt','fontWeight':'bold' if i==0 else 'normal','color':'#FFFFFF' if dark else '#30485B'}}]} for i,line in enumerate(lines)]}}]},'vcObjects':{'background':[{'properties':{'show':lit('true'),'color':color('#15354A' if dark else '#EDF4F8'),'transparency':lit('0D')}}]}}}
 if dark:
  for paragraph in cfg['singleVisual']['objects']['general'][0]['properties']['paragraphs'][1:]:
   for run in paragraph['textRuns']:run['textStyle']['fontSize']='14pt'
 d=page/'visualContainers'/('p_'+name);save(d/'config.json',cfg);save(d/'visualContainer.json',pos)

def page(proj,folder,name,ordinal):
 d=proj/'Report/sections'/folder;save(d/'section.json',{'displayName':name,'name':uid(str(proj)+folder),'ordinal':ordinal,'displayOption':1,'width':1280,'height':850});save(d/'config.json',{'objects':{'background':[{'properties':{'color':color('#F3F6FA'),'transparency':lit('0D')}}]}});save(d/'filters.json',[]);return d

def field(role,t,f,measure=True,fmt='#,0'):return(role,t,f,measure,fmt if measure else None)