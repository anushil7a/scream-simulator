"""Actual client wiring/controller/queue with simulated lifecycle and frame time."""
from pathlib import Path
import subprocess,sys,tempfile
root=Path(__file__).resolve().parents[1]
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
constructor=client[client.index(' sustainedControl=require'):client.index(' script.Destroying:Connect(function() sustainedControl:Destroy()')]
constructor=constructor.replace('require(script.Parent:WaitForChild("SustainedControls"))','Controls')
toggle=client[client.index('local function toggleVoice()'):client.index('local function releaseCapture(')]
removal=next(line for line in client.splitlines() if line.startswith('connectClient(p.CharacterRemoving,function() hitFeedback:DiscardThrough'))
suspend=client[client.index('local function suspendGameplay()'):client.index('connectClient(UIS.WindowFocusReleased')]
payload='''
local Queue=require('../src/StarterPlayer/StarterPlayerScripts/NotificationQueue')
local Controls=require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')
local VoiceActivation=require('../src/ReplicatedStorage/Shared/VoiceActivation')
local notifications=Queue.new();local sustainedControl;local windowFocused=true
local action={FireServer=function()end};local unavailable=false
local function blocked()return unavailable end
local function notify(text,urgent,key)notifications:Push(text,urgent,key)end
local p={CharacterRemoving={}};local removalCallback
local function connectClient(_,fn)removalCallback=fn end
local hitFeedback={DiscardThrough=function()end};local function setSprint()end
local function cancelCapture()end;local closeConversation=nil
'''+constructor+toggle+removal+suspend+'''
local checks=0;local function check(ok,msg)assert(ok,msg);checks+=1 end
local function noVoice(reason)
 check(not (notifications.active and notifications.active.key=='voice'),reason..': stale active voice notice')
 for _,entry in ipairs(notifications.pending) do check(entry.key~='voice',reason..': stale queued voice notice') end
end
for _,kind in ipairs({'respawn','unavailable','suspend'}) do
 notifications=Queue.new();sustainedControl:SetArmed(false)
 notify('Saving is unavailable',true);toggleVoice()
 check(sustainedControl.armed and #notifications.pending==1,'Setup did not queue ON behind warning')
 if kind=='respawn' then removalCallback()
 elseif kind=='unavailable' then sustainedControl:ObserveAvailability(false)
 else suspendGameplay() end
 check(not sustainedControl.armed,'Lifecycle did not disarm')
 noVoice(kind)
 check(notifications:Step(1/60,true)=='Saving is unavailable','Clearing guidance lost save warning')
 for _=1,400 do check(notifications:Step(1/60,true)~='Beams ON. Normal speech can fire attacks. Go quiet, then speak. Turn OFF to talk freely; voice chat is unchanged.','Disarmed ON guidance replayed') end
end
-- Active ON is withdrawn too, without removing unrelated queued feedback.
notifications=Queue.new();toggleVoice();notify('Reward');notifications:Step(1/60,true)
suspendGameplay();noVoice('active');check(notifications:Step(1/60,true)=='Reward','Voice removal lost unrelated reward')
-- Initial automatic arming invalidates setup guidance even without a click.
notifications=Queue.new();sustainedControl.initialized=nil;unavailable=true;toggleVoice();unavailable=false
check(notifications.active.key=='voice','Setup refusal missing')
sustainedControl:ObserveAvailability(true);noVoice('initial arm')
-- A no-op observation must not discard current, valid status.
toggleVoice();local current=notifications.active
sustainedControl:ObserveAvailability(true)
check(notifications.active==current and current.key=='voice','No-op availability removed valid OFF guidance')
print('PASS '..checks..' voice notice lifecycle assertions; synthetic timing and callbacks')
'''
def run(source,failure=None):
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(source)
 try:
  result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
  if failure:
   assert result.returncode!=0 and failure in result.stderr,result.stdout+result.stderr
   print('PASS lifecycle negative control: '+failure)
  else:
   print(result.stdout,end='');assert result.returncode==0,result.stderr
 finally:path.unlink()
run(payload)
if '--negative-controls' in sys.argv:
 needle='function() notifications:Remove("voice") end'
 assert payload.count(needle)==1
 run(payload.replace(needle,'function() end'),'respawn: stale queued voice notice')
 controls=(root/'src/StarterPlayer/StarterPlayerScripts/SustainedControls.luau').read_text()
 hook='if self.onArmedChanged then self.onArmedChanged(armed) end'
 assert controls.count(hook)==1
 require="require('../src/StarterPlayer/StarterPlayerScripts/SustainedControls')"
 run(payload.replace(require,'(function()\n'+controls.replace(hook,'')+'\nend)()'),'respawn: stale queued voice notice')
