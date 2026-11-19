"""Presentation module with UI doubles. No microphone/device or Studio evidence."""
from pathlib import Path
import subprocess,tempfile
R=Path(__file__).resolve().parents[1]
module=(R/'src/StarterPlayer/StarterPlayerScripts/VoiceReactor.luau').read_text()
setup='''
local objects={}
Color3={fromRGB=function(r,g,b)return {r,g,b}end}
UDim={new=function(s,o)return {Scale=s,Offset=o}end}
UDim2={new=function(a,b,c,d)return {X={Scale=a,Offset=b},Y={Scale=c,Offset=d}}end}
UDim2.fromOffset=function(x,y)return UDim2.new(0,x,0,y)end
UDim2.fromScale=function(x,y)return UDim2.new(x,0,y,0)end
Vector2={new=function(x,y)return {X=x,Y=y}end}
Enum={Font={GothamMedium='GothamMedium'},TextXAlignment={Left='Left'}}
Instance={new=function(class)local o={ClassName=class};table.insert(objects,o);return o end}
local Reactor=(function()
'''
checks=r'''
end)()
local n=0;local function check(v,msg)assert(v,msg);n+=1 end
for _,entry in ipairs({{-.5,0},{2,1},{0,0},{.42,.42},{math.huge,1},{-math.huge,0},{0/0,0},{'bad',0}})do check(Reactor.Power(entry[1])==entry[2],'Unbounded power')end
check(Reactor.Power(nil)==0,'Missing power')
local r=Reactor.new({})
check(#r.bars==28 and #r.history==28,'Incorrect sample bank')
check(not r.root.Active,'Decorative view intercepts input')
r:Step(.8,.04,false,true)
check(r.history[28]==.8 and r.history[27]==0,'History not actual samples')
check(r.bars[28].Size.Y.Offset==18 and r.bars[27].Size.Y.Offset==2,'Amplitude geometry incorrect')
r:Step(.2,.04,true,true)
for _,b in ipairs(r.bars)do check(b.Size.Y.Offset==6,'Reduced effects animates history')end
for i=1,28 do r:Step(0,.04,false,false)end
for _,b in ipairs(r.bars)do check(b.Size.Y.Offset==2 and b.BackgroundColor3==Reactor.Theme.Quiet,'Silence fabricated activity')end
r:Step(0/0,0/0,false,true);check(r.fill.Size.X.Scale==0,'Invalid input leaked into geometry')
for _,v in ipairs({{320,true},{390,true},{844,true},{819,false},{820,false},{1280,false}})do
 local w,h=Reactor.Layout(v[1],v[2]);check(w<=v[1]-28 and h<=96,'Unsafe viewport size')
 local bottom=12;local top=bottom+h
 if v[2] or v[1]<820 then check(top<=99,'Meter overlaps reserved actions')end
 if not v[2] and v[1]>=820 then check((v[1]-w)/2>=256 and (v[1]+w)/2<=v[1]-274,'Desktop side HUD overlap')end
end
-- Native baseline footprints from stock Studio emulation. These coordinates
-- are specific to the profiles; physical touch and other stick modes are separate.
for _,v in ipairs({{388,762,103,293},{359,690,103,264}})do
 local w,h=Reactor.Layout(v[1],true,v[2])
 local left=(v[1]-w)/2
 local right=left+w
 check(left-v[3]>=8 and v[4]-right>=8,'Known stock-control clearance not preserved')
 check(h==84,'This fix should not push the meter upward toward actions')
 check(Reactor.Status('live',false,true,v[1],v[2],true)=='BEAMS OFF\nVoice chat unchanged','Compact state suggests mic mute')
 check(Reactor.Status('live',true,true,v[1],v[2],true)=='MIC UNAVAILABLE\nOpen voice settings','Unavailable status precedence changed')
 check(Reactor.Status('live status unchanged',false,false,v[1],v[2],true)=='live status unchanged','Live status must stay truthful')
end
for _,v in ipairs({{749,388,true},{844,390,true},{388,762,false},{1280,900,false},{320,568,true},{343,942,true},{452,800,true}})do
 local oldW,oldH=Reactor.Layout(v[1],v[3])
 local w,h=Reactor.Layout(v[1],v[3],v[2])
 check(oldW==w and oldH==h,'Out-of-scope screen allocation changed')
 check(Reactor.Status('live',false,true,v[1],v[2],v[3])=='BEAMS OFF · TALK FREELY\nVoice chat is unchanged','Out-of-scope copy changed')
end
for width=344,451 do
 local w=Reactor.Layout(width,true,700)
 check((w-20)/28-3>0,'Portrait waveform has negative-width bars')
end
check(r.text.TextSize>=12,'Unreadable status')
print('PASS '..n..' VoiceReactor contracts with UI doubles; no Studio or live mic')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.reactor-',dir=R/'tests',delete=False) as f:
 f.write(setup+module+checks);p=Path(f.name)
try:subprocess.run(['luau',str(p)],check=True,cwd=R)
finally:p.unlink()
s=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
targets=s[s.index('local function playerTargetInfo'):s.index('local sprintButton=')]
assert ' HP' not in targets and 'humanoid.MaxHealth' not in targets
assert 'hf.Size=UDim2.fromScale(current/maximum,1)' in s, 'Player health was removed'
assert 'academy.reactor:Step(power,dt,data.settings.reducedShake' in s
