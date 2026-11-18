-- Original coastal districts, isolated MAP-10 v2.1 preview only.
-- Inspected IMG_1526 master blueprint; vault-derived flow/landmark constraints
-- in docs/MAP10_REVIEW.md and MAP10_ART_FINISH.md. No remote assets.
return function(build,id,spec)
 local cx,y,cz=table.unpack(spec.center)
 local w,d=table.unpack(spec.size)
 local sand={220,202,157};local timber={122,85,52};local dockTimber={156,109,69};local teal={38,118,126}
 local dark={34,49,61};local gold={192,151,70};local cyan={60,220,225}
 local function p(n,x,h,z,s,c,rot,mat,tags)
  build:part('Coast'..id..n,{cx+x,y+h,cz+z},s,c,true,rot,mat or 'SmoothPlastic',tags or {'CoastalPOI'})
 end
 local function disk(n,x,h,z,r,thick,c,mat)
  build:disk('Coast'..id..n,cx+x,y+h,cz+z,r,thick,c,true,mat or 'SmoothPlastic',{'CoastalPOI'})
 end
 local function steps(n,x,z,width,count,depth,joinDeck)
  for j=1,count do
   local height=j*1.2-(joinDeck and j==count and .02 or 0)
   p(n..j,x,height/2,z+(j-1)*depth,{width,height,math.abs(depth)},sand,nil,'Sandstone')
  end
 end
 if id=='03' then
  -- Stage is in NW quadrant. A broad three-step approach starts outside cross.
  local sx=-w*.26;local sz=-d*.25
  p('Stage',sx,1.8,sz,{140,3.6,56},dockTimber,nil,'SmoothPlastic',{'WalkablePOI','DJStage'})
  steps('StageStep',sx,sz+34,64,3,-5,true)
  for _,side in ipairs({-1,1}) do
   p('Speaker'..side,sx+side*55,13.6,sz-8,{16,20,16},dark)
   for k=1,2 do
    -- Front grille is collidable because it extends from a reachable speaker.
    p('Grille'..side..k,sx+side*55,8+k*6,sz+.15,{12,4,.3},teal,nil,'Metal')
   end
   p('CanopyPost'..side,sx+side*66,20,sz-21,{3,36,3},gold,nil,'Metal')
  end
  for _,side in ipairs({-1,1}) do p('CanopyWing'..side,sx,39,sz-5+side*15,{148,3,32},teal,{side*12,0,0},'Metal') end
  p('CanopyRidge',sx,43,sz-5,{150,2,3},gold,nil,'Metal')
  p('MixDesk',sx,6.6,sz-5,{28,6,8},dark)
  for k=1,5 do p('Equalizer'..k,sx-12+k*4,12+k%3*2,sz-25,{2,12+(k%3)*4,1},cyan,nil,'Neon') end
  -- Open-sided shaded booths in NE; no enclosing walls or hidden doors.
  for i=1,3 do
   local x=65+i*72
   p('BoothCounter'..i,x,3.5,-76,{44,7,12},sand,nil,'Sandstone')
   for _,s in ipairs({-1,1}) do p('BoothPost'..i..s,x+s*22,11,-91,{2,22,2},timber,nil,'Wood') end
   p('BoothRoof'..i,x,23,-80,{48,2,34},i%2==0 and gold or teal,nil,'Fabric')
  end
  -- SE dance circle is flush relief; speakers/stalls never invade the cross.
  disk('DanceDeck',w*.25,.1,d*.25,45,.2,timber,'WoodPlanks')
  disk('DanceInlay',w*.25,.22,d*.25,31,.04,teal,'Metal')
  for i=1,8 do
   local a=i*math.pi/4
   p('DanceMark'..i,w*.25+38*math.cos(a),.24,d*.25+38*math.sin(a),{5,.06,2},gold,{0,-math.deg(a),0},'Metal')
  end
  -- SW seating with generous gaps, low dock bollards and warm lamp fixtures.
  for i=1,4 do
   local x=-w*.4+(i-1)*66
   p('Bench'..i,x,2.2,75,{36,1,7},timber,nil,'WoodPlanks')
   for _,s in ipairs({-1,1}) do p('BenchLeg'..i..s,x+s*13,1,75,{2,2,5},dark,nil,'Metal') end
   p('BenchBack'..i,x,4.5,78,{36,4,1},timber,nil,'WoodPlanks')
  end
  for _,x in ipairs({-w*.4,w*.4}) do
   p('LampPole'..x,x,9,105,{1.5,18,1.5},dark,nil,'Metal')
   p('LampHousing'..x,x,19,105,{4,3,4},gold,nil,'Metal')
   p('LampGlow'..x,x,19,107.1,{2,1.8,.2},{255,209,130},nil,'Neon')
  end

  -- Boardwalk rebuild: broad timber precincts and dressed stage, not isolated toys.
  for _,sign in ipairs({-1,1}) do
   for j=1,10 do
    local x=sign*(42+j*28)
    p('PromenadePlank'..sign..j,x,.12,80,{26,.24,92},dockTimber,nil,'SmoothPlastic')
   end
  end
  for j=1,9 do
   local x=sx-64+(j-1)*16
   p('StageFascia'..j,x,1.8,sz+28.3,{13,3,.6},j%2==0 and teal or gold,nil,'Wood')
   p('StageBackFin'..j,x,19,sz-26,{3,31,3},timber,nil,'Wood')
  end
  for _,side in ipairs({-1,1}) do
   p('StageCornice'..side,sx,35,sz+side*24,{140,3,3},gold,nil,'Metal')
   for j=1,3 do p('StageLight'..side..j,sx-45+j*23,33,sz+side*24,{4,2,4},{255,207,126},nil,'Neon') end
  end
  -- Four shaded coastal pergola bays frame a sitting promenade without walls.
  for j=1,4 do
   local x=-w*.4+(j-1)*66
   for _,side in ipairs({-1,1}) do
    p('PergolaPier'..j..side,x+side*24,12,101,{3,24,3},sand,nil,'Sandstone')
    p('PergolaFoot'..j..side,x+side*24,1,101,{6,2,6},sand,nil,'Sandstone')
   end
   p('PergolaLintel'..j,x,25,101,{54,3,6},timber,nil,'Wood')
   for k=1,3 do p('PergolaRafter'..j..k,x-20+k*10,27,91,{3,2,28},timber,nil,'Wood') end
   disk('Planter'..j,x,2,112,7,4,sand,'Sandstone')
   p('PalmTrunk'..j,x,13,112,{3,22,3},timber,{0,0,6},'Wood')
   for _,side in ipairs({-1,1}) do p('PalmCrown'..j..side,x+side*6,25,112,{17,3,10},{69,120,81},{0,0,side*13},'Grass') end
  end
  -- Merchant goods and striped canopy edges give the market a human scale.
  for j=1,3 do
   local x=65+j*72
   p('MarketPedestal'..j,x,.4,-80,{54,.8,48},timber,nil,'WoodPlanks')
   for k=1,4 do
    p('AwningStripe'..j..k,x-24+k*10,24.1,-80,{5,.2,34},sand,nil,'Fabric')
    p('GoodsCrate'..j..k,x-20+k*8,9,-76,{6,4,6},k%2==0 and teal or timber,nil,'Wood')
   end
   p('MarketSign'..j,x,16,-62,{28,5,1},dark,nil,'Wood')
  end
  for _,x in ipairs({w*.25-55,w*.25+55}) do
   p('DancePylon'..x,x,15,80,{5,30,5},teal,nil,'Metal')
   p('DanceCap'..x,x,31,80,{9,3,9},gold,nil,'Metal')
  end
 elseif id=='10' then
  -- Four recognizable sub-POIs: reef shrine, shell arch, lookout, coral grove.
  -- Underlying district platform stays intact; pools are low safe mosaics, not water traps.
  local qx=w*.24;local qz=d*.24
  disk('ReefPool',-qx,.1,-qz,55,.2,{62,151,165},'Glass')
  for i=1,10 do
   local a=i*math.pi/5
   disk('PoolRim'..i,-qx+58*math.cos(a),1.3,-qz+58*math.sin(a),5,2.6,sand,'Sandstone')
  end
  disk('ShrineIsland',-qx,1.2,-qz,20,2.4,sand,'Sandstone')
  steps('ShrineSteps',-qx,-qz+26,16,2,-4)
  disk('ShrinePlinth',-qx,4,-qz,8,3.2,teal,'Slate')
  p('ShrineCrystal',-qx,11,-qz,{5,11,5},cyan,{0,45,0},'Neon')
  -- Wide shell gate opening is physically empty, readable from cross.
  for _,s in ipairs({-1,1}) do
   p('ShellPier'..s,qx+s*26,17,-qz,{10,34,14},sand,{0,0,s*8},'Sandstone')
   p('ShellShoulder'..s,qx+s*15,34,-qz,{29,9,14},{237,216,173},{0,0,s*24},'Sandstone')
  end
  p('ShellKeystone',qx,39,-qz,{10,10,16},teal,nil,'Slate')
  for i=1,6 do p('ShellInlay'..i,qx-21+i*6,.15,-qz+30,{3,.3,10},gold,nil,'Metal') end
  -- Accessible lookout at only7.2studs: six1.2stud steps, open skyline.
  steps('LookoutSteps',-qx,qz-48,32,6,6,true)
  p('LookoutDeck',-qx,3.6,qz,{64,7.2,46},sand,nil,'Sandstone',{'WalkablePOI','ReefLookout'})
  for _,s in ipairs({-1,1}) do
   p('LookoutSideRail'..s,-qx+s*31,10,qz,{2,5.6,46},timber,nil,'Wood')
  end
  p('LookoutRearRail',-qx,10,qz+22,{64,5.6,2},timber,nil,'Wood')
  p('TelescopeStand',-qx,11,qz+4,{3,7.6,3},gold,nil,'Metal')
  p('Telescope',-qx,15,qz+4,{5,5,17},dark,{-12,0,0},'Metal')
  -- Coral silhouettes, solid trunks with no promised passages through branches.
  for i=1,5 do
   local a=i*math.pi*.4;local x=qx+32*math.cos(a);local z=qz+32*math.sin(a)
   local c=i%2==0 and {220,126,110} or {134,129,190}
   disk('CoralRock'..i,x,2,z,9,4,sand,'Sandstone')
   p('CoralTrunk'..i,x,10,z,{4,18,4},c,nil,'Slate')
   for _,s in ipairs({-1,1}) do p('CoralBranch'..i..s,x+s*4,16,z,{3,11,3},c,{0,0,-s*38},'Slate') end
  end

  -- Broken limestone ring and tidal strata enlarge the reef's silhouette.
  -- They stay outside the arrival cross and leave the central shrine approach open.
  for j=1,7 do
   local a=math.rad(20+j*35);local x=-qx+70*math.cos(a);local z=-qz+70*math.sin(a)
   disk('AtollFoot'..j,x,2,z,16,4,{151,156,139},'Slate')
   disk('AtollLedge'..j,x,6,z,13,4,sand,'Sandstone')
   p('AtollCrown'..j,x,11+j%3*4,z,{14,10+j%3*8,14},{189,181,151},{0,j*28,0},'Sandstone')
  end
  -- Tall fossil ribs behind shell gate tell a lost tidal observatory story.
  for _,side in ipairs({-1,1}) do
   for j=1,3 do
    local x=qx+side*(31+j*10);local z=-qz-25-j*5
    p('FossilBase'..side..j,x,3,z,{10,6,18},{155,163,153},nil,'Slate')
    p('FossilRib'..side..j,x,15+j*5,z,{5,24+j*10,7},sand,{0,0,side*(7+j*2)},'Sandstone')
    p('FossilCrown'..side..j,x-side*5,29+j*10,z,{16,5,7},sand,{0,0,side*25},'Sandstone')
   end
  end
  for j=1,4 do
   p('GatePaving'..j,qx,.12,-qz+10+j*12,{48,.24,10},j%2==0 and sand or teal,nil,'Sandstone')
  end
  -- Observatory on the lookout: open colonnade, broken roof, brass lens.
  for _,side in ipairs({-1,1}) do
   for j=1,2 do
    local x=-qx+side*25;local z=qz-10+(j-1)*24
    disk('ObservatoryFoot'..side..j,x,8,z,4,1.6,sand,'Sandstone')
    disk('ObservatoryColumn'..side..j,x,20,z,2.2,24,sand,'Sandstone')
    disk('ObservatoryCapital'..side..j,x,32,z,4,2,teal,'Slate')
   end
   p('ObservatoryBeam'..side,-qx+side*25,34,qz+2,{7,3,36},sand,nil,'Sandstone')
  end
  p('ObservatoryRearArch',-qx,34,qz+14,{54,4,8},sand,nil,'Sandstone')
  for j=1,3 do p('ObservatoryRoofRib'..j,-qx-23+j*12,37,qz+8,{4,3,24},teal,nil,'Slate') end
  -- Coral is a clustered fossil garden, with a low tide path around its heart.
  disk('CoralMosaic',qx,.15,qz,54,.3,{71,139,145},'Slate')
  for j=1,9 do
   local a=j*math.pi*2/9;local x=qx+61*math.cos(a);local z=qz+61*math.sin(a)
   disk('CoralStratum'..j,x,2,z,11,4,{166,174,154},'Sandstone')
   p('CoralShard'..j,x,6+j%3,z,{6,8+j%3*2,5},j%2==0 and sand or teal,{0,j*34,0},'Slate')
  end
  for _,side in ipairs({-1,1}) do
   p('ReefSeat'..side,qx+side*38,2.2,qz-52,{20,4.4,6},sand,nil,'Sandstone')
  end
 else
  error('DistrictCoast only builds03 or10')
 end
end
