local Healing=require(script.Parent:WaitForChild("Healing"))
local VoiceCombat=require(script.Parent:WaitForChild("VoiceCombat"))
local Progression=require(script.Parent:WaitForChild("Progression"))
local Config = {}
Config.AutomaticVoice = true -- next local release; server owns the selected mode
Config.Progression=Progression
Config.VoiceCombat=VoiceCombat
Config.MaxLevel = VoiceCombat.MaxLevel
Config.MaxHealth = 100
Config.MapMin=Vector3.new(-720,-20,-600)
Config.MapMax=Vector3.new(720,200,600)
function Config.HealthForLevel(level) return VoiceCombat.Stats(level,1,false).health end
Config.HealQuietSeconds = Healing.QuietSeconds
Config.HealAmount = Healing.Fraction*100 -- percent of maximum health
Config.BotMaxHealth = 60
Config.BotRespawnSeconds = 6
Config.WalkSpeed = 16
Config.SprintSpeed = 25
Config.SprintDuration = 10
Config.SprintRecovery = 5
Config.SpawnProtection = 5
Config.MovementPassId = 0 -- Configure only after the owner creates the pass.
Config.MicroSpeakerPrice = 1500
Config.DodgeCooldown = 4
Config.DodgeDuration = 0.6
Config.DodgeDistance = 14
Config.DeliveryStops={
 {id="StageDelivery",name="boardwalk music stage",position=Vector3.new(150,2,403)},
 {id="LookoutDelivery",name="lifeguard lookout",position=Vector3.new(-240,2,427)},
 {id="PierDelivery",name="end of the timber pier",position=Vector3.new(525,3,580)},
}
function Config.GetDeliveryStop(id) for _,stop in ipairs(Config.DeliveryStops) do if stop.id==id then return stop end end end
Config.ZoneMin = Vector3.new(-480,-20,-360)
Config.ZoneMax = Vector3.new(480,200,360)
Config.Sounds = {
 {id="TinyAah",name="Tiny Aah",level=1,effect="Pulse",description="A clean pulse around your aimed voice beam.",assetId=""},
 {id="IyoPop",name="Echo Pop",level=10,effect="Echo",description="Three echo rings wrap your aimed voice beam.",assetId=""},
 {id="PanicChicken",name="Panic Chicken",level=20,effect="Feathers",description="Feather-shaped sparks follow your voice beam.",assetId=""},
 {id="Laughquake",name="Laughquake",level=30,effect="Quake",description="Jagged ribbons trace your aimed voice beam.",assetId=""},
 {id="MegaChaos",name="Storm Siren",level=40,effect="Storm",description="Electric strands trace your aimed voice beam.",assetId=""},
 {id="Supernova",name="Supernova",level=50,effect="Nova",description="A bright starburst marks the end of your beam.",assetId=""},
}
-- Reuse existing visuals at the new ten-level cadence; no cosmetic expansion.
local families={"Pulse","Echo","Feathers","Quake","Storm","Nova"}
local titles={"Resonance","Prism","Sunburst","Aftershock","Tempest","Aurora"}
local ranks={"Coastal","Mosaic","Moonlit","Radiant","Spectral","Celestial","Royal","Mythic","Astral","Legendary"}
for level=60,Config.MaxLevel,10 do
 local n=(level-60)/10
 local family=n%#families+1
 local rank=math.floor(n/#families)+1
 table.insert(Config.Sounds,{id="VoiceStyle"..level,name=ranks[rank].." "..titles[family],level=level,effect=families[family],description="Mic-powered "..string.lower(families[family]).." visuals. Power and reach scale with your level.",assetId="",variant=rank})
end
for _,style in ipairs(Config.Sounds) do style.cooldown=4 end
Config.Auras={Gold=Color3.fromRGB(255,203,99),Mint=Color3.fromRGB(98,244,187),Violet=Color3.fromRGB(188,137,255),Ice=Color3.fromRGB(110,207,255),Coral=Color3.fromRGB(255,128,128)}
Config.Quests={
 {id="nick",name="The Worst Striker’s Best Assist",hidden=true,giver="Nick Booty · hidden coastal court",description="Find Nick’s three lost balls (120s), steer through four cone-course gates (90s), then hit five targets (120s). Final targets move and Nick’s assist drifts right. Soft mic shots give control. Restart at his court.",goal=1,xp=1800,coins=1200,event="Soccer"},
 {id="garden",name="A Little More Color",description="Help Mar Soler water the three raised flowerbeds in Rambla Gardens. Hold F beside each bed.",giver="Mar Soler · Rambla Gardens",goal=3,xp=130,coins=80,event="Garden"},
 {id="beach",name="Leave Only Footprints",description="Collect 6 washed-up bottles on the beach. Hold F near litter.",goal=6,xp=100,coins=50,event="Litter"},
 {id="delivery",name="Coffee on the Coast",description="Collect a café order, then deliver it to your assigned waterfront stop within 90 seconds. Check your objective for the recipient.",goal=1,xp=120,coins=60,event="Delivery"},
 {id="crowd",name="Three's a Crowd",description="Line up 3 training residents and hit them with one beam.",goal=1,xp=100,coins=40,event="Crowd"},
 {id="sprint",name="Boardwalk Dash",description="Start beside the lifeguard tower and follow the promenade east to the finish in 25 seconds.",goal=1,xp=120,coins=50,event="Race"},
 {id="dodge",name="Can't Touch This",description="Dodge 3 enemy screams in the central arena.",goal=3,xp=160,coins=70,event="Evade"},
 {id="arena",name="Underdog",description="Knock out a player whose level is at least yours in the central arena.",goal=1,xp=180,coins=80,event="Underdog"},
}
local questGivers={beach="Mar Soler · Rambla Gardens",delivery="Pau Vidal · Mercat del Mar",crowd="Busker · west gardens",sprint="Commuter · Plaça del Sol",dodge="Fighter · Rambla Gardens",arena="Fighter · Rambla Gardens"}
for _,quest in ipairs(Config.Quests) do quest.giver=quest.giver or questGivers[quest.id] end
function Config.SoundForLevel(level)
 local chosen=Config.Sounds[1]
 for _,s in ipairs(Config.Sounds) do if s.level<=level then chosen=s end end
 return chosen
end
function Config.GetSound(id)
 for _,s in ipairs(Config.Sounds) do if s.id==id then return s end end
 -- Resolve retired save IDs; Profiles archives the original selection.
 local legacy=type(id)=="string" and tonumber(id:match("^VoiceStyle(%d+)$"))
 if legacy and legacy>=30 and legacy<=300 and legacy%5==0 then
  return Config.SoundForLevel(math.min(Config.MaxLevel,legacy))
 end
end
function Config.GetQuest(id) for _,q in ipairs(Config.Quests) do if q.id==id then return q end end end
function Config.XPToNext(level) return Progression.XPToNext(level) end
function Config.PlayerKOXP(level) return Progression.PlayerKOXP(level) end
function Config.InArena(p) return p.X>=Config.ZoneMin.X and p.X<=Config.ZoneMax.X and p.Z>=Config.ZoneMin.Z and p.Z<=Config.ZoneMax.Z and p.Y>=Config.ZoneMin.Y and p.Y<=Config.ZoneMax.Y end
return Config
