"""Actual client dialogue lifetime with mocked characters/UI/time."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=source.index('local function refreshConversation()')
b=source.index('button(conversationPanel,"Close"',a)
setup='''
local now=0;local os={clock=function()return now end}
local conversationPanel={Visible=true};local modal={Visible=false}
local conversationNPC,conversationUntil,p
local closes=0
local function closeConversation() closes+=1;conversationPanel.Visible=false end
local mt={__sub=function(a,b)return {Magnitude=math.abs(a.x-b.x)}end}
local function character(x)
 local c={Parent=true,root={Position=setmetatable({x=x},mt)},humanoid={Health=100}}
 function c:GetAttribute() return self.active end
 function c:FindFirstChild() return self.root end
 function c:FindFirstChildOfClass() return self.humanoid end
 return c
end
'''
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
local function reset()
 now=0;closes=0;conversationUntil=20;conversationPanel.Visible=true;modal.Visible=false
 p={Character=character(0)};conversationNPC=character(10)
end
reset();refreshConversation();check(closes==0,'Valid conversation closed')
for _,case in ipairs({'player knocked','npc knocked','player dead','npc dead','npc recovering','player missing','npc removed','player root','npc root','player humanoid','npc humanoid','range','expired','menu'}) do
 reset()
 if case=='player knocked' then p.Character.humanoid.PlatformStand=true
 elseif case=='npc knocked' then conversationNPC.humanoid.PlatformStand=true
 elseif case=='player dead' then p.Character.humanoid.Health=0
 elseif case=='npc recovering' then conversationNPC.active=false
 elseif case=='npc dead' then conversationNPC.humanoid.Health=0
 elseif case=='player missing' then p.Character=nil
 elseif case=='npc removed' then conversationNPC.Parent=nil
 elseif case=='player root' then p.Character.root=nil
 elseif case=='npc root' then conversationNPC.root=nil
 elseif case=='player humanoid' then p.Character.humanoid=nil
 elseif case=='npc humanoid' then conversationNPC.humanoid=nil
 elseif case=='range' then conversationNPC.root.Position.x=19
 elseif case=='expired' then now=20
 else modal.Visible=true end
 refreshConversation();check(closes==1,'Stale dialogue survived '..case)
 refreshConversation();check(closes==1,'Closed dialogue repeatedly ended '..case)
end
print('PASS '..checks..' actual dialogue lifecycle checks with mocked UI/characters')
'''
request_start=source.index('local function requestTalk()')
request_end=source.index('local talkButton=button(',request_start)
request_setup='''
local windowFocused=true
local GuiService={MenuIsOpen=false}
local UIS={GetFocusedTextBox=function()return nil end}
local devPanel={Visible=false}
local sent={}
local action={FireServer=function(_,verb,arg)table.insert(sent,{verb,arg})end}
local stopped=0
local function cancelCapture() stopped+=1 end
local visible=true
local InteractionRules={CanReachNpc=function(_,_,range)return visible and range==13 end}
local talkTarget={Name='Mar',Parent=true,GetAttribute=function(_,name)
 if name=='NpcId' then return 'mar' end
end}
'''
request_checks='''
local n=0
local function check(v,msg)assert(v,msg);n+=1 end
conversationPanel.Visible=false;modal.Visible=false
requestTalk()
check(#sent==1 and sent[1][1]=='Talk' and sent[1][2]=='mar','Talk did not request the reachable resident')
check(stopped==0,'Unconfirmed Talk already cancelled active capture')
visible=false;requestTalk()
check(#sent==1 and stopped==0,'Blocked resident sent a request or cancelled capture')
visible=true;modal.Visible=true;requestTalk()
check(#sent==1 and stopped==0,'Open menu sent a request or cancelled capture')
print('PASS '..n..' actual Talk request checks with mocked availability')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source[a:b]+checks+request_setup+source[request_start:request_end]+request_checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
