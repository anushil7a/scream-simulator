"""Build a separate geometry-only city draft. No production edits, Studio launch or upload."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
DRAFT=ROOT/'prototypes/compact-city'
def sha(data):return hashlib.sha256(data).hexdigest()
def prop(parent,kind,name,value):
    e=ET.SubElement(parent,kind,{'name':name});e.text=str(value).lower() if isinstance(value,bool) else str(value);return e
def vector(parent,name,values,kind='Vector3'):
    e=ET.SubElement(parent,kind,{'name':name})
    for key,val in zip(('X','Y','Z'),values):ET.SubElement(e,key).text=str(val)
    return e
def color(parent,name,values):
    e=ET.SubElement(parent,'Color3',{'name':name})
    for key,val in zip(('R','G','B'),values):ET.SubElement(e,key).text=str(val/255)
def frame(parent,pos):
    e=ET.SubElement(parent,'CoordinateFrame',{'name':'CFrame'})
    for key,val in zip(('X','Y','Z'),pos):ET.SubElement(e,key).text=str(val)
    for i in range(3):
        for j in range(3):ET.SubElement(e,f'R{i}{j}').text='1' if i==j else '0'
def item(parent,cls,name):
    node=ET.SubElement(parent,'Item',{'class':cls});pr=ET.SubElement(node,'Properties');prop(pr,'string','Name',name);return node,pr
def udim(parent,name,xs,xo,ys,yo):
    e=ET.SubElement(parent,'UDim2',{'name':name})
    for k,v in zip(('XS','XO','YS','YO'),(xs,xo,ys,yo)):ET.SubElement(e,k).text=str(v)
def block(parent,part,cls='Part'):
    node,pr=item(parent,cls,part['id']);vector(pr,'size',part['size']);frame(pr,part['position']);color(pr,'Color',part['color'])
    for key,val in {'Anchored':True,'CanCollide':part['collidable'],'CanQuery':True,'CanTouch':False,'CastShadow':part['collidable']}.items():prop(pr,'bool',key,val)
    prop(pr,'token','TopSurface',0);prop(pr,'token','BottomSurface',0)
    if cls=='SpawnLocation':prop(pr,'bool','Neutral',True);prop(pr,'bool','Enabled',True);prop(pr,'int','Duration',0)
    return node
def label(parent,text):
    node,pr=item(parent,'BillboardGui','DraftLabel');udim(pr,'Size',0,260,0,48);vector(pr,'StudsOffsetWorldSpace',(0,7,0));prop(pr,'float','MaxDistance',65);prop(pr,'bool','AlwaysOnTop',False)
    node,pr=item(node,'TextLabel','Text');udim(pr,'Size',1,0,1,0);prop(pr,'string','Text',text);prop(pr,'float','TextSize',15);prop(pr,'bool','TextWrapped',True);prop(pr,'float','BackgroundTransparency',.15);color(pr,'BackgroundColor3',(30,48,54));color(pr,'TextColor3',(255,243,214));prop(pr,'int','BorderSizePixel',0)
def xml_bytes(tree):ET.indent(tree,space='  ');return ET.tostring(tree,encoding='utf-8',xml_declaration=True)
def model_xml(layout):
    tree=ET.Element('roblox',{'version':'4'});model,_=item(tree,'Model','CompactCity')
    for part in layout['parts']:block(model,part)
    for anchor in layout['anchors']:
        pos=anchor['position'];node=block(model,{'id':anchor['id'],'position':[pos[0],.17,pos[2]],'size':[8,.2,8],'color':[255,203,99] if anchor['kind']=='spawn' else [94,158,154],'collidable':False},'SpawnLocation' if anchor['kind']=='spawn' else 'Part')
        label(node,anchor['label'])
    return xml_bytes(tree)
def notice_xml():
    tree=ET.Element('roblox',{'version':'4'});gui,pr=item(tree,'ScreenGui','DraftNotice');prop(pr,'bool','ResetOnSpawn',False);prop(pr,'int','DisplayOrder',50)
    node,pr=item(gui,'TextLabel','Notice');udim(pr,'Size',.9,0,0,54);udim(pr,'Position',.05,0,0,8);prop(pr,'string','Text','COMPACT CITY DRAFT 01 | Geometry only\nNo beams, training AI, quests, saves or purchases. Do not publish.');prop(pr,'float','TextSize',17);prop(pr,'bool','TextWrapped',True);prop(pr,'float','BackgroundTransparency',.1);color(pr,'BackgroundColor3',(30,48,54));color(pr,'TextColor3',(255,243,214));prop(pr,'int','BorderSizePixel',0)
    return xml_bytes(tree)
def verify_preservation(layout):
    folder=ROOT/'assets/drafts/original-city-2026-11-11'/layout['preservedCommit']
    manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
    if not manifest['status'].startswith('complete') or manifest['commit']!=layout['preservedCommit']:raise ValueError('Original city preservation is not complete')
    if sha((folder/'original-city-source.zip').read_bytes())!=manifest['zipSha256']:raise ValueError('Original city archive hash mismatch')
    return manifest['zipSha256']
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--generate-only',action='store_true');args=parser.parse_args()
    layout=json.loads((DRAFT/'layout.json').read_text(encoding='utf-8'));preserved_hash=verify_preservation(layout)
    # Validate before overwriting only these task-owned generated models.
    import importlib.util
    spec=importlib.util.spec_from_file_location('compact_validation',ROOT/'tests/compact_city_draft.py');audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    audit.validate(layout)
    for name,data in [('CompactCity.rbxmx',model_xml(layout)),('DraftNotice.rbxmx',notice_xml())]:(DRAFT/name).write_bytes(data)
    if args.generate_only:return
    compiler=shutil.which('luau-compile');rojo=shutil.which('rojo')
    if not compiler or not rojo:raise SystemExit('Official luau-compile and rojo required')
    subprocess.run([compiler,str(DRAFT/'DraftGuard.server.luau')],check=True,stdout=subprocess.DEVNULL)
    project=ROOT/'compact-city-draft.project.json';out=ROOT/'build';out.mkdir(exist_ok=True)
    paths=[project,DRAFT/'layout.json',DRAFT/'CompactCity.rbxmx',DRAFT/'DraftNotice.rbxmx',DRAFT/'DraftGuard.server.luau',Path(__file__).resolve()]
    before={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}
    for suffix in ('rbxlx','rbxl'):subprocess.run([rojo,'build',str(project),'-o',str(out/('CompactCityDraft.'+suffix))],cwd=ROOT,check=True)
    after={str(p.relative_to(ROOT)):sha(p.read_bytes()) for p in paths}
    if before!=after:raise RuntimeError('Draft changed during build; rerun')
    audit.audit_built(layout,(out/'CompactCityDraft.rbxlx').read_bytes())
    (out/'CompactCityDraft.provenance.json').write_text(json.dumps({'status':'built/compiled only; native geometry/input untested; never publish','preservedCommit':layout['preservedCommit'],'preservedZipSha256':preserved_hash,'sourceHashes':before,'artifacts':{n:sha((out/n).read_bytes()) for n in ('CompactCityDraft.rbxl','CompactCityDraft.rbxlx')}},indent=2)+'\n',encoding='utf-8')
    print('PASS geometry-only compact preview built; builder did not alter production files. Native execution NOT performed.')
if __name__=='__main__':main()
