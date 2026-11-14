"""Actual health HUD function with mocked replicated Humanoid/UI values.
No Roblox replication timing or rendered-layout evidence.
"""
from pathlib import Path
import subprocess
import tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
start=source.index('local displayedHealth,displayedMaximum')
end=source.index('local xpText=',start)
setup='''
local p={};local data={health=100,maxHealth=100};local health={};local hf={}
local UDim2={fromScale=function(x,y)return {x=x,y=y}end}
'''
checks='''
local checks=0
local function check(v,msg)assert(v,msg);checks+=1 end
refreshHealth();check(health.Text=='100/100' and hf.Size.x==1,'Initial fallback failed')
local h={Health=70,MaxHealth=100};p.Character={FindFirstChildOfClass=function()return h end}
refreshHealth();check(health.Text=='70/100' and hf.Size.x==.7,'Replicated damage was not reflected')
local size=hf.Size;refreshHealth();check(hf.Size==size,'Unchanged health rewrote UI')
h.Health=0;data.health=100;refreshHealth();check(health.Text=='0/100' and hf.Size.x==0,'Dead character used full-health snapshot')
p.Character=nil;refreshHealth();check(health.Text=='0/100','Between-character gap showed full health')
h={Health=135,MaxHealth=135};p.Character={FindFirstChildOfClass=function()return h end}
refreshHealth();check(health.Text=='135/135' and hf.Size.x==1,'Respawn/level health was stale')
h.Health=12.2;refreshHealth();check(health.Text=='13/135' and hf.Size.x==12.2/135,'Fractional health display wrong')
h.Health=200;refreshHealth();check(hf.Size.x==1,'Health fill exceeded its track')
h.MaxHealth=0;h.Health=0;refreshHealth();check(hf.Size.x==0,'Zero max health divided by zero')
print('PASS '..checks..' actual HUD health checks with mocked replication/UI')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.hud_',dir=root/'tests',delete=False) as file:
    path=Path(file.name);file.write(setup+source[start:end]+checks)
try:
    subprocess.run(['luau',str(path)],cwd=root,check=True)
finally:
    path.unlink()
