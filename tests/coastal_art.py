"""Actual CompactCity art constructor and baseline geometry fingerprint; not native render/performance."""
from pathlib import Path
import argparse,hashlib,subprocess,ast
import compact_world as world
ROOT=Path(__file__).resolve().parents[1]
BASE="09e0996"
TAIL=r'''
end)()
local result=City.Build({Name="World"})
local count=0;local fgCount=0;local names={};local originals={}
local function overlapsXZ(p,s,cx,cz,sx,sz)
 return math.abs(p.X-cx)<(s.X+sx)/2 and math.abs(p.Z-cz)<(s.Z+sz)/2
end
for _,n in ipairs(nodes)do
 if n.ClassName=='Part' then
  if n.Parent and n.Parent.Name=='CoastalAcademyArt' then
   count+=1
   check(not names[n.Name],'Duplicate cosmetic name');names[n.Name]=true
   check(n.Anchored==true and n.CanCollide==false and n.CanQuery==false and n.CanTouch==false and n.CastShadow==false,'Cosmetic changes physics or shadow')
   check(next(n.attributes)==nil and n.Transparency==0,'Cosmetic carries gameplay state or is hidden')
   check(n.Size.X>0 and n.Size.Y>0 and n.Size.Z>0,'Invalid cosmetic dimensions')
   check(n.Position.X-n.Size.X/2>=-360 and n.Position.X+n.Size.X/2<=360 and n.Position.Z-n.Size.Z/2>=-300 and n.Position.Z+n.Size.Z/2<=300,'Cosmetic outside compact map')
   local p,s=n.Position,n.Size
   if n.Name:match('^Foreground') then
    fgCount+=1
    check(p.Y+s.Y/2<12,'Foreground dressing obstructs overhead header sightline')
    for _,route in ipairs(Layout.GuidanceSpecs)do
     check(not overlapsXZ(p,s,route.position.X,route.position.Z,route.size.X,route.size.Z),'Foreground dressing overlaps guidance route')
    end
    for _,spec in ipairs(Layout.PartSpecs)do
     if spec.kind=='pad' then check(not overlapsXZ(p,s,spec.position.X,spec.position.Z,spec.size.X,spec.size.Z),'Foreground dressing overlaps training pad') end
    end
   end
   if p.X+s.X/2>-120 and p.X-s.X/2<200 and p.Z+s.Z/2>-180 and p.Z-s.Z/2<140 and p.Y-s.Y/2>.2 and p.Y-s.Y/2<12 then
    local contained=false
    for _,spec in ipairs(Layout.PartSpecs)do if spec.kind=='cover' then
     local c,t=spec.position,spec.size
     if math.abs(p.X-c.X)+s.X/2<=t.X/2+.08 and math.abs(p.Y-c.Y)+s.Y/2<=t.Y/2+.08 and math.abs(p.Z-c.Z)+s.Z/2<=t.Z/2+.08 then contained=true end
    end end
    check(contained,'Cosmetic creates false arena cover')
   end
  else
   local p,s=n.Position,n.Size
   if n.Name=='ArenaWayfinding' then check(p.X==-122.6 and p.Y==13.5 and p.Z==50 and s.X==.2 and s.Y==3 and s.Z==39,'Arena guide not on header');p=Vector3.new(-137,4,50);s=Vector3.new(.2,.2,.2) end
   local attrs={};for k,v in pairs(n.attributes)do if k=='RestColor' then table.insert(attrs,k..'=target-color')else table.insert(attrs,k..'='..tostring(v))end end;table.sort(attrs)
   table.insert(originals,string.format('%s|%s|%.6f,%.6f,%.6f|%.6f,%.6f,%.6f|%s,%s,%s,%s|%s',n.Name,n.Parent.Name or 'World',p.X,p.Y,p.Z,s.X,s.Y,s.Z,tostring(n.CanCollide),tostring(n.CanQuery),tostring(n.CanTouch),tostring(n.Anchored),table.concat(attrs,',')))
  end
 elseif n.Parent and n.Parent.Name=='CoastalAcademyArt' then error('Unexpected art child class') end
end
check(Layout.Practice==nil,'Retired layout practice metadata remains')
for _,n in ipairs(nodes)do check(not n.Name or not n.Name:match('^Practice') and n.Name~='StandLine' and n.Name~='SpawnWayfinding','Retired mic area was recreated') end
table.sort(originals);for _,line in ipairs(originals)do print('ORIGINAL|'..line)end
check(fgCount==38,'Unexpected foreground dressing budget')
check(count==347 and count<=348,'Unexpected cosmetic budget')
for _,name in ipairs({'CanopyCrown0','MarketCornice0','OldTownCornice0','TowerLantern256','ArenaFascia','CourtyardJoint0','PromenadeJoint0','CoverTop0','ForegroundBollardPost1','ForegroundBollardLantern8','ForegroundPlazaTrimW','ForegroundPlazaAccentS','ForegroundPromenadeCurb1','ForegroundPromenadeInlay2','ForegroundPlanterBase1','ForegroundPlanterAccent2','ForegroundGatewayPillarN','ForegroundGatewayCapS'})do check(names[name],'Missing art family '..name)end
print('PASS '..checks..' coastal art assertions; '..count..' static cosmetic parts ('..fgCount..' foreground)')
'''
def run(source,tail=TAIL):
 return world.execute(world.setup+world.layout+world.between+source+tail)
