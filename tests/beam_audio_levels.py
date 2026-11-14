"""Actual beam mix/settings and client control in mocks; no audio playback/listening claim."""
from pathlib import Path
import argparse,subprocess,tempfile,hashlib
root=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser();p.add_argument('--baseline',action='store_true');p.add_argument('--negative-controls',action='store_true');args=p.parse_args()
def read(path):return subprocess.check_output(['git','show','47f3d46:'+path],cwd=root,text=True,encoding='utf-8') if args.baseline else (root/path).read_text(encoding='utf-8')
settings=read('src/ReplicatedStorage/Shared/AttackAudioConfig.luau');mix=read('src/StarterPlayer/StarterPlayerScripts/BeamAudioMix.luau');client=read('src/StarterPlayer/StarterPlayerScripts/Client.client.luau')
setup=r'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function near(a,b)return math.abs(a-b)<.000001 end
local settings=(function()
'''
between='\nend)()\nlocal Mix=(function()\n'
tests=r'''
end)()
local handles,creates,destroys={},0,0
local function fresh()
 handles={};creates=0;destroys=0
 return Mix.new(settings,function(pos,tier)creates+=1;local h={pos=pos,tier=tier,volume=0};table.insert(handles,h);return h end,
 function(h,pos,gain,pitch)check(not h.dead,'Updated destroyed handle');h.pos=pos;h.volume=gain;h.pitch=pitch end,
 function(h)check(not h.dead,'Double destroy');h.dead=true;destroys+=1 end)
end
local function total()local t=0;for _,h in ipairs(handles)do if not h.dead then t+=h.volume end end;return t end
local m=fresh();check(m.level=='NORMAL' and m.enabled,'Default NORMAL missing')
check(settings.TotalVolume==.4 and settings.LowVolume==.24,'Beam budgets differ from approved levels')
local expected={'112589551277234','71125574109613','72820033812084','116444869617367','110531388862916','72657289722275','8899285496','102380291908556','80523108386394','79853512837585'}
for i,id in ipairs(expected)do check(settings.AssetForLevel(i*10)=='rbxassetid://'..id,'Selected asset changed')end
check(settings.AssetForLevel(1)==nil and settings.AssetForLevel(99)==nil,'Unconfigured asset became playable')
for _,bad in ipairs({'normal','LOUD','',true,42,{}})do
 check(m:SetLevel(bad)==false,'Invalid level did not reject');check(m.level=='NORMAL' and m.enabled,'Invalid level accepted')
end
check(m:SetLevel(nil)==false,'Nil level did not reject');check(m.level=='NORMAL','Nil level accepted')
for _,level in ipairs({'NORMAL','LOW'})do
 for count=1,settings.Limit do
  m=fresh();m:SetLevel(level)
  for i=1,count do check(m:Pulse(i,0,{i},i%2==0,i*10),'Valid pulse rejected')end
  m:Step(.2,.2,false,false)
  local budget=level=='LOW' and .24 or .4
  check(total()<=budget+.000001,'Concurrent mix exceeds total budget')
  for i,h in ipairs(handles)do check(h.pitch==1 and h.tier==i*10,'Pitch or tier altered');check(near(h.volume,budget/count*(i%2==0 and settings.LocalMultiplier or 1)),'Per-handle volume incorrect')end
  m:Stop(1,.2);m:Step(.25,.05,false,false);check(total()<=budget+.000001,'Fading mix exceeds budget')
  check(not m:Pulse(1,.26,{},false,10),'Stopped sound revived')
  m:Step(.26,.01,true,false);check(total()<=.24*m.duck+.000001,'Voice-active ceiling exceeds previous budget')
  m:Step(.27,.01,true,true);check(total()==0,'Calibration not silent')
 end
