"""Actual guarded Client UI and silent effect branch, mocked services/layout only."""
from pathlib import Path
import subprocess, tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index(' if localFlightTools then\n  local TestBeamTools=')
ui=s[a:s.index('\nend\nlocal testButton=',a)]
a=s.index(' if kind=="TestBeamEnd" then')
fx=s[a:s.index(' if kind=="SustainedHit" then',a)]
setup=r'''
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local Module=require('../src/StarterPlayer/StarterPlayerScripts/TestBeamTools')
local now=1;local os={clock=function()return now end}
local localFlightTools=true;local script={Parent={}};local clientDestroyed=false
local function loadClientDependency()return Module end;local function clientCheckpoint()return true end
local data={settings={},devAccess=true,testBeamAvailable=true,testBeamActive=false,testBeamPower=0,testBeamCooldown=0}
local windowFocused=true;local modal={Visible=false};local conversationPanel={Visible=false}
local GuiService={MenuIsOpen=false,MenuOpened='menu'}
local UIS={WindowFocusReleased='blur',GetFocusedTextBox=function()return nil end}
local flight=false;local p={CharacterRemoving='respawn',GetAttribute=function()return flight end}
local devPanel={Visible=true,GetPropertyChangedSignal=function()return 'visible'end}
local aimGui={};local Enum={TextXAlignment={Center=1}}
local workspace={CurrentCamera={ViewportSize={X=800,Y=600},ViewportPointToRay=function(_,x,y)check(x==400 and y==300,'Test beam did not use viewport center');return {Origin=23,Direction=1}end}}
local testContent={};local gold={};local muted={};local connections={};local cleanups={};local controls={};local sent={}
local action={FireServer=function(_,verb,arg)table.insert(sent,{verb,arg})end}
local Run={Heartbeat='tick'}
local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end,new=function(xs,x,ys,y)return {X=196*xs+x,Y=y}end}
local function button(_,name,text,size,pos,callback)local b={Text=text,Size=size,Position=pos,call=callback};controls[name]=b;return b end
local function label(_,text,size,pos)local b={Text=text,Size=size,Position=pos};table.insert(controls,b);return b end
local function connectClient(signal,fn)connections[signal]=fn end
local function ownClient(fn)table.insert(cleanups,fn)end
local function cancelCapture()end
local function aimRay()error("Normal mic/cursor aim must not be used for Test Beam")end
'''
checks=r'''
local function last()return sent[#sent]end
connections.tick()
check(controls.TestBeam.Text=='TEST BEAM','Action label')
local crosshair;for _,v in ipairs(controls)do if v.Name=='TestBeamCrosshair' then crosshair=v end end
check(crosshair and crosshair.Visible,'Test center crosshair missing')
for _,name in ipairs({'BeamZero','BeamLess','BeamMore','BeamFull','TestBeam'})do
 local b=controls[name];check(b.Selectable and b.Size.X>=44 and b.Size.Y>=44,'Not touch/keyboard accessible: '..name)
 check(b.Position.X+b.Size.X<=196 and b.Position.Y+b.Size.Y<=164,'Clipped narrow UI: '..name)
end
controls.BeamZero.call();controls.TestBeam.call();check(#sent==0,'Zero fired from UI')
controls.BeamFull.call();controls.BeamLess.call();controls.TestBeam.call();check(last()[1]=='TestBeamBegin' and last()[2].power==90 and last()[2].aim==1023,'UI power/aim mapping')
connections.tick();check(controls.TestBeam.Text=='STOP TEST BEAM','Stop affordance missing')
data.testBeamActive=true;data.testBeamPower=90;connections.tick()
local actual=false;for _,v in ipairs(controls)do if v.Text=='Active: 90% · silent / visual only' then actual=true end end
check(actual,'Acknowledged power missing')
controls.TestBeam.call();check(last()[1]=='TestBeamStop','Click did not stop')
for _,signal in ipairs({'visible','blur','menu','respawn'})do
 data.testBeamActive=false;devPanel.Visible=true;controls.TestBeam.call()
 if signal=='visible' then devPanel.Visible=false end
 connections[signal]();check(last()[1]=='TestBeamStop','Lifecycle stop failed: '..signal)
end
devPanel.Visible=true;controls.TestBeam.call();flight=true;connections.tick();check(last()[1]=='TestBeamStop','Flight and beam overlap');check(not crosshair.Visible,'Crosshair shown during flight');flight=false
controls.TestBeam.call();cleanups[1]();check(last()[1]=='TestBeamStop','Retirement did not stop')
workspace.CurrentCamera=nil;data.testBeamActive=false;local before=#sent;controls.TestBeam.call();check(#sent==before,'Absent camera fired')
workspace.CurrentCamera={ViewportSize={X=320,Y=240},ViewportPointToRay=function(_,x,y)check(x==160 and y==120,'Resized viewport center mismatch');return {Origin=10,Direction=2}end}
UIS.TouchEnabled=true;controls.TestBeam.call();check(last()[1]=='TestBeamBegin' and last()[2].aim==2010,'Touch aim differs from desktop center');controls.TestBeam.call()
-- Separate effect path has no attackAudio/playGameplayCue globals at all.
local removed,updated;local sustainedBeams={Remove=function(_,key)removed=key end,Update=function(_,key)updated=key end}
local pos={};local position={};setmetatable(position,{__sub=function()return {Magnitude=1}end})
p.Character={FindFirstChild=function()return {Position=position}end}
local Players={GetPlayerByUserId=function(_,id)return id==7 end}
local function typeof()return 'Color3'end
local function effect(kind,id,length)
 local aura={};local direction={};local beamWidth=4;local attackLevel=10
__EFFECT_FRAGMENT__
end
localFlightTools=false;effect('TestBeam',7,20);check(updated==nil,'Test FX outside local fixture')
localFlightTools=true;effect('TestBeam',7,20);check(updated=='test:7','Test visuals missing/disturb normal beam key')
effect('TestBeamEnd',7);check(removed=='test:7','End did not clear test beam')
updated=nil;effect('TestBeam',8,20);check(updated==nil and removed=='test:8','Unknown attacker admitted')
effect('TestBeam',7,0);check(removed=='test:7','Zero length not cleared')
print('PASS '..checks..' actual Test Beam UI/silent-effect checks; mocked services and layout')
'''.replace('__EFFECT_FRAGMENT__',fx)
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+ui+checks)
try:subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:path.unlink()
