"""Run the cosmetic controller with mocked engine objects and events."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
source = (ROOT / 'src/StarterPlayer/StarterPlayerScripts/PassCosmetics.client.luau').read_text(encoding='utf-8')
setup = r'''
local function signal()
 local callback
 return {Connect=function(_,fn)callback=fn;return {Disconnect=function()callback=nil end}end,
  Fire=function(_,...)if callback then callback(...)end end}
end
local V={}
V.__sub=function(a,b)return setmetatable({Magnitude=math.abs(a.X-b.X)},V)end
local Vector3={new=function(x,y,z)return setmetatable({X=x,Y=y,Z=z},V)end}
local function typeof(v)return getmetatable(v)==V and 'Vector3' or type(v)end
local function n(...)return {...}end
local Color3={fromRGB=n};local ColorSequence={new=n};local NumberSequence={new=n};local NumberSequenceKeypoint={new=n}
local UDim2={fromOffset=n,fromScale=n};local UDim={new=n};local Enum={Font={GothamBold='bold'},HighlightDepthMode={Occluded='occluded'}}
local nodes={}
local Instance={new=function(kind)
 local obj={ClassName=kind,Enabled=true}
 function obj:Destroy()self.destroyed=true;self.Parent=nil end
 table.insert(nodes,obj);return obj
end}
local function alive(name)
 for i=#nodes,1,-1 do local obj=nodes[i];if obj.Name==name and not obj.destroyed then return obj end end
end
local settings={EncorePass=false,AfterimagePass=false,CityGlowPass=false}
local root={Position=Vector3.new(-12,0,0)};local health={Health=100};local head={}
local character={FindFirstChild=function(_,key)return key=='Head' and head or root end,FindFirstChildOfClass=function()return health end}
local owner={UserId=1,Character=character,GetAttribute=function(_,name)return settings[name] end}
local viewerSettings={}
local gui={}
local viewer={UserId=2,Character=character,GetAttribute=function(_,name)
 if name=='CityGlowPass' then return settings.CityGlowPass end
 return viewerSettings[name]
end,WaitForChild=function()return gui end}
local players={LocalPlayer=viewer,PlayerRemoving=signal(),GetPlayers=function()return {owner,viewer}end,
 GetPlayerByUserId=function(_,id)if id==1 then return owner elseif id==2 then return viewer end end}
local run={Heartbeat=signal(),IsStudio=function()return false end}
local effect={OnClientEvent=signal()}
local remotes={WaitForChild=function()return effect end}
local shared={WaitForChild=function(_,key)return key end}
local storage={WaitForChild=function(_,key)return key=='Shared' and shared or remotes end}
local guiService={ReducedMotionEnabled=false}
local services={Players=players,RunService=run,ReplicatedStorage=storage,GuiService=guiService}
local game={PlaceId=1,GameId=1,GetService=function(_,name)return services[name]end}
local Config={CompactCity=true,InArena=function(v)return v.X>=0 end}
local Catalog={Get=function()return {id=1}end}
local function require(key)return key=='Config' and Config or Catalog end
local script={Destroying=signal()}
local elapsed=0;local os={clock=function()return elapsed end}
do
'''
checks = r'''
end
local count=0
local function check(v,message)assert(v,message);count+=1 end
local function step(seconds)elapsed+=seconds;run.Heartbeat:Fire()end
local function dodge(x,id)effect.OnClientEvent:Fire('Dodge',Vector3.new(x,0,0),id or 1)end
step(1);dodge(-12);check(not alive('EncorePassTitle') and not alive('AfterimagePassTrail'),'Unowned cosmetics enabled')
settings.EncorePass=true;settings.AfterimagePass=true;step(1)
local plate=alive('EncorePassTitle');check(plate and plate.Adornee==head and not plate.AlwaysOnTop,'Title missing or visible through cover')
dodge(-12,2);check(not alive('AfterimagePassTrail'),'Non-owner move got a trail')
dodge(2);check(not alive('AfterimagePassTrail'),'PvP origin got a trail')
guiService.ReducedMotionEnabled=true;dodge(-12)
check(not alive('AfterimagePassTrail') and alive('EncorePassTitle'),'Reduced motion did not suppress only the trail')
guiService.ReducedMotionEnabled=false
dodge(-12);local trail=alive('AfterimagePassTrail');check(trail and trail.Parent==root,'Owned safe dodge missed trail')
step(.30);check(trail.Parent and not trail.Enabled,'Trail kept emitting after the move')
step(.20);check(not alive('AfterimagePassTrail') and not alive('AfterimageBottom'),'Trail or attachments leaked after expiry')
dodge(-12);root.Position=Vector3.new(1,0,0);step(.01)
check(not alive('AfterimagePassTrail') and not alive('EncorePassTitle'),'Cosmetic remained into combat')
root.Position=Vector3.new(-12,0,0);step(1);dodge(-12);settings.AfterimagePass=false;step(.01)
check(not alive('AfterimagePassTrail'),'Lost entitlement retained trail')
health.Health=0;step(.01);check(not alive('EncorePassTitle'),'Dead player kept title')
health.Health=100;settings.AfterimagePass=true;step(1);dodge(-12)
check(not alive('CityGlowPassOutline'),'Unowned glow appeared')
settings.CityGlowPass=true;step(.01)
local glow=alive('CityGlowPassOutline')
check(glow and glow.Adornee==character and glow.DepthMode=='occluded' and glow.FillTransparency==1,'Owned glow is missing or fills/shows through walls')
step(.01);check(alive('CityGlowPassOutline')==glow,'Glow duplicated while standing still')
root.Position=Vector3.new(1,0,0);step(.01)
check(not alive('CityGlowPassOutline'),'Glow remained inside PvP')
root.Position=Vector3.new(-12,0,0);step(.01)
check(alive('CityGlowPassOutline')~=nil,'Glow did not return in safety')
settings.CityGlowPass=false;step(.01)
check(not alive('CityGlowPassOutline'),'Glow remained after entitlement cleared')
settings.HarborBadgePass=true;settings.SprintRibbonPass=true;settings.Sprinting=true;step(.01)
check(not alive('HarborBadgePassIcon') and not alive('SprintRibbonPassTrail'),'Other player ownership created personal cosmetics')
viewerSettings.HarborBadgePass=true;step(.01)
local badge=alive('HarborBadgePassIcon')
check(badge and badge.Adornee==head and badge.Parent==gui and not badge.AlwaysOnTop,'Owned personal Harbor Badge missing or visible through cover')
check(not alive('SprintRibbonPassTrail'),'Harbor Badge ownership granted Sprint Ribbon')
viewerSettings.SprintRibbonPass=true;step(.01)
check(not alive('SprintRibbonPassTrail'),'Owned ribbon emitted without a sprint')
viewerSettings.Sprinting=true;step(.01)
local ribbon=alive('SprintRibbonPassTrail')
check(ribbon and ribbon.Parent==root and ribbon.Attachment0.Parent==root and ribbon.Attachment1.Parent==root,'Owned safe sprint missed its ribbon')
step(.01)
check(alive('SprintRibbonPassTrail')==ribbon and alive('HarborBadgePassIcon')==badge,'Cosmetics duplicated during steady state')
guiService.ReducedMotionEnabled=true;step(.01)
check(not alive('SprintRibbonPassTrail') and not alive('SprintRibbonBottom') and alive('HarborBadgePassIcon')==badge,'Reduced motion did not clean up only the ribbon')
guiService.ReducedMotionEnabled=false;step(.01)
root.Position=Vector3.new(1,0,0);step(.01)
check(not alive('SprintRibbonPassTrail') and not alive('HarborBadgePassIcon'),'Personal cosmetics entered PvP')
root.Position=Vector3.new(-12,0,0);step(.01)
check(alive('SprintRibbonPassTrail') and alive('HarborBadgePassIcon'),'Owned cosmetics did not return in safety')
viewerSettings.Sprinting=false;step(.01)
check(not alive('SprintRibbonPassTrail') and not alive('SprintRibbonTop'),'Sprint end left ribbon or attachment')
viewerSettings.HarborBadgePass=false;step(.01)
check(not alive('HarborBadgePassIcon'),'Harbor Badge remained after entitlement cleared')
viewerSettings.Sprinting=true;step(.01)
viewerSettings.SprintRibbonPass=false;step(.01)
check(not alive('SprintRibbonPassTrail'),'Sprint Ribbon remained after entitlement cleared')
viewerSettings.HarborBadgePass=true;viewerSettings.SprintRibbonPass=true;step(.01)
health.Health=0;step(.01)
check(not alive('HarborBadgePassIcon') and not alive('SprintRibbonPassTrail'),'Dead avatar retained personal effects')
health.Health=100;step(.01)
local oldBadge,oldRibbon=alive('HarborBadgePassIcon'),alive('SprintRibbonPassTrail')
head={};root={Position=Vector3.new(-12,0,0)};step(.01)
check(oldBadge.destroyed and oldRibbon.destroyed and alive('HarborBadgePassIcon').Adornee==head and alive('SprintRibbonPassTrail').Parent==root,'Replacement avatar did not cleanly replace effects')
settings.CityGlowPass=true;step(.01);script.Destroying:Fire()
check(not alive('HarborBadgePassIcon') and not alive('SprintRibbonPassTrail') and not alive('SprintRibbonBottom'),'Destroy left personal cosmetics')
check(not alive('CityGlowPassOutline'),'Destroy left an outline')
check(not alive('AfterimagePassTrail') and not alive('EncorePassTitle'),'Destroy did not clean effects')
step(1);dodge(-12);check(not alive('EncorePassTitle') and not alive('AfterimagePassTrail'),'Destroy left callbacks')
print('PASS '..count..' actual pass cosmetic checks; mocked engine only')
'''

def run(code, expected=None):
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / 'PassCosmetics.luau'
        fixture.write_text(code, encoding='utf-8')
        result = subprocess.run(['luau', str(fixture)], text=True, capture_output=True)
    if expected:
        assert result.returncode and expected in result.stderr, result.stderr
        print('PASS negative control:', expected)
    else:
        assert not result.returncode, result.stderr
        print(result.stdout.strip())

run(setup + source + checks)
for key, object_name in (('HarborBadge', 'HarborBadgePassIcon'), ('SprintRibbon', 'SprintRibbonPassTrail')):
    single_pass = setup.replace('local Catalog={Get=function()return {id=1}end}',
                                f"local Catalog={{Get=function(key) return {{id=key=='{key}' and 1 or 0}} end}}")
    configured_check = f"""
end
viewerSettings['{key}Pass']=true
viewerSettings.Sprinting=true
run.Heartbeat:Fire()
assert(alive('{object_name}'),'An independently configured pass did not start its controller')
print('PASS independently configured {key}')
"""
    run(single_pass + source + configured_check)
if '--negative-controls' in sys.argv:
    for old, new, expected in (
        ('localPlayer:GetAttribute("HarborBadgePass")==true', 'true', 'Other player ownership created personal cosmetics'),
        ('localPlayer:GetAttribute("SprintRibbonPass")==true', 'true', 'Sprint Ribbon remained after entitlement cleared'),
        ('localPlayer:GetAttribute("Sprinting")==true', 'true', 'Owned ribbon emitted without a sprint'),
        ('viewer and not GuiService.ReducedMotionEnabled', 'viewer', 'Reduced motion did not clean up only the ribbon'),
        ('updateGlow(nil);updatePersonalExtras(nil)', 'updateGlow(nil)', 'Destroy left personal cosmetics'),
    ):
        assert source.count(old) == 1
        run(setup + source.replace(old, new) + checks, expected)