end
m=fresh();m:Pulse(1,0,{},false,10);m:Step(.2,.2,false,false);check(near(total(),.4),'NORMAL not louder')
m:SetLevel('LOW');m:Step(.21,.01,false,false);check(near(total(),.24),'LOW not applied')
m:SetLevel('NORMAL');m:Step(.22,.01,false,false);check(near(total(),.4),'NORMAL not restored')
m:Step(.23,.01,true,false);check(total()<=.24*m.duck+.000001,'Immediate voice ceiling missing')
for i=1,80 do local now=.23+i*.025;m:Pulse(1,now,{},false,10);m:Step(now,.025,false,false)end
check(total()>.399 and total()<=.4,'Voice duck recovery incorrect')
local before=creates;m:SetLevel('OFF');check(m.level=='OFF' and not m.enabled and m.count==0 and destroys==before,'OFF did not clear immediately')
for i=1,10 do check(not m:Pulse(i,3,{},false,10),'OFF accepted pulse');m:Step(3,.1,false,false)end
check(creates==before,'OFF recreated sound')
m:SetLevel('LOW');m:Step(3,.1,false,false);check(creates==before and m.count==0,'Reenable recreated old attack')
check(m:Pulse(100,3,{},false,20) and creates==before+1,'Next pulse did not resume')
m:SetEnabled(false);check(m.level=='OFF' and not m.enabled and m.count==0,'Legacy disable inconsistent')
m:SetEnabled(true);check(m.level=='NORMAL' and m.enabled,'Legacy enable did not restore NORMAL')
m=fresh();for i=1,settings.Limit do m:Pulse(i,0,{},i%2==0,10)end
m:Stop(1,.1);m:SetLevel('OFF');check(m.count==0 and destroys==settings.Limit,'OFF left active or fading handles')
for _,mode in ipairs({'LOW','OFF'})do m:SetLevel(mode);check(m:SetLevel('INVALID')==false and m.level==mode and m.enabled==(mode~='OFF'),'Invalid mode changed existing setting')end
m=fresh();for i=1,settings.Limit do m:Pulse(i,0,{},false,10)end
check(not m:Pulse(99,0,{},false,10),'Concurrency limit bypassed')
m:Step(settings.Timeout+settings.FadeOut+.01,.1,false,false);check(m.count==0,'Timeout cleanup changed')
m=fresh();for i=0,100 do local now=i*.05;m:Pulse(1,now,{},false,10);m:Step(now,.05,false,false)end
check(destroys>=1,'Maximum lifetime cleanup changed')
m:Destroy();check(m:SetLevel('NORMAL')==false,'Destroyed mixer changed level');local before=creates;check(not m:Pulse(100,6,{},false,10),'Destroyed mixer accepted pulse');m:Destroy();check(creates==before,'Destroyed mixer recreated handle')
'''
ui_setup=r'''
local UDim2={new=function(...)return {...}end,fromOffset=function(...)return {...}end}
local buttons,notes={},{};local function card()return {}end
local function button(_,id,text,_,_,fn)local b={Text=text,call=fn};buttons[id]=b;return b end
local function info(text)table.insert(notes,text)end
local attackAudio=fresh();local narrow=false
local function draw()
 buttons={};notes={}
'''
a=client.index('  local audioCard=');ui=client[a:client.index('  local cueCard=',a)]
ui_tests=r'''
end
for _,small in ipairs({false,true})do
 narrow=small;attackAudio:SetLevel('NORMAL')
 for _,expected in ipairs({'NORMAL','LOW','OFF','NORMAL','LOW','OFF'})do
 draw();local b=buttons.AttackAudio;check(b and b.Text=='BEAM SFX: '..expected,'Beam level label or reopen incorrect')
 check(attackAudio.level==expected,'Drawing settings changed level')
 local help=table.concat(notes,' ');check(string.find(help,'Session only',1,true) and string.find(help,'Starter beam has no SFX',1,true) and string.find(help,'voice chat unchanged',1,true),'Beam setting limitations missing')
 b.call();local nextLevel=expected=='NORMAL' and 'LOW' or expected=='LOW' and 'OFF' or 'NORMAL'
 check(attackAudio.level==nextLevel and b.Text=='BEAM SFX: '..nextLevel,'Beam level cycle incorrect')
