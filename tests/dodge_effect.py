"""Actual client Effect callback in deterministic mocks; no native rendering/audio claim."""
from pathlib import Path
import argparse,subprocess,tempfile
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');p.add_argument('--scope-check',action='store_true');args=p.parse_args()
name='src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def baseline(path):return subprocess.check_output(['git','show','078dbb1:'+path],cwd=root,text=True,encoding='utf-8')
client=baseline(name) if args.baseline else (root/name).read_text(encoding='utf-8')
def extract(s):
 a=s.index('local function fxPart(');constructor=s[a:s.index('local BeamVisuals=',a)]
 a=s.index('connectClient(remotes.Effect.OnClientEvent,');return constructor+s[a:s.index('\nlocal elapsed=0',a)]
fragment=extract(client)
setup=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local V={};V.__index=function(t,k)if k=="Magnitude" then return math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z) end return V[k] end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
V.__add=function(a,b)return Vector3.new(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end
V.__sub=function(a,b)return Vector3.new(a.X-b.X,a.Y-b.Y,a.Z-b.Z)end
local function color()return {tag="Color3"}end
local function typeof(x)return type(x)=="table" and x.tag or type(x)end
local gold,blue= color(),color();local parts,tweens,debris,cues,renders,lookups={},{},{},{},{},0
local Instance={new=function(class)local f={ClassName=class};table.insert(parts,f);return f end}
local Enum={Material={Neon="Neon"}};local workspace={}
local Debris={AddItem=function(_,f,t)table.insert(debris,{f,t})end}
local TweenInfo={new=function(t)return t end}
local Tween={Create=function(_,f,t,props)local rec={f=f,t=t,props=props,played=false};table.insert(tweens,rec);return {Play=function()rec.played=true end}end}
local function playGameplayCue(kind,pos)table.insert(cues,{kind,pos})end
local root={Position=Vector3.new(0,0,0)}
local character={FindFirstChild=function(_,key)return key=="HumanoidRootPart" and root end}
local p={Character=character,UserId=7};local data={level=20,settings={reducedShake=false}}
local Config={Auras={Blue=blue},GetSound=function(id)lookups+=1;if id=="Known" then return {effect="beam",variant=2,level=10}end end,VoiceCombat={Stats=function()return {range=55}end}}
local ScreamEffects={Render=function(...)table.insert(renders,{...})end}
local accepted=true;local hitFeedback={Accept=function()return accepted end}
-- Decorative feedback is verified separately; preserve this fixture's audio/world assertions.
local beamScreenFeedback={Hit=function()end,Clear=function()end};local sustainedControl=nil
local function screenFeedbackAllowed()return false end
local stops,removed,pulses,updates={},{},{},{}
local attackAudio={Stop=function(_,id)table.insert(stops,id)end,Remove=function(_,id)table.insert(removed,id)end,Pulse=function(...)table.insert(pulses,{...})end}
local sustainedBeams={Remove=function(_,id)table.insert(removed,id)end,Update=function(...)table.insert(updates,{...})end}
local Players={GetPlayerByUserId=function(_,id)return id==7 and p end};local attackAudioSettings={Range=100}
local remotes={Effect={OnClientEvent={}}};local handler
local function connectClient(signal,fn)check(signal==remotes.Effect.OnClientEvent,"Wrong event");handler=fn end
local function reset()parts={};tweens={};debris={};cues={};renders={};lookups=0 end
'''
tests=r'''
local pos=Vector3.new(2,0,0)
for _,reduced in ipairs({false,true}) do
 data.settings.reducedShake=reduced
 for _,id in ipairs({"Blue","Known","Unknown",color()}) do
  reset();handler("Dodge",pos,id)
  check(#parts==0,"Dodge allocated cosmetic Part")
  check(#tweens==0 and #debris==0,"Dodge allocated tween or debris")
  check(#cues==1 and cues[1][1]=="Dodge" and cues[1][2]==pos,"Dodge cue changed")
  check(#renders==0 and lookups==0,"Dodge fell through")
 end
end
for _,distance in ipairs({180,180.001,1000}) do
 reset();handler("Dodge",Vector3.new(distance,0,0),"Known")
 check(#cues==(distance<=180 and 1 or 0),"Dodge range guard changed")
 check(#parts==0 and #renders==0,"Distant Dodge rendered")
end
for _,missing in ipairs({"character","root"}) do
 reset();if missing=="character" then p.Character=nil else root=nil end
 handler("Dodge",pos,"Known");check(#cues==0 and #parts==0,"Missing root emitted effect")
 p.Character=character;root={Position=Vector3.new(0,0,0)}
end
for _,id in ipairs({"Blue","Unknown",color()}) do
 reset();handler("Break",pos,id)
 check(#parts==6 and #tweens==6 and #debris==6,"Break chips changed")
 check(#cues==1 and cues[1][1]=="Break" and cues[1][2]==pos,"Break cue changed")
 local expected=typeof(id)=="Color3" and id or Config.Auras[id] or gold
 for i,f in ipairs(parts) do
  check(f.ClassName=="Part" and f.Material=="Neon" and f.Color==expected,"Break appearance changed")
  check(f.Anchored and not f.CanCollide and not f.CanTouch and not f.CanQuery,"Break physics changed")
  check(f.Size.X==.5 and f.Size.Y==.5 and f.Size.Z==.5 and f.Position==pos and f.Transparency==.3 and f.Parent==workspace,"Break geometry changed")
  check(debris[i][1]==f and debris[i][2]==1.1 and tweens[i].f==f and tweens[i].t==.45 and tweens[i].played and tweens[i].props.Transparency==1,"Break lifecycle changed")
 end
end
reset();handler("Attack",pos,"Known","Blue")
check(#renders==1 and renders[1][1]=="beam" and renders[1][4]==55 and renders[1][5]==4 and renders[1][6]==blue and renders[1][7]==true and renders[1][8]==2,"Attack rendering changed")
check(#parts==0 and #cues==0,"Attack gained Dodge effects")
reset();handler("Attack",pos,"Invalid",{})
check(#renders==0 and #parts==0 and #cues==0,"Unknown sound rendered")
reset();handler("Dodge",pos,nil);check(#cues==1 and #parts==0,"Nil color behavior changed")
reset();handler("SustainedHit",nil,7,1);check(#cues==1 and cues[1][1]=="Hit","Hit cue changed")
accepted=false;handler("SustainedHit",nil,7,1);check(#cues==1,"Rejected hit emitted cue")
handler("SustainedBeamEnd",nil,7);check(stops[1]==7 and removed[1]==7,"Beam end changed")
handler("SustainedBeam",pos,7,"Blue",Vector3.new(0,0,-1),10,4,"Known",20)
check(#updates==1 and #pulses==1,"Sustained beam changed")
print("PASS "..checks.." actual Effect callback assertions; mocked rendering/audio only")
'''
def run(source,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False) as f:f.write(source);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],cwd=root,text=True,capture_output=True)
 finally:path.unlink()
 if expected:
  assert r.returncode and expected in r.stdout+r.stderr,r.stdout+r.stderr
  print('PASS expected failure: '+expected)
 else:
  assert r.returncode==0,r.stdout+r.stderr
  print(r.stdout.strip())
if args.baseline:
 run(setup+fragment+tests,'Dodge allocated cosmetic Part')
else:
 run(setup+fragment+tests)
 if args.scope_check:
  paths=[p for p in (root/'src').rglob('*.luau') if 'ServerScriptService' in p.parts or p.name in ['RunAnimation.client.luau','Config.luau'] or 'Audio' in p.name]
  for path in paths:
   rel=path.relative_to(root).as_posix();assert path.read_text(encoding='utf-8')==baseline(rel),'Out-of-scope production change: '+rel
  print('PASS '+str(len(paths))+' server/animation/config/audio source-equality contracts against 078dbb1')
 if args.negative_controls:
  fixed='if kind=="Dodge" then playGameplayCue("Dodge",pos);return end'
  assert fixed in fragment,'Missing fixed branch'
  old=extract(baseline(name));oldline=next(line.strip() for line in old.splitlines() if 'if kind=="Dodge" then playGameplayCue' in line)
  cases=[(fragment.replace(fixed,oldline),'Dodge allocated cosmetic Part'),(fragment.replace('playGameplayCue("Dodge",pos);',''),'Dodge cue changed'),(fragment.replace(fixed,'if kind=="Dodge" then playGameplayCue("Dodge",pos) end'),'Dodge fell through'),(fragment.replace('if not root or (root.Position-pos).Magnitude>180 then return end','if not root then return end'),'Dodge range guard changed')]
  for mutated,error in cases:
   assert mutated!=fragment
   run(setup+mutated+tests,error)
