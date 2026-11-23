"""Actual label-selection function with mocked residents/camera; no streaming evidence."""
from pathlib import Path
import subprocess
import sys
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local function refreshResidentLabels(');b=s.index('local function requestTalk()',a)
t=s.index('local function liveTalkHumanoid(')
presentation=s[t:s.index('\nownClient(',t)]
setup='''
local academy={}
local InteractionRules={CanReachNpc=function()return true end}
local pos=setmetatable({},{__sub=function()return {Magnitude=5}end})
local root={Position=pos,Parent={}}
local camera={WorldToViewportPoint=function()return {},true end}
local writes=0
local function billboard(props)
 local enabled=true
 return setmetatable(props,{
  __index=function(_,key)if key=="Enabled" then return enabled end end,
  __newindex=function(self,key,value)
   if key=="Enabled" then writes+=1;enabled=value else rawset(self,key,value) end
  end,
 })
end
local nameplate=billboard({});local words={Visible=true}
local speech=billboard({FindFirstChildOfClass=function()return words end})
local head={Position=pos,FindFirstChild=function(_,name)return name=='Nameplate' and nameplate or speech end}
local bot={root={Position=pos},head=head,h={Health=100,MaxHealth=100},active=true}
function bot:FindFirstChild(name)return name=='Head' and self.head or self.root end
function bot:FindFirstChildOfClass()return self.h end
function bot:GetAttribute()return self.active end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
check(refreshResidentLabels(root,camera,{bot})==bot and nameplate.Enabled and speech.Enabled,'Valid resident labels missing')
local before=writes
for _=1,30 do refreshResidentLabels(root,camera,{bot}) end
check(writes==before and nameplate.Enabled and speech.Enabled,'Steady selection rewrote resident billboards')
academy.talkNameplate=nameplate;nameplate.Enabled=false;before=writes
refreshResidentLabels(root,camera,{bot})
check(writes==before and not nameplate.Enabled,'Selection re-enabled compact Talk identity')
bot.h.Health=80;refreshResidentLabels(root,camera,{bot})
check(nameplate.Enabled,'Compact Talk suppression hid newly hurt resident HP')
bot.h.Health=100;academy.talkNameplate=nil
local saved=bot.root;bot.root=nil
check(refreshResidentLabels(root,camera,{bot})==nil,'Incomplete resident remained target')
check(not nameplate.Enabled and not speech.Enabled,'Missing root retained stale labels')
bot.root=saved
check(refreshResidentLabels(root,camera,{bot})==bot and nameplate.Enabled,'Restored resident failed to recover')
bot.active=false;refreshResidentLabels(root,camera,{bot})
check(not nameplate.Enabled and not speech.Enabled,'Inactive resident retained labels')
bot.active=true;refreshResidentLabels(root,camera,{bot});refreshResidentLabels(root,nil,{bot})
check(not nameplate.Enabled and not speech.Enabled,'Missing camera retained labels')
print('PASS '..checks..' actual resident label checks with mocked objects')
'''
talk_checks='''
local identity={Text='Rookie · Lv 1'}
bot.Parent={}
bot.GetAttribute=function(_,name)
 if name=='TrainingTier' then return bot.tier end
 return bot.active
end
function nameplate:FindFirstChild(name) if name=='Identity' then return identity end end
function nameplate:IsDescendantOf(target) return target==bot end
local talk={Visible=true,Size={X={Offset=120}},TextSize=14}
bot.tier='rookie';nameplate.Enabled=true
academy.presentTalk(talk,bot,false,true)
check(talk.Text=='TALK [T]\\nRookie · Lv 1' and talk.TextSize==12 and not nameplate.Enabled,'Compact trainer identity missing or doubled')
bot.h.Health=40
academy.presentTalk(talk,bot,false,true)
check(nameplate.Enabled and talk.Text=='TALK [T]\\nRookie · Lv 1','Damage did not restore world HP presentation')
bot.h.Health=100
academy.presentTalk(talk,bot,false,true)
academy.presentTalk(talk,bot,false,false)
check(nameplate.Enabled and talk.Text=='TALK [T]' and talk.TextSize==14,'Wide layout did not restore the nameplate')
academy.presentTalk(talk,bot,true,true)
check(talk.Text=='TALK\\nRookie · Lv 1' and not nameplate.Enabled,'Touch caption retained a keyboard hint')
talk.Size.X.Offset=44
academy.presentTalk(talk,bot,true,true)
check(talk.Text=='TALK' and nameplate.Enabled,'Narrow target lost identity or control')
talk.Size.X.Offset=120;academy.presentTalk(talk,bot,false,true);talk.Visible=false
academy.presentTalk(talk,bot,false,true)
check(nameplate.Enabled and talk.Text=='TALK [T]','A hidden Talk action retained the combined identity')
talk.Visible=true;academy.presentTalk(talk,bot,false,true)
academy.presentTalk(talk,nil,false,true)
check(not nameplate.Enabled and talk.Text=='TALK [T]','Cleared target re-enabled an out-of-range plate')
academy.presentTalk(talk,bot,false,true);bot.active=false
academy.presentTalk(talk,bot,false,true)
check(not nameplate.Enabled and talk.Text=='TALK [T]','Inactive cached fighter regained its plate')
bot.active=true;bot.h.Health=100;academy.presentTalk(talk,bot,false,true);bot.h.Health=0
academy.presentTalk(talk,bot,false,true)
check(not nameplate.Enabled and talk.Text=='TALK [T]','Dead cached fighter regained its plate')
bot.h.Health=100
bot.tier=nil;nameplate.Enabled=true
academy.presentTalk(talk,bot,false,true)
check(nameplate.Enabled and talk.Text=='TALK [T]','Ordinary residents lost their world plate')
print('PASS '..checks..' resident selection and Talk presentation checks with mocked objects')
'''

selection=s[a:b]

def run(presenter,selector=selection):
 with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False,encoding='utf-8') as f:
  path=Path(f.name);f.write(setup+selector+presenter+checks+talk_checks)
 try: return subprocess.run(['luau',str(path)],cwd=root,text=True,capture_output=True)
 finally: path.unlink()

result=run(presentation)
assert not result.returncode,result.stderr
print(result.stdout,end='')
if '--negative-controls' in sys.argv:
 for before,after,error in (
  ('if nameplate and nameplate.Enabled then table.insert(enabled,nameplate) end',
   'if nameplate then nameplate.Enabled=false end','Steady selection rewrote resident billboards'),
  ('nearestPlate=(nameplate~=academy.talkNameplate or h.Health<h.MaxHealth) and nameplate or nil',
   'nearestPlate=nameplate','Selection re-enabled compact Talk identity'),
 ):
  assert selection.count(before)==1,before
  result=run(presentation,selection.replace(before,after))
  assert result.returncode and error in result.stderr,result.stderr
  print('PASS negative control:',error)
 for before,after,error in (
  ('caption..="\\n"..identity.Text','caption=caption','Compact trainer identity missing or doubled'),
  ('if humanoid.Health>=humanoid.MaxHealth then','if true then','Damage did not restore world HP presentation'),
  ('and width>=84','and true','Narrow target lost identity or control'),
  ('and humanoid and previous:IsDescendantOf(target)','and true','Cleared target re-enabled an out-of-range plate'),
  ('and humanoid.Health>0','and true','Dead cached fighter regained its plate'),
 ):
  assert presentation.count(before)==1,before
  result=run(presentation.replace(before,after))
  assert result.returncode and error in result.stderr,result.stderr
  print('PASS negative control:',error)
