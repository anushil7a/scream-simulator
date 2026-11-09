"""Actual server spawn/removal handlers with fake characters, sessions and events.
No real character-loading, networking or save evidence.
"""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start=source.index(' local function spawn(c)')
end=source.index(' p.CharacterAdded:Connect(spawn)',start)
setup='''
local now=20;local os={clock=function()return now end}
local Config={HealQuietSeconds=10,HealthForLevel=function()return 135 end}
local closes,protects,states,cancels=0,0,0,0
local closeConversation=function()closes+=1 end
local protect=function()protects+=1 end
local state=function()states+=1 end
local cancelSustained=function()cancels+=1 end
local VoiceCombat={Cancel=function(v)v.capture=nil end}
local removed
local p={Parent=true,attributes={},CharacterRemoving={Connect=function(_,fn)removed=fn end}}
function p:SetAttribute(k,v)self.attributes[k]=v end
local s={data={level=100},micReady=true,nextDodge=24,voice={capture=true}}
local sessions={[p]=s}
local function character()
 local h={JumpPower=50,JumpHeight=7.2,Health=30}
 return {h=h,WaitForChild=function()return h end}
end
'''
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local c=character();p.Character=c;s.knockedUntil=25;s.premiumRoll=true;s.sprintRequested=true
spawn(c)
check(s.character==c and c.h.Health==135 and c.h.MaxHealth==135,'Spawn did not initialize health')
check(s.knockedUntil==0 and s.dodgingUntil==0 and not s.premiumRoll and not s.sprintRequested,'Spawn carried old motion state')
check(p.attributes.KnockdownEnds==0 and p.attributes.DodgeEnds==0 and p.attributes.DodgeStarted==0 and p.attributes.Sprinting==false,'Spawn retained animation attributes')
check(s.nextDodge==24 and s.sprintCharge==10 and s.nextHeal==30,'Spawn changed dodge deadline or missed heal/sprint setup')
check(protects==1 and states==1 and closes==1,'Spawn side effects missing')
c.h.Health=42;spawn(c)
check(c.h.Health==42 and protects==1,'Duplicate registration healed/reprotected same character')
removed(character());check(s.character==c and cancels==0,'Old character removal canceled current character')
removed(c);check(s.character==nil and s.voice.capture==nil and cancels==1 and p.attributes.CaptureStarted==0,'Character removal retained attack')
local replacement=character();p.Character=replacement;s.micReady=false;spawn(replacement)
check(replacement.h.WalkSpeed==0 and s.character==replacement,'New character did not respect microphone gate')
local late=character();p.Character=late;p.Parent=nil;spawn(late)
check(s.character==replacement and protects==2,'Late spawn initialized departed player')
p.Parent=true;sessions[p]={};spawn(late)
check(s.character==replacement and protects==2,'Late spawn initialized replaced session')
sessions[p]=s;p.Character=replacement;spawn(late)
check(s.character==replacement and protects==2,'Old character initialized after replacement')
print('PASS '..checks..' actual server respawn/removal checks with mocked characters/events')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.respawn_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
