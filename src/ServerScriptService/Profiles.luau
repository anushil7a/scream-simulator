local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local Profiles = {}
local store
local storeReady, storeResult = pcall(function()
    return DataStoreService:GetDataStore("ScreamSimulator_v1")
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
    return {coins=0,level=1,xp=0,sound="TinyAah",aura="Gold",quests={},settings={volume=0.55,reducedShake=false}}
end
function Profiles.Sanitize(raw)
    local data=Profiles.Default()
    if type(raw)~="table" then return data end
    data.coins=wholeNumber(raw.coins,0,0,1000000000)
    data.level=wholeNumber(raw.level,1,1,Config.MaxLevel)
    data.xp=wholeNumber(raw.xp,0,0,Config.XPToNext(data.level)-1)
    local sound=Config.GetSound(raw.sound)
    if sound and sound.level<=data.level then data.sound=sound.id end
    if type(raw.aura)=="string" and Config.Auras[raw.aura] then data.aura=raw.aura end
    if type(raw.quests)=="table" then
        for _,q in ipairs(Config.Quests) do
            local old=raw.quests[q.id]
            if type(old)=="table" then data.quests[q.id]={progress=wholeNumber(old.progress,0,0,q.goal),claimed=old.claimed==true} end
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
    if not store then
        return Profiles.Default(), false
    end
    local key = "Player_" .. userId
    for attempt = 1, 3 do
        local success, result = pcall(function()
            return store:GetAsync(key)
        end)
        if success then
            return Profiles.Sanitize(result), true
        end
        warn("ScreamSimulator profile load failed", userId, attempt, result)
        task.wait(attempt)
    end
    -- Keep an in-memory profile, but never overwrite stored data after a failed load.
    return Profiles.Default(), false
end

function Profiles.Save(userId, data)
    if not store then
        return false
    end
    local snapshot = Profiles.Sanitize(data)
    local key = "Player_" .. userId
    for attempt = 1, 3 do
        local success, err = pcall(function()
            store:UpdateAsync(key, function()
                return snapshot
            end)
        end)
        if success then
            return true
        end
        warn("ScreamSimulator profile save failed", userId, attempt, err)
        task.wait(attempt)
    end
    return false
end

return Profiles
