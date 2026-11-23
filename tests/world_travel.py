"""Actual Studio-only travel gate with engine and transport doubles."""
from pathlib import Path
import subprocess
import tempfile
import sys

ROOT = Path(__file__).resolve().parents[1]
GATE = (ROOT / 'prototypes/resonance-arena/travel/TravelGate.luau').read_text(encoding='utf-8-sig')
SETUP = r'''
local count=0
local function check(ok,reason) assert(ok,reason);count+=1 end
local function signal()
 local event,handlers={},{}
 function event:Connect(callback) table.insert(handlers,callback) end
 function event:Once(callback)
  local ran=false
  self:Connect(function(...) if not ran then ran=true;callback(...) end end)
 end
 function event.emit(...) for _,callback in ipairs(handlers) do callback(...) end end
 return event
end
local function vector(x)
 return setmetatable({}, {__sub=function(_,other)return {Magnitude=math.abs(x-other.x)} end,__index={x=x}})
end
local workspace={}
local Vector3={zero=vector(0)}
local task={defer=function(callback,...)callback(...)end}
local players={PlayerRemoving=signal(),PlayerAdded=signal(),current={}}
function players:GetPlayers() return self.current end
local events=signal()
local attempts={}
local mode
local transport={TeleportInitFailed=events}
function transport:TeleportAsync(id,users,options)
 if mode=="throw" then error("offline") end
 table.insert(attempts,{id=id,player=users[1],options=options})
end
local studio=true
local settings={rehearsal=true,universe=0,source=0,destination=0}
local contacted=0
local game={GameId=0,PlaceId=0}
function game:GetService(name)
 if name=="RunService" then return {IsStudio=function()return studio end} end
 if name=="Players" then return players end
 assert(name=="TeleportService");contacted+=1;return transport
end
local script={Parent={TravelSettings={}}}
local function require()return settings end
local Enum={KeyCode={F="F"}}
local Instance={new=function(class)
 assert(class=="TeleportOptions");local data
 return {SetTeleportData=function(_,value)data=value end,GetTeleportData=function()return data end}
end}
local function gate()
'''
CHECKS = r'''
end
local function actor(x)
 local root={Position=vector(x)};local human={Health=100}
 local character={FindFirstChild=function()return root end,FindFirstChildOfClass=function()return human end}
 local p={Parent=players,Character=character,CharacterAdded=signal(),CharacterRemoving=signal(),join={}}
 root.Parent=character
 function character:WaitForChild() if self.onWait then self.onWait() end;return root end
 function character:IsDescendantOf(world) return world==workspace end
 function character:PivotTo(destination)root.Position=destination end
 function p:SetAttribute(_,status)self.status=status end
 function p:GetAttribute()return self.status end
 function p:GetJoinData()return self.join end
 return p,root,human
end
local function bind(module)
 local prompt={Enabled=true,MaxActivationDistance=10,Parent={Position=vector(0)},Triggered=signal()}
 module.Bind(prompt);return prompt,prompt.Triggered.emit
end
local p,root,human=actor(8)
local prompt,activate=bind(gate());activate(p)
check(contacted==0 and #attempts==0 and p.status:find("rehearsal"),"Zero-ID rehearsal attempted service access")
check(prompt.KeyboardKeyCode=="F" and root.Position.x==8,"Rehearsal did not leave avatar at source")
settings={universe=10,source=20,destination=30}
game.GameId=10;game.PlaceId=20
studio=false;check(not pcall(gate) and contacted==0,"Travel gate accepted live context")
studio=true;game.PlaceId=99;check(not pcall(gate) and contacted==0,"Travel gate accepted wrong source place")
game.PlaceId=20;game.GameId=99;check(not pcall(gate) and contacted==0,"Travel gate accepted wrong experience")
game.GameId=10;prompt,activate=bind(gate())
root.Position=vector(11);activate(p);check(#attempts==0,"Out of range started travel")
root.Position=vector(8);human.Health=0;activate(p);check(#attempts==0,"Defeated character started travel")
human.Health=100;mode="throw";activate(p);check(p.status:find("failed") and root.Position.x==8,"Thrown initialization left source in pending travel")
mode=nil;activate(p);activate(p)
check(#attempts==1 and attempts[1].id==30 and attempts[1].player==p,"Duplicate hold or wrong travel target")
local first=attempts[1].options
check(first:GetTeleportData().travelAttempt==1+1 and next(first:GetTeleportData(),"travelAttempt")==nil,"Travel carried unexpected gameplay data")
events.emit(p,nil,nil,99,first);activate(p);check(#attempts==1,"Unrelated destination reopened travel")
events.emit(p,nil,nil,30,first);check(p.status:find("failed"),"Matching delayed failure did not restore retry")
activate(p);events.emit(p,nil,nil,30,first);activate(p)
check(#attempts==2,"Stale failure unlocked a newer pending attempt")
players.PlayerRemoving.emit(p);p.Parent=nil;activate(p)
check(#attempts==2 and root.Position.x==8,"Departed character reused the source prompt")
local landing=vector(54)
local fromPeer={SourceGameId=10,SourcePlaceId=30}
local direct,directRoot=actor(8)
local existing,existingRoot=actor(9);existing.join=fromPeer
players.current={direct,existing}
gate().BindArrival(landing,"Safe arrival")
check(existingRoot.Position.x==54 and existing.status=="Safe arrival","Already-spawned peer did not reach arrival")
check(existingRoot.AssemblyLinearVelocity==Vector3.zero,"Arrival retained spawn velocity")
check(directRoot.Position.x==8,"Direct join moved to peer arrival")
for _,source in ipairs({{SourceGameId=10,SourcePlaceId=20},{SourceGameId=99,SourcePlaceId=30},
 {TeleportData={SourceGameId=10,SourcePlaceId=30}}}) do
 local other,otherRoot=actor(7);other.join=source;players.PlayerAdded.emit(other)
 check(otherRoot.Position.x==7,"Arrival trusted a different place or payload")
end
local traveler,firstRoot=actor(7);traveler.join=fromPeer
local firstCharacter=traveler.Character;traveler.Character=nil
players.PlayerAdded.emit(traveler);players.PlayerAdded.emit(traveler)
traveler.Character=firstCharacter;traveler.CharacterAdded.emit(firstCharacter)
check(firstRoot.Position.x==54,"Deferred peer arrival missed its first character")
traveler.CharacterRemoving.emit(firstCharacter)
check(traveler.status==nil,"Arrival guidance survived character removal")
existing:SetAttribute("TravelStatus","Opening the other world...")
existing.CharacterRemoving.emit(existing.Character)
check(existing.status=="Opening the other world...","Character removal cleared newer travel feedback")
local respawn,respawnRoot=actor(4);traveler.Character=respawn.Character
traveler.CharacterAdded.emit(traveler.Character);players.PlayerAdded.emit(traveler)
check(respawnRoot.Position.x==4,"Respawn replayed inbound arrival")
local replaced,replacedRoot=actor(7);replaced.join=fromPeer
replaced.Character.onWait=function()replaced.Character=respawn.Character end
players.PlayerAdded.emit(replaced)
check(replacedRoot.Position.x==7 and respawnRoot.Position.x==4,"Arrival moved a replaced character")
local rehearsalPlayer,rehearsalRoot=actor(6)
players.current={rehearsalPlayer}
settings={rehearsal=true};game.GameId=0;game.PlaceId=0
gate().BindArrival(landing,"Safe arrival")
check(rehearsalRoot.Position.x==54 and rehearsalPlayer.status=="Arrival rehearsal. Safe arrival","Zero-ID rehearsal did not stage the same landing")
print("PASS "..count.." travel gate assertions; simulated Roblox transport and events")
'''


