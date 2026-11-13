"""Actual Client lock context/aim/input/cancel/marker slices + real controller/range rules.
Synthetic services and projections; whole startup is covered separately, not native input.
"""
from pathlib import Path
import subprocess,tempfile,argparse
import lock_on
R=Path(__file__).resolve().parents[1]
P=R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def build(s):
 context=s[s.index('local function lockContext('):s.index('if remotes:GetAttribute("AutomaticVoice")==true then',s.index('local function lockContext('))]
 cancel=s[s.index('local function cancelCapture()'):s.index('local function blocked()')]
 receiver=s[s.index('local function observeVoiceEligibility('):s.index('local function toggleVoice()')]
 voice=s[s.index('local function toggleVoice()'):s.index('local function screamToggleLabel(')]
 tab=s[s.index('local function toggleTab(name)'):s.index('local function toggle()')]
 respawns=[line for line in s.splitlines() if line.startswith('connectClient(p.CharacterRemoving,') and 'lockController:Clear()' in line]
 assert len(respawns)==1,'Expected one actual respawn lock-clear callback'
 respawn=respawns[0]
 art=s[s.index('local lockButton=button('):s.index('local talkTarget',s.index('local lockButton=button('))]
 inp=s[s.index('connectClient(UIS.InputBegan,function(input,processed)'):s.index('connectClient(UIS.InputEnded',s.index('connectClient(UIS.InputBegan,function(input,processed)'))]
 marker=s[s.index(' local lockedPoint='):s.index(' beamScreenFeedback:Step(',s.index(' local lockedPoint='))]
 base=lock_on.SETUP.replace("return V[k]end", "if k=='Unit'then local m=math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z);return setmetatable({X=t.X/m,Y=t.Y/m,Z=t.Z/m,_type='Vector3'},V)end;return V[k]end")
 base+='\nV.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end\nV.__mul=function(a,b)return v(a.X*b,a.Y*b,a.Z*b)end\n'
 fixture=lock_on.CHECKS[:lock_on.CHECKS.index('local lock,c,o,npc')]
 rules=(R/'src/ReplicatedStorage/Shared/VoiceCombat.luau').read_text()
 pre=r"""
local lockController,initial,o,npc,enemy=fixture()
local p=o.localPlayer;local workspace=o.world;workspace.CurrentCamera=initial.camera
local originalProjection=workspace.CurrentCamera.WorldToViewportPoint
local clock=10;local os={clock=function()return clock end};function workspace:GetServerTimeNow()return clock end
local Config={VoiceCombat=VoiceCombat};local data={level=1,amplifierEquipped=false}
local clientDestroyed=false;local windowFocused=true;local blockedState=false
local mic={ready=true,power=1,cancels=0,Cancel=function(self)self.cancels+=1 end}
local sustainedControl={armed=true,Cancel=function(self)self.cancelled=true end,SetArmed=function(self,value)self.armed=value end}
local standardControl=sustainedControl
local voiceAccessInterrupted=false;local captureSource;local commands={};local action={FireServer=function(_,verb)commands[#commands+1]=verb end}
local function beamBlocked()return blockedState end
local UIS={TouchEnabled=false,GamepadEnabled=false,typing=false}
function UIS:GetMouseLocation()return {X=111,Y=222}end
function UIS:GetFocusedTextBox()return self.typing end
local rawRay={Origin=v(9,9,9),Direction=v(0,0,1)}
function workspace.CurrentCamera:ViewportPointToRay(x,y)check(x==111 and y==222,'OFF changed desktop cursor');return rawRay end
local Vector3={new=v};local freeHit={Position=v(99,0,99)}
local oldRaycast=workspace.Raycast
function workspace:Raycast(origin,delta,params)if origin==rawRay.Origin then return freeHit end;return oldRaycast(self,origin,delta,params)end
local GuiService={MenuIsOpen=false};Enum.KeyCode={E='E',Q='Q',B='B',R='R',ButtonR3='R3',M='M',LeftShift='Shift',T='T'}
local input,respawnCallback;p.CharacterRemoving={}
local function connectClient(signal,fn)if signal==p.CharacterRemoving then respawnCallback=fn else input=fn end end
local function beginCapture()end;local function dodge()end;local function toggle()end;local function setSprint()end;local function requestTalk()end
local modal={Visible=false};local selected='Shop';local devPanel={Visible=false}
local function closeMenu()modal.Visible=false end;local function render()end;local function closeConversation()end
local function notify()end;local function voiceEligibilityHint()return nil end
local academy={lockLostUntil=0,surface=function()end};local gold,dark,panel,white='gold','dark','panel','white'
local gameplayVisible=true;local touch=false;local controls={};local aimGui={}
local UDim2={new=function(sx,ox,sy,oy)return {X={Scale=sx or 0,Offset=ox or 0},Y={Scale=sy or 0,Offset=oy or 0}}end}
UDim2.fromOffset=function(x,y)return UDim2.new(0,x,0,y)end
local UDim={new=function(s,o)return {Scale=s,Offset=o}end};local Vector2={new=function(x,y)return {X=x,Y=y}end}
Enum.Font={GothamBold='GothamBold'};Enum.TextXAlignment={Center='Center'};Enum.ApplyStrokeMode={Border='Border'}
local artObjects={};local Instance={new=function(class)local o={ClassName=class};table.insert(artObjects,o);return o end}
local function button(parent,name,words,size,pos,callback)
 local o=Instance.new('TextButton');o.Parent=parent;o.Name=name;o.Text=words;o.Size=size;o.Position=pos;o.callback=callback;return o
end
local function label(parent,words,size,pos,fontSize,color)
 local o=Instance.new('TextLabel');o.Parent=parent;o.Text=words;o.Size=size;o.Position=pos;o.TextSize=fontSize;o.TextColor3=color;return o
end
"""
 checks=r"""
local ray,hit=aimRay();check(ray==rawRay and hit==freeHit,'OFF fallback changed')
input({KeyCode='R'},true);check(lockController.target==nil,'Processed input acquired')
UIS.typing=true;input({KeyCode='R'},false);check(lockController.target==nil,'Typing input acquired');UIS.typing=false
GuiService.MenuIsOpen=true;input({KeyCode='R3'},false);check(lockController.target==nil,'Platform menu acquired');GuiService.MenuIsOpen=false
input({KeyCode='R'},false);check(lockController.target.model==npc and sustainedControl.armed and #commands==0,'R failed or fired/armed')
ray,hit=aimRay();check(hit.Instance==npc and hit.Position==npc.HumanoidRootPart.Position and ray.Origin.X==0,'Locked aim differs from selected target')
updateMarker();check(lockMarker.Visible and lockButton.Text=='UNLOCK' and lockMarker.Position.X.Offset==330,'Marker differs from submitted target')
check(lockButton.BackgroundColor3==gold and lockButton.TextColor3==dark,'Acquired button lacks distinct treatment')
input({KeyCode='R3'},false);check(lockController.target==nil,'R3 did not unlock');input({KeyCode='R'},false);check(lockController.target==nil,'Acquire debounce bypassed')
clock+=.21;input({KeyCode='R3'},false);check(lockController.target.model==npc,'R3 acquire failed')
blockedState=true;updateMarker();check(lockController.target==nil and not lockMarker.Visible,'Modal/focus policy did not clear marker');blockedState=false
clock+=.21;toggleLock();windowFocused=false;aimRay();check(lockController.target==nil,'Focus loss retained');windowFocused=true
clock+=.21;toggleLock();observeVoiceEligibility({voiceEligible=false});check(lockController.target==nil and not sustainedControl.armed,'Eligibility transition retained lock')
sustainedControl.armed=true;clock+=.21;toggleLock();cancelCapture();check(lockController.target==nil and sustainedControl.cancelled,'Cancel retained lock')
clock+=.21;toggleLock();o.world.cover=true;ray,hit=aimRay();check(lockController.target==nil and ray==rawRay,'Cover not rechecked at aim sample');o.world.cover=false
clock+=.21;toggleLock();sustainedControl.armed=false;aimRay();check(lockController.target==nil,'OFF retained aim assist');check(#commands==0,'Lock sent an attack command')
sustainedControl=nil;mic.power=0;clock+=.21;toggleLock();check(lockController.target~=nil,'Legacy acquire failed')
npc.HumanoidRootPart.Position=v(1,0,25)
ray,hit=aimRay(1);check(hit.Instance==npc,'Legacy captured power not used')
ray,hit=aimRay(0);check(lockController.target==nil and ray==rawRay,'Actual range not rechecked')
clientDestroyed=true;clock+=1;toggleLock();check(lockController.target==nil,'Destroyed callback reacquired')

-- Actual constructor values, not native TextFits, glyph metrics or visual proof.
check(lockButton.Size.X.Offset==88 and lockButton.Size.Y.Offset==44 and lockButton.TextSize==12 and lockButton.Selectable,'Lock button geometry/input changed')
check(lockMarker.Parent==aimGui and lockMarker.Size.X.Offset==108 and lockMarker.Size.Y.Offset==28 and lockMarker.Text=='' and lockMarker.Font==Enum.Font.GothamBold,'Lock chip geometry/font changed')
check(lockMarker.BackgroundColor3==dark and lockMarker.BackgroundTransparency==0,'Lock chip has no opaque dark backing')
local symbol,edge,words,center
for _,o in ipairs(artObjects)do
 if o.Parent==lockMarker and o.Name=='LockSymbol'then symbol=o end
 if o.Parent==lockMarker and o.ClassName=='UIStroke'then edge=o end
 if o.Parent==lockMarker and o.Name=='LockText'then words=o end
 check(not(o.Parent==lockMarker and o.ClassName=='UIPadding'),'Caption relies on unmodeled padding semantics')
end
check(edge and edge.Color==gold and edge.Thickness==1 and edge.ApplyStrokeMode==Enum.ApplyStrokeMode.Border,'Lock chip border missing')
check(words and words.Text=='LOCKED' and words.TextSize==13 and words.Font==Enum.Font.GothamBold and words.TextXAlignment==Enum.TextXAlignment.Center,'Explicit lock text missing')
check(words.Position.X.Offset==28 and words.Position.Y.Offset==0 and words.Size.X.Scale==1 and words.Size.X.Offset==-32 and words.Size.Y.Scale==1 and words.Size.Y.Offset==0,'Lock symbol/text lane changed')
check(symbol and symbol.Size.X.Offset==12 and symbol.Size.Y.Offset==12 and symbol.Position.X.Offset==10 and symbol.Position.Y.Offset==8 and symbol.Position.X.Offset+symbol.Size.X.Offset<words.Position.X.Offset,'Lock symbol/text lane changed')
for _,o in ipairs(artObjects)do if o.Parent==symbol and o.Name=='Center'then center=o end end
check(center and center.Size.X.Offset==2 and center.Size.Y.Offset==2 and center.Position.X.Offset==5 and center.Position.Y.Offset==5 and center.BackgroundColor3==gold,'Lock symbol center missing')

local function resetFeedbackCase()
 clientDestroyed=false;windowFocused=true;blockedState=false;gameplayVisible=true
 sustainedControl=standardControl;sustainedControl.armed=true;mic.power=1
 npc.Humanoid.Health=100;npc.HumanoidRootPart.Position=v(1,0,10)
 workspace.cover=false;workspace.CurrentCamera.hidden=false
 workspace.CurrentCamera.ViewportSize={X=640,Y=360};workspace.CurrentCamera.WorldToViewportPoint=originalProjection
 modal.Visible=false;devPanel.Visible=false;touch=false;UIS.GamepadEnabled=false
 lockController:Clear();academy.lockLostUntil=0;clock+=1
 toggleLock();check(lockController.target and lockController.target.model==npc,'Feedback setup did not acquire')
end
local function breakTarget(kind)
 if kind=='cover'then workspace.cover=true elseif kind=='range'then npc.HumanoidRootPart.Position=v(1,0,100)
 elseif kind=='dead'then npc.Humanoid.Health=0 elseif kind=='offscreen'then workspace.CurrentCamera.hidden=true end
end
local function restoreTarget()
 workspace.cover=false;npc.Humanoid.Health=100;npc.HumanoidRootPart.Position=v(1,0,10);workspace.CurrentCamera.hidden=false
end
for _,kind in ipairs({'cover','range','dead','offscreen'})do for _,order in ipairs({'aim-first','ui-first'})do
 resetFeedbackCase();breakTarget(kind)
 if order=='aim-first'then local ray=aimRay();check(ray==rawRay,'Lost lock did not return free aim')else updateMarker()end
 local deadline=academy.lockLostUntil
 check(math.abs(deadline-(clock+.8))<.000001,'Involuntary loss deadline absent: '..kind..' '..order)
 updateMarker();check(not lockMarker.Visible and not lockController.target,'Lost target ghost retained')
 check(lockButton.Text=='LOCK LOST\nLOCK [R]' and lockButton.BackgroundColor3==panel and lockButton.TextColor3==white,'Lost button did not distinguish failure')
 restoreTarget();clock+=.4
 for i=1,3 do aimRay();updateMarker()end
 check(academy.lockLostUntil==deadline and lockButton.Text=='LOCK LOST\nLOCK [R]','Lost deadline extended or cue expired early')
 check(lockController.target==nil and not lockMarker.Visible,'Target automatically reacquired')
 clock=deadline;updateMarker();check(lockButton.Text=='AIM CENTER\nLOCK [R]' and not lockMarker.Visible,'Lost cue did not expire')
end end

resetFeedbackCase();workspace.cover=true;aimRay();updateMarker();restoreTarget();clock+=.21
toggleLock();updateMarker();check(lockController.target and lockMarker.Visible and academy.lockLostUntil==0 and lockButton.Text=='UNLOCK','Immediate reacquire retained lost cue')
toggleLock();updateMarker();check(not lockController.target and academy.lockLostUntil==0 and lockButton.Text=='AIM CENTER\nLOCK [R]','Manual unlock reported loss')

for _,policy in ipairs({'blocked','focus','off'})do
 resetFeedbackCase()
 if policy=='blocked'then blockedState=true elseif policy=='focus'then windowFocused=false else sustainedControl.armed=false end
 updateMarker();check(not lockController.target and academy.lockLostUntil==0 and not lockMarker.Visible,'Policy clear reported loss: '..policy)
 resetFeedbackCase();workspace.cover=true;aimRay();restoreTarget()
 if policy=='blocked'then blockedState=true elseif policy=='focus'then windowFocused=false else sustainedControl.armed=false end
 updateMarker();check(academy.lockLostUntil==0,'Policy retained pending loss: '..policy)
 blockedState=false;windowFocused=true;sustainedControl.armed=true;updateMarker()
 check(lockButton.Text=='AIM CENTER\nLOCK [R]' and not lockController.target,'Policy exit restored stale loss/target')
end

local clearCases={
 {name='cancel',run=cancelCapture},{name='eligibility',run=function()observeVoiceEligibility({voiceEligible=false})end},
 {name='voice-off',run=toggleVoice},{name='respawn',run=function()respawnCallback()end},{name='tab',run=function()toggleTab('Map')end},
}
for _,case in ipairs(clearCases)do
 resetFeedbackCase();case.run();check(not lockController.target and academy.lockLostUntil==0,'Direct clear retained target: '..case.name)
 resetFeedbackCase();workspace.cover=true;aimRay();restoreTarget();check(academy.lockLostUntil>clock,'Pending loss setup failed')
 case.run();check(academy.lockLostUntil==0 and not lockController.target,'Direct clear retained pending loss: '..case.name)
end
for _,mode in ipairs({'touch','gamepad','keyboard'})do
 resetFeedbackCase();workspace.cover=true;aimRay();touch=mode=='touch';UIS.GamepadEnabled=mode=='gamepad';updateMarker()
 local suffix=touch and 'LOCK' or UIS.GamepadEnabled and 'LOCK [R3]' or 'LOCK [R]'
 check(lockButton.Text=='LOCK LOST\n'..suffix,'Lost cue dropped input suffix: '..mode)
 clock=academy.lockLostUntil;updateMarker();check(lockButton.Text=='AIM CENTER\n'..suffix,'Expired cue dropped input suffix')
end
for _,bounds in ipairs({{640,360,1,1,62,36,true},{640,360,639,359,578,335,true},{124,44,62,22,62,36,true},{123,44,61,22,0,0,false},{124,43,62,21,0,0,false}})do
 resetFeedbackCase();local camera=workspace.CurrentCamera;camera.ViewportSize={X=bounds[1],Y=bounds[2]}
 function camera:WorldToViewportPoint()return v(bounds[3],bounds[4],10),true end
 updateMarker();check(lockMarker.Visible==bounds[7],'Caption minimum viewport gate changed')
 check(lockController.target and lockButton.Text=='UNLOCK','Caption layout changed selection')
 local ray,hit=aimRay();check(hit.Instance==npc and hit.Position==npc.HumanoidRootPart.Position and ray.Origin.X==0,'Caption clamp changed submitted aim')
 if bounds[7]then
  check(lockMarker.Position.X.Offset==bounds[5] and lockMarker.Position.Y.Offset==bounds[6],'Caption clamp incorrect')
  local x,y=lockMarker.Position.X.Offset,lockMarker.Position.Y.Offset
  check(x-54>=8 and x+54<=bounds[1]-8 and y-28>=8 and y<=bounds[2]-8,'Caption outside eight-pixel viewport margin')
 end
end
check(#commands==0,'Feedback sent an attack command')
print('PASS '..n..' actual Client lock-on integration assertions; mocked input/LOS/GUI')
"""
 return base+'local LockOn=(function()\n'+lock_on.source+'\nend)()\nlocal VoiceCombat=(function()\n'+rules+'\nend)()\n'+fixture+pre+cancel+tab+context+receiver+voice+respawn+'\n'+art+inp+'\nlocal function updateMarker()\n'+marker+'\nend\n'+checks

