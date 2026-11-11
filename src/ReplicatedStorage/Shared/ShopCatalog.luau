-- Set IDs only after the owner creates and approves the matching Roblox products.
local Catalog={Duration=30*60}
Catalog.Items={
 {key="Spectrum",name="SPECTRUM",tag="PERMANENT PASS",description="Choose your beam hue. Your signature.",kind="pass",id=0},
 {key="XP",name="DOUBLE XP",tag="30-MINUTE BOOST",description="Earn twice the XP from combat and quests.",kind="product",id=0,boost="xp"},
 {key="Coins",name="DOUBLE COINS",tag="30-MINUTE BOOST",description="Earn twice the coins from gameplay rewards.",kind="product",id=0,boost="coins"},
 {key="Movement",name="FREERUNNER",tag="PERMANENT PASS",description="Extra jumps and consecutive rolls in safe areas.",kind="pass",id=0},
}
function Catalog.Get(key) for _,item in ipairs(Catalog.Items) do if item.key==key then return item end end end
function Catalog.Product(id)
 if type(id)~="number" or id<=0 then return end
 local found
 for _,item in ipairs(Catalog.Items) do
  if item.kind=="product" and item.id==id then if found then return end;found=item end
 end
 return found
end
function Catalog.Hex(value)
 if type(value)~="string" or #value>7 then return end
 local hex=value:gsub("^#",""):upper()
 if #hex==6 and hex:match("^%x+$") then return hex end
end
return Catalog
