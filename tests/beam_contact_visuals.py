"""Actual contact renderer, frozen-base differential and pool lifecycle; no native/GPU claim."""
from pathlib import Path
import argparse
import subprocess
import tempfile
import beam_silhouette as support

ROOT = Path(__file__).resolve().parents[1]
VISUAL = ROOT / 'src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'
BASE = '5622daa54424e639e7d3f671b2e453ff377b2cb6'
ENV = """
local clock=20;local os={clock=function()return clock end}
local function typeof(v)return getmetatable(v)==V and 'Vector3' or type(v)end
"""


def fixture(source, checks):
    previous = support.CHECKS
    support.CHECKS = ''
    try:
        body = support.fixture(source)
    finally:
        support.CHECKS = previous
    anchor = "local StyleSource=require('../src/ReplicatedStorage/Shared/BeamStyle')"
    assert body.count(anchor) == 1
    return body.replace(anchor, ENV + anchor) + checks


CHECKS = r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local function near(a,b)return math.abs(a-b)<.000001 end
local function vector(a,b)return a and b and a.X==b.X and a.Y==b.Y and a.Z==b.Z end
local function equal(a,b)
 if a==b then return true end
 if type(a)~='table' then return a==b end
 if a.X~=nil then return vector(a,b) end
 if a.R~=nil then return a.R==b.R and a.G==b.G and a.B==b.B end
 return (not a.Position and not b.Position or vector(a.Position,b.Position)) and (not a.Target and not b.Target or vector(a.Target,b.Target)) and vector(a.RightVector,b.RightVector) and vector(a.UpVector,b.UpVector)
end
local function unchanged(a,b,highSpec)
 check(#a==#b,'Original beam geometry count changed')
 for i,p in ipairs(a)do
  local collarEnd=highSpec and 5+highSpec.rings*10 or 0
  local ribbonEnd=highSpec and collarEnd+highSpec.strands*12 or 0
  local support=highSpec and i>15 and i<=collarEnd
  local ribbon=highSpec and i>collarEnd and i<=ribbonEnd
  local spark=highSpec and i>ribbonEnd
  for _,key in ipairs({'Name','Anchored','CanCollide','CanTouch','CanQuery','CastShadow','Material','TopSurface','BottomSurface','Shape','Size','CFrame','Color','Transparency','Parent'})do
   local styled=highSpec and i<=2 and key=='Transparency' or (support or ribbon or spark) and (key=='Material' or key=='Transparency') or (support or ribbon) and key=='Color'
   if support and key=='Size' then check(p.Size.X==b[i].Size.X,'Original supporting collar length changed')
   elseif not styled then check(equal(p[key],b[i][key]),'Original beam property changed: '..i..' '..key)end
  end
 end
end
local function create(level,reduced,width)
 local r=Visuals.Create();Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,width or 7,color,level or 100,reduced or false);return r