def marker_contract(s):
 assert 'local lockMarker=label(aimGui,' in s and 'aimGui.ScreenInsets=Enum.ScreenInsets.None' in s,'Viewport marker uses inset parent'

def run(s):
 code=build(s)
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(code);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=15)
 finally:p.unlink()
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--negative-controls',action='store_true');args=ap.parse_args();s=P.read_text()
 r=run(s);print(r.stdout,end='');assert r.returncode==0,r.stderr
 marker_contract(s)
 print('PASS marker parent/inset source contract (not native absolute rendering)')
 if args.negative_controls:
  bad_parent=s.replace('local lockMarker=label(aimGui,','local lockMarker=label(gui,',1)
  try:marker_contract(bad_parent)
  except AssertionError as e:assert 'Viewport marker uses inset parent' in str(e)
  else:raise AssertionError('Inset parent control survived')
  mutations=[('local locked,target=academy.resolveLock(lockContext(power))','local locked,target=nil,nil','Locked aim differs'),('now<nextLockAcquire','false','Acquire debounce'),('k==Enum.KeyCode.R or k==Enum.KeyCode.ButtonR3','k==Enum.KeyCode.R','R3 did not unlock'),('if lockController then lockController:Clear();academy.lockLostUntil=0 end\n if sustainedControl then sustainedControl:Cancel()','if sustainedControl then sustainedControl:Cancel()','Cancel retained'),('local lockedPoint=academy.resolveLock(lockContext())','local lockedPoint=nil','Marker differs'),
   ('local locked,target=academy.resolveLock(lockContext(power))','local locked,target=lockController:Resolve(lockContext(power))','Involuntary loss deadline absent'),
   ('local lockedPoint=academy.resolveLock(lockContext())','local lockedPoint=lockController:Resolve(lockContext())','Involuntary loss deadline absent'),
   ('elseif hadTarget then academy.lockLostUntil=os.clock()+.8','else academy.lockLostUntil=os.clock()+.8','Lost deadline extended'),
   ('if point or not context.allowed then academy.lockLostUntil=0','if point then academy.lockLostUntil=0','Policy clear reported loss'),
   ('lockMarker.BackgroundTransparency=0','lockMarker.BackgroundTransparency=1','Lock chip has no opaque'),
   ('lockButton.BackgroundColor3=lockedPoint and gold or panel','lockButton.BackgroundColor3=panel','Acquired button lacks distinct'),
   ('UDim2.fromOffset(28,0),13,gold','UDim2.fromOffset(0,0),13,gold','Lock symbol/text lane changed'),
   ('math.clamp(screen.X,insetX,view.X-insetX)','screen.X','Caption clamp incorrect'),
   ('view.X>=insetX*2 and view.Y>=insetY+8','true','max must be greater than or equal to min'),
   ('if lockController then lockController:Clear();academy.lockLostUntil=0 end\n if sustainedControl then sustainedControl:Cancel()','if lockController then lockController:Clear() end\n if sustainedControl then sustainedControl:Cancel()','Direct clear retained pending loss: cancel'),
   ('lockController:Clear();academy.lockLostUntil=0\n if nextData.voiceStatus','lockController:Clear()\n if nextData.voiceStatus','Direct clear retained pending loss: eligibility'),
   ('if not sustainedControl.armed then lockController:Clear();academy.lockLostUntil=0 end','if not sustainedControl.armed then lockController:Clear() end','Direct clear retained pending loss: voice-off'),
   ('connectClient(p.CharacterRemoving,function() lockController:Clear();academy.lockLostUntil=0 end)','connectClient(p.CharacterRemoving,function() lockController:Clear() end)','Direct clear retained pending loss: respawn'),
   ('local function toggleTab(name)\n if lockController then lockController:Clear();academy.lockLostUntil=0 end','local function toggleTab(name)\n if lockController then lockController:Clear() end','Direct clear retained pending loss: tab')]
  for old,new,expected in mutations:
   assert old in s
   r=run(s.replace(old,new,1));assert r.returncode and expected in r.stderr,(old,r.stdout,r.stderr)
  print(f'PASS {1+len(mutations)} Client wiring/presentation negative controls')
