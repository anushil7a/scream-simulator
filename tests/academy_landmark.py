"""Actual CompactCity constructor differential; mocks do not prove native text fit or appearance."""
from pathlib import Path
import subprocess,sys
import compact_world as world

R=Path(__file__).resolve().parents[1];P='src/ServerScriptService/CompactCity.luau'
source=(R/P).read_text(encoding='utf8')
try:baseline=subprocess.check_output(['git','show','5622daa54424e639e7d3f671b2e453ff377b2cb6:'+P],cwd=R,text=True,encoding='utf8',stderr=subprocess.PIPE)
except subprocess.CalledProcessError as exc:raise SystemExit('Required local baseline 5622daa54424e639e7d3f671b2e453ff377b2cb6 unavailable; no fetch attempted.') from exc
assert world.layout==subprocess.check_output(['git','show','5622daa54424e639e7d3f671b2e453ff377b2cb6:src/ReplicatedStorage/Shared/CompactLayout.luau'],cwd=R,text=True,encoding='utf8'),'Shared layout changed from baseline'

CHECKS=r'''
end)()
local function capture(city)
 local start=#nodes;local result=city.Build({Name='World'});local current={}
 for i=start+1,#nodes do table.insert(current,nodes[i])end
 return current,result
end
local oldNodes,oldResult=capture(Old)
local current,result=capture(City)
local function path(o)if not o then return 'nil'end;return (o.Parent and path(o.Parent)..'/' or '')..(o.Name or o.ClassName or '?')end
local function serial(value)
 if type(value)~='table'then return tostring(value)end
 if value.ClassName then return '@'..path(value)end
 local keys={};for k,v in pairs(value)do if type(v)~='function'then table.insert(keys,k)end end
 table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
 local out={};for _,k in ipairs(keys)do table.insert(out,tostring(k)..'='..serial(value[k]))end
 return '{'..table.concat(out,';')..'}'
end
local function properties(node)
 local out={kind=node.ClassName};for k,v in pairs(node)do if k~='ClassName' and type(v)~='function'then out[k]=v end end;return serial(out)
end
local originals,added,foreground,byName={},{},{},{}
for _,node in ipairs(current)do
 if node.Name and node.Name:match('^Academy')then table.insert(added,node);check(not byName[node.Name] or node.Name=='AcademyName','Duplicate landmark object');byName[node.Name]=node
 elseif node.Name and node.Name:match('^Foreground')then table.insert(foreground,node);check(not byName[node.Name],'Duplicate foreground object');byName[node.Name]=node
 else table.insert(originals,node)end
end
check(#originals==#oldNodes,'Existing hierarchy count changed')
for i,node in ipairs(oldNodes)do
 check(path(node)==path(originals[i]) and properties(node)==properties(originals[i]),'Existing object changed: '..path(node))
end
check(serial(oldResult)==serial(result),'City gameplay outputs changed')
check(#added==22,'Expected only18parts/twosigns/twolabels')
check(#foreground==38,'Expected38foreground dressing parts')
for _,node in ipairs(foreground)do
 check(next(node.attributes)==nil,'Foreground carries gameplay attributes')
 check(node.ClassName=='Part' and node.Parent.Name=='CoastalAcademyArt' and node.Anchored==true and node.CanCollide==false and node.CanQuery==false and node.CanTouch==false and node.CastShadow==false,'Foreground changes physics/query/shadow')
 check(node.Transparency==0 and node.Material==Enum.Material.SmoothPlastic,'Foreground hidden/emissive')
end
local parts,signs,texts=0,0,0;local faces={};local bars={[-1]=0,[1]=0}
local nameplate=byName.AcademyNameplate
for _,node in ipairs(added)do
 check(next(node.attributes)==nil,'Landmark carries gameplay attributes')
 if node.ClassName=='Part'then
  parts+=1
  check(node.Parent.Name=='CoastalAcademyArt' and node.Anchored==true and node.CanCollide==false and node.CanQuery==false and node.CanTouch==false and node.CastShadow==false,'Landmark changes physics/query/shadow')
  check(node.Transparency==0 and node.Material==Enum.Material.SmoothPlastic,'Landmark hidden/emissive')
  local p,s=node.Position,node.Size
  check(s.X>0 and s.X<=1 and s.Y>0 and s.Z>0 and p.Y-s.Y/2>=14 and p.Y+s.Y/2<=32,'Landmark is not bounded overhead decoration')
  check(math.abs(p.X+120)+s.X/2<=1 and p.Z-s.Z/2>=28 and p.Z+s.Z/2<=72,'Landmark left the existing gate plane')
  if node.Name:match('^AcademyCrest')then check(node.Shape==Enum.PartType.Cylinder and s.Y==s.Z,'Crest is not a round X-axis disk')end
  local side=node.Name:match('^AcademyVoiceBar(-?1)_')
  if side then bars[tonumber(side)]+=1 end
 elseif node.ClassName=='SurfaceGui'then
  signs+=1
  check(node.Parent==nameplate and (node.Face==Enum.NormalId.Left or node.Face==Enum.NormalId.Right) and not faces[node.Face],'Academy sign does not cover both faces')
  faces[node.Face]=true
  check(node.SizingMode==Enum.SurfaceGuiSizingMode.FixedSize and node.CanvasSize.X==600 and node.CanvasSize.Y==72 and node.LightInfluence==0 and node.AlwaysOnTop==false and node.MaxDistance==140,'Academy sign occlusion/text canvas settings changed')
 elseif node.ClassName=='TextLabel'then
  texts+=1
  check(node.Parent.ClassName=='SurfaceGui' and node.Parent.Parent==nameplate and node.Text=='SCREAM ACADEMY','Academy identity or text hierarchy changed')
  check(node.Size.X==1 and node.Size.Y==1 and node.TextWrapped==false and node.TextSize==50 and node.Font==Enum.Font.GothamBold and node.BackgroundTransparency==1,'Academy authored text settings changed')
  check(serial(node.TextColor3)==serial({R=239,G=224,B=190}),'Academy text contrast palette changed')
 else error('Unexpected landmark object class')end
end
check(parts==18 and signs==2 and texts==2 and bars[-1]==5 and bars[1]==5,'Landmark inventory/signals incomplete')
local artCount=0;for _,node in ipairs(current)do if node.ClassName=='Part' and node.Parent.Name=='CoastalAcademyArt'then artCount+=1 end end
check(artCount==347 and artCount<=348 and artCount<=350,'Art budget exceeded')
print('PASS '..checks..' actual academy constructor/differential assertions;347parts, no native text-fit claim')
'''

