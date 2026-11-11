"""Independent compact draft geometry validation. Static data only, not gameplay/navigation proof."""
from pathlib import Path
import argparse,copy,json,math,hashlib,importlib.util,xml.etree.ElementTree as ET,re
ROOT=Path(__file__).resolve().parents[1]
checks=0

def check(value,message):
 global checks
 assert value,message
 checks+=1

def finite(values,count):
 return isinstance(values,list) and len(values)==count and all(type(v) in (int,float) and math.isfinite(v) for v in values)

def intersects_segment(a,b,lo,hi):
 """Closed slab intersection, including grazing collisions; no sampling gaps."""
 near,far=0.,1.
 for i in range(2):
  delta=b[i]-a[i]
  if abs(delta)<1e-12:
   if a[i]<lo[i] or a[i]>hi[i]:return False
  else:
   first,last=sorted(((lo[i]-a[i])/delta,(hi[i]-a[i])/delta))
   near=max(near,first);far=min(far,last)
   if near>far:return False
 return True

def validate(data):
 bounds=data['bounds'];lo,hi=bounds['min'],bounds['max']
 check(lo==[-360,-300] and hi==[360,300],'Draft footprint changed')
 check((hi[0]-lo[0])*(hi[1]-lo[1])==1440*1200/4,'Draft is not quarter old footprint')
 arena=data['arena'];check(arena['min']==[-120,-180] and arena['max']==[200,140],'Arena bounds changed')
 ids=set()
 for category in ('anchors','routes','parts'):
  for obj in data[category]:
   check(isinstance(obj['id'],str) and bool(obj['id']) and obj['id'] not in ids,'Duplicate or invalid draft ID');ids.add(obj['id'])
 for part in data['parts']:
  check(finite(part['position'],3) and finite(part['size'],3) and all(v>0 for v in part['size']),'Invalid part dimensions')
  check(finite(part['color'],3) and all(0<=v<=255 for v in part['color']),'Invalid part color')
  check(type(part['collidable']) is bool,'Invalid collision flag')
  pos,size=part['position'],part['size']
  check(lo[0]<=pos[0]-size[0]/2 and pos[0]+size[0]/2<=hi[0] and lo[1]<=pos[2]-size[2]/2 and pos[2]+size[2]/2<=hi[1],'Part outside compact bounds')
 for anchor in data['anchors']:
  pos=anchor['position'];check(finite(pos,3),'Invalid anchor position')
  check(lo[0]<=pos[0]<=hi[0] and lo[1]<=pos[2]<=hi[1],'Anchor outside compact bounds')
  supported=False
  for part in data['parts']:
   p,s=part['position'],part['size'];top=p[1]+s[1]/2
   if part['collidable'] and p[0]-s[0]/2<=pos[0]<=p[0]+s[0]/2 and p[2]-s[2]/2<=pos[2]<=p[2]+s[2]/2 and top<=pos[1]<=top+8:supported=True
  check(supported,'Anchor lacks nearby supporting ground')
 ground=next((p for p in data['parts'] if p['id']=='Ground'),None)
 check(ground is not None and ground['collidable'] and ground['position']==[0,-1,0] and ground['size']==[720,2,600],'Ground does not support full draft footprint')
 for route in data['routes']:
  check(route['clearance']>=4 and len(route['points'])>=2,'Route clearance or path missing')
  for point in route['points']:check(finite(point,2) and lo[0]<=point[0]<=hi[0] and lo[1]<=point[1]<=hi[1],'Route outside bounds')
  for part in data['parts']:
   if not part['collidable'] or part['position'][1]+part['size'][1]/2<=1 or part['position'][1]-part['size'][1]/2>=7:continue
   p,s=part['position'],part['size'];clearance=route['clearance']
   lower=[p[0]-s[0]/2-clearance,p[2]-s[2]/2-clearance];upper=[p[0]+s[0]/2+clearance,p[2]+s[2]/2+clearance]
   for a,b in zip(route['points'],route['points'][1:]):check(not intersects_segment(a,b,lower,upper),'Route intersects expanded obstacle: '+route['id']+'/'+part['id'])
 practice=next(a for a in data['anchors'] if a['id']=='Practice')
 target=next(p for p in data['parts'] if p['id']=='PracticeTarget')
 backstop=next(p for p in data['parts'] if p['id']=='PracticeBackstop')
 origin=practice['position'];aim=practice.get('aim');destination=target['position']
 check(math.dist(origin,destination)<=12,'Practice target beyond conservative starter range')
 check(aim==[-1,0,0] and destination[0]<origin[0] and abs(destination[2]-origin[2])<.000001,'Practice target does not align west')
 check(target['position'][1]-target['size'][1]/2<=origin[1]<=target['position'][1]+target['size'][1]/2,'Practice horizontal aim misses target height')
 check(backstop['position'][0]<destination[0] and backstop['collidable'],'Practice backstop not behind target')
 trainers=[a for a in data['anchors'] if a['kind']=='trainer']
 check(len(trainers)==3,'Three trainer homes required')
 for index,trainer in enumerate(trainers):
  x,_,z=trainer['position'];distance=math.hypot(max(arena['min'][0]-x,0,x-arena['max'][0]),max(arena['min'][1]-z,0,z-arena['max'][1]))
  check(distance>32,'Trainer eligibility radius enters PvP')
  check(lo[0]+32<=x<=hi[0]-32 and lo[1]+32<=z<=hi[1]-32,'Trainer radius outside map')
  for other in trainers[index+1:]:check(math.hypot(x-other['position'][0],z-other['position'][2])>=85,'Trainer homes too close')
 check(any(p['kind']=='cover' and arena['min'][0]<=p['position'][0]<=arena['max'][0] and arena['min'][1]<=p['position'][2]<=arena['max'][1] for p in data['parts']),'Arena cover missing')
 check(sum(any(intersects_segment(a,b,arena['min'],arena['max']) for a,b in zip(r['points'],r['points'][1:])) for r in data['routes'])>=2,'Multiple arena routes missing')
 return data

