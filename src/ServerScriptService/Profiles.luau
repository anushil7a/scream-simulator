local DataStoreService = game:GetService("DataStoreService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Config = require(ReplicatedStorage.Shared.Config)

local Lease=require(ReplicatedStorage.Shared.ProfileLease)
local RunService=game:GetService("RunService")
local HttpService=game:GetService("HttpService")
local owner=game.JobId~="" and game.JobId or HttpService:GenerateGUID(false)
local locks,owned={},{}
local bindings=setmetatable({},{__mode="k"})
local acquisition=0
local incarnation=HttpService:GenerateGUID(false)
local RECOVERY_WINDOW=12
local RECOVERY_NOTICE="Loaded the last confirmed save. Recent progress may be missing."
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
    return {schemaVersion=4,amplifierOwned=false,amplifierEquipped=false,achievements={},availableQuests={},coins=0,level=1,xp=0,sound="TinyAah",aura="Gold",quests={},combatChallenges={},settings={volume=0.55,reducedShake=false}}
end
function Profiles.Sanitize(raw)
    local data=Profiles.Default()
    if type(raw)~="table" then return data end
    -- Archive pre-cap progress once; never apply it to active level-100 combat.
    local legacy=type(raw.legacyProgress)=="table" and raw.legacyProgress or raw.schemaVersion~=4 and raw or nil
    if legacy then
        data.legacyProgress={level=wholeNumber(legacy.level,1,1,300),xp=wholeNumber(legacy.xp,0,0,1000000000)}
        if Config.GetSound(legacy.sound) then data.legacyProgress.sound=legacy.sound end
    end
    data.amplifierOwned=raw.amplifierOwned==true
    data.amplifierEquipped=data.amplifierOwned and raw.amplifierEquipped==true
    if type(raw.achievements)=="table" then
        for _,id in ipairs({"FoundNick","NickChampion","FirstBeam"}) do if raw.achievements[id]==true then data.achievements[id]=true end end
    end
    data.coins=wholeNumber(raw.coins,0,0,1000000000)
    data.level,data.xp=Config.Progression.Normalize(raw.level,raw.xp)
    if type(raw.combatChallenges)=="table" then
        for _,spec in ipairs(Config.Progression.Challenges) do
            data.combatChallenges[spec.id]=wholeNumber(raw.combatChallenges[spec.id],0,0,spec.goal-1)
        end
    end
    local sound=Config.GetSound(raw.sound)
    if sound then data.sound=(sound.level<=data.level and sound or Config.SoundForLevel(data.level)).id end
    if type(raw.customColor)=="string" and #raw.customColor==6 and raw.customColor:match("^%x+$") then data.customColor=raw.customColor:upper();data.useCustomColor=raw.useCustomColor==true end
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
    -- Preserve only the in-memory acquisition binding for legitimate baseline
    -- copies. No token is accepted from player data or persisted by Sanitize.
    bindings[data]=bindings[raw]
    -- Legacy shield and purchased-track fields are deliberately discarded.
    return data
end

-- Every retry uses the same immutable snapshot and (acquisition, revision).
-- An already committed operation is acknowledged without restamping its lease.
-- Callback retries must recheck the current record, not a cached ownership flag.
local function commit(userId,session,operation,deadline)
    for attempt=1,3 do
        if deadline and os.clock()>=deadline then break end
        local success,result=pcall(function()
            return store:UpdateAsync("Player_"..userId,function(raw)
                local saved=type(raw)=="table" and raw._save
                if type(saved)=="table" and saved.token==session.token and saved.revision==operation.revision then return raw end
                if not Lease.Owns(raw,owner,session.token) then return nil end
                if type(saved)=="table" and saved.token==session.token and type(saved.revision)=="number" and saved.revision>=operation.revision then return nil end
                local record=Profiles.Sanitize(operation.snapshot)
                record._save={token=session.token,revision=operation.revision}
                if operation.release then return record end
                return Lease.Stamp(record,owner,os.time(),session.token)
            end)
        end)
        if success then
            if result==nil then return false,"ownership" end
            session.confirmed=Profiles.Sanitize(result)
            return true
        end
        warn("ScreamSimulator profile save failed",userId,attempt)
        if deadline then
            if attempt<3 then task.wait(math.max(0,math.min(attempt,deadline-os.clock()))) end
        else task.wait(attempt) end
    end
    return false,"retry"
end

function Profiles.Load(userId)
    if not store then return Profiles.Default(),false,"Saving is unavailable. This session uses temporary progress." end
    while locks[userId] do task.wait(.05) end
    local previous=owned[userId]
    if previous and not previous.pending then
        return Profiles.Default(),false,"Your previous session is still saving. Rejoin shortly."
    end
    locks[userId]=true
    local fallback=false
    local confirmed=previous and previous.confirmed
    if previous then
        -- Recovery only runs on rejoin, within the same lock as acquisition.
        -- A slow engine request cannot be cancelled; the deadline bounds new
        -- attempts/backoff, not the duration of an already in-flight request.
        local recovered=commit(userId,previous,previous.pending,os.clock()+RECOVERY_WINDOW)
        fallback=not recovered
        confirmed=previous.confirmed
        owned[userId]=nil
    end
    acquisition+=1
    local token=owner..":"..incarnation..":"..acquisition
    local observed,hadLease
    for attempt=1,3 do
        local success,result=pcall(function()
            return store:UpdateAsync("Player_"..userId,function(raw)
                observed=type(raw)=="table" and Profiles.Sanitize(raw) or nil
                hadLease=type(raw)=="table" and type(raw._lease)=="table" and not Lease.Owns(raw,owner,token)
                if not Lease.CanAcquire(raw,owner,os.time(),token) then
                    -- A terminal local release has finished its bounded retry.
                    -- Only its exact token may be replaced before expiry.
                    if not (previous and Lease.Owns(raw,owner,previous.token)) then return nil end
                end
                if Lease.Owns(raw,owner,token) then return raw end
                local record=Profiles.Sanitize(raw)
                record._save=type(raw)=="table" and raw._save or nil
                -- Retain a warning across a lost acquisition response.
                record._recovered=fallback or hadLease or false
                return Lease.Stamp(record,owner,os.time(),token)
            end)
        end)
        if success then
            locks[userId]=nil
            if Lease.Owns(result,owner,token) then
                local data=Profiles.Sanitize(result)
                local session={token=token,revision=0,confirmed=Profiles.Sanitize(result)}
                owned[userId]=session;bindings[data]=session
                local notice=result._recovered==true
                return data,true,notice and RECOVERY_NOTICE or nil,notice
            end
            return observed or confirmed or Profiles.Default(),false,
                RECOVERY_NOTICE.." Another session owns this profile; progress here is temporary. Rejoin shortly.",true
        end
        warn("ScreamSimulator profile load failed",userId,attempt)
        -- A callback may have read a durable checkpoint before the write or
        -- response failed. It is safe to display, never to grant ownership.
        confirmed=observed or confirmed
        task.wait(attempt)
    end
    locks[userId]=nil
    -- Never enable saving or overwrite storage with a default/cached fallback.
    return confirmed and Profiles.Sanitize(confirmed) or Profiles.Default(),false,
        (confirmed and RECOVERY_NOTICE.." " or "Could not confirm a saved profile. ").."Saving is unavailable; progress here is temporary.",confirmed~=nil
end

function Profiles.Save(userId,data,release)
    if not store then return false,"unavailable" end
    local session=owned[userId]
    if not session or bindings[data]~=session then return false,"ownership" end
    while locks[userId] do task.wait(.05) end
    if owned[userId]~=session or session.pending then return false,"ownership" end
    locks[userId]=true
    session.revision+=1
    local operation={snapshot=Profiles.Sanitize(data),release=release==true,revision=session.revision}
    local ok,reason=commit(userId,session,operation)
    if release and not ok then
        -- Keep only one frozen final snapshot. Caller tables may change later.
        session.pending=operation
    elseif reason=="ownership" or release then owned[userId]=nil end
    locks[userId]=nil
    return ok,reason
end

return Profiles