end
local function spokes(parts,anchor,count,extent,inner)
 check(#parts==count*2,'Contact stroke count changed')
 for i=1,count do
  local angle=(i-.5)*math.pi*2/count;local x,y=math.cos(angle),math.sin(angle)
  for layer=1,2 do
   local p=parts[(i-1)*2+layer];local finish=p.CFrame.Target;local start=p.CFrame.Position*2-finish
   local depth=layer==1 and .7 or .82;local thickness=layer==1 and .18 or .1
   check(near(start.X-anchor.X,x*inner) and near(start.Y-anchor.Y,y*inner),'Contact stroke lost open center')
   check(near(finish.X-anchor.X,x*extent) and near(finish.Y-anchor.Y,y*extent),'Contact stroke not radial/outward')
   check(inner>0 and extent>inner and near(p.Size.X,extent-inner),'Contact stroke collapsed or crossed center')
   check(near(start.Z,anchor.Z-depth) and near(finish.Z,anchor.Z-depth),'Contact stroke left target front plane')
   -- Modeled torso half-depth only; actual visibility is a separate native check.
   check(math.min(anchor.Z-start.Z,anchor.Z-finish.Z)-thickness*.5>.5,'Contact stroke buried in half-stud target depth')
  end
 end
end
-- Preserve the original oracle except the authorized L80+ near-detail styling.
for _,level in ipairs({1,9,10,19,20,29,30,39,40,49,50,59,60,69,70,79,80,89,90,99,100})do
 for _,tint in ipairs({color,Color3.fromRGB(35,150,105),Color3.fromRGB(85,60,225)})do
  for _,mode in ipairs({{false,0},{true,0},{false,111},{false,181}})do
   local old=Baseline.Create();local r=create(level)
   Baseline.Update(old,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
   Visuals.Update(r,Vector3.zero,Vector3.zAxis,40,7,tint,level,false)
   local time=clock+.6;local viewer=vec(0,0,mode[2])
   local highSpec=level>=80 and not mode[1] and mode[2]==0 and StyleSource.Detail(level,false,0) or nil
   Baseline.Animate(old,time,viewer,mode[1]);Visuals.Animate(r,time,viewer,mode[1])
   unchanged(old.parts,r.parts,highSpec);check(#r.contact.parts==0,'Endpoint alone produced contact')
   check(Visuals.Contact(r,vec(2,1,24),time,level),'Valid contact rejected')
   Visuals.Animate(r,time,viewer,mode[1]);unchanged(old.parts,r.parts,highSpec)
   check(#r.contact.parts==(mode[2]>180 and 0 or (mode[1] or mode[2]>110) and 8 or 16),'Contact complexity changed')
   Baseline.Destroy(old);Visuals.Destroy(r)
  end
 end
end
Baseline.Clear();Visuals.Clear()
local uninitialized=Visuals.Create();check(not Visuals.Contact(uninitialized,Vector3.zero,clock),'Uninitialized contact accepted');Visuals.Destroy(uninitialized)
local r=create();local anchor=vec(2,1,24)
for _,bad in ipairs({'bad',{},vec(0/0,0,0),vec(0,math.huge,0),vec(0,0,-math.huge),vec(math.huge,0,0),vec(0,0/0,0),vec(0,0,0/0),vec(181,0,0)})do
 check(not Visuals.Contact(r,bad,clock),'Malformed/out-of-range position accepted')
end
check(not Visuals.Contact(r,nil,clock),'Missing position accepted')
for _,bad in ipairs({'bad',0/0,math.huge,-math.huge})do check(not Visuals.Contact(r,anchor,bad),'Invalid contact clock accepted')end
check(not Visuals.Contact(r,anchor,nil),'Missing contact clock accepted')
check(not r.contactPosition and not r.nextContact and #r.contact.parts==0,'Rejected input mutated contact')
check(Visuals.Contact(r,anchor,clock,7),'Initial contact rejected')
Visuals.Animate(r,clock,Vector3.zero,false)
check(#r.contact.parts==16 and r.contactPosition==anchor,'Regular contact missing')
local backing,core=r.contact.parts[1],r.contact.parts[2]
check(backing.Material==Enum.Material.SmoothPlastic and core.Material==Enum.Material.Neon and near(backing.Size.Y,.18) and near(core.Size.Y,.1),'Contact hierarchy changed')
spokes(r.contact.parts,anchor,8,1.65,1.65*.58)
check(backing.Transparency==.15 and core.Transparency==.1,'Contact initial alpha changed')
for _,p in ipairs(r.contact.parts)do check(p.Anchored and not p.CanCollide and not p.CanQuery and not p.CanTouch and not p.CastShadow,'Contact gained physics')end
local ending=clock+.28;local nextContact=clock+.4
for _,offset in ipairs({-.1,.01,.15,.279})do
 check(not Visuals.Contact(r,vec(4,3,30),clock+offset,8),'Rate limit accepted repeated/backward contact')
 check(r.contactBorn==clock and r.nextContact==nextContact and r.contactPosition==anchor,'Repeated contact extended/replaced pulse')
end
Visuals.Animate(r,clock+.14,Vector3.zero,false);spokes(r.contact.parts,anchor,8,2.025,2.025*.64)
Visuals.Animate(r,ending-.000001,Vector3.zero,false);check(#r.contact.parts==16,'Contact expired early')
Visuals.Animate(r,ending,Vector3.zero,false);check(#r.contact.parts==0 and not r.contactPosition,'Contact TTL boundary retained pulse')
check(not Visuals.Contact(r,anchor,nextContact-.000001),'Contact cooldown ended early')
check(Visuals.Contact(r,anchor,nextContact,9),'Contact cooldown boundary rejected')
Visuals.Animate(r,nextContact,Vector3.zero,false,false);check(#r.contact.parts==0 and not r.contactPosition,'Blocked contact retained')
Visuals.Animate(r,nextContact+.01,Vector3.zero,false,true);check(#r.contact.parts==0,'Unblock replayed contact')
Visuals.Destroy(r);check(not Visuals.Contact(r,anchor,clock+1),'Destroyed rig accepted contact');Visuals.Destroy(r)
-- Quiet/far/OS comfort stay static; rig updates cannot drag a target-anchored cue.
for _,mode in ipairs({{true,0,false,false},{false,111,false,false},{false,0,true,false},{false,0,false,true}})do
 r=create(100,mode[4]);check(Visuals.Contact(r,anchor,clock,11),'Quiet contact rejected')
 local viewer=vec(0,0,mode[2]);Visuals.Animate(r,clock,viewer,mode[1],true,mode[3])
 check(#r.contact.parts==8,'Quiet/far contact budget changed')
 spokes(r.contact.parts,anchor,4,1.8,1.8*.72)
 local before={};for i,p in ipairs(r.contact.parts)do before[i]={Size=p.Size,CFrame=p.CFrame,Transparency=p.Transparency,Color=p.Color}end
 Visuals.Update(r,vec(2,3,4),Vector3.yAxis,20,7,color,100,mode[4])
 if mode[2]>0 then viewer=vec(2,3,mode[2]+4) end
 Visuals.Animate(r,clock+.15,viewer,mode[1],true,mode[3])
 for i,p in ipairs(r.contact.parts)do
  check(equal(before[i].Size,p.Size) and equal(before[i].CFrame,p.CFrame) and equal(before[i].Color,p.Color) and before[i].Transparency==p.Transparency,'Quiet contact moved/flashed after aim update')
 end
 Visuals.Animate(r,clock+.28,viewer,mode[1],true,mode[3]);check(#r.contact.parts==0,'Quiet TTL retained')
 Visuals.Destroy(r)
end
r=create();check(Visuals.Contact(r,anchor,clock,12),'Switch contact rejected');Visuals.Animate(r,clock,Vector3.zero,false)
Visuals.Animate(r,clock+.05,Vector3.zero,true);check(#r.contact.parts==8,'Reduced switch retained regular strokes')
Visuals.Animate(r,clock+.1,vec(0,0,181),false);check(#r.parts==0 and #r.contact.parts==0,'Cull retained core/contact parts')
Visuals.Animate(r,clock+.15,Vector3.zero,false);check(#r.contact.parts==0 and not r.contactPosition,'Cull replayed old contact')
Visuals.Destroy(r);Visuals.Clear()
local edge=create();check(Visuals.Contact(edge,vec(180,0,0),clock),'Draw-distance contact boundary rejected');Visuals.Destroy(edge);Visuals.Clear()
-- Contact uses the existing optional allowance, including slots one through five.
local rigs={}
local function audit(coreCount)
 local seen={};local active,optional=0,0
 for _,rig in ipairs(rigs)do
  check(#rig.parts>=coreCount,'Contact pressure starved beam core')
  optional+=math.max(0,#rig.parts-coreCount)+#rig.contact.parts
  for _,parts in ipairs({rig.parts,rig.contact.parts})do for _,p in ipairs(parts)do
   check(not seen[p] and not p.dead and p.Parent==workspace,'Duplicate/stale contact pool part');seen[p]=true;active+=1
   check(p.Material==Enum.Material.Neon or p.Material==Enum.Material.SmoothPlastic,'Pooled material uninitialized')
  end end
 end
 local allocated,cached=Visuals.Budget()
 check(allocated<=512 and allocated==made-dead and active+cached==allocated,'Contact pool cap/accounting leaked')
 check(optional<=392,'Contact exceeded optional allowance')
 return active,optional
end
for i=1,24 do rigs[i]=create();check(Visuals.Contact(rigs[i],anchor,clock,i),'Crowded contact rejected');Visuals.Animate(rigs[i],clock,Vector3.zero,false)end
local peak=Visuals.Budget();local active,optional=audit(5)
check(peak==512 and active==512 and optional==392,'Optional budget not fully reusable')
local extra=create();Visuals.Animate(extra,clock,Vector3.zero,false)
check(#extra.parts==0 and Visuals.Budget()==512,'Global contact pool cap exceeded');Visuals.Destroy(extra)
for cycle=1,4 do
 clock+=.5
 for _,rig in ipairs(rigs)do check(Visuals.Contact(rig,anchor,clock),'Reused crowded contact rejected');Visuals.Animate(rig,clock,Vector3.zero,true)end
 audit(4)
 for _,rig in ipairs(rigs)do Visuals.Animate(rig,clock+.02,vec(0,0,111),false)end;audit(4)
 for _,rig in ipairs(rigs)do Visuals.Animate(rig,clock+.04,vec(0,0,181),false)end
 local n,cached=Visuals.Budget();check(n==cached and n==peak,'Culled contact pool leaked/grew')
 for _,rig in ipairs(rigs)do Visuals.Animate(rig,clock+.06,Vector3.zero,false)end
 active,optional=audit(5);check(active==512 and optional==392,'Released contact/detail budget not reusable')
end
for _,rig in ipairs(rigs)do Visuals.Destroy(rig)end
local n,cached=Visuals.Budget();check(n==cached,'Destroy orphaned contact parts')
Visuals.Clear();check(Visuals.Budget()==0 and made==dead,'Clear leaked contact parts');Visuals.Clear()
print('PASS',checks,'actual contact/base-property/pool checks; vector and orientation doubles, no native rendering')
'''


def run(source, baseline, expected=None):
    baseline = baseline.replace('require(game:GetService("ReplicatedStorage").Shared.BeamStyle)', 'StyleSource')
    body = fixture(source, '\nlocal Baseline=(function()\n' + baseline + '\nend)()\n' + CHECKS)
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', prefix='tmp_contact_', dir=ROOT / 'tests', delete=False) as f:
        path = Path(f.name)
        f.write(body)
    try:
        result = subprocess.run(['luau', str(path)], cwd=ROOT, capture_output=True, text=True, timeout=30)
    finally:
        path.unlink()
    output = result.stdout + result.stderr
    if expected:
        assert result.returncode and expected in output, output
        print('PASS control:', expected)
    else:
        assert result.returncode == 0, output
        print(output.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--negative-controls', action='store_true')
    args = parser.parse_args()
    source = VISUAL.read_text(encoding='utf-8-sig')
    baseline = subprocess.check_output(['git', 'show', BASE + ':src/StarterPlayer/StarterPlayerScripts/BeamVisuals.luau'], cwd=ROOT, text=True)
    style = subprocess.check_output(['git', 'show', BASE + ':src/ReplicatedStorage/Shared/BeamStyle.luau'], cwd=ROOT, text=True)
    baseline = 'local StyleSource=(function()\n' + style + '\nend)()\n' + baseline
    run(source, baseline)
    if args.negative_controls:
        cases = [
            ('detailed and 1.35 or 1.65', 'detailed and 1.36 or 1.65', 'Original beam property changed'),
            ('now<(rig.nextContact or -math.huge)', 'false', 'Rate limit accepted'),
            ('now>=rig.contactBorn+.28', 'now>rig.contactBorn+.28', 'Contact TTL boundary'),
            ('n~=n or math.abs(n)==math.huge', 'math.abs(n)==math.huge', 'Malformed/out-of-range position accepted'),
            ('contactAllowed==false', 'false', 'Blocked contact retained'),
            ('quiet or contactReduced or distance>Style.FarDistance', 'quiet or distance>Style.FarDistance', 'Quiet/far contact budget'),
            ('local contactDir=rig.contactDirection', 'local contactDir=dir', 'Quiet contact moved/flashed'),
            ('take(detail or rig.used>5)', 'take(rig.used>5)', 'Contact pressure starved beam core'),
            ('if allocated>=Style.MaxParts then return end', 'if false then return end', 'Global contact pool cap exceeded'),
            ('decoration[part]=nil;detailCount-=1', 'decoration[part]=nil', 'Contact complexity changed'),
            ('for _,part in ipairs(rig.contact.parts) do release(part) end', 'for _,part in ipairs(rig.contact.parts) do end', 'Original beam geometry count changed'),
            ('local from=center+radial*inner;local to=center+radial*extent', 'local from=center;local to=center+radial*extent', 'Contact stroke lost open center'),
            ('local to=center+radial*extent', 'local to=center-radial*extent', 'Contact stroke not radial/outward'),
            ('rig.contactPosition-contactDir*.7', 'rig.contactPosition-contactDir*.4', 'Contact stroke left target front plane'),
        ]
        for old, new, expected in cases:
            assert source.count(old) == 1, old
            run(source.replace(old, new), baseline, expected)


if __name__ == '__main__':
    main()
