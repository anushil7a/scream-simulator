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
 inp=s[s.index('connectClient(UIS.InputBegan,function(input,processed)'):s.index('connectClient(UIS.InputEnded',s.index('connectClient(UIS.InputBegan,function(input,processed)'))]
 marker=s[s.index(' local lockedPoint='):s.index(' beamScreenFeedback:Step(',s.index(' local lockedPoint='))]
 base=lock_on.SETUP.replace("return V[k]end", "if k=='Unit'then local m=math.sqrt(t.X*t.X+t.Y*t.Y+t.Z*t.Z);return setmetatable({X=t.X/m,Y=t.Y/m,Z=t.Z/m,_type='Vector3'},V)end;return V[k]end")
 base+='\nV.__add=function(a,b)return v(a.X+b.X,a.Y+b.Y,a.Z+b.Z)end\nV.__mul=function(a,b)return v(a.X*b,a.Y*b,a.Z*b)end\n'
 fixture=lock_on.CHECKS[:lock_on.CHECKS.index('local lock,c,o,npc')]
 rules=(R/'src/ReplicatedStorage/Shared/VoiceCombat.luau').read_text()
 pre=r"""
local lockController,initial,o,npc,enemy=fixture()
local p=o.localPlayer;local workspace=o.world;workspace.CurrentCamera=initial.camera
local clock=10;local os={clock=function()return clock end};function workspace:GetServerTimeNow()return clock end
local Config={VoiceCombat=VoiceCombat};local data={level=1,amplifierEquipped=false}
local clientDestroyed=false;local windowFocused=true;local blockedState=false
local mic={ready=true,power=1,cancels=0,Cancel=function(self)self.cancels+=1 end}
local sustainedControl={armed=true,Cancel=function(self)self.cancelled=true end,SetArmed=function(self,value)self.armed=value end}
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
local input;local function connectClient(_,fn)input=fn end
local function toggleVoice()end;local function beginCapture()end;local function dodge()end;local function toggle()end;local function toggleTab()end;local function setSprint()end;local function requestTalk()end
local lockMarker={};local lockButton={};local gameplayVisible=true;local touch=false
local UDim2={fromOffset=function(x,y)return {X=x,Y=y}end}
"""
 checks=r"""
local ray,hit=aimRay();check(ray==rawRay and hit==freeHit,'OFF fallback changed')
input({KeyCode='R'},true);check(lockController.target==nil,'Processed input acquired')
UIS.typing=true;input({KeyCode='R'},false);check(lockController.target==nil,'Typing input acquired');UIS.typing=false
GuiService.MenuIsOpen=true;input({KeyCode='R3'},false);check(lockController.target==nil,'Platform menu acquired');GuiService.MenuIsOpen=false
input({KeyCode='R'},false);check(lockController.target.model==npc and sustainedControl.armed and #commands==0,'R failed or fired/armed')
ray,hit=aimRay();check(hit.Instance==npc and hit.Position==npc.HumanoidRootPart.Position and ray.Origin.X==0,'Locked aim differs from selected target')
updateMarker();check(lockMarker.Visible and lockButton.Text=='UNLOCK' and lockMarker.Position.X==330,'Marker differs from submitted target')
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
print('PASS '..n..' actual Client lock-on integration assertions; mocked input/LOS/GUI')
"""
 return base+'local LockOn=(function()\n'+lock_on.source+'\nend)()\nlocal VoiceCombat=(function()\n'+rules+'\nend)()\n'+fixture+pre+cancel+context+receiver+inp+'\nlocal function updateMarker()\n'+marker+'\nend\n'+checks

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
  mutations=[('local locked,target=lockController:Resolve(lockContext(power))','local locked,target=nil,nil','Locked aim differs'),('now<nextLockAcquire','false','Acquire debounce'),('k==Enum.KeyCode.R or k==Enum.KeyCode.ButtonR3','k==Enum.KeyCode.R','R3 did not unlock'),('if lockController then lockController:Clear() end\n if sustainedControl then sustainedControl:Cancel()','if sustainedControl then sustainedControl:Cancel()','Cancel retained'),('local lockedPoint=lockController:Resolve(lockContext())','local lockedPoint=nil','Marker differs')]
  for old,new,expected in mutations:
   assert old in s
   r=run(s.replace(old,new,1));assert r.returncode and expected in r.stderr,(old,r.stdout,r.stderr)
  print('PASS 6 Client wiring/marker negative controls')
