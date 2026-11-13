"""Actual CompactCity art constructor and baseline geometry fingerprint; not native render/performance."""
from pathlib import Path
import argparse,hashlib,subprocess
import compact_world as world
ROOT=Path(__file__).resolve().parents[1]
BASE="dda67e3943b85398616fed487340dca60ccc0741"
TAIL=r'''
end)()
local result=City.Build({Name="World"})
local count=0;local names={};local originals={}
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
   local inShot=p.X+s.X/2>-280.7 and p.X-s.X/2<-269 and p.Y+s.Y/2>2.5 and p.Y-s.Y/2<9.5 and p.Z+s.Z/2>61.5 and p.Z-s.Z/2<68.5
   check(not inShot,'Cosmetic obscures practice shot')
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
   -- Deliberate side-positioning of one nonphysical sign is separately checked.
   if n.Name=='SpawnWayfinding' then
    check(p.X==-288 and p.Y==4 and p.Z==135,'Spawn sign still obscures arrival axis')
    p=Vector3.new(-270,4,130)
   end
   if n.Name=='PracticeWayfinding' then check(p.X==-280.45 and p.Y==19 and p.Z==65 and s.X==.2 and s.Y==4 and s.Z==36,'Practice guide not on header');p=Vector3.new(-270,4,65);s=Vector3.new(.2,.2,.2) end
   if n.Name=='ArenaWayfinding' then check(p.X==-122.6 and p.Y==13.5 and p.Z==50 and s.X==.2 and s.Y==3 and s.Z==39,'Arena guide not on header');p=Vector3.new(-137,4,50);s=Vector3.new(.2,.2,.2) end
   local attrs={};for k,v in pairs(n.attributes)do if k=='RestColor' then table.insert(attrs,k..'=target-color')else table.insert(attrs,k..'='..tostring(v))end end;table.sort(attrs)
   table.insert(originals,string.format('%s|%s|%.6f,%.6f,%.6f|%.6f,%.6f,%.6f|%s,%s,%s,%s|%s',n.Name,n.Parent.Name or 'World',p.X,p.Y,p.Z,s.X,s.Y,s.Z,tostring(n.CanCollide),tostring(n.CanQuery),tostring(n.CanTouch),tostring(n.Anchored),table.concat(attrs,',')))
  end
 elseif n.Parent and n.Parent.Name=='CoastalAcademyArt' then error('Unexpected art child class') end
end
table.sort(originals);for _,line in ipairs(originals)do print('ORIGINAL|'..line)end
check(count==304,'Unexpected cosmetic budget')
for _,name in ipairs({'CanopyCrown0','MarketCornice0','OldTownCornice0','TowerLantern256','PracticeHeader','PracticeBeaconFace','ArenaFascia','CourtyardJoint0','PromenadeJoint0','CoverTop0'})do check(names[name],'Missing art family '..name)end
print('PASS '..checks..' coastal art assertions; '..count..' static cosmetic parts')
'''
def run(source,tail=TAIL):
 return world.execute(world.setup+world.layout+world.between+source+tail)
def digest(output):
 return hashlib.sha256(('\n'.join(x for x in output.splitlines() if x.startswith('ORIGINAL|'))+'\n').encode()).hexdigest()
EXPECTED='8fb4902b8eed8c3a0f1ece3bea4f2a50a970212a741224d8428cf57e42f38529'
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');p.add_argument('--baseline',action='store_true');args=p.parse_args()
 source=(ROOT/'src/ServerScriptService/CompactCity.luau').read_text(encoding='utf-8')
 output=run(source)
 assert digest(output)==EXPECTED,'Original gameplay geometry or flags changed'
 print('\n'.join(x for x in output.splitlines() if x.startswith('PASS')))
 print('PASS unchanged original geometry/flags/attributes fingerprint')
 if args.baseline:
  old=subprocess.check_output(['git','show',BASE+':src/ServerScriptService/CompactCity.luau'],cwd=ROOT,text=True,encoding='utf-8')
  tail=TAIL.replace("check(p.X==-288 and p.Y==4 and p.Z==135,'Spawn sign still obscures arrival axis')", "check(p.X==-270 and p.Y==4 and p.Z==130,'Baseline sign differs')")
  tail=tail.replace("check(p.X==-280.45 and p.Y==19 and p.Z==65 and s.X==.2 and s.Y==4 and s.Z==36,'Practice guide not on header')","check(p.X==-270 and p.Y==4 and p.Z==65,'Baseline practice guide differs')")
  tail=tail.replace("check(p.X==-122.6 and p.Y==13.5 and p.Z==50 and s.X==.2 and s.Y==3 and s.Z==39,'Arena guide not on header')","check(p.X==-137 and p.Y==4 and p.Z==50,'Baseline arena guide differs')")
  tail=tail[:tail.index("check(count==304")]+"check(count==0,'Baseline art exists')"
  assert digest(run(old,tail))==EXPECTED
  print('PASS pinned baseline original inventory matches')
 if args.negative_controls:
  cases=[('"ArenaWayfinding",V(-122.6,13.5,50)','"ArenaWayfinding",V(-137,4,50)','Arena guide not on header'),('\"PracticeWayfinding\",V(-280.45,19,65)','\"PracticeWayfinding\",V(-270,4,65)','Practice guide not on header'),('  p.CanQuery=false\n  p.CastShadow=false','  p.CanQuery=true\n  p.CastShadow=false','Cosmetic changes physics or shadow'),
   ('  p.CanQuery=false\n  p.CastShadow=false','  p.CanQuery=false\n  p.CanCollide=true;p.CastShadow=false','Cosmetic changes physics or shadow'),
   ('V(-282,19,65)','V(-275,6,65)','Cosmetic obscures practice shot'),
   ('  c.Color=slate','  c.Color=slate;c.Position=V(0,0,0)','Original gameplay geometry'),
   ('V(Layout.Spawn.X-18,4,Layout.Spawn.Z+5)','V(Layout.Spawn.X,4,Layout.Spawn.Z)','Spawn sign still obscures arrival axis'),
   ('V(pos.X,6.04,pos.Z)','V(pos.X+8,6.04,pos.Z)','Cosmetic creates false arena cover')]
  for old,new,message in cases:
   assert source.count(old)==1,old
   try:
    o=run(source.replace(old,new));assert digest(o)==EXPECTED,'Original gameplay geometry or flags changed'
   except AssertionError as e:assert message in str(e),str(e);print('PASS negative control:',message)
   else:raise AssertionError('Mutation accepted: '+message)