def run(source, expected=None):
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.luau', delete=False) as f:
        f.write(SETUP + source + '\n' + CHECKS)
        path = Path(f.name)
    try:
        result = subprocess.run(['luau', str(path)], capture_output=True, text=True, timeout=10)
    finally:
        path.unlink()
    if expected:
        assert result.returncode and expected in result.stderr, result.stdout + result.stderr
        print('PASS control:', expected)
    else:
        assert result.returncode == 0, result.stdout + result.stderr
        print(result.stdout.strip())


run(GATE)
if '--negative-controls' in sys.argv:
    run(GATE.replace(' or pending[player]',''), 'Duplicate hold or wrong travel target')
    run(GATE.replace('failed(player,data.travelAttempt,','failed(player,pending[player],'), 'Stale failure unlocked a newer pending attempt')
    run(GATE.replace('assert(studio and (','assert(('), 'Travel gate accepted live context')
    run(GATE.replace(' or from.SourcePlaceId~=settings.destination',''), 'Arrival trusted a different place or payload')
    run(GATE.replace('player.CharacterAdded:Once(land)','player.CharacterAdded:Connect(land)'), 'Respawn replayed inbound arrival')
    run(GATE.replace('player:SetAttribute("TravelStatus",nil)', ''), 'Arrival guidance survived character removal')
    run(GATE.replace(' and player:GetAttribute("TravelStatus")==arrivalStatus', ''), 'Character removal cleared newer travel feedback')
