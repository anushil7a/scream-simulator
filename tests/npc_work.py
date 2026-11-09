"""Actual NPC work wait/completion block with mocked clock and interruptions."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'src/ServerScriptService/World.luau').read_text()
start = source.index('                            local workVersion=')
end = source.index('                            bot.working=false;', start)
setup = '''
local now=0
local os={clock=function() return now end}
local bot,model,interrupt
local repairs=0
local task={wait=function(dt) now+=dt; if interrupt then interrupt() end end}
local World={FinishMaintenance=function() repairs+=1 end}
local station={maintenanceModel={}}
local rng={NextNumber=function() return 5 end}
local role='Sanitation'
local function work()
'''
checks = '''
end
local checks=0
local function check(value,message) assert(value,message);checks+=1 end
local function reset()
 now=0;repairs=0;interrupt=nil;model={Parent=true}
 bot={alive=true,working=true,pathVersion=1}
end
reset();work()
check(repairs==1 and now>=5,'Uninterrupted repair must complete')
for _,case in ipairs({'stopped','new route','removed','KO','conversation','reaction'}) do
 reset()
 interrupt=function()
  if case=='stopped' then bot.working=false
  elseif case=='new route' then bot.pathVersion+=1
  elseif case=='removed' then model.Parent=nil
  elseif case=='KO' then bot.alive=false
  elseif case=='conversation' then bot.socialUntil=10
  else bot.reactionUntil=10 end
 end
 work()
 check(now<.3,'Interrupted routine kept waiting: '..case)
 check(repairs==0,'Interrupted routine repaired: '..case)
end
-- Cancellation on the final wake must not receive completion credit.
for _,case in ipairs({'stopped','new route','removed','conversation','reaction'}) do
 reset()
 interrupt=function()
  if now>=5 then
   if case=='stopped' then bot.working=false
   elseif case=='new route' then bot.pathVersion+=1
   elseif case=='removed' then model.Parent=nil
   elseif case=='conversation' then bot.socialUntil=10
   else bot.reactionUntil=10 end
  end
 end
 work();check(repairs==0,'Final-wake cancellation repaired: '..case)
end
print('PASS '..checks..' actual NPC work checks with mocked time/activity')
'''
with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', dir=root/'tests', delete=False) as f:
    path=Path(f.name)
    f.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau', str(path)], cwd=root, check=True)
finally:
    path.unlink()