validate_layout=validate

def serialized_audit(layout,xml):
 tree=ET.fromstring(xml)
 objects={}
 for item in tree.iter('Item'):
  if item.get('class') not in ('Part','SpawnLocation'):continue
  props={p.get('name'):p for p in item.find('Properties')}
  name=props['Name'].text;check(name not in objects,'Duplicate serialized part');objects[name]=(item,props)
 check(set(objects)=={o['id'] for o in layout['parts']+layout['anchors']},'Serialized part membership mismatch')
 def vector(element,names):return [float(element.find(k).text) for k in names]
 def close(a,b):return len(a)==len(b) and all(abs(x-y)<1e-6 for x,y in zip(a,b))
 for part in layout['parts']:
  item,p=objects[part['id']]
  check(item.get('class')=='Part','Wrong geometry class')
  check(close(vector(p['size'],'XYZ'),part['size']),'Serialized size differs from layout')
  check(close(vector(p['CFrame'],'XYZ'),part['position']),'Serialized position differs from layout')
  packed=p.get('Color3uint8')
  rgb=vector(p['Color'],'RGB') if packed is None else [((int(packed.text)>>shift)&255)/255 for shift in (16,8,0)]
  check(all(abs(a-b/255)<=1/255+.000001 for a,b in zip(rgb,part['color'])),'Serialized color differs from layout')
  check(p['CanCollide'].text==str(part['collidable']).lower(),'Serialized collision differs from layout')
  check(p['Anchored'].text=='true' and p['CanTouch'].text=='false','Draft part not static')
 for anchor in layout['anchors']:
  item,p=objects[anchor['id']]
  check(item.get('class')==('SpawnLocation' if anchor['kind']=='spawn' else 'Part'),'Anchor class mismatch')
  check(close(vector(p['CFrame'],'XYZ'),[anchor['position'][0],.17,anchor['position'][2]]),'Anchor marker position mismatch')
  check(close(vector(p['size'],'XYZ'),[8,.2,8]) and p['CanCollide'].text=='false' and p['Anchored'].text=='true','Anchor marker collision/size mismatch')
  texts=[q.text for child in item.iter('Item') for q in child.findall('Properties/string') if q.get('name')=='Text']
  check(anchor['label'] in texts,'Anchor label missing')
  if anchor['kind']=='spawn':check(p['Neutral'].text=='true' and p['Enabled'].text=='true' and float(p['Duration'].text)==0,'Draft spawn behavior differs')
 check(not any(i.get('class') in ('Script','LocalScript','ModuleScript','RemoteEvent','RemoteFunction') for i in tree.iter('Item')),'Geometry model includes runtime services/scripts')


