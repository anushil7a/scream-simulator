"""Execute actual Config/Profiles with real pure rules and mocked engine services.

No Roblox data is read/written. Covers the temporary level-cap reduction and
preservation of pre-cap progress through repeated sanitize/save snapshots.
"""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
config = (root / "src/ReplicatedStorage/Shared/Config.luau").read_text()
profiles = (root / "src/ServerScriptService/Profiles.luau").read_text()
preamble = r'''
local Healing=require("../src/ReplicatedStorage/Shared/Healing")
local Combat=require("../src/ReplicatedStorage/Shared/VoiceCombat")
local Progression=require("../src/ReplicatedStorage/Shared/Progression")
local Lease=require("../src/ReplicatedStorage/Shared/ProfileLease")
local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z}end}
local Color3={fromRGB=function(r,g,b)return {r,g,b}end}
local script={Parent={WaitForChild=function(_,name)return name end}}
local config
local require=function(name)
 if name=="Healing" then return Healing elseif name=="VoiceCombat" then return Combat elseif name=="Progression" then return Progression
 elseif name=="Config" then return config elseif name=="Lease" then return Lease end
 error("Unexpected dependency "..tostring(name))
end
local function loadConfig()
'''
between = r'''
end
config=loadConfig()
local services={DataStoreService={GetDataStore=function()error("No real stores in migration tests")end},
 ReplicatedStorage={Shared={Config="Config",ProfileLease="Lease"}},
 RunService={IsStudio=function()return true end},HttpService={GenerateGUID=function()return "test-owner"end}}
local game={JobId="migration-test",GetService=function(_,name)return services[name]end}
local warn=function()end
local function loadProfiles()
'''
checks = r'''
end
local P=loadProfiles();local checks=0
local function check(v,msg) assert(v,msg);checks+=1 end
check(config.MaxLevel==100 and Progression.MaxLevel==100 and Combat.MaxLevel==100,"Inconsistent caps")
check(#config.Sounds==11,"Expected base plus ten unlocks")
for level=1,100 do
 local style=config.SoundForLevel(level)
 check(style.level==(level<10 and 1 or math.floor(level/10)*10),"Unlock cadence")
 check(config.GetSound(style.id)==style,"Canonical style lookup")
end
for oldLevel=30,300,5 do
 local style=config.GetSound("VoiceStyle"..oldLevel)
 check(style and style.level<=100,"Retired style not resolved")
end
check(config.GetSound("VoiceStyle301")==nil and config.GetSound("VoiceStyle31")==nil,"Invalid aliases accepted")
for _,level in ipairs({1,5,9,10,25,50,99,100,101,150,299,300}) do
 local raw={schemaVersion=3,level=level,xp=17,sound="VoiceStyle300",coins=243,
  amplifierOwned=true,amplifierEquipped=true,achievements={FoundNick=true},
  availableQuests={garden=true},quests={garden={progress=2,claimed=false}},settings={volume=.4}}
 local a=P.Sanitize(raw)
 check(a.schemaVersion==4 and a.level==math.min(100,level),"Migration cap")
 check(a.legacyProgress.level==level and a.legacyProgress.xp==17 and a.legacyProgress.sound==raw.sound,"Legacy progress lost")
 check(a.coins==243 and a.amplifierOwned and a.amplifierEquipped and a.achievements.FoundNick,"Unrelated ownership lost")
 check(a.quests.garden.progress==2 and a.availableQuests.garden and a.settings.volume==.4,"Unrelated task/settings lost")
 check(config.GetSound(a.sound).level<=a.level,"Equipped locked style")
 if level>=100 then check(a.xp==0,"Cap XP not cleared") else check(a.xp==17,"XP unexpectedly lost") end
 a.coins+=10
 local b=P.Sanitize(a);local c=P.Sanitize(b)
 check(c.legacyProgress.level==level and c.legacyProgress.xp==17 and c.legacyProgress.sound==raw.sound,"Repeated migration replaced archive")
 check(c.coins==253 and c.level==a.level and c.sound==a.sound,"Repeated sanitize changed live data")
 check(c.legacyProgress~=b.legacyProgress,"Archive retained mutable reference")
end
local objectives=P.Sanitize({schemaVersion=4,level=50,xp=12,combatChallenges={fighters=2,elite=99,cover=0/0,unknown=7}})
check(objectives.combatChallenges.fighters==2 and objectives.combatChallenges.elite==1 and objectives.combatChallenges.cover==0 and objectives.combatChallenges.unknown==nil,"Challenge sanitization failed")
local reload=P.Sanitize(objectives)
check(reload.combatChallenges.fighters==2 and reload.level==50 and reload.xp==12,"Challenge reload changed progress")
local new=P.Sanitize(P.Default());check(new.legacyProgress==nil,"New profile archived synthetic old data")
local bad=P.Sanitize({schemaVersion=4,level=math.huge,xp=0/0,legacyProgress={level=math.huge,xp="bad",sound={}}})
check(bad.level==1 and bad.xp==0 and bad.legacyProgress.level==1 and bad.legacyProgress.xp==0 and bad.legacyProgress.sound==nil,"Malformed archive not sanitized")
local old=P.Sanitize({level=5,xp=0,sound="IyoPop"})
check(old.sound=="TinyAah" and old.legacyProgress.sound=="IyoPop","Moved unlock not archived safely")
local unrelated=P.Sanitize({schemaVersion=4,level=20,xp=0,sound="not-a-style"})
check(unrelated.sound=="TinyAah","Invalid style became unlocked selection")
print("PASS "..checks.." actual Config/Profiles level-100 migration checks (mock engine)")
'''
with tempfile.NamedTemporaryFile(mode="w", suffix=".luau", prefix=".migration_", dir=root / "tests", delete=False) as f:
    path = Path(f.name)
    f.write(preamble + config + between + profiles + checks)
try:
    subprocess.run(["luau", str(path)], cwd=root, check=True)
finally:
    path.unlink()
