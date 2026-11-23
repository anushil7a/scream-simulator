-- Set IDs only after the owner creates and approves the matching Roblox products.
local Catalog={Duration=30*60}
Catalog.Items={
 {key="Spectrum",name="SPECTRUM",tag="PERMANENT PASS",description="Choose your beam hue. Your signature.",kind="pass",id=0,suggestedPrice=149},
 {key="XP",name="DOUBLE XP",tag="30-MINUTE BOOST",description="Earn twice the XP from combat and quests.",kind="product",id=0,boost="xp",suggestedPrice=39},
 {key="Coins",name="DOUBLE COINS",tag="30-MINUTE BOOST",description="Earn twice the coins from gameplay rewards.",kind="product",id=0,boost="coins",suggestedPrice=29},
 {key="Movement",name="FREERUNNER",tag="PERMANENT PASS",description="Extra jumps and consecutive rolls in safe areas.",kind="pass",id=0,suggestedPrice=99},
 {key="Encore",name="ENCORE",tag="PERMANENT PASS",description="See an Encore title above your name in safe areas.",kind="pass",id=0,suggestedPrice=79},
 {key="Afterimage",name="AFTERIMAGE",tag="PERMANENT PASS",description="Leave a cosmetic trail when you dodge in safe areas.",kind="pass",id=0,suggestedPrice=99},
 {key="CityGlow",name="CITY GLOW",tag="PERMANENT PASS",description="Soft gold outline in safe areas. Only you can see it.",kind="pass",id=0,suggestedPrice=59},
 {key="SignalDeck",name="SIGNAL DECK",tag="PERMANENT PASS",description="Give your Beam Collection a neon instrument-panel theme.",kind="pass",id=0,suggestedPrice=69},
 {key="CityCrest",name="CITY CREST",tag="PERMANENT PASS",description="Give your personal City map a gold Academy crest and trim.",kind="pass",id=0,suggestedPrice=49},
 {key="PulseFrame",name="PULSE FRAME",tag="PERMANENT PASS",description="Add a cosmetic frame to your personal beam status HUD.",kind="pass",id=0,suggestedPrice=49},
 {key="RouteLights",name="ROUTE LIGHTS",tag="PERMANENT PASS",description="Tint your personal guide markers blue on safe ground.",kind="pass",id=0,suggestedPrice=39},
 {key="HarborBadge",name="HARBOR BADGE",tag="PERMANENT PASS",description="Wear a harbor badge above your avatar in safe areas. Only you can see it.",kind="pass",id=0,suggestedPrice=49},
 {key="SprintRibbon",name="SPRINT RIBBON",tag="PERMANENT PASS",description="Leave a short ribbon while sprinting in safe areas. Only you can see it.",kind="pass",id=0,suggestedPrice=69},
}
function Catalog.Get(key) for _,item in ipairs(Catalog.Items) do if item.key==key then return item end end end
local function effectiveId(item,movementPassId)
 if item.key=="Movement" then return movementPassId end
 return item.id
end
local function uniqueOffer(kind,id,movementPassId)
 if type(id)~="number" or not (id>0 and id<2^53) or id%1~=0 then return end
 local found
 for _,item in ipairs(Catalog.Items) do
  if item.kind==kind and effectiveId(item,movementPassId)==id then
   if found then return end
   found=item
  end
 end
 return found
end
function Catalog.Product(id)
 return uniqueOffer("product",id)
end
function Catalog.Pass(id,movementPassId)
 return uniqueOffer("pass",id,movementPassId)
end
function Catalog.OfferId(item,movementPassId)
 local id=effectiveId(item,movementPassId)
 if uniqueOffer(item.kind,id,movementPassId)==item then return id end
end
function Catalog.Hex(value)
 if type(value)~="string" or #value>7 then return end
 local hex=value:gsub("^#",""):upper()
 if #hex==6 and hex:match("^%x+$") then return hex end
end
return Catalog
