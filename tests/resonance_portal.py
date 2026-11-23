"""Exercise the local portal transaction and its actual Bootstrap preparation with doubles."""
from pathlib import Path
import subprocess
import sys
import tempfile

root=Path(__file__).resolve().parents[1]
travel=(root/'prototypes/resonance-arena/PortalTravel.luau').read_text()
builder=(root/'tests/build_sustained_review.py').read_text()
prepare=builder.split("portal_prep = '''",1)[1].split("'''",1)[0]
setup=r'''
local checks=0
local function check(value,message)assert(value,message);checks+=1 end
local function vector(x)
 return setmetatable({X=x,Magnitude=math.abs(x)},{__sub=function(a,b)return vector(a.X-b.X)end})
end
local Vector3={zero=vector(0)}
local combat=false
local game={GetService=function()return {Shared={FindFirstChild=function(_,name)return name=="Config" and combat or nil end}} end}
local function loadTravel()
'''
checks=r'''
end
local function fixture(position)
 local root={Position=vector(position),AssemblyLinearVelocity=vector(3),AssemblyAngularVelocity=vector(2)}
 local humanoid={Health=100}
 local character={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return humanoid end}
 local player={Character=character}
 function character:PivotTo(destination)root.Position=destination end
 function player:SetAttribute(key,value)self[key]=value end
 root.Parent=character;humanoid.Parent=character
 return player,character,root,humanoid
end
local anchor={Position=vector(0)}
local destination=vector(200)
local player,character,root,humanoid=fixture(10)
local standalone=loadTravel()
check(standalone.Move(player,anchor,10,destination) and root.Position==destination,"Standalone portal lost exact boundary or travel")
check(root.AssemblyLinearVelocity==Vector3.zero and root.AssemblyAngularVelocity==Vector3.zero,"Portal retained movement")
combat=true
local portal=loadTravel()
player,character,root,humanoid=fixture(9)
check(not portal.Move(player,anchor,10,destination),"Combat portal moved before its handler was installed")
local installed
portal.SetPreparation(function(p,c)return installed(p,c)end)
installed=function(p)p.Character={};return true end
check(not portal.Move(player,anchor,10,destination) and root.Position.X==9,"Portal moved a replaced character")
player,character,root,humanoid=fixture(9)
installed=function()root.Position=vector(11);return true end
check(not portal.Move(player,anchor,10,destination) and root.Position.X==11,"Portal skipped the second range check")
player,character,root,humanoid=fixture(9)
installed=function()return false end
check(not portal.Move(player,anchor,10,destination) and root.Position.X==9,"Denied preparation moved the player")

portal=loadTravel()
local script={Parent={PortalTravel=true}}
local function require()return portal end
local session={character=character,active=true,voice={capture=true},test=true,readyAt=0}
local sessions={[player]=session}
local closing=false
local now=7
local os={clock=function()return now end}
local function cancelSustained(p,s,time)
 check(p==player and root.Position.X==9 and time==7,"Cast cancelled after relocation or with wrong clock")
 s.active=false;s.readyAt=time+5
end
local VoiceCombat={Cancel=function(voice)voice.capture=nil end}
local function testBeamEnd(p,s,time)
 check(p==player and time==7,"Test cast used a different transition clock")
 s.test=false;return true
end
local function state()end
local synced=false
local task={defer=function(fn,p)check(fn==state and p==player,"Test state refresh dispatched incorrectly");synced=true end}
PREPARE
root.Position=vector(11)
check(not portal.Move(player,anchor,10,destination) and session.active,"Out-of-range prompt cancelled a cast")
root.Position=vector(9);session.flight=true
check(not portal.Move(player,anchor,10,destination) and session.active,"Flying avatar moved or lost its cast")
session.flight=false;closing=true
check(not portal.Move(player,anchor,10,destination) and session.active,"Closing server allowed portal travel")
closing=false
check(portal.Move(player,anchor,10,destination) and root.Position==destination,"Prepared combat portal did not move")
check(not session.active and session.readyAt==12,"Portal lost the sustained cooldown")
check(not session.voice.capture and player.CaptureStarted==0 and not session.test and synced,"Portal carried a legacy/test cast")
check(not portal.Move(player,anchor,10,destination),"Duplicate source prompt moved the player again")
print("PASS "..checks.." actual portal movement and preparation assertions")
'''
def run(module, initializer, expected=None):
    with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',prefix='tmp_portal_',delete=False) as file:
        file.write(setup+module+checks.replace('PREPARE',initializer))
        path=Path(file.name)
    try:
        result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr, result.stderr
        print('PASS control:',expected)
    else:
        assert result.returncode==0,result.stderr
        print(result.stdout.strip())

run(travel,prepare)
if '--negative-controls' in sys.argv:
    run(travel.replace(' or not ready()', ''),prepare,'Portal moved a replaced character')
    run(travel,prepare.replace('cancelSustained(p,s,now)',''),'Portal lost the sustained cooldown')
    run(travel,prepare.replace('VoiceCombat.Cancel(s.voice);',''),'Portal carried a legacy/test cast')
