-- Reference-led foundry set dressing, entirely original and built from local parts.
-- Floor/route geometry is owned by Zone05Geometry; no route, gameplay or spawn changes.
local cream={222,205,170}
local pale={242,224,182}
local mortar={170,153,124}
local dark={52,52,47}
local roof={50,90,95}
local bronze={105,68,46}
local brass={183,128,64}
local teal={57,190,188}
local function draw(b)
 local old=b.zone;b.zone="05"
 local function part(n,x,y,z,sx,sy,sz,c,mat,rot,cosmetic)
  b:part("Harbor_"..n,{x,y,z},{sx,sy,sz},c,not cosmetic,rot,mat,cosmetic and {"CosmeticDetail"} or {})
 end
 local function disk(n,x,y,z,r,h,c,mat)
  b:disk("Harbor_"..n,x,y,z,r,h,c,true,mat)
 end
 local function cross(n,a,bb,w,color,mat)
  local dx,dy,dz=bb[1]-a[1],bb[2]-a[2],bb[3]-a[3]
  local horizontal=math.sqrt(dx^2+dz^2)
  local yaw=math.deg(math.atan2(dx,dz));local pitch=-math.deg(math.atan2(dy,horizontal))
  part(n,(a[1]+bb[1])*.5,(a[2]+bb[2])*.5,(a[3]+bb[3])*.5,w,w,math.sqrt(horizontal^2+dy^2),color,mat,{pitch,yaw,0})
 end
 -- Deepen the three recognizable suspended bell cranes with rear frames
 -- and paired diagonals. The shells remain physically solid in the master map.
 for i,q in ipairs({{250,-810,24},{420,-840,32},{580,-800,40}}) do
  local x,z,d=table.unpack(q);local half=d/2+11;local back=z-19
  for _,side in ipairs({-1,1})do
   local xs=x+side*half
   part("CraneRearFoot"..i.."_"..side,xs,50,back,10,4,13,mortar,"Sandstone")
   part("CraneRearLeg"..i.."_"..side,xs,70,back,6,40,6,bronze,"Metal")
   cross("CraneRake"..i.."_"..side,{xs,56,z-3},{xs,87,back+3},2.8,dark,"Metal")
   part("CraneTopTie"..i.."_"..side,xs,89,z-9.5,8,3,28,brass,"Metal")
   for j=0,2 do
    part("CranePostPlate"..i.."_"..side.."_"..j,xs,57+j*13,back-3.15,5.6,3,.3,brass,"Metal",nil,true)
   end
  end
  part("CraneRearHead"..i,x,90,back,d+32,5,8,bronze,"Metal")
  -- Seven stacked, beveled bronze rings give the entire bell unmistakable
  -- flare without 48 individual solid side segments per bell.
  for tier=0,6 do
   local factor=({1,.90,.74,.61,.54,.51,.49})[tier+1]
   local h=({2.4,3.1,3.35,3.6,3.8,4.15,4.3})[tier+1]
   local top=({61.6,64.65,67.95,71.5,75.25,79.35,83.6})[tier+1]
   disk("BronzeBell"..i.."_"..tier,x,top-h*.5,z,d*.5*factor,h,tier==0 and brass or tier%2==0 and bronze or {125,82,51},"Metal")
  end
  disk("BellCastingCap"..i,x,84.05,z,d*.2,1.6,brass,"Metal")
  local sh=4+i*.85
  b:part("Harbor_Winch"..i,{x,91,z-9},{3,sh*2,sh*2},brass,true,{0,90,0},"Metal",{"Winch"},"Cylinder")
 end

 -- Playable open-front stonemason hall. Entry sits behind the arena, not on the 32-stud path.
 local x,z=673,-851
 part("HallFloor",x,48.3,z,114,.6,74,mortar,"Sandstone")
 part("HallRear",x,64,z-35,111,32,5,cream,"Sandstone")
 for _,s in ipairs({-1,1}) do
  part("HallSide"..s,x+s*54,63,z,5.0,30,71,cream,"Sandstone")
  part("HallCorner"..s,x+s*51,64,z+34,7,32,7,mortar,"Sandstone")
  part("HallHead"..s,x+s*27.5,82,z,58,3,83,roof,"Slate",{0,0,-s*10})
  for i=0,2 do
   part("HallLouver"..s.."_"..i,x+s*56.55,64,z-23+i*20,.12,9,7,bronze,"Metal",nil,true)
   part("HallLintel"..s.."_"..i,x+s*3.6+i*0,76+i*.6,z+34,3.2,.65,5.8,pale,"Sandstone")
  end
 end
 part("HallLowerCornice",x,78.8,z,118,2,76,pale,"Sandstone")
 part("HallFrontBeam",x,70.5,z+33.5,110,4,6,cream,"Sandstone")
 for _,s in ipairs({-1,1}) do
  part("HallEntryPier"..s,x+s*15,59,z+34,4,22,5,cream,"Sandstone")
  part("HallEntryPlinth"..s,x+s*15,49.6,z+34,7,3.2,8,mortar,"Sandstone")
 end
 for i=0,3 do
  local xs=x-36+i*24
  disk("WorkshopDrum"..i,xs,51,z-23,4.5,6,bronze,"Wood")
  disk("WorkshopHoop"..i,xs,52.8,z-23,4.75,.85,dark,"Metal")
 end

 -- Industrial loading yard and floor mosaic distinguish open combat from the
 -- decorative alcoves. All stripes are flush and have no touch, query or collision.
 for i=0,6 do
  local xf=139+i*85
  for j=0,1 do
   part("ApronCourse"..i.."_"..j,xf,48.055,-537+j*74,72,.07,3.7,(i+j)%2==0 and {193,175,140} or {210,189,149},"Sandstone",nil,true)
  end
 end
 for i=0,10 do
  local az=math.pi*(.06+i*.083)
  local r=101
  part("ArenaBand"..i,420+math.cos(az)*r,48.094,-680+math.sin(az)*r,13,.105,2.1,{109,118,98},"Concrete",{0,90-math.deg(az),0},true)
 end

 -- Stone lighthouse shaft windows, bronze ladder frame and luminous lens crown.
 -- The original bridge and islet still support the exact tested route.
 for j=0,5 do
  local y=70+j*17;local radius=15-math.floor(j*.9)
  for _,side in ipairs({-1,1}) do
   part("TowerSlit"..j.."_"..side,840,y,-650+side*(radius-.1),2.6,7.8,.42,dark,"Metal",nil,true)
   part("TowerSill"..j.."_"..side,840,y-3.8,-650+side*(radius+.2),4.3,.65,1.05,pale,"Sandstone")
  end
 end
 disk("LanternLensBase",840,212.5,-650,8.9,3.5,brass,"Metal")
 b:part("Harbor_LanternLens",{840,220,-650},{11,14.9,11},{0,240,255},true,{0,45,0},"Neon",{"HeroLandmark"},"Ball")
 for i=0,7 do
  local a=i*math.pi/4
  local x,z=840+math.cos(a)*17.8,-650+math.sin(a)*17.8
  part("LanternBaluster"..i,x,184,z,2.15,5.1,2.15,brass,"Metal")
 end
 -- The seaward masonry face responds to the many bays in the reference.
 -- This is a visible low retaining arcade below the play floor, not a
 -- raised fake crosswalk. The bays remain open at sea level.
 for i=0,3 do
  local x0=104+i*35
  part("SeaArcadeFoot"..i,x0,10,-409,9,20,21,mortar,"Sandstone")
  part("SeaArcadeCornice"..i,x0,28,-410,9.4,4,23,pale,"Sandstone")
 end
 for i=0,2 do
  local cx=121.5+i*35
  for j=0,6 do
   local a=(j+.5)*math.pi/7
   part("SeaArcadeVossoir"..i.."_"..j,cx+math.cos(a)*17.5,27+math.sin(a)*13,-409,8.8,4,20,
    j%2==0 and pale or cream,"Sandstone",{0,0,math.deg(a)+90})
  end
 end
 part("SeaArcadeDeckEdge",156,44,-407,118,5,22,pale,"Sandstone")
 -- A working forge yard, just off the lighthouse approach, uses a layered
 -- row of counter blocks and covered racks rather than geometric scatter.
 for i=0,2 do
  local x=565+i*47;local z=-552-i*8
  part("ForgeYardPad"..i,x,48.29,z,37,.55,35,mortar,"Sandstone")
  part("ForgeStack"..i,x,58,z,12,20,11,bronze,"Slate")
  part("ForgeCap"..i,x,69,z,16,3,15,dark,"Metal")
  part("ForgeAshBox"..i,x+12,51.9,z-9,10,7.8,11,bronze,"Metal")
  part("ForgePilot"..i,x,57,z+5.61,5,3,.18,{211,131,58},"Neon",nil,true)
 end
 -- Usable dock hardware: solid capstans strengthened with believable cross arms
 -- at the side edges of the lower platform, away from ramp lanes.
 for i,q in ipairs({{387,-264},{451,-261}}) do
  local x,z=table.unpack(q)
  disk("BerthBollard"..i,x,26,z,2.75,4,dark,"Metal")
  part("BerthArm"..i,x,27,z,9,1.4,2.1,bronze,"Metal")
  part("BerthArmCross"..i,x,27,z,2.1,1.4,9,bronze,"Metal")
  disk("BerthCap"..i,x,28.35,z,3.1,.7,brass,"Metal")
 end
 b.zone=old
end
return draw
