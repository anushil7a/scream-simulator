"""Actual knockout reset function with mocked character/session state; no physics evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
start=source.index('local function eject(p,h)')
end=source.index('local function audible(',start)
setup='''
local Vector3={zero='zero'};local os={clock=function()return 50 end}
local Config={HealthForLevel=function(level)return level==100 and 135 or 100 end,HealQuietSeconds=10}
local World={SafeSpawn='hub'};local messages,protected=0,0
local state=function()messages+=1 end
local protect=function(p,s)protected+=1;s.protectedUntil=55 end
local sessions={}
'''
callback_start=source.index('    local recoveryEnds=s.knockedUntil')
callback_end=source.index('    end)',callback_start)+len('    end)')
callback=source[callback_start:callback_end]
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local root={Anchored=false,AssemblyLinearVelocity='moving',AssemblyAngularVelocity='spinning'}
function root:SetNetworkOwnershipAuto()self.auto=true end
local character={FindFirstChild=function()return root end,PivotTo=function(self,cf)self.position=cf end}
local p={Character=character,attributes={}}
function p:SetAttribute(k,v)self.attributes[k]=v end
local s={data={level=100},dodgingUntil=60,knockedUntil=61,premiumRoll=true,sprintRequested=true,nextDodge=64,sprintCharge=3}
sessions[p]=s
local h={Health=1,PlatformStand=true,AutoRotate=false}
eject(p,h)
check(h.Health==135 and character.position=='hub','KO did not restore health/eject')
check(root.AssemblyLinearVelocity=='zero' and root.AssemblyAngularVelocity=='zero','KO carried attack/car momentum into hub')
check(not h.PlatformStand and h.AutoRotate and root.auto,'KO retained ragdoll/server ownership')
check(s.dodgingUntil==0 and s.knockedUntil==0 and not s.premiumRoll and not s.sprintRequested,'KO retained movement state')
check(p.attributes.DodgeEnds==0 and p.attributes.DodgeStarted==0 and p.attributes.KnockdownEnds==0 and p.attributes.Sprinting==false,'KO retained animation attributes')
check(s.nextDodge==64 and s.sprintCharge==3,'KO reset movement budgets')
check(protected==1 and s.protectedUntil==55 and s.nextHeal==60 and messages==1,'KO protection/heal/status changed')
root.Anchored=true;root.auto=false;eject(p,h)
check(not root.auto,'Anchored fixture attempted ownership mutation')
local player=p;local humanoid={Parent=true,Health=20,PlatformStand=true}
local pending
local task={delay=function(_,fn)pending=fn end}
s.knockedUntil=80
''' + callback + '''
s.knockedUntil=0;pending()
check(humanoid.PlatformStand,'Old car recovery ran after knockout cancellation')
s.knockedUntil=80;sessions[player]={};pending()
check(humanoid.PlatformStand,'Old car recovery ran after session replacement')
sessions[player]=s;player.Character={};pending()
check(humanoid.PlatformStand,'Old car recovery ran after character replacement')
print('PASS '..checks..' actual knockout recovery checks with mocked character/session')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.ko_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
