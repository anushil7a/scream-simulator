-- Earned coins only. Candidate balance, not monetization. One active gear bonus.
local Gear={}
Gear.Items={
 {id="Megaphone",name="Academy Megaphone",level=1,price=100,bonus=.06,template="AcademyMegaphoneAccessory"},
 {id="MicroSpeaker",name="Micro-speaker",level=1,price=200,bonus=.12,template="MicroSpeakerAccessory"},
 {id="MosaicMic",name="Mosaic Studio Mic",level=15,price=300,bonus=.18,template="MosaicMic"},
 {id="StreetBoombox",name="Street Boombox",level=35,price=600,bonus=.23,template="StreetBoombox"},
 {id="SonicCannon",name="Parabolic Sonic Cannon",level=65,price=1200,bonus=.28,template="SonicCannon"},
 {id="CelestialOrgan",name="Celestial Organ Pack",level=90,price=1800,bonus=.32,template="CelestialOrgan",mount="back"},
}
function Gear.Get(id) for _,item in ipairs(Gear.Items) do if item.id==id then return item end end end
function Gear.Owned(data,id)
 if id=="Megaphone" then return data.megaphoneOwned==true end
 if id=="MicroSpeaker" then return data.amplifierOwned==true end
 return type(data.gearOwned)=="table" and data.gearOwned[id]==true
end
function Gear.Selected(data)
 local item=Gear.Get(data.gearEquipped)
 if item and Gear.Owned(data,item.id) and (data.level or 1)>=item.level then return item end
 if data.amplifierOwned and data.amplifierEquipped then return Gear.Get("MicroSpeaker") end
 if data.megaphoneOwned and data.megaphoneEquipped then return Gear.Get("Megaphone") end
end
function Gear.Multiplier(data) local item=Gear.Selected(data);return item and 1+item.bonus or 1 end
function Gear.Sanitize(data,raw)
 data.gearOwned={}
 for _,item in ipairs(Gear.Items) do
  if type(raw.gearOwned)=="table" and raw.gearOwned[item.id]==true then data.gearOwned[item.id]=true end
 end
 local item=Gear.Get(raw.gearEquipped)
 data.gearEquipped=item and Gear.Owned(data,item.id) and item.id or nil
 -- Keep legacy ownership/selection fields intact for rollback. Combat chooses only one.
end
function Gear.Act(data,id,intent)
 local item=Gear.Get(id)
 if not item then return false,"Unknown gear." end
 if (data.level or 1)<item.level then return false,"Unlocks at level "..item.level.."." end
 local owned=Gear.Owned(data,id)
 local selected=Gear.Selected(data)
 local equipped=selected and selected.id==id
 if owned and not intent then return false,"Already owned. Equip from Gear." end
 if intent=="buy" and owned or intent=="equip" and equipped or intent=="unequip" and not equipped then return true end
 if intent=="equip" and not owned then return false,"Buy this gear before equipping it." end
 if not owned and data.coins<item.price then return false,"Need "..(item.price-data.coins).." more coins." end
 -- No yield: validate everything before debit. Duplicate buy requests never debit again.
 if not owned then
  data.coins-=item.price
  data.gearOwned=data.gearOwned or {};data.gearOwned[id]=true
  if id=="Megaphone" then data.megaphoneOwned=true elseif id=="MicroSpeaker" then data.amplifierOwned=true end
 end
 local equip=not (intent=="unequip" or intent==true and equipped)
 data.gearEquipped=equip and id or nil
 data.amplifierEquipped=equip and id=="MicroSpeaker"
 data.megaphoneEquipped=equip and id=="Megaphone"
 return true,item.name..(equip and " equipped. One gear bonus active; power capped at 100%." or " unequipped.")
end
function Gear.Products(data)
 local out={}
 for _,item in ipairs(Gear.Items) do table.insert(out,{id=item.id,name=item.name,price=item.price,owned=Gear.Owned(data,item.id),description=string.format("Level %d · +%d%% normalized power, capped at 100%%. One gear at a time.",item.level,math.floor(item.bonus*100+.5))}) end
 return out
end
return Gear
