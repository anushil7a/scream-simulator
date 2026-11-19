-- Original v2.1 west district art. Reference IMG_1526; vault landmark/flow guidance.
-- Host owns base floors, borders, portals. Central44-stud cross and32-stud
-- perimeter corridor remain open. Reachable physical-looking objects are solid.
return function(build,id,spec)
 local cx,y,cz=table.unpack(spec.center);local w,d=table.unpack(spec.size)
 local cream={223,205,165};local pale={242,225,187};local sand={174,149,111}
 local teal={57,147,145};local brass={171,131,67};local leaf={83,135,73}
 local earth={110,88,61};local ink={48,66,66};local water={52,175,193}
 local prefix="West"..tostring(id).."_";local serial=0
 local function part(n,x,h,z,sx,sy,sz,c,rot,mat,shape,solid)
  serial+=1
  build:part(prefix..n..serial,{cx+x,y+h,cz+z},{sx,sy,sz},c,solid~=false,rot,mat or ((id=="01" or id==1) and "SmoothPlastic" or "Sandstone"),{},shape)
 end
 local function disk(n,x,h,z,r,height,c,mat,solid)
  serial+=1;build:disk(prefix..n..serial,cx+x,y+h,cz+z,r,height,c,solid~=false,mat or ((id=="01" or id==1) and "SmoothPlastic" or "Sandstone"),{})
 end
 local function tree(n,x,z,base,scale)
  if id=="01" or id==1 then
   disk(n.."Planter",x,base+.45*scale,z,5*scale,.9*scale,sand,"SmoothPlastic")
   disk(n.."Trunk",x,base+6*scale,z,1.1*scale,12*scale,earth,"Wood")
   part(n.."Foliage",x,base+18*scale,z,13*scale,30*scale,12*scale,{60,98,74},{0,0,-4},"SmoothPlastic","Ball",false)
   if build.compact then
    part(n.."Bough",x+3*scale,base+13*scale,z+2*scale,9*scale,17*scale,8*scale,{74,111,77},{6,0,-18},"SmoothPlastic","Ball",false)
   end
  else
   disk(n.."Trunk",x,base+5*scale,z,1.4*scale,10*scale,earth,"Wood")
   part(n.."Crown",x,base+12*scale,z,12*scale,18*scale,12*scale,leaf,nil,"Grass","Ball")
  end
 end
 local function steps(n,x,z,sx,sz)
  -- Three low continuous risers; upper sill4.5studs, no tall hidden blocker.
  for k=0,2 do part(n.."Step",x,(k+1)*.75,z,sx-k*5,(k+1)*1.5,sz-k*5,pale)end
 end
 local function pavilion(n,x,z,size,height,dome)
  steps(n,x,z,size+14,size+14)
  for _,a in ipairs({-1,1})do for _,b in ipairs({-1,1})do
   local px,pz=x+a*size*.36,z+b*size*.36
   disk(n.."Foot",px,5.5,pz,3,2,sand)
   disk(n.."Column",px,5+height/2,pz,2,height,cream)
   disk(n.."Capital",px,5+height,pz,3.2,2,pale)
  end end
  part(n.."Entablature",x,7+height,z,size+7,3,size+7,pale)
  if dome then
   disk(n.."DomeDrum",x,12+height,z,size*.40,8,cream)
   part(n.."TealDome",x,16+height,z,size*.85,size*.65,size*.85,teal,nil,"Slate","Ball")
   disk(n.."DomeCollar",x,13+height,z,size*.44,2,brass,"Metal")
   part(n.."Finial",x,20+height+size*.325,z,2,9,2,brass,nil,"Metal")
  else
   for _,side in ipairs({-1,1})do part(n.."RoofSlope",x+side*size*.23,13+height,z,size*.56,3,size+13,teal,{0,0,-side*18},"SmoothPlastic")end
   part(n.."Ridge",x,21+height,z,5,5,size+14,brass,nil,"Metal")
  end
 end
 if id=="01" or id==1 then
  -- One dominant palace, not a set of equal pavilions. The old street cross stays open.
  local x,z=-155,-140
  for k=0,3 do part("PalaceTerrace",x,(k+1)*.7,z,216-k*13,(k+1)*1.4,184-k*13,k%2==0 and sand or pale)end
  part("PalaceBody",x,27,z,148,44,120,cream)
  part("PalaceCorniceLower",x,49,z,160,4,132,pale)
  part("PalaceUpperStorey",x,61,z,112,22,94,cream)
  part("PalaceCorniceUpper",x,74,z,124,4,106,pale)
  -- A narrow, supported central tower echoes the approved Academy silhouette.
  part("CentralTower",x,96,z,50,40,50,cream)
  part("TowerCornice",x,117,z,56,3,56,pale)
  disk("PalaceDomeDrum",x,122,z,23,8,pale)
  disk("PalaceDomeGoldBand",x,126,z,24,2,brass,"Metal")
  part("GreatTealDome",x,136,z,50,22,50,teal,nil,"SmoothPlastic","Ball")
  disk("GreatDomeCrown",x,147,z,4,3,brass,"Metal")
  part("GreatDomeFinial",x,154,z,2,12,2,brass,nil,"Metal")
  for _,side in ipairs({-1,1}) do
   part("TowerPier",x+side*21,96,z+26,4,36,4,pale)
   part("TowerWindow",x+side*10,98,z+25.5,7,18,1.5,ink)
  end
  -- Deep attached facade reveals, pilasters and a portal; not a fake walk-through door.
  for _,side in ipairs({-1,1})do
   for i=-2,2 do
    local px=x+i*27
    part("PalacePilaster",px,27,z+side*61,3,40,3,pale)
    if i~=0 then
     part("WindowRecess",px+8,32,z+side*61,9,18,1.4,ink)
     part("WindowSill",px+8,22,z+side*63,12,2,4,brass)
     part("WindowHood",px+8,41.6,z+side*62,11,1.6,3,pale)
     if build.compact then
      part("WindowTransom",px+8,34,z+side*62,9,.9,1,brass,nil,"Metal",nil,false)
      part("WindowMullion",px+8,32,z+side*62,.75,18,1,teal,nil,"SmoothPlastic",nil,false)
     end
    end
   end
  end
  -- Shallow glazed bays and lintels articulate both long side elevations.
  -- They are applied surface detail, not openings through the solid hall.
  for _,side in ipairs({-1,1}) do
   for _,i in ipairs({-1,1}) do
    local bz=z+i*28
    part("SideBayGlass",x+side*74.2,29,bz,.5,23,11,{53,95,99},nil,"SmoothPlastic",nil,false)
    part("SideBayArch",x+side*74.4,41,bz,1,5,12,pale,nil,"SmoothPlastic","Ball",false)
    part("SideBaySill",x+side*75,17,bz,2,1.5,13,brass,nil,"Metal",nil,false)
   end
  end
  part("PortalRecess",x,22,z+61,21,32,2,ink)
  for _,side in ipairs({-1,1})do part("PortalJamb",x+side*14,23,z+65,5,34,7,pale)end
  if build.compact then
   for _,side in ipairs({-1,1}) do
    part("DoorLeaf",x+side*4.8,21,z+62,8.8,29,1,{47,90,89})
    part("DoorPull",x+side*1.8,20,z+63,1,5,1.4,brass,nil,"Metal",nil,false)
   end
  end
  part("PortalLintel",x,42,z+65,33,5,7,brass)
  for _,side in ipairs({-1,1}) do
   part("PortalGable",x+side*8,47,z+65,19,2,12,teal,{0,0,-side*18},"SmoothPlastic")
   part("UpperWingRoof",x+side*39,78,z,34,3,104,teal,nil,"SmoothPlastic")
  end
  -- Four narrow minarets frame the dominant dome, all grounded on terrace/floor.
  for _,tx in ipairs({-250,-60})do for _,tz in ipairs({-227,-53})do
   disk("MinaretPlinth",tx,3,tz,11,6,sand)
   disk("MinaretShaft",tx,36,tz,6.5,66,cream)
   disk("MinaretBalcony",tx,63,tz,10,3,pale)
   disk("MinaretLantern",tx,72,tz,5.5,16,teal)
   disk("MinaretEave",tx,81,tz,8,2,brass,"Metal")
   part("MinaretCap",tx,86,tz,14,12,14,teal,nil,"SmoothPlastic","Ball")
   part("MinaretSpire",tx,96,tz,1.5,12,1.5,brass,nil,"Metal")
  end end
  pavilion("Library",150,-140,94,31,false)
  -- A continuous inset back wall with a clear central opening and shelf bands.
  -- The open front and column structure stay intact.
  for _,side in ipairs({-1,1}) do
   local bx=150+side*25
   part("LibraryBackWall",bx,17,-173,34,25,4,cream)
   part("LibraryShelfInset",bx,18,-170.8,29,20,.4,ink,nil,"SmoothPlastic",nil,false)
   for _,h in ipairs({13,20}) do
    part("LibraryShelfBand",bx,h,-170.4,29,1,1,brass,nil,"SmoothPlastic",nil,false)
   end
  end
  -- Library-side faculty wings taper down from the palace skyline, forming a civic block.
  for _,wing in ipairs({{65,38},{244,26}})do
   local wx,wh=wing[1],wing[2]
   part("FacultyPlinth",wx,1,-145,48,2,112,sand)
   part("FacultyWing",wx,wh/2+2,-145,42,wh,104,cream)
   part("FacultyCornice",wx,wh+3,-145,48,3,112,pale)
   part("FacultyTealRoof",wx,wh+6,-145,46,3,110,teal,nil,"SmoothPlastic")
   for j=-1,1 do part("FacultyFrontPier",wx+j*16,wh/2+2,-91,3,wh,3,pale)end
   for _,side in ipairs({-1,1})do part("FacultyWindow",wx+side*8,wh*.55,-91.5,8,wh*.42,1.5,ink)end
  end
  part("LibraryGardenTerrace",150,1,-225,200,2,34,pale)
  part("LibraryGardenSoil",150,2.15,-225,192,.3,26,earth,nil,"Ground")
  for _,tx in ipairs({85,150,215})do tree("LibraryTerraceCypress",tx,-225,2.3,1.4)end
  -- Open southeast cloister: real columns and high roof, no interior blocker.
  for i=0,4 do
   disk("CloisterColumn",78+i*35,17,88,3,34,cream)
   disk("CloisterColumn",78+i*35,17,132,3,34,cream)
  end
  part("CloisterArchitrave",148,36,110,160,4,58,pale)
  part("CloisterTealRoof",148,41,110,166,6,64,teal,nil,"SmoothPlastic")
  for i=0,3 do tree("CloisterCypress",85+i*42,190,0,1.1)end
  local fx,fz=-147,137
  -- Low planting beds flank the fountain without crossing either main axis.
  for _,side in ipairs({-1,1}) do
   local bx=fx+side*78
   part("CourtPlantingBed",bx,.35,fz,18,.7,34,sand,nil,"SmoothPlastic",nil,false)
   part("CourtPlantingSoil",bx,.75,fz,15,.2,31,earth,nil,"Ground",nil,false)
   for j=-1,1 do
    part("CourtShrub",bx,2.6,fz+j*10,8,4,7,{79,126,72},nil,"SmoothPlastic","Ball",false)
   end
  end
  -- Two flush borders lead from the south steps toward the fountain plaza.
  for _,side in ipairs({-1,1}) do
   part("ApproachBorder",fx+side*19,.075,4,1.2,.15,110,brass,nil,"SmoothPlastic",nil,false)
  end
  disk("FountainPlaza",fx,.12,fz,66,.24,sand)
  disk("FountainFoundation",fx,.65,fz,36,1.3,cream)
  disk("BasinFoot",fx,1.6,fz,33,1.2,sand)
  disk("Basin",fx,2,fz,30,4,pale)
  disk("Water",fx,4.08,fz,26,.16,water,"SmoothPlastic",false)
  disk("Pedestal",fx,10,fz,5,12,cream)
  disk("PedestalBase",fx,5.4,fz,8,2.4,sand)
  disk("PedestalCollar",fx,15.3,fz,7,1.4,brass,"Metal")
  disk("UpperBowl",fx,17,fz,15,3,pale)
  disk("UpperWater",fx,18.58,fz,12,.16,water,"SmoothPlastic",false)
  part("FountainCrown",fx,21,fz,5,5,5,brass,nil,"Metal","Ball")
  for i=0,7 do
   local angle=i*math.pi/4
   part("FountainRim",fx+29*math.cos(angle),4.5,fz+29*math.sin(angle),23,2,3,pale,{0,90-math.deg(angle),0})
  end
  for _,side in ipairs({-1,1})do
   tree("FountainCypress",fx+side*54,fz+46,0,1.05)
   part("CourtBench",fx+side*43,2.5,fz-42,23,2,7,cream)
   part("CourtBenchBack",fx+side*43,5.5,fz-45,23,4,1.2,sand)
  end
 elseif id=="02" or id==2 then
  -- A single warm shore amphitheater, six continuous radial tiers with cardinal cuts.
  -- Two-stud rises are reachable; every tier is a true solid, not a cosmetic shell.
  for quadrant=0,3 do
   for tier=0,5 do
    local r=88+tier*14
    for segment=0,3 do
     local angle=math.rad(quadrant*90+24+segment*14)
     local length=2*r*math.tan(math.rad(6.8))
     part("BowlTier",r*math.cos(angle),tier+1,r*math.sin(angle),length,2*(tier+1),14,
      {159,149,129},{0,90-math.deg(angle),0},"SmoothPlastic")
     part("BowlCoping",r*math.cos(angle),2*(tier+1)+.3,r*math.sin(angle),length,.6,2.2,pale,{0,90-math.deg(angle),0})
    end
   end
  end
  -- An asymmetrical musician's dais gives the bowl an orientation while preserving both axes.
  part("MusicDais",-51,1,-51,40,2,40,sand)
  part("MusicBackdrop",-51,8,-70,38,14,2,cream)
  for _,xx in ipairs({-67,-35})do
   disk("StagePier",xx,11,-68,2.2,22,pale)
   part("StageBanner",xx,17,-66,4,9,1,teal,nil,"Fabric")
  end
  part("StagePediment",-51,24,-68,40,3,5,pale)
  for _,position in ipairs({{49,49},{-49,49},{49,-49}})do
   disk("ArenaCover",position[1],3,position[2],4,6,sand)
   disk("CoverCoping",position[1],6.5,position[2],5,1,pale)
  end
  -- Shore-tone outer accent piers, kept off entry paths.
  for _,sx in ipairs({-1,1})do for _,sz in ipairs({-1,1})do
   disk("OuterPier",sx*119,7,sz*119,4,14,cream)
   part("OuterPierCap",sx*119,15,sz*119,9,2,9,brass,nil,"Metal")
  end end
 elseif id=="04" or id==4 then
  -- Long planted ribbons, cafe court and water pergola replace four identical planters.
  for _,bed in ipairs({{-110,-105},{110,105}})do
   local x,z=bed[1],bed[2]
   part("LongGardenKerb",x,.75,z,68,1.5,122,cream)
   part("LongGardenSoil",x,1.65,z,62,.3,116,earth,nil,"Ground")
   for i=-1,1 do
    tree("RamblaCypress",x,z+i*36,1.8,1.3)
    for _,side in ipairs({-1,1})do
     part("HedgeMound",x+side*23,4,z+i*36,14,5,22,leaf,nil,"Grass","Ball")
     part("FlowerRibbon",x+side*26,2.6,z+i*36,6,1.2,26,i%2==0 and {209,157,118} or pale,nil,"Grass")
    end
   end
   for _,side in ipairs({-1,1})do
    part("GardenBench",x+side*46,2.5,z,6,2,28,pale)
    part("GardenBenchBack",x+side*48,5,z,1.3,4,28,sand)
   end
  end
  -- Southwest terrace cafe: two separate stalls and a shared shallow courtyard.
  part("CafePaving",-130,.15,105,146,.3,126,sand,nil,"Cobblestone")
  for _,x in ipairs({-174,-94})do
   part("CafeCounter",x,4,145,30,8,12,earth,nil,"Wood")
   for _,side in ipairs({-1,1})do part("CafePost",x+side*18,11,145,2.5,22,2.5,cream)end
   part("CafeCanopy",x,24,145,42,3,26,teal,nil,"Slate")
   for stripe=-2,2 do part("CanvasStripe",x+stripe*7,25.56,145,3,.12,26,pale,nil,"Fabric",nil,false)end
   disk("CafeTableStem",x,3.5,90,1.5,7,earth,"Wood")
   disk("CafeTableTop",x,7.5,90,9,1,pale)
   for _,side in ipairs({-1,1})do part("CafeSeat",x+side*16,2.5,90,7,5,7,cream)end
  end
  -- A landmark-scale garden reading house closes the north vista behind the pergola.
  part("ReadingHousePlinth",130,1,-177,146,2,34,sand)
  part("ReadingHouse",130,18,-177,140,34,30,cream)
  part("ReadingHouseCornice",130,36,-177,146,3,34,pale)
  part("ReadingHouseRoof",130,40,-177,144,5,32,teal,nil,"Slate")
  for _,wx in ipairs({82,130,178})do
   part("ReadingHouseArcadeReveal",wx,19,-161,26,23,1.5,ink)
  end
  for _,wx in ipairs({106,154})do part("ReadingHousePier",wx,19,-159,4,32,4,pale)end
  -- Northeast water garden: elongated rill + a long open pergola.
  part("RillBasin",130,1,-95,112,2,30,pale)
  part("RillWater",130,2.08,-95,106,.16,24,water,nil,"SmoothPlastic",nil,false)
  for i=0,4 do
   for _,z in ipairs({-151,-119})do part("PergolaPost",70+i*30,11,z,3,22,3,earth,nil,"Wood")end
   part("PergolaRafter",70+i*30,24,-135,4,3,46,cream,nil,"Wood")
  end
  for _,z in ipairs({-151,-119})do part("PergolaBeam",130,22,z,132,3,4,earth,nil,"Wood")end
  for _,x in ipairs({65,195})do
   tree("WaterCourtCypress",x,-60,0,1)
   part("WaterCourtBench",x,2.5,-79,16,2,6,pale)
  end
 else
  error("DistrictWest received unsupported zone "..tostring(id))
 end
 return serial
end
