"""Exercise actual entitlement source with mocked Roblox services, never purchases."""
from pathlib import Path
import subprocess
import tempfile
source = Path('src/ServerScriptService/Entitlements.luau').read_text()
setup = '''
local studio=false
local handlers={}
local function event(name) return {Connect=function(_,fn) handlers[name]=fn end} end
local config={MovementPassId=0,InArena=function(position) return position=="arena" end}
local services={RunService={IsStudio=function() return studio end},Players={PlayerRemoving=event("removed")},MarketplaceService={PromptGamePassPurchaseFinished=event("purchase"),UserOwnsGamePassAsync=function() error("No purchase/ownership calls permitted") end}}
local game={ReplicatedStorage={Shared={Config={}}},GetService=function(_,name) return services[name] end}
local function require(_) return config end
local Entitlements=(function()
'''
checks = '''
end)()
local checks=0
local function check(ok) assert(ok);checks+=1 end
local player={UserId=123,Parent=true}
check(not Entitlements.SetStudioMovement(player,true))
check(not Entitlements.HasMovement(player))
studio=true
check(Entitlements.SetStudioMovement(player,true))
check(Entitlements.HasMovement(player))
check(Entitlements.CanUseMovement(player,"safe"))
check(not Entitlements.CanUseMovement(player,"arena"))
studio=false
check(not Entitlements.HasMovement(player))
check(not Entitlements.SetStudioMovement(player,true))
studio=true
handlers.removed(player)
check(not Entitlements.HasMovement(player))
print("PASS "..checks.." actual entitlement checks with mocked services")
'''
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / 'entitlement_checks.luau'
    path.write_text(setup + source + checks)
    subprocess.run(['luau', str(path)], check=True)
