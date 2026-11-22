"""Run the server's training strike against a fake clock and geometry."""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = 'src/ServerScriptService/Bootstrap.server.luau'
setup = r'''
local player={}
local session={micReady=true,protectedUntil=0,dodgingUntil=0}
local other={}
local otherSession={micReady=true,protectedUntil=0,dodgingUntil=0}
local sessions={[player]=session,[other]=otherSession}
local vector={}
vector.__index=function(v,k)
 if k=="Magnitude" then return math.sqrt(v.X*v.X+v.Y*v.Y+v.Z*v.Z) end
end
vector.__sub=function(a,b) return setmetatable({X=a.X-b.X,Y=a.Y-b.Y,Z=a.Z-b.Z},vector) end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},vector)end}
local pos=Vector3.new(8,35,12)
local root={Position=pos}
local health={Health=100}
local otherRoot={Position=pos}
local otherHealth={Health=100}
local function character()
 local attributes={}
 return {SetAttribute=function(_,key,value)attributes[key]=value end,GetAttribute=function(_,key)return attributes[key]end}
end
local playerCharacter,otherCharacter=character(),character()
local function parts(who)
 if who==other then return otherCharacter,otherRoot,otherHealth end
 return playerCharacter,root,health
end
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
local serverClock=50
local workspace={GetServerTimeNow=function()return serverClock end}
local TrainingRules=require("../src/ReplicatedStorage/Shared/TrainingRules")
local bot={training={y=32,damage=8},trainingSurfaceY=32.26,alive=true,start=pos,root={Position=pos},health=80,maxHealth=80,trainingTarget=player}
local World={Bots={bot}}
local function state()end
'''
checks = r'''
stepTraining(10)
local mark=assert(partsCreated[1],"Windup did not show")
assert(mark.Size.Y==8 and not mark.CanQuery,"Warning footprint changed")
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

-- Both players initially overlap. A later hit changes the next target,
-- but must not transfer damage for a strike already telegraphed at player.
stepTraining(18)
mark=assert(partsCreated[3])
bot.trainingTarget=other
stepTraining(18+TrainingRules.Windup)
assert(health.Health==84 and otherHealth.Health==100,"Strike retargeted during windup")
assert(mark.destroyed and bot.trainingTarget==other,"Resolution lost the next target")
stepTraining(21.9)
assert(#partsCreated==3,"Retarget shortened the attack interval")
otherRoot.Position=Vector3.new(15,35,12)
stepTraining(22)
mark=assert(partsCreated[4])
assert(mark.CFrame.X==15,"Next strike did not aim at the latest target")
stepTraining(22+TrainingRules.Windup)
assert(health.Health==84 and otherHealth.Health==92,"Next strike ignored the latest target")

-- If the original target loses eligibility, clear their strike and keep
-- the newer target for the next interval instead of silently substituting.
bot.trainingTarget=player
stepTraining(26)
mark=assert(partsCreated[5])
bot.trainingTarget=other
session.flight=true
stepTraining(26.1)
assert(mark.destroyed and not bot.strike,"Original target cancellation was ignored")
assert(bot.trainingTarget==other,"Cancellation lost the next target")
stepTraining(26+TrainingRules.Windup)
assert(health.Health==84 and otherHealth.Health==92,"Cancelled strike still dealt damage")
stepTraining(30)
assert(#partsCreated==6 and bot.strike,"New target could not begin the next strike")
assert(otherCharacter:GetAttribute("TrainingStrikeAt")==50+TrainingRules.Windup,"Selected character missed the deadline")
local center=otherCharacter:GetAttribute("TrainingStrikeCenter")
assert(center.X==otherRoot.Position.X and center.Z==otherRoot.Position.Z and center.Y==bot.trainingSurfaceY,"Selected character missed the ground center")
assert(playerCharacter:GetAttribute("TrainingStrikeAt")==nil,"Cue leaked to a bystander")
session.flight=false
otherSession.flight=true
stepTraining(30.1)
assert(otherCharacter:GetAttribute("TrainingStrikeAt")==nil and otherCharacter:GetAttribute("TrainingStrikeCenter")==nil,"Cancelled strike retained HUD")
otherSession.flight=false
bot.trainingTarget=player
stepTraining(34)
serverClock=100
playerCharacter:SetAttribute("TrainingStrikeAt",serverClock)
playerCharacter:SetAttribute("TrainingStrikeCenter",otherRoot.Position)
stepTraining(34+TrainingRules.Windup)
assert(playerCharacter:GetAttribute("TrainingStrikeAt")==serverClock and playerCharacter:GetAttribute("TrainingStrikeCenter")==otherRoot.Position,"Older strike cleared a newer cue")
bot.trainingTarget=player
stepTraining(38)
mark=assert(bot.strike.warning)
assert(math.abs(mark.CFrame.Y-mark.Size.X/2-bot.trainingSurfaceY-.02)<.0001,"Strike warning floats above painted pad")
local before=health.Health
root.Position=Vector3.new(pos.X,bot.trainingSurfaceY+6.1,pos.Z)
stepTraining(38+TrainingRules.Windup)
assert(health.Health==before and mark.destroyed,"Ground strike hit above its vertical band")
root.Position=pos
print("PASS training strike visibility, cancellation, targeting, deadlines and cue fencing")
'''


