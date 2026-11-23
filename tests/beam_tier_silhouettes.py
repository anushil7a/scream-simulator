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
 {1,1,0,0,'round','lightning',1.5},{10,1,1,0,'diamond','lightning',1.7},
 {20,1,1,2,'diamond','lightning',1.9},{30,1,1,4,'diamond','lightning',2.1},
 {40,1,2,4,'diamond','lightning',2.3},{50,1,2,6,'diamond','lightning',2.5},
 {60,1,2,8,'diamond','lightning',2.7},{70,2,3,8,'diamond','lightning',2.9},
 {80,2,3,10,'star','lightning',3.1},{90,2,3,12,'star','lightning',3.3},
 {100,2,3,16,'star','lightning',3.5}}

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
 check(s.collar==e[5] and s.ribbon==e[6] and near(s.turns,e[7]),'Authored tier identity missing')
 local signature=s.rings..s.strands..s.sparks..s.collar..s.ribbon..s.turns
 if level==1 or level%10==0 then check(signature~=previous,'Adjacent tier has identical authored silhouette');previous=signature end
 if level%10==0 then local before=StyleSource.Detail(level-1,false,0);check(before.tier==s.tier-1,'Threshold early/late')end
 for _,tint in ipairs({color,Color3.fromRGB(90,70,220),Color3.fromRGB(22,150,100)})do
  local r=Visuals.Create();Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
  local age=.6;local radius=7*(.24+s.tier*.012)*StyleSource.WidthScale(level,false)
  Visuals.Animate(r,r.born+age,Vector3.zero,false)
  check(#r.parts==5+s.rings*10+s.strands*12+s.sparks,'Actual geometry count mismatches profile')
  check(r.parts[1].Transparency==(level>=80 and .78 or .55) and r.parts[2].Transparency==(level>=80 and .7 or .18),'Body transparency tier boundary changed')
  local travel=(age*(.6+s.tier*.025)+1/s.rings)%1;local rr=radius*(.85+.2*math.sin(travel*math.pi))*(s.tier>=1 and 1.25 or 1);local angle=(1-.28)*math.pi/5+age*.9+.6
  local radial=rr
  if e[5]=='diamond' then radial/=math.abs(math.cos(angle))+math.abs(math.sin(angle)) elseif e[5]=='star' then radial*=.72+.28*(.5+.5*math.cos(angle*5)) end
  local endPoint=r.parts[6].CFrame.Target
  check(near(endPoint.X,math.cos(angle)*radial) and near(endPoint.Y,math.sin(angle)*radial),'Actual collar ignores authored silhouette')
  check(near(endPoint.Z,travel*40+(e[5]=='diamond' and math.cos(angle)*radial*.75 or 0)),'Side-view collar sweep missing')
  check(near(r.parts[6].Size.Y,.16+s.tier*.012),'Readable collar thickness missing')
  if level>=80 then
   for i=16,5+s.rings*10 do check(near(r.parts[i].Size.Y,.1) and near(r.parts[i].Size.Z,.1),'Supporting collar thickness changed')end
  end
  if s.strands>0 then
   for strand=1,s.strands do
    for i=1,12 do
     local t=i/12
     local phase=strand*math.pi*2/s.strands+t*s.turns+age*.35
     local distance=radius*(i%2==0 and .95 or .48)*math.sin(t*math.pi)
     local part=r.parts[5+s.rings*10+(strand-1)*12+i];local endpoint=part.CFrame.Target
     check(near(endpoint.X,math.cos(phase)*distance) and near(endpoint.Y,math.sin(phase)*distance) and near(endpoint.Z,40*t),'Actual ribbon ignores authored silhouette')
    end
   end
  end
  for _,p in ipairs(r.parts)do check(not p.CanCollide and not p.CanQuery and not p.CanTouch and not p.CastShadow,'Cosmetic became physical')end
  radius=7*(.24+s.tier*.012)*StyleSource.WidthScale(level,true)
  Visuals.Animate(r,r.born+age,Vector3.zero,true)
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*.72) and r.parts[1].Transparency==(level>=80 and .42 or .83) and near(r.parts[1].Size.X,level>=80 and 1.15 or 40),'Reduced geometry changed')
  for i,p in ipairs(r.parts)do check(p.Material==(i==3 and Enum.Material.Neon or Enum.Material.SmoothPlastic),'Reduced material changed')end
  Visuals.Animate(r,r.born+age,vec(0,0,111),false)
  check(#r.parts==4 and near(r.parts[1].Size.Y,radius*1.65) and r.parts[1].Transparency==.68,'Far geometry changed')
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
  cases=[(style.replace('tier>=1 and "diamond"','tier>=1 and "round"'),visual,'Authored tier identity missing'),(style,visual.replace('local offset=collarOffset','local offset=offset'),'Actual collar ignores'),(style,visual.replace('i%2==0 and .95 or .48','.65'),'Actual ribbon ignores'),(style,visual.replace('t*spec.turns','t*1.5'),'Actual ribbon ignores')]
  cases += [(style,visual.replace('*(tier>=1 and 1.25 or 1)',''),'Actual collar ignores'),(style,visual.replace('math.cos(angle)*r*.75','0'),'Side-view collar sweep missing'),(style,visual.replace('.16+tier*.012,support and color','.055+tier*.008,support and color'),'Readable collar thickness missing')]
  for st,vs,message in cases:
   assert st!=style or vs!=visual;r=run(st,vs);assert r.returncode and message in r.stderr,r.stdout+r.stderr
  print('PASS 7 targeted silhouette controls')
if __name__=='__main__':main()