def audit_built(layout,xml):
 tree=ET.fromstring(xml)
 scripts=[i for i in tree.iter('Item') if i.get('class') in ('Script','LocalScript','ModuleScript')]
 check(len(scripts)==1 and scripts[0].get('class')=='Script','Unexpected script in draft artifact')
 source=next(e.text for e in scripts[0].find('Properties') if e.get('name')=='Source')
 check(source==(ROOT/'prototypes/compact-city/DraftGuard.server.luau').read_text(),'Draft guard source changed during build')
 for node in tree.iter('Item'):
  for child in list(node):
   if child in scripts:node.remove(child)
 serialized_audit(layout,ET.tostring(tree))
 return True


def audit_draft(layout):
 spec=importlib.util.spec_from_file_location('compact_builder',ROOT/'tools/build_compact_city_draft.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
 xml=builder.model_xml(layout);serialized_audit(layout,xml)
 model_path=ROOT/'prototypes/compact-city/CompactCity.rbxmx'
 check(model_path.read_bytes()==xml,'Checked-in generated model differs from layout/builder')
 check((ROOT/'prototypes/compact-city/DraftNotice.rbxmx').read_bytes()==builder.notice_xml(),'Generated draft notice differs from builder')
 guard=(ROOT/'prototypes/compact-city/DraftGuard.server.luau').read_text()
 check('IsStudio() and game.PlaceId==0' in guard,'Draft guard is not local Studio only')
 check(re.findall(r'GetService\(["\']([^"\']+)',guard)==['RunService'],'Draft guard accesses unintended service')
 check(not any(token in guard for token in ('require(', 'DataStore', 'RemoteEvent','RemoteFunction','LoadAsset','HttpService')),'Draft guard imports gameplay/services')
 check('assert(count=='+str(len(layout['parts'])+len(layout['anchors'])) in guard,'Draft guard part count stale')
 project=json.loads((ROOT/'compact-city-draft.project.json').read_text())
 refs=[]
 def walk(node):
  if isinstance(node,dict):
   for k,v in node.items():
    if k=='$path':refs.append(v)
    else:walk(v)
  elif isinstance(node,list):
   for v in node:walk(v)
 walk(project)
 check(set(refs)=={'prototypes/compact-city/CompactCity.rbxmx','prototypes/compact-city/DraftNotice.rbxmx','prototypes/compact-city/DraftGuard.server.luau'},'Draft project imports live gameplay')
 return xml

if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');parser.add_argument('--scope-check',action='store_true');parser.add_argument('--built-check','--artifact-check',dest='artifact_check',action='store_true');args=parser.parse_args()
 data=json.loads((ROOT/'prototypes/compact-city/layout.json').read_text())
 validate(data)
 xml=audit_draft(data)
 print('PASS',checks,'independent compact draft static geometry assertions')

 if args.negative_controls:
  def reject(mutated,expected):
   try:validate(mutated)
   except AssertionError as e:assert expected in str(e),str(e);print('PASS negative control:',expected)
   else:raise AssertionError('Mutation accepted: '+expected)
  modified=copy.deepcopy(data);next(p for p in modified['parts'] if p['id']=='PracticeTarget')['position'][0]=-323.8
  reject(modified,'Practice target beyond conservative starter range')
  modified=copy.deepcopy(data);point=modified['routes'][0]['points'][0]
  modified['parts'].append({'id':'injected-route-obstacle','kind':'obstacle','position':[point[0],4,point[1]],'size':[2,8,2],'color':[1,2,3],'collidable':True})
  reject(modified,'Route intersects expanded obstacle')
  modified=copy.deepcopy(data);next(a for a in modified['anchors'] if a['kind']=='trainer')['position']=[0,4,0]
  reject(modified,'Trainer eligibility radius enters PvP')
  modified=copy.deepcopy(data);modified['parts']=[p for p in modified['parts'] if p['position'][1]+p['size'][1]/2>1]
  reject(modified,'Anchor lacks nearby supporting ground')
  modified=copy.deepcopy(data);modified['parts'].append(copy.deepcopy(modified['parts'][0]))
  reject(modified,'Duplicate or invalid draft ID')
  modified=copy.deepcopy(data);modified['parts'][0]['size'][0]=721
  reject(modified,'Part outside compact bounds')
  modified=copy.deepcopy(data);next(p for p in modified['parts'] if p['id']=='Ground')['size'][0]=700
  reject(modified,'Ground does not support full draft footprint')
  broken=ET.fromstring(xml);part=next(i for i in broken.iter('Item') if i.get('class')=='Part');part.find("Properties/Vector3[@name='size']/X").text='999'
  try:serialized_audit(data,ET.tostring(broken))
  except AssertionError as e:assert 'Serialized size differs' in str(e);print('PASS negative control: serialized geometry corruption')
  else:raise AssertionError('Serialized corruption accepted')
 if args.scope_check:
  manifest=json.loads((ROOT/'assets/drafts/original-city-2026-11-11/72c886cb6f8a60ab26dff962e28da77e4b2d4609/manifest.json').read_text())
  n=0
  for name,entry in manifest['files'].items():
   raw=(ROOT/name).read_bytes()
   # Git source archive uses canonical LF; checkout may use CRLF.
   canonical=raw.replace(b'\r\n',b'\n') if name.endswith(('.luau','.json','.rbxmx')) else raw
   assert hashlib.sha256(raw).hexdigest()==entry['sha256'] or hashlib.sha256(canonical).hexdigest()==entry['sha256'],'Production changed: '+name
   n+=1
  print('PASS',n,'optional original-source scope checks')

 if args.artifact_check:
  provenance=json.loads((ROOT/'build/CompactCityDraft.provenance.json').read_text())
  for name,expected in provenance['sourceHashes'].items():
   path=(ROOT/name).resolve();assert path.is_relative_to(ROOT),'Unsafe provenance path'
   assert hashlib.sha256(path.read_bytes()).hexdigest()==expected,'Stale artifact source: '+name
  for name,expected in provenance['artifacts'].items():
   assert name in ('CompactCityDraft.rbxl','CompactCityDraft.rbxlx'),'Unexpected artifact'
   assert hashlib.sha256((ROOT/'build'/name).read_bytes()).hexdigest()==expected,'Artifact hash mismatch: '+name
  built_xml=(ROOT/'build/CompactCityDraft.rbxlx').read_bytes();before=checks
  audit_built(data,built_xml)
  print('PASS',checks-before,'actual built-place serialization/source assertions')
  if args.negative_controls:
   tree=ET.fromstring(built_xml);ET.SubElement(tree,'Item',{'class':'Script'})
   try:audit_built(data,ET.tostring(tree))
   except AssertionError as e:assert 'Unexpected script' in str(e);print('PASS negative control: extra built script rejected')
   else:raise AssertionError('Extra built script accepted')
  assert provenance['preservedCommit']==data['preservedCommit'],'Wrong preserved source provenance'
  print('PASS built draft artifact hashes, isolated guard and146-part serialized layout audit')