def run(s):
 code=world.setup+world.layout+world.between.replace('local City=(function()','local Old=(function()')+baseline+'\nend)()\nlocal City=(function()\n'+s+CHECKS
 return world.execute(code)

if __name__=='__main__':
 print('PASS unchanged CompactLayout source contract against 5622daa54424e639e7d3f671b2e453ff377b2cb6')
 print(run(source).strip())
 if '--negative-controls' in sys.argv:
  cases=[
   ('V(-120,19,50),slate)','V(-120,9,50),slate)','bounded overhead'),
   ('local academySign=detail("AcademyNameplate",V(.8,4,37),V(-120,19,50),slate)','local academySign=detail("AcademyNameplate",V(.8,4,37),V(-120,19,50),slate);academySign.CanQuery=true','physics/query/shadow'),
   ('gui.Face=side<0 and Enum.NormalId.Left or Enum.NormalId.Right','gui.Face=Enum.NormalId.Left','both faces'),
   ('gui.LightInfluence=0;gui.MaxDistance=140;gui.AlwaysOnTop=false','gui.LightInfluence=0;gui.MaxDistance=140;gui.AlwaysOnTop=true','occlusion/text canvas'),
   ('text.Text="SCREAM ACADEMY"','text.Text="ACADEMY"','identity or text hierarchy'),
   ('V(-120,26,50),gold,Enum.PartType.Cylinder)','V(-120,26,50),gold,Enum.PartType.Ball)','round X-axis disk'),
   ('\n academyArt(parent,byId)\n','\n byId.ArenaGate30.CanCollide=false;academyArt(parent,byId)\n','Existing object changed'),
   ('detail("ForegroundGatewayPillarN",V(2.4,8.5,2.4),V(-196,4.33,34),ivory)','local p=detail("ForegroundGatewayPillarN",V(2.4,8.5,2.4),V(-196,4.33,34),ivory);p.CanQuery=true','Foreground changes physics/query/shadow'),
  ]
  for old,new,reason in cases:
   assert source.count(old)==1,old
   try:run(source.replace(old,new,1))
   except AssertionError as exc:assert reason in str(exc),(reason,str(exc))
   else:raise AssertionError('Control survived: '+reason)
  print(f'PASS {len(cases)} academy negative controls')
