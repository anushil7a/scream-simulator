"""Run the server's training strike against a fake clock and geometry."""
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src/ServerScriptService/Bootstrap.server.luau').read_text(encoding='utf-8')
start = source.index('local function stepTraining(')
end = source.index('local function stepSprint(', start)
helper = ''
if 'local function clearTrainingStrike(' in source:
    start_helper = source.index('local function clearTrainingStrike(')
    helper = source[start_helper:source.index('local function restoreBot(', start_helper)]
setup = r'''
local player={}
local session={micReady=true,protectedUntil=0,dodgingUntil=0}
local sessions={[player]=session}
local vector={}
vector.__index=function(v,k)
 if k=="Magnitude" then return math.sqrt(v.X*v.X+v.Y*v.Y+v.Z*v.Z) end
end
vector.__sub=function(a,b) return setmetatable({X=a.X-b.X,Y=a.Y-b.Y,Z=a.Z-b.Z},vector) end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},vector)end}
local pos=Vector3.new(8,35,12)
local root={Position=pos}
local health={Health=100}
local function parts()return {},root,health end
local function audible()return true end
local Config={HealQuietSeconds=4,InArena=function()return false end}
local partsCreated={}
local Instance={new=function()
 local p={Destroy=function(self)self.destroyed=true end}
 table.insert(partsCreated,p)
 return p
end}
local game={GetService=function()return {AddItem=function()end}end}
local transform={__mul=function(a)return a end}
local CFrame={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},transform)end,Angles=function()return {}end}
local Enum={PartType={Cylinder=1},Material={Neon=1}}
local Color3={fromRGB=function(...)return {...}end}
local workspace={}
local TrainingRules=require("../src/ReplicatedStorage/Shared/TrainingRules")
local bot={training={y=32,damage=8},alive=true,start=pos,root={Position=pos},health=80,maxHealth=80,trainingTarget=player}
local World={Bots={bot}}
local function state()end
'''
checks = r'''
stepTraining(10)
local mark=assert(partsCreated[1],"Windup did not show")
assert(mark.Size.Y==8 and mark.CFrame.Y==33.4 and not mark.CanQuery,"Warning footprint or placement changed")
local initial=mark.Transparency
local strikeTime=bot.strike.at
session.flight=true
stepTraining(10.2)
assert(mark.destroyed and not bot.strike,"Cancelled strike leaves a visible warning")
assert(health.Health==100,"Cancelled strike damaged player")
session.flight=false
bot.trainingTarget=player
stepTraining(14)
mark=assert(partsCreated[2])
stepTraining(14.5)
assert(mark.Transparency<initial and mark.Size.Y==8,"Windup progress missing or changed footprint")
assert(health.Health==100,"Strike hit before windup")
stepTraining(14+TrainingRules.Windup)
assert(mark.destroyed and health.Health==92 and not bot.strike,"Resolved strike did not clear exactly once")
assert(strikeTime==10+TrainingRules.Windup,"Windup changed")
print("PASS training strike warning, cancellation, progress and authoritative resolution")
'''
with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', dir=ROOT / 'tests', delete=False) as file:
    file.write(setup + helper + source[start:end] + checks)
    path = Path(file.name)
try:
    subprocess.run(['luau', str(path)], check=True)
finally:
    path.unlink()
