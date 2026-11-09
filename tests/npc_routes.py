"""Actual NPC route coroutine with synthetic path/time/movement, not engine navigation."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/World.luau').read_text()
start=source.index('local function roamTo(')
end=source.index('local function usableSeat(',start)
setup='''
local now=0;local os={clock=function()return now end}
local V={};V.__index=function(v,k)
 if k=='Magnitude' then return math.sqrt(v.X*v.X+v.Y*v.Y+v.Z*v.Z) end
 if k=='Unit' then local m=v.Magnitude;return setmetatable({X=v.X/m,Y=v.Y/m,Z=v.Z/m},V) end
 return V[k]
end
V.__sub=function(a,b)return setmetatable({X=a.X-b.X,Y=a.Y-b.Y,Z=a.Z-b.Z},V)end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
Vector3.zero=Vector3.new(0,0,0)
local Enum={PathStatus={Success='success'},PathWaypointAction={Jump='jump'}}
local task={};local PathfindingService={};local scenario,bot,path
local function releaseSeat()error('Unexpected seat release')end
function PathfindingService:CreatePath()
 path={Status=scenario.failed and 'failed' or 'success',destroyed=false,disconnected=false}
 path.Blocked={Connect=function(_,fn)path.onBlocked=fn;return {Disconnect=function()path.disconnected=true end}end}
 function path:ComputeAsync()if scenario.replaceDuringCompute then bot.pathVersion+=1 end end
 function path:GetWaypoints()return scenario.waypoints end
 function path:Destroy()self.destroyed=true end
 return path
end
function task.wait(dt)
 now+=dt
 if scenario.interrupt then bot.pathVersion+=1;scenario.interrupt=false end
end
'''
checks='''
local count=0
local function check(v,msg)assert(v,msg);count+=1 end
local function run(options)
 now=0;scenario=options
 bot={alive=true,model={Parent=true},root={Position=Vector3.zero},pathVersion=0,humanoid={WalkSpeed=9}}
 bot.moves={};bot.preciseMoves=0
 function bot.humanoid:MoveTo(pos)
  table.insert(bot.moves,pos)
  if scenario.blockIndex then path.onBlocked(scenario.blockIndex) end
  if scenario.arrive then bot.root.Position=pos end
 end
 function bot.humanoid:Move(direction)
  bot.preciseMoves+=1
  if direction.Magnitude==0 then bot.stoppedPrecisely=true
  elseif scenario.preciseArrival then bot.root.Position=scenario.destination end
 end
 roamTo(bot,options.destination or Vector3.new(3,0,0),true)
 check(path.destroyed,'Route leaked path')
end
run({waypoints={{Position=Vector3.new(3,0,0),Action='jump'}}})
check(bot.preciseMoves==0 and #bot.moves==1 and bot.moves[1]==bot.root.Position,'Jump-required path used direct precision movement')
check(path.disconnected,'Jump path leaked blocker listener')
run({failed=true,waypoints={}})
check(#bot.moves==0 and bot.preciseMoves==0,'Failed path attempted movement')
run({replaceDuringCompute=true,waypoints={{Position=Vector3.new(3,0,0)}}})
check(#bot.moves==0,'Obsolete computed path attempted movement')
run({waypoints={{Position=Vector3.new(10,0,0)},{Position=Vector3.new(20,0,0)}},blockIndex=1})
check(#bot.moves==2 and bot.moves[2]==bot.root.Position and bot.preciseMoves==0,'Blocked path skipped ahead')
run({waypoints={{Position=Vector3.new(10,0,0)},{Position=Vector3.new(20,0,0)}}})
check(now>=.8 and now<2 and bot.preciseMoves==0 and #bot.moves==3,'Stalled route did not stop without skipping')
run({waypoints={{Position=Vector3.new(10,0,0)}},interrupt=true})
check(#bot.moves==1 and bot.preciseMoves==0,'Interrupted route overwrote replacement movement')
run({waypoints={{Position=Vector3.new(10,0,0)},{Position=Vector3.new(20,0,0)}},arrive=true,blockIndex=0,destination=Vector3.new(20,0,0)})
check(#bot.moves==2 and bot.root.Position.X==20,'Obstruction behind route stopped forward travel')
run({waypoints={{Position=Vector3.new(1,0,0)}},destination=Vector3.new(3,0,0),preciseArrival=true})
check(bot.root.Position.X==3 and bot.preciseMoves==2 and bot.stoppedPrecisely,'Final approach did not move then stop at work surface')
check(bot.humanoid.WalkSpeed==9 and path.disconnected,'Completed precision approach retained slow speed or path listener')
run({waypoints={{Position=Vector3.new(1,0,0)}},destination=Vector3.new(3,0,0),interrupt=true})
check(bot.preciseMoves==1 and not bot.stoppedPrecisely,'Interrupted precision approach stopped replacement movement')
check(bot.humanoid.WalkSpeed==9 and now<.1,'Interrupted precision approach retained slow speed or kept waiting')
run({waypoints={{Position=Vector3.new(1,0,0)}},destination=Vector3.new(3,0,0)})
check(now>=2 and now<2.1 and bot.stoppedPrecisely and bot.humanoid.WalkSpeed==9,'Stalled precision approach did not stop and restore speed within its deadline')
print('PASS '..count..' actual NPC route checks with synthetic paths/time; no native navigation evidence')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.route_',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
