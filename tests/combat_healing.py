"""Actual sustained damage handler with mocked targets; no native/network claims."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
source = source[source.index('local function stepSustained('):source.index('local function cast(')]
setup = '''
local Healing=require('../src/ReplicatedStorage/Shared/Healing')
local Config={HealQuietSeconds=Healing.QuietSeconds}
local queuedHits,queuedDetails={},{}
local sustained={Step=function()return queuedHits,nil,queuedDetails,nil end}
local function sustainedContext()return {position=0}end
local function sustainedEnd()end
local function resolveSustained()end
local function xp()end
local function questProgress()end
local function state()end
local function destructionHint()end
local World={UpdateBot=function()end,ReactToScream=function()end}
local SustainedRewards={Hit=function()return 0,0 end}
local effect={FireClient=function()end,FireAllClients=function()end}
local p={GetAttribute=function()return 1 end}
local Destruction={Damage=function(object,_,damage)
 if object.locked then return {reason='level',required=100} end
 object.health=math.max(0,object.health-damage);return {health=object.health}
end}
local s={sustained={intent={level=1}},data={coins=0},botRewards={},nextHeal=0}
'''
checks = '''
local n=0;local function check(v,msg)assert(v,msg);n+=1 end
local victim={Health=100};local defender={nextHeal=0}
queuedDetails={target={player={},session=defender,humanoid=victim}}
queuedHits={{id='target',damage=3,firstHit=true}}
stepSustained(p,s,10)
check(victim.Health==97 and s.nextHeal==22 and defender.nextHeal==22,'Damage did not tag both combatants')
stepSustained(p,s,10.2)
check(s.nextHeal==22.2 and defender.nextHeal==22.2,'Continued damage did not extend both deadlines')
queuedHits={};stepSustained(p,s,20)
check(s.nextHeal==22.2,'Miss/blocked/dodged target extended healing')
local hp=Healing.Step(50,100,s.nextHeal,22.19)
check(hp==50,'Attacker healed while combat delay remained')
hp=Healing.Step(50,100,s.nextHeal,22.2)
check(hp==70,'Recovery did not resume after combat')
local object={health=50,GetAttribute=function(self)return self.health end}
queuedDetails={target={object=object}};queuedHits={{id='target',damage=3}}
stepSustained(p,s,30)
check(object.health==47 and s.nextHeal==42,'Object damage did not tag attacker')
object.locked=true;stepSustained(p,s,31)
check(s.nextHeal==42,'Rejected object damage tagged attacker')
local bot={health=60,id=1}
queuedDetails={target={bot=bot}};queuedHits={{id='target',damage=3,firstHit=true}}
stepSustained(p,s,40)
check(bot.health==57 and s.nextHeal==52,'NPC damage did not tag attacker')
print('PASS '..n..' actual combat-healing checks with mocked targets')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', prefix='.combat_heal_', dir=root/'tests', delete=False) as f:
    path = Path(f.name)
    f.write(setup+source+checks)
try:
    subprocess.run(['luau', str(path)], cwd=root, check=True)
finally:
    path.unlink()
