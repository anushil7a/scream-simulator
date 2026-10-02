local VoiceCombat=require(script.Parent.VoiceCombat)
local Config = {}
Config.VoiceCombat=VoiceCombat
Config.MaxLevel = 300
Config.MaxHealth = 100
Config.MapMin=Vector3.new(-720,-20,-600)
Config.MapMax=Vector3.new(720,200,600)
function Config.HealthForLevel(level) return VoiceCombat.Stats(level,1,false).health end
Config.HealQuietSeconds = 10
Config.HealAmount = 20
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
Config.ZoneMin = Vector3.new(-480,-20,-360)
Config.ZoneMax = Vector3.new(480,200,360)
Config.Sounds = {
 {id="TinyAah",name="Tiny Aah",level=1,damage=12,range=30,width=4,cooldown=2.4,effect="Pulse",description="A focused forward sound beam.",assetId=""},
 {id="IyoPop",name="Echo Pop",level=5,damage=18,range=42,width=5,cooldown=2.6,effect="Echo",description="A longer beam wrapped in echo rings.",assetId=""},
 {id="PanicChicken",name="Panic Chicken",level=10,damage=25,range=56,width=6,cooldown=2.8,effect="Feathers",description="A piercing stream of golden feathers.",assetId=""},
 {id="Laughquake",name="Laughquake",level=15,damage=32,range=72,width=7,cooldown=3,effect="Quake",description="A broad ground-rumbling sound beam.",assetId=""},
 {id="MegaChaos",name="Storm Siren",level=20,damage=40,range=90,width=8,cooldown=3.2,effect="Storm",description="A crackling electric sound lance.",assetId=""},
 {id="Supernova",name="Supernova",level=25,damage=48,range=112,width=10,cooldown=3.5,effect="Nova",description="A brilliant long-range sound ray.",assetId=""},
}
-- Familiar early unlocks retain their save IDs. Further styles unlock every five levels.
local families={"Pulse","Echo","Feathers","Quake","Storm","Nova"}
local titles={"Resonance","Prism","Sunburst","Aftershock","Tempest","Aurora"}
local ranks={"Coastal","Mosaic","Moonlit","Radiant","Spectral","Celestial","Royal","Mythic","Astral","Legendary"}
for level=30,300,5 do
 local n=(level-30)/5
 local family=n%#families+1
 local rank=math.floor(n/#families)+1
 table.insert(Config.Sounds,{id="VoiceStyle"..level,name=ranks[rank].." "..titles[family],level=level,effect=families[family],description="Mic-powered "..string.lower(families[family]).." visuals. Power and reach scale with your level.",assetId="",variant=rank})
end
for _,style in ipairs(Config.Sounds) do style.cooldown=4 end
Config.Auras={Gold=Color3.fromRGB(255,203,99),Mint=Color3.fromRGB(98,244,187),Violet=Color3.fromRGB(188,137,255),Ice=Color3.fromRGB(110,207,255),Coral=Color3.fromRGB(255,128,128)}
Config.Quests={
 {id="nick",name="The Worst Striker’s Best Assist",hidden=true,giver="Nick Booty · hidden coastal court",description="Guide your personal ball through five targets with mic beams in 120 seconds. Final targets move. Speak softly for control; scream for distance. Restart here while at the court.",goal=1,xp=1800,coins=1200,event="Soccer"},
 {id="garden",name="A Little More Color",description="Help Mar Soler water the three raised flowerbeds in Rambla Gardens. Hold F beside each bed.",giver="Mar Soler · Rambla Gardens",goal=3,xp=130,coins=80,event="Garden"},
 {id="beach",name="Leave Only Footprints",description="Collect 6 washed-up bottles on the beach. Hold F near litter.",goal=6,xp=100,coins=50,event="Litter"},
 {id="delivery",name="Coffee Before the Encore",description="Pick up a café order, then deliver it to the boardwalk stage within 90 seconds.",goal=1,xp=120,coins=60,event="Delivery"},
 {id="crowd",name="Three's a Crowd",description="Line up 3 training residents and hit them with one beam.",goal=1,xp=100,coins=40,event="Crowd"},
 {id="sprint",name="Boardwalk Dash",description="Start beside the lifeguard tower and follow the promenade east to the finish in 25 seconds.",goal=1,xp=120,coins=50,event="Race"},
 {id="dodge",name="Can't Touch This",description="Dodge 3 enemy screams in the central arena.",goal=3,xp=160,coins=70,event="Evade"},
 {id="arena",name="Underdog",description="Knock out a player whose level is at least yours in the central arena.",goal=1,xp=180,coins=80,event="Underdog"},
}
local questGivers={beach="Mar Soler · Rambla Gardens",delivery="Pau Vidal · Mercat del Mar",crowd="Busker · west gardens",sprint="Commuter · Plaça del Sol",dodge="Fighter · Rambla Gardens",arena="Fighter · Rambla Gardens"}
for _,quest in ipairs(Config.Quests) do quest.giver=quest.giver or questGivers[quest.id] end
function Config.GetSound(id) for _,s in ipairs(Config.Sounds) do if s.id==id then return s end end end
function Config.GetQuest(id) for _,q in ipairs(Config.Quests) do if q.id==id then return q end end end
function Config.XPToNext(level) return math.floor(70+level*25+level^1.55*8) end
function Config.PlayerKOXP(level) return 50+math.clamp(level,1,Config.MaxLevel)*12 end
function Config.InArena(p) return p.X>=Config.ZoneMin.X and p.X<=Config.ZoneMax.X and p.Z>=Config.ZoneMin.Z and p.Z<=Config.ZoneMax.Z and p.Y>=Config.ZoneMin.Y and p.Y<=Config.ZoneMax.Y end
return Config