end
end
print('PASS '..checks..' actual beam audio mix/settings/control assertions; synthetic handles only')
'''
def run(code,expected=None):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',encoding='utf-8',delete=False)as f:f.write(code);path=Path(f.name)
 try:r=subprocess.run(['luau',str(path)],text=True,capture_output=True)
 finally:path.unlink()
 out=r.stdout+r.stderr
 if expected:assert r.returncode and expected in out,out;print('PASS negative control:',expected)
 else:assert r.returncode==0,out;print(out.strip())
code=setup+settings+between+mix+tests+ui_setup+ui+ui_tests
if args.baseline:run(code,'Default NORMAL missing')
else:
 run(code)
 if args.negative_controls:
  cases=[(code.replace('level="NORMAL",duck=1','level="LOW",duck=1'),'Default NORMAL missing'),(code.replace('if voiceActive then budget=math.min(budget,self.settings.LowVolume) end',''),'Voice-active ceiling exceeds previous budget'),(code.replace('budget/math.max(1,self.count)','budget'),'Concurrent mix exceeds total budget'),(code.replace('if not self.enabled then self:Clear() end',''),'OFF did not clear immediately'),(code.replace('local pitch=1','local pitch=1.2'),'Pitch or tier altered'),(code.replace('local gain=calibrating and 0 or','local gain='),'Calibration not silent'),(code.replace('attackAudio.level=="NORMAL" and "LOW"','attackAudio.level=="NORMAL" and "OFF"'),'Beam level cycle incorrect'),(code.replace('local budget=self.level=="LOW" and self.settings.LowVolume or self.settings.TotalVolume','local budget=self.settings.TotalVolume'),'Concurrent mix exceeds total budget')]
  for changed,error in cases:
   assert changed!=code,'Mutation did not match: '+error
   run(changed,error)


if not args.baseline:
 # Exact historical fixtures from commit47f3d46; pinned byte hashes, no Git needed.
 fixture_dir=root/'tests/support/beam-audio-low-baseline'
 fixture_hashes={'AttackAudioConfig.luau': '5dbba1850546d8732c3d998be33f2013718c53c3c8a023a5aeb017ba711bf2fc', 'BeamAudioMix.luau': 'f6a05600323921af36578107915ec4dd08b6178a99e664533bf3e306b2a1153d'}
 def fixture(name):
  data=(fixture_dir/name).read_bytes()
  assert hashlib.sha256(data).hexdigest()==fixture_hashes[name], 'Baseline fixture hash mismatch: '+name
  return data.decode('utf-8')
 old_settings=fixture('AttackAudioConfig.luau')
 old_mix=fixture('BeamAudioMix.luau')
 comparison=r"""
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function wrap(Module,settings)
 local handles={};local m=Module.new(settings,function(pos,tier)local h={pos=pos,tier=tier};table.insert(handles,h);return h end,
 function(h,pos,volume,pitch)h.pos=pos;h.volume=volume;h.pitch=pitch end,function(h)h.dead=true end)
 return m,handles
end
local a,ah=wrap(OldMix,oldSettings);local b,bh=wrap(NewMix,newSettings);b:SetLevel('LOW')
for frame=0,200 do
 local now=frame*.025
 if frame%4==0 and frame<150 then
  for id=1,4 do check(a:Pulse(id,now,id,id%2==0,id*10)==b:Pulse(id,now,id,id%2==0,id*10),'LOW pulse acceptance differs from baseline')end
 end
 if frame==30 then a:Stop(1,now);b:Stop(1,now)end
 if frame==60 then a:Remove(2);b:Remove(2)end
 local voice=frame>=15 and frame<55;local calibrating=frame>=70 and frame<80
 a:Step(now,.025,voice,calibrating);b:Step(now,.025,voice,calibrating)
 check(a.count==b.count and #ah==#bh,'LOW handle lifecycle differs from baseline')
 for i,h in ipairs(ah)do
  local other=bh[i];check(h.dead==other.dead,'LOW destruction differs from baseline')
  if not h.dead then check(math.abs(h.volume-other.volume)<.0000001 and h.pitch==other.pitch and h.pos==other.pos and h.tier==other.tier,'LOW mix differs from baseline')end
 end
end
print('PASS '..checks..' current LOW versus baseline mix sequence assertions; synthetic handles only')
"""
 compare='local oldSettings=(function()\n'+old_settings+'\nend)()\nlocal newSettings=(function()\n'+settings+'\nend)()\nlocal OldMix=(function()\n'+old_mix+'\nend)()\nlocal NewMix=(function()\n'+mix+'\nend)()\n'+comparison
 run(compare)
 if args.negative_controls:
  run(compare.replace("b:SetLevel('LOW')","b:SetLevel('NORMAL')"),'LOW mix differs from baseline')