def run(source, expected=None, historical_rules=None):
    start = source.index('local function stepTraining(')
    end = source.index('local function stepSprint(', start)
    start_helper = source.index('local function clearTrainingStrike(')
    helper = source[start_helper:source.index('local function restoreBot(', start_helper)]
    fixture = setup
    if historical_rules is not None:
        fixture = fixture.replace(
            'local TrainingRules=require("../src/ReplicatedStorage/Shared/TrainingRules")',
            'local TrainingRules=(function()\n'+historical_rules+'\nend)()',
            1,
        )
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', dir=ROOT / 'tests', delete=False) as file:
        file.write(fixture + helper + source[start:end] + checks)
        path = Path(file.name)
    try:
        result = subprocess.run(['luau', str(path)], text=True, capture_output=True)
    finally:
        path.unlink()
    output = result.stdout + result.stderr
    if expected:
        assert result.returncode and expected in output, output
        print('PASS negative control:', expected)
    else:
        assert not result.returncode, output
        print(output.strip())


parser = argparse.ArgumentParser()
parser.add_argument('--negative-controls', action='store_true')
args = parser.parse_args()
source = (ROOT / SOURCE_PATH).read_text(encoding='utf-8')
run(source)
if args.negative_controls:
    baseline = subprocess.check_output(['git', 'show', f'b97f944:{SOURCE_PATH}'], cwd=ROOT, text=True, encoding='utf-8')
    baseline_rules = subprocess.check_output(['git', 'show', 'b97f944:src/ReplicatedStorage/Shared/TrainingRules.luau'], cwd=ROOT, text=True, encoding='utf-8')
    run(baseline, 'Strike retargeted during windup', baseline_rules)
    clear_if_current = 'if bot.trainingTarget==p then bot.trainingTarget=nil end'
    assert source.count(clear_if_current) == 1
    run(source.replace(clear_if_current, 'bot.trainingTarget=nil'), 'Cancellation lost the next target')
    cue_guard = 'strike.character:GetAttribute("TrainingStrikeAt")==strike.cueUntil'
    assert source.count(cue_guard)==1
    run(source.replace(cue_guard,'true'),'Older strike cleared a newer cue')
    run(source.replace('center.Y+.07','center.Y+1.4',1),'Strike warning floats above painted pad')
    run(source.replace('TrainingRules.Hits(strike.position,r.Position,','TrainingRules.Hits(strike.position,Vector3.new(r.Position.X,strike.position.Y+3,r.Position.Z),',1),'Ground strike hit above its vertical band')
