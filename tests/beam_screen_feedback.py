"""Actual presentation module with mock GUI properties/clock; no native layout claim."""
from pathlib import Path
import argparse,subprocess,tempfile
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
s=(R/'src/StarterPlayer/StarterPlayerScripts/BeamScreenFeedback.luau').read_text(encoding='utf-8-sig')
setup=r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local count=0;local destroyed=0;local instances={}
local Instance={new=function(kind)count+=1;local x={kind=kind};function x:Destroy()destroyed+=1;self.Parent=nil end;table.insert(instances,x);return x end}
local Vector2={new=function(x,y)return {X=x,Y=y}end}
local UDim2={new=function(xs,xo,ys,yo)return {X={Scale=xs,Offset=xo},Y={Scale=ys,Offset=yo}}end}
function UDim2.fromScale(x,y)return UDim2.new(x,0,y,0)end
function UDim2.fromOffset(x,y)return UDim2.new(0,x,0,y)end
local Color3={fromRGB=function(r,g,b)return {kind='Color3',R=r/255,G=g/255,B=b/255}end}
local function typeof(x)return type(x)=='table' and x.kind or type(x)end
local function load()
'''
checks=r'''
end
local F=load();local f=F.new({});check(count==13 and #f.rays==8 and #f.marks==4,'Pool size wrong')
check(not f.root.Visible,'Overlay visible initially')
for _,v in ipairs(instances)do check(v.Active==false and v.Selectable==false and v.Interactable==false and v.ZIndex==0,'Interactive or foreground overlay')end
for _,v in ipairs(f.marks)do
 local x,y=v.Position.X.Offset,v.Position.Y.Offset
 check(math.abs(x)>=27 or math.abs(y)>=27,'Hit mark crosses central40px sightline')
 check(v.Size.X.Offset==6 and v.Size.Y.Offset==2,'Hit geometry changed')
end
for _,v in ipairs(f.rays)do check(v.Position.X.Scale<.1 or v.Position.X.Scale>.9 or v.Position.Y.Scale<.1 or v.Position.Y.Scale>.9,'Launch not peripheral')end
local color=Color3.fromRGB(120,200,255)
check(f:Begin(1,1,color,true),'Start rejected');f:Step(1,true,false)
check(f.root.Visible and math.abs(f.rays[1].BackgroundTransparency-.88)<1e-9 and f.rays[1].BackgroundColor3==color,'Start appearance wrong')
check(not f:Begin(1,1.1,color,true) and not f:Begin(0,1.1,color,true),'Duplicate start accepted')
f:Step(1.225,true,false);check(math.abs(f.rays[1].BackgroundTransparency-.94)<1e-9,'Launch fade wrong')
f:Step(1.45,true,false);check(not f.root.Visible,'Launch did not expire')
check(f:Hit(2,true),'Hit rejected');f:Step(2,true,false);check(math.abs(f.marks[1].BackgroundTransparency-.6)<1e-9,'Hit alpha wrong')
for i=1,24 do check(not f:Hit(2+i*.01,true),'Hit restarted inside cooldown')end
f:Step(2.25,true,false);check(not f.root.Visible,'Coalesced hits extended expiry')
check(not f:Hit(2.349,true) and f:Hit(2.35,true),'Hit cooldown boundary wrong')
f:Clear();check(not f.root.Visible and f.sequence==1,'Clear reset sequence floor')
check(not f:Begin(1,3,color,true),'Clear replayed stale start')
check(not f:Begin(2,3,color,false),'Disallowed start animated');check(not f:Begin(2,3,color,true),'Hidden start replayed')
check(not f:Hit(3,false),'Hidden hit animated')
check(f:Begin(3,4,nil,true),'Fallback color failed');f:Step(4,false,false);f:Step(4.1,true,false);check(not f.root.Visible,'Hidden Step queued feedback')
check(f:Begin(4,5,color,true),'Start4 failed');f:Hit(5,true);f:Step(5,true,true);f:Step(5.1,true,false);check(not f.root.Visible,'Reduced effects queued feedback')
for _,v in ipairs({0,-1,1.5,math.huge,0/0,9007199254740992,'6',false,{}})do check(not f:Begin(v,6,color,true),'Malformed sequence accepted')end
for _,t in ipairs({-1,math.huge,0/0,'6',false,{}})do check(not f:Hit(t,true),'Malformed time accepted')end
check(not f:Begin(5,4,color,true) and not f:Begin(5,6,color,true),'Backdated start replayed')
f:Begin(6,7,color,true);f:Step(0/0,true,false);check(not f.root.Visible,'Invalid Step left feedback visible')
local startCount=count
for i=1,10000 do local t=8+i*.01;f:Begin(i+6,t,color,true);f:Hit(t,true);f:Step(t,true,false)end
check(count==startCount,'Events grew instance pool')
f:Destroy();local again=pcall(function()f:Destroy()end);check(again and destroyed==1 and f.root==nil and #f.rays==0 and #f.marks==0,'Destroy not bounded/idempotent')
check(not f:Begin(20000,200,color,true) and not f:Hit(200,true),'Destroyed feedback restarted');f:Step(200,true,false);f:Clear();check(count==startCount,'Destroyed feedback allocated')
print('PASS',n,'actual module assertions; mock GUI only')
'''
def run(source,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.beam_screen_',dir=R/'tests',encoding='utf-8',delete=False)as t:t.write(setup+source+checks);q=Path(t.name)
 try:r=subprocess.run(['luau',str(q)],capture_output=True,text=True,timeout=20)
 finally:q.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
run(s)
if args.negative_controls:
 for old,new,message in [
 ('sequence<=self.sequence','sequence<self.sequence','Duplicate start accepted'),
 ('self.sequence=sequence','if allowed then self.sequence=sequence end','Hidden start replayed'),
 ('self.hitEnds=now+.25','self.hitEnds=now+.5','Coalesced hits extended expiry'),
 ('now<self.nextHit','false','Hit restarted inside cooldown'),
 ('visible~=true or reduced==true','visible~=true','Reduced effects queued feedback'),
 ('visible~=true or reduced==true','reduced==true','Hidden Step queued feedback'),
 ('f.Interactable=false','f.Interactable=true','Interactive or foreground overlay'),
 ('now<self.clock','false','Backdated start replayed'),
 ('self.destroyed=true;self.root:Destroy()','self.root:Destroy()','Destroy not bounded/idempotent'),
 ]:
  assert s.count(old)==1,old;run(s.replace(old,new),message)
assert not any(v in s for v in ('TweenService','CurrentCamera','FieldOfView','FireServer','task.spawn','task.delay','Connect('))
print('PASS source contract: no camera, transport, scheduled work or connections')
