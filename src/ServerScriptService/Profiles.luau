local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local Lease=require(ReplicatedStorage.Shared.ProfileLease)
local RunService=game:GetService("RunService")
local HttpService=game:GetService("HttpService")
local owner=game.JobId~="" and game.JobId or HttpService:GenerateGUID(false)
local locks,owned={},{}
local Profiles = {}
local store
local storeReady, storeResult = pcall(function()
    return DataStoreService:GetDataStore(RunService:IsStudio() and "ScreamSimulator_Studio_v2" or "ScreamSimulator_v1")
end)
if storeReady then
    store = storeResult
else
    warn("ScreamSimulator save data unavailable; using temporary test profiles.")
end

local function wholeNumber(value, fallback, minimum, maximum)
    if type(value) ~= "number" or value ~= value or value == math.huge or value == -math.huge then
        return fallback
    end
    return math.clamp(math.floor(value), minimum, maximum)
end

function Profiles.Default()
    return {schemaVersion=3,amplifierOwned=false,amplifierEquipped=false,achievements={},availableQuests={},coins=0,level=1,xp=0,sound="TinyAah",aura="Gold",quests={},settings={volume=0.55,reducedShake=false}}
end
function Profiles.Sanitize(raw)
    local data=Profiles.Default()
    if type(raw)~="table" then return data end
    data.amplifierOwned=raw.amplifierOwned==true
    data.amplifierEquipped=data.amplifierOwned and raw.amplifierEquipped==true
    if type(raw.achievements)=="table" then
        for _,id in ipairs({"FoundNick","NickChampion"}) do if raw.achievements[id]==true then data.achievements[id]=true end end
    end
    data.coins=wholeNumber(raw.coins,0,0,1000000000)
    data.level,data.xp=Config.Progression.Normalize(raw.level,raw.xp)
    local sound=Config.GetSound(raw.sound)
    if sound and sound.level<=data.level then data.sound=sound.id end
    if type(raw.aura)=="string" and Config.Auras[raw.aura] then data.aura=raw.aura end
    if type(raw.availableQuests)=="table" then
        for _,q in ipairs(Config.Quests) do if raw.availableQuests[q.id]==true then data.availableQuests[q.id]=true end end
    end
    if type(raw.quests)=="table" then
        for _,q in ipairs(Config.Quests) do
            local old=raw.quests[q.id]
            if type(old)=="table" then data.availableQuests[q.id]=true;data.quests[q.id]={progress=wholeNumber(old.progress,0,0,q.goal),claimed=old.claimed==true} end
        end
    end
    if type(raw.settings)=="table" then
        local v=raw.settings.volume
        if type(v)=="number" and v==v then data.settings.volume=math.clamp(v,0,1) end
        data.settings.reducedShake=raw.settings.reducedShake==true
    end
    -- Legacy shield and purchased-track fields are deliberately discarded.
    return data
end

function Profiles.Load(userId)
    if not store then return Profiles.Default(),false end
    local key="Player_"..userId
    for attempt=1,3 do
        local success,result=pcall(function()
            return store:UpdateAsync(key,function(raw)
                if not Lease.CanAcquire(raw,owner,os.time()) then return nil end
                return Lease.Stamp(Profiles.Sanitize(raw),owner,os.time())
            end)
        end)
        if success then
            if Lease.Owns(result,owner) then owned[userId]=true;return Profiles.Sanitize(result),true end
            return Profiles.Default(),false,"Another server is still saving this profile. Rejoin shortly."
        end
        warn("ScreamSimulator profile load failed",userId,attempt)
        task.wait(attempt)
    end
    return Profiles.Default(),false,"Saving is unavailable. This session uses temporary progress."
end

function Profiles.Save(userId,data,release)
    if not store or not owned[userId] then return false end
    -- Snapshot after waiting, so an older autosave cannot overwrite a leave/save.
    while locks[userId] do task.wait(.05) end
    if not owned[userId] then return false end
    locks[userId]=true
    local snapshot=Profiles.Sanitize(data)
    local key="Player_"..userId
    for attempt=1,3 do
        local success,result=pcall(function()
            return store:UpdateAsync(key,function(raw)
                if not Lease.Owns(raw,owner) then return nil end
                if release then snapshot._lease=nil;return snapshot end
                return Lease.Stamp(snapshot,owner,os.time())
            end)
        end)
        if success then
            locks[userId]=nil
            if result==nil then owned[userId]=nil;return false end
            if release then owned[userId]=nil end
            return true
        end
        warn("ScreamSimulator profile save failed",userId,attempt)
        task.wait(attempt)
    end
    locks[userId]=nil
    return false
end

return Profiles
