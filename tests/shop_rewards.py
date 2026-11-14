"""Actual server reward/color helpers with synthetic time and entitlement decisions."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'src/ServerScriptService/Bootstrap.server.luau').read_text()
coins=s[s.index('local function coins('):s.index('local function syncHealth(')]
xp=s[s.index('local function xp('):s.index('local function questProgress(')]
color=s[s.index('local function beamColor('):s.index('local function state(')]
source='''
local Ledger=require('../src/ReplicatedStorage/Shared/BoostLedger')
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
local now=100;local entitlement=false
local p={};local sessions={[p]={data={level=1,xp=0,coins=0,aura='Gold',customColor='FA4FFF',useCustomColor=true}}}
local saved={ends={xp=200,coins=150}}
local Commerce={Multiplier=function(_,kind)return Ledger.Multiplier(saved,kind,now)end}
local Config={MaxLevel=100,XPToNext=function()return 1000 end,Sounds={}}
local Entitlements={HasSpectrum=function()return entitlement end}
local Color3={fromHex=function(hex)return 'color:'..hex end}
local function syncHealth()end;local function state()end
'''+coins+xp+color+'''
xp(p,20);coins(p,5)
assert(sessions[p].data.xp==40 and sessions[p].data.coins==10,'Server did not apply 2x')
now=150;xp(p,20);coins(p,5)
assert(sessions[p].data.xp==80 and sessions[p].data.coins==15,'Types did not expire independently')
now=200;xp(p,20);coins(p,5)
assert(sessions[p].data.xp==100 and sessions[p].data.coins==20,'Expired boost still paid')
assert(beamColor(p,sessions[p])=='Gold','Saved paid color bypassed ownership')
entitlement=true;assert(beamColor(p,sessions[p])=='color:FA4FFF','Owned custom color missing')
sessions[p].data.useCustomColor=false;assert(beamColor(p,sessions[p])=='Gold','Free color could not be re-equipped')
assert(Catalog.Hex('#ab12fe')=='AB12FE' and not Catalog.Hex('xyz') and not Catalog.Hex({}),'Hex validation failed')
print('PASS actual boosted reward helpers, expiry boundaries and color entitlement fallback')
'''
client=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
assert client.index('beamFrame+=dt')<client.index('elapsed+=dt;if elapsed<.15'), 'Beam animation was placed behind slow HUD throttle'
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(source)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
