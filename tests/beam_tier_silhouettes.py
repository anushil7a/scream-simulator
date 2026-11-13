"""Authored tier profiles + actual renderer geometry; native distinctness remains pending."""
from pathlib import Path
import argparse,subprocess,tempfile
import beam_silhouette as support
ROOT=Path(__file__).resolve().parents[1]
STYLE=ROOT/'src/ReplicatedStorage/Shared/BeamStyle.luau'
VISUAL=ROOT/'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
CHECKS='''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local function near(a,b)return math.abs(a-b)<.00001 end
local expected={
 {1,1,0,0,'round','helix',1.5},{10,1,0,0,'diamond','helix',1.5},
 {20,1,0,4,'diamond','helix',1.5},{30,2,0,4,'round','helix',1.5},
 {40,2,1,4,'round','helix',1.5},{50,2,1,4,'round','zigzag',1.5},
 {60,3,1,4,'round','helix',1.5},{70,3,1,8,'round','helix',1.5},
 {80,3,2,8,'round','helix',1.5},{90,4,2,8,'star','helix',2.5},
 {100,4,2,8,'star','braid',3.5}}
local cases={}
for i,e in ipairs(expected)do
 table.insert(cases,e)
 if expected[i+1] and expected[i+1][1]-1>e[1] then local last=table.clone(e);last[1]=expected[i+1][1]-1;table.insert(cases,last)end
end
check(StyleSource.Tier('bad')==0 and StyleSource.Tier(0/0)==0 and StyleSource.Tier(-math.huge)==0 and StyleSource.Tier(math.huge)==10 and StyleSource.Tier(999)==10,'Malformed/clamped tier failed')
local previous
for _,e in ipairs(cases)do
 local level=e[1];local s=StyleSource.Detail(level,false,0)
 check(s.rings==e[2] and s.strands==e[3] and s.sparks==e[4],'Tier budget changed')
 check(s.collar==e[5] and s.ribbon==e[6] and s.turns==e[7],'Authored tier identity missing')
 local signature=s.rings..s.strands..s.sparks..s.collar..s.ribbon..s.turns
 if level==1 or level%10==0 then check(signature~=previous,'Adjacent tier has identical authored silhouette');previous=signature end
 if level%10==0 then local before=StyleSource.Detail(level-1,false,0);check(before.tier==s.tier-1,'Threshold early/late')end
 for _,tint in ipairs({color,Color3.fromRGB(90,70,220),Color3.fromRGB(22,150,100)})do
  local r=Visuals.Create();Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
  local age=.6;local radius=7*(.24+s.tier*.012)
  Visuals.Animate(r,r.born+age,Vector3.zero,false)
  check(#r.parts==5+s.rings*10+s.strands*12+s.sparks,'Actual geometry count mismatches profile')
  local travel=(age*(.6+s.tier*.025)+1/s.rings)%1;local rr=radius*(.85+.2*math.sin(travel*math.pi))*(s.tier>=1 and 1.25 or 1);local angle=(1-.28)*math.pi/5+age*.9+.6
  local radial=rr
  if e[5]=='diamond' then radial/=math.abs(math.cos(angle))+math.abs(math.sin(angle)) elseif e[5]=='star' then radial*=.72+.28*(.5+.5*math.cos(angle*5)) end
  local endPoint=r.parts[6].CFrame.Target
  check(near(endPoint.X,math.cos(angle)*radial) and near(endPoint.Y,math.sin(angle)*radial),'Actual collar ignores authored silhouette')
  check(near(endPoint.Z,travel*40+(e[5]=='diamond' and math.cos(angle)*radial*.75 or 0)),'Side-view collar sweep missing')
  check(near(r.parts[6].Size.Y,.16+s.tier*.012),'Readable collar thickness missing')
  if s.strands>0 then
   for strand=1,s.strands do
    for i=1,12 do
     local t=i/12;local winding=e[6]=='braid' and (strand==1 and 1 or -1) or 1
     local phase=t*math.pi*2*e[7]*winding-age*5+strand*math.pi
     local distance=radius*.95*math.sin(t*math.pi)
     if e[6]=='zigzag' then phase=age*.35+strand*math.pi;distance*=i%2==0 and -1 or 1 end
     local part=r.parts[5+s.rings*10+(strand-1)*12+i];local endpoint=part.CFrame.Target
     check(near(endpoint.X,math.cos(phase)*distance) and near(endpoint.Y,math.sin(phase)*distance) and near(endpoint.Z,40*t),'Actual ribbon ignores authored silhouette')
    end
   end
  end
  for _,p in ipairs(r.parts)do check(not p.CanCollide and not p.CanQuery and not p.CanTouch and not p.CastShadow,'Cosmetic became physical')end
  Visuals.Animate(r,r.born+age,Vector3.zero,true)
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*1.65) and r.parts[1].Transparency==.72,'Reduced geometry changed')
  for _,p in ipairs(r.parts)do check(p.Material==Enum.Material.Neon,'Reduced material changed')end
  Visuals.Animate(r,r.born+age,vec(0,0,111),false)
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*1.65*(1+.035*math.sin(age*9))) and r.parts[1].Transparency==.68,'Far geometry changed')
  Visuals.Destroy(r)
 end
end
Visuals.Clear();check(Visuals.Budget()==0,'Tier cleanup leaked')
print('PASS '..checks..' authored tier/actual geometry assertions; mocked orientation')
'''
def run(style,visual):
 previous=support.CHECKS;support.CHECKS=CHECKS
 try:script=support.fixture(visual)
 finally:support.CHECKS=previous
 anchor="local StyleSource=require('../src/ReplicatedStorage/Shared/BeamStyle')";assert script.count(anchor)==1
 script=script.replace(anchor,'local StyleSource=(function()\n'+style+'\nend)()')
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',prefix='tmp_tiers_',dir=ROOT/'tests',delete=False)as f:p=Path(f.name);f.write(script)
 try:return subprocess.run(['luau',str(p)],cwd=ROOT,text=True,capture_output=True)
 finally:p.unlink()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');args=parser.parse_args();style=STYLE.read_text();visual=VISUAL.read_text()
 r=run(style,visual);assert r.returncode==0,r.stdout+r.stderr;print(r.stdout.strip())
 # Optional local contributor fade is not our dependency or feature. Verify the same
 # authored geometry with its prior alpha expression when that local hunk is present.
 fade='local fade=math.abs(2*travel-1)^3'
 if fade in visual:
  plain=visual.replace(fade,'').replace('color,.26+.74*fade)','color,.26+travel*.32)')
  r=run(style,plain);assert r.returncode==0,r.stdout+r.stderr;print('PASS same tier assertions without pre-existing local collar fade')
 if args.negative_controls:
  cases=[(style.replace('[1]={collar="diamond"','[1]={collar="round"'),visual,'Authored tier identity missing'),(style,visual.replace('local offset=collarOffset','local offset=offset'),'Actual collar ignores'),(style,visual.replace('if spec.ribbon=="zigzag" then','if false then'),'Actual ribbon ignores'),(style,visual.replace('spec.ribbon=="braid" and (strand==1 and 1 or -1) or 1','1'),'Actual ribbon ignores'),(style,visual.replace('2*spec.turns*winding','3*winding'),'Actual ribbon ignores')]
  cases += [(style,visual.replace('*(tier>=1 and 1.25 or 1)',''),'Actual collar ignores'),(style,visual.replace('math.cos(angle)*r*.75','0'),'Side-view collar sweep missing'),(style,visual.replace('.16+tier*.012,color','.055+tier*.008,color'),'Readable collar thickness missing')]
  for st,vs,message in cases:
   assert st!=style or vs!=visual;r=run(st,vs);assert r.returncode and message in r.stderr,r.stdout+r.stderr
  print('PASS 8 targeted silhouette controls')
if __name__=='__main__':main()
