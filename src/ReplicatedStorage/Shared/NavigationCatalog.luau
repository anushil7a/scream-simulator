-- Read-only destinations. Selection belongs to the client, never to quest acceptance.
local Config=require(script.Parent:WaitForChild("Config"))
local BossCatalog=require(script.Parent:WaitForChild("BossCatalog"))
local TrainingRules=require(script.Parent:WaitForChild("TrainingRules"))
local Catalog={Places={
 {id="spawn",label="Spawn"},{id="training",label="Training"},{id="arena",label="Arena"},
 {id="gardens",label="Gardens"},{id="market",label="Market / café"},{id="coast",label="Coast"},
}}
if Config.CompactCity and Config.CityLayout.AmphitheatreEntrance then
 table.insert(Catalog.Places,{id="amphitheatre",label="Amphitheatre entrance",position=Config.CityLayout.AmphitheatreEntrance})
end
local function eligible(q,data)
 local progress=(data.quests or {})[q.id]
 return not q.retired and (q.menuAvailable==true or (data.availableQuests or {})[q.id]==true or data.activeQuest==q.id)
  and not (progress and (progress.claimed or (progress.progress or 0)>=q.goal))
end
local function target(position,label)
 return position and {position=position,label=label} or nil
end
function Catalog.Resolve(kind,id,data)
 if not Config.CompactCity or type(id)~="string" then return nil end
 data=data or {}
 if kind=="boss" then
  for _,boss in ipairs(BossCatalog.Entries) do
   if boss.id==id then return target(Vector3.new(boss.x,(boss.y or 0)+3,boss.z),boss.name.." · Lv "..boss.level) end
  end
 elseif kind=="place" then
  if id=="training" then
   local tier=TrainingRules.Recommended(data.level or 1)
   local index=table.find(TrainingRules.Tiers,tier)
   local home=Config.CityLayout.TrainingHomes[index]
   return home and target(Vector3.new(home.x,home.y+3,home.z),tier.name.." Training · Lv "..tier.level)
  end
  for index,place in ipairs(Catalog.Places) do
   if place.id==id then
    if place.position then return target(place.position,place.label) end
    local landmark=Config.CityLayout.MapLandmarks[index]
    return landmark and target(Vector3.new(landmark.x,(landmark.y or 0)+3,landmark.z),place.label) or nil
   end
  end
 elseif kind=="quest" then
  local quest=Config.GetQuest(id)
  if quest and eligible(quest,data) then return (data.questNavigation or {})[id] end
 end
 return nil
end
-- Build once after World.Build. Giver starts and quest assignments are static for
-- this world; rebuild this index if a future caller rebuilds/replaces the world.
-- An entry (even with no position) preserves the first-giver semantics.
function Catalog.IndexQuestGivers(bots)
 local index={}
 for _,bot in ipairs(bots) do
  for _,id in ipairs(bot.questIds or {}) do
   if index[id]==nil then index[id]={position=bot.start} end
  end
 end
 return index
end
-- Server-only call with authoritative session and the prebuilt giver index. This never
-- changes quest state and never exports soccer lost-ball positions or puzzle gates.
function Catalog.QuestTargets(session,givers)
 local result={}
 if not Config.CompactCity then return result end
 local data=session.data
 local eligibility={quests=data.quests,availableQuests=data.availableQuests,activeQuest=session.activeQuest}
 local function marker(action)
  for _,m in ipairs(Config.CityLayout.QuestMarkers) do
   if m.action==action and not (session.collected or {})[m.id] then return target(m.position,m.text) end
  end
 end
 for _,q in ipairs(Config.Quests) do
  if eligible(q,eligibility) then
   local giver=givers[q.id]
   local destination=giver and target(giver.position,"Talk to "..(q.giver or "quest giver")) or nil
   if q.id=="arena_assist" then destination=target(Config.CityLayout.Teleports.Arena,"Arena · team effort") end
   if session.activeQuest==q.id then
    if q.id=="garden" then destination=marker("Garden")
    elseif q.id=="beach" then destination=marker("Litter")
    elseif q.id=="delivery" then
     if session.carrying then
      local stop=Config.GetDeliveryStop(session.deliveryStop)
      destination=stop and target(stop.position,stop.name) or nil
     else destination=marker("Pickup") end
    elseif q.id=="sprint" then destination=marker(session.raceStart and "RaceFinish" or "RaceStart")
    elseif q.id=="dodge" or q.id=="arena" then destination=target(Config.CityLayout.Teleports.Arena,"Arena · "..q.name)
    end
   end
   result[q.id]=destination
  end
 end
 return result
end
return Catalog
