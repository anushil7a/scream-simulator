"""Actual label-selection function with mocked residents/camera; no streaming evidence."""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('local function refreshResidentLabels(');b=s.index('local function requestTalk()',a)
setup='''
local InteractionRules={CanReachNpc=function()return true end}
local pos=setmetatable({},{__sub=function()return {Magnitude=5}end})
local root={Position=pos,Parent={}}
local camera={WorldToViewportPoint=function()return {},true end}
local nameplate={Enabled=true};local words={Visible=true}
local speech={Enabled=true,FindFirstChildOfClass=function()return words end}
local head={Position=pos,FindFirstChild=function(_,name)return name=='Nameplate' and nameplate or speech end}
local bot={root={Position=pos},head=head,h={Health=100,MaxHealth=100},active=true}
function bot:FindFirstChild(name)return name=='Head' and self.head or self.root end
function bot:FindFirstChildOfClass()return self.h end
function bot:GetAttribute()return self.active end
'''
checks='''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
check(refreshResidentLabels(root,camera,{bot})==bot and nameplate.Enabled and speech.Enabled,'Valid resident labels missing')
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
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
 path=Path(f.name);f.write(setup+s[a:b]+checks)
try: subprocess.run(['/opt/homebrew/bin/luau',str(path)],cwd=root,check=True)
finally: path.unlink()