def digest(output):
 return hashlib.sha256(('\n'.join(sorted(x for x in output.splitlines() if x.startswith('ORIGINAL|')))+'\n').encode()).hexdigest()
EXPECTED='5ef036ad23b972f1fc95aad878e6de684d3c6e51bd82fb90261e0f1ed4b2499b'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
 source=(ROOT/'src/ServerScriptService/CompactCity.luau').read_text(encoding='utf-8')
 output=run(source)
 assert digest(output)==EXPECTED,'Original gameplay geometry or flags changed'
 print('\n'.join(x for x in output.splitlines() if x.startswith('PASS')))
 print('PASS unchanged original geometry/flags/attributes fingerprint')
 if args.baseline:
  old=subprocess.check_output(['git','show',BASE+':src/ServerScriptService/CompactCity.luau'],cwd=ROOT,text=True,encoding='utf-8')
  old_layout=subprocess.check_output(['git','show',BASE+':src/ReplicatedStorage/Shared/CompactLayout.luau'],cwd=ROOT,text=True,encoding='utf-8')
  old_test=subprocess.check_output(['git','show',BASE+':tests/coastal_art.py'],cwd=ROOT,text=True,encoding='utf-8')
  tree=ast.parse(old_test);tail=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='TAIL' for t in n.targets))
  output=world.execute(world.setup+old_layout+world.between+old+tail)
  removed={'PracticeTarget','PracticeBackstop','PracticeFrameNear','PracticeFrameFar','PracticeFrameCrown','StandLine','SpawnWayfinding','PracticeWayfinding'}
  kept='\n'.join(line.replace('ORIGINAL|RouteToPractice|','ORIGINAL|RouteFromSpawn|') for line in output.splitlines() if line.startswith('ORIGINAL|') and line.split('|')[1] not in removed)
  assert digest(kept)==EXPECTED,'Surviving original inventory differs from pinned pre-removal build'
  print('PASS pinned pre-removal surviving original inventory matches')
 if args.negative_controls:
  cases=[('"ArenaWayfinding",V(-122.6,13.5,50)','"ArenaWayfinding",V(-137,4,50)','Arena guide not on header'),('local byId={}','local byId={};part(parent,"PracticeTarget",V(1,1,1),V(0,0,0),Color3.fromRGB(1,1,1),false)','Retired mic area was recreated'),('  p.CanQuery=false\n  p.CastShadow=false','  p.CanQuery=true\n  p.CastShadow=false','Cosmetic changes physics or shadow'),
   ('  p.CanQuery=false\n  p.CastShadow=false','  p.CanQuery=false\n  p.CanCollide=true;p.CastShadow=false','Cosmetic changes physics or shadow'),
   ('  c.Color=slate','  c.Color=slate;c.Position=V(0,0,0)','Original gameplay geometry'),
   ('V(pos.X,6.04,pos.Z)','V(pos.X+8,6.04,pos.Z)','Cosmetic creates false arena cover'),
   ('detail("ForegroundGatewayPillarN",V(2.4,8.5,2.4),V(-196,4.33,34),ivory)','detail("ForegroundGatewayPillarN",V(2.4,8.5,2.4),V(-196,8.5,34),ivory)','Foreground dressing obstructs overhead header sightline'),
   ('V(-280,0,114),V(-260,0,114)','V(-270,0,114),V(-260,0,114)','Foreground dressing overlaps guidance route'),
   ('detail("ForegroundGatewayCapS",V(3,.9,3),V(-196,9.03,66),terracotta)','detail("ForegroundGatewayCapS",V(3,.9,3),V(-196,9.03,66),terracotta);detail("ForegroundExtra",V(1,1,1),V(-280,1,110),ivory)','Unexpected foreground dressing budget')]
  for old,new,message in cases:
   assert source.count(old)==1,old
   try:
    o=run(source.replace(old,new));assert digest(o)==EXPECTED,'Original gameplay geometry or flags changed'
   except AssertionError as e:assert message in str(e),str(e);print('PASS negative control:',message)
   else:raise AssertionError('Mutation accepted: '+message)
