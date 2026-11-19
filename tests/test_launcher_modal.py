"""Actual launcher visibility/transition bodies under mocked GUI; not native rendering/input QA."""
from pathlib import Path
import re,subprocess,tempfile,argparse
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
def assemble(s, state_override=None):
 helper=s[s.index('function academy.canShowTestLauncher()'):s.index('\n-- Flight controls exist only',s.index('function academy.canShowTestLauncher()'))]
 close=s[s.index('local function closeMenu()'):s.index('\nbutton(modal,"Close"')]
 toggle=s[s.index('local function toggleTab('):s.index('\nlocal shop=button(top,')]
 state_start=s.index('connectClient(remotes.State.OnClientEvent')
 state_prefix=s[state_start:s.index(' local q=Config.GetQuest(data.activeQuest)',state_start)]
 state=state_prefix.rstrip().splitlines()[-1]
 frame=next(line for line in s[s.index(' saveNotice.Visible='):].splitlines() if 'academy.refreshTestLauncher()' in line)
 conversation_open=s[s.index('showConversation=function(info)'):].splitlines()[1]
 conversation_finish=s[s.index(' conversationList.CanvasPosition=Vector2.zero;conversationPanel.Visible=true'):].splitlines()[:2]
 conversation_finish='\n'.join(conversation_finish)
 activated=re.search(r'local testButton=button.*?function\(\)(.*?)end\);testButton',s).group(1)
 if state_override is not None: state=state_override
 return r'''
local n=0;local function check(v,m)assert(v,m);n+=1 end
local clientDestroyed=false
local academy={};local data={devAccess=true};local GuiService={MenuIsOpen=false}
local modal={Visible=false};local conversationPanel={Visible=false};local testButton={Visible=false}
local miniMapButton={Visible=true};local devPanel={Visible=false};local selected='Shop';local lockController
local renderedMenuKey='old';local renderRevision=0;local clears=0;local renders=0
local Vector2={zero={X=0,Y=0}};local conversationList={};local function cancelCapture()end
local function clearShop()clears+=1 end
local function closeConversation()conversationPanel.Visible=false end
local function render()renders+=1;check(not testButton.Visible,'Launcher leaked before modal render')end
local action={FireServer=function(_,verb)check(not testButton.Visible,'Launcher leaked during ShopRefresh')end}
''' + helper+'\n'+close+'\n'+toggle+'''
local function activateLauncher()
'''+activated+'''
end
local function beginConversation()
'''+conversation_open+'''
end
local function finishConversation()
'''+conversation_finish+'''
end
local function stateUpdate(access)data={devAccess=access}
'''+state+'''
end
local function frameUpdate()
'''+frame+'''
end
for _,device in ipairs({'desktop','touch portrait','touch landscape','controller'}) do
 for cycle=1,25 do
  GuiService.MenuIsOpen=false;conversationPanel.Visible=false;modal.Visible=false;devPanel.Visible=false
  stateUpdate(true);check(testButton.Visible,'Authorized launcher hidden at rest')
  toggleTab('Shop');check(modal.Visible and not testButton.Visible,'Shop opening exposed launcher')
  activateLauncher();check(modal.Visible and not devPanel.Visible,'Queued obscured launcher press closed Shop')
  for i=1,20 do
   stateUpdate(true);check(not testButton.Visible,'State update flashes launcher in Shop')
   frameUpdate();check(not testButton.Visible,'Frame disagrees with State in Shop')
  end
  toggleTab('Style');check(modal.Visible and not testButton.Visible,'Tab transition exposed launcher')
  stateUpdate(true);check(not testButton.Visible,'Style state flashes launcher')
  toggleTab('Shop');check(not testButton.Visible,'Return to Shop exposed launcher')
  closeMenu();check(testButton.Visible and not modal.Visible,'Close did not restore launcher synchronously')
  toggleTab('Shop');toggleTab('Shop');check(testButton.Visible and not modal.Visible,'Repeated toggle did not close')
  activateLauncher();check(devPanel.Visible,'Normal launcher did not open Test Tools')
  stateUpdate(true);check(testButton.Visible and devPanel.Visible,'Existing Test Tools panel/toggle broken')
  activateLauncher();check(not devPanel.Visible,'Normal launcher did not close Test Tools')
  activateLauncher()
  toggleTab('Shop');check(not devPanel.Visible and not testButton.Visible,'Shop did not dismiss tools without flashing')
  closeMenu()
  toggleTab('Shop');beginConversation();check(not testButton.Visible and not modal.Visible,'Shop to conversation exposed launcher')
  stateUpdate(true);frameUpdate();check(not testButton.Visible,'State/frame exposed launcher during conversation construction')
  activateLauncher();check(not devPanel.Visible,'Queued launcher opened during conversation construction')
  finishConversation();check(conversationPanel.Visible and not testButton.Visible,'Conversation completion exposed launcher')
  academy.testLauncherBlocked=false;conversationPanel.Visible=false;frameUpdate()
  GuiService.MenuIsOpen=true;stateUpdate(true);check(not testButton.Visible,'Core menu exposed tools')
  GuiService.MenuIsOpen=false;conversationPanel.Visible=true;stateUpdate(true);check(not testButton.Visible,'Conversation exposed tools')
  conversationPanel.Visible=false
  for _,v in ipairs({false,1,'true'})do stateUpdate(v);check(not testButton.Visible,'Nonboolean authorization exposed tools')end
  stateUpdate(nil);check(not testButton.Visible,'Missing access exposed tools')
  stateUpdate(true);check(testButton.Visible,'Launcher failed to recover')
  check(miniMapButton.Visible,'Minimap changed')
 end
end
conversationPanel=nil;frameUpdate();check(testButton.Visible,'Initialization without conversation panel fails')
clientDestroyed=true;frameUpdate();check(not testButton.Visible,'Retired client resurrected launcher')
print('PASS '..n..' actual launcher visibility/transition checks; mocked events, not physical devices')
'''
def run(s,negative=False,state_override=None):
 code=assemble(s,state_override)
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=ROOT/'tests',delete=False)as f:f.write(code);p=Path(f.name)
 try:
  r=subprocess.run(['luau',str(p)],capture_output=True,text=True)
  if negative:assert r.returncode!=0,'Negative control unexpectedly passed';print('PASS negative control:',(r.stdout+r.stderr).splitlines()[0])
  else:assert r.returncode==0,r.stdout+r.stderr;print(r.stdout,end='')
 finally:p.unlink()
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('--negative-controls',action='store_true');parser.add_argument('--baseline-client');args=parser.parse_args();s=SOURCE.read_text();run(s)
 if args.negative_controls:
  run(s.replace(' and not modal.Visible and not (conversationPanel',' and not (conversationPanel',1),True)
  run(s.replace(' if academy.refreshTestLauncher then academy.refreshTestLauncher() end','',1),True)
  toggle_start=s.index('local function toggleTab(')
  launcher=' if academy.refreshTestLauncher then academy.refreshTestLauncher() end'
  cut=s.index(launcher,s.index('modal.Visible=true',toggle_start))
  assert cut<s.index('local shop=button(top,',toggle_start)
  run(s[:cut]+s[cut+len(launcher):],True)

  run(s.replace('if not academy.canShowTestLauncher() then return end;','',1),True)
  conversation_start=s.index('showConversation=function(info)')
  before, after=s[:conversation_start],s[conversation_start:]
  assert 'academy.testLauncherBlocked=true;' in after and 'academy.refreshTestLauncher();cancelCapture();' in after
  run(before+after.replace('academy.testLauncherBlocked=true;','',1).replace('academy.refreshTestLauncher();cancelCapture();','cancelCapture();',1),True)
  if args.baseline_client:
   baseline=Path(args.baseline_client).read_text()
   old=next(line for line in baseline.splitlines() if line.strip()=='testButton.Visible=data.devAccess==true')
   run(s,True,state_override=old)
