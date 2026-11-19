-- Original MAP10 v2.1 east district architecture. No assets, scripts or remote dependencies.
-- Read actual IMG_1526 and vault-backed MAP10_ART_FINISH before authoring.
-- Local quadrant construction deliberately preserves the full 44-stud route cross.
return function(build,id,spec)
 local c=spec.center;local width,depth=spec.size[1],spec.size[2]
 local count=0;local prefix='Z'..id..'East'
 local function part(name,x,y,z,sx,sy,sz,color,rot,material,shape)
  -- Full Euler world-AABB guards. Only supported high architecture may span a lane.
  local rx,ry,rz=math.rad(rot and rot[1] or 0),math.rad(rot and rot[2] or 0),math.rad(rot and rot[3] or 0)
  local cx,sx0,cy,sy0,cz,sz0=math.cos(rx),math.sin(rx),math.cos(ry),math.sin(ry),math.cos(rz),math.sin(rz)
  local ex=(math.abs(cy*cz+sy0*sx0*sz0)*sx+math.abs(-cy*sz0+sy0*sx0*cz)*sy+math.abs(sy0*cx)*sz)/2
  local ey=(math.abs(cx*sz0)*sx+math.abs(cx*cz)*sy+math.abs(sx0)*sz)/2
  local ez=(math.abs(-sy0*cz+cy*sx0*sz0)*sx+math.abs(sy0*sz0+cy*sx0*cz)*sy+math.abs(cy*cx)*sz)/2
  assert((math.abs(x)-ex>=22 and math.abs(z)-ez>=22) or y-ey>=80,'east cross intrusion '..name)
  assert(math.abs(x)+ex<=width/2-32 and math.abs(z)+ez<=depth/2-32,'east perimeter intrusion '..name)
  count+=1
  build:part(prefix..name,{c[1]+x,c[2]+y,c[3]+z},{sx,sy,sz},color,true,rot,material or 'Concrete',y-ey>=80 and {'EastArchitecture','SolidLandmark','OverheadLandmark'} or {'EastArchitecture','SolidLandmark'},shape)
 end
 local function disk(name,x,y,z,r,h,color,material)
  assert(math.abs(x)-r>=22 and math.abs(z)-r>=22,'east disk cross '..name)
  assert(math.abs(x)+r<=width/2-32 and math.abs(z)+r<=depth/2-32,'east disk perimeter '..name)
  count+=1;build:disk(prefix..name,c[1]+x,c[2]+y,c[3]+z,r,h,color,true,material or 'Concrete',{'EastArchitecture','SolidLandmark'})
 end
 local function inlay(name,x,z,sx,sz,color,yaw)
  -- Sub-stud paint-like floor markings, never a fake walkable solid or blocking sheet.
  count+=1;build:part(prefix..name,{c[1]+x,c[2]+.025,c[3]+z},{sx,.05,sz},color,false,{0,yaw or 0,0},'Neon',{'FlushInlay'})
 end
 local dark={39,37,57};local stone={78,72,102};local metal={94,94,116}
 local violet={114,61,178};local cyan={60,193,219};local brass={174,132,70}
 if id=='06' then
  -- One fitted monumental bowl: stepped concave seating, massive exterior skin,
  -- continuous cornice rhythm and four open entrance slots, not four pavilions.
  for k=0,31 do
   local angle=k*11.25+5.625;local a=math.rad(angle);local ca,sa=math.cos(a),math.sin(a)
   if math.abs(ca)>.22 and math.abs(sa)>.22 then
    for tier=1,4 do
     local r=155+tier*22;local h=12+tier*14
     part('BowlSeat'..k..'_'..tier,r*ca,h/2,r*sa,math.pi*r/16+1,h,22,tier%2==0 and stone or dark,{0,90-angle,0})
    end
    local r=258
    part('ArenaFacade'..k,r*ca,45,r*sa,52,90,17,violet,{0,90-angle,0},'Concrete')
    part('ArenaCornice'..k,r*ca,91,r*sa,54,7,22,metal,{0,90-angle,0},'Metal')
    part('ArenaSignal'..k,r*ca,96,r*sa,37,2,7,cyan,{0,90-angle,0},'Neon')
    part('FacadeButtress'..k,269*ca,48,269*sa,7,96,14,dark,{0,90-angle,0},'Metal')
    -- Raised color-packed seat blocks evoke audience bands without NPC cost.
    part('CrowdBand'..k,214*ca,61,214*sa,33,5,4,k%3==0 and brass or {83,128,164},{0,90-angle,0},'SmoothPlastic')
   end
  end
  for sx=-1,1,2 do for sz=-1,1,2 do
   local x,z=sx*176,sz*176
   part('ArenaTower'..sx..sz,x,65,z,26,130,26,dark,nil,'Metal')
   part('ArenaTowerCap'..sx..sz,x,134,z,34,8,34,violet,nil,'Metal')
   part('ArenaTowerSignal'..sx..sz,x,102,z-14,8,48,2,cyan,nil,'Neon')
   part('ArenaCover'..sx..sz,sx*82,7,sz*82,18,14,18,stone)
   inlay('CombatCorner'..sx..sz,sx*65,sz*65,42,2,cyan,45*sx*sz)
  end end
 elseif id=='07' then
  local basalt={43,38,39};local ash={78,59,53};local oxide={113,65,42}
  local lava={242,88,15};local hot={255,166,34}
  -- Asymmetric dominant mountain, broad continuous overlapping rock mass.
  -- Its open cleavage faces the plaza; all apparent rock is physical.
  local x,z=184,164
  if build.compact then
   -- Six inclined basalt faces converge on the same crater. The open side
   -- frames the molten chute instead of enclosing it with overlapping cubes.
   for k=0,7 do
    if k~=5 and k~=6 then
     local a=math.rad(k*45)
     local nx,nz=math.cos(a),math.sin(a)
     local yaw=math.deg(math.atan2(-nx,-nz))
     part("CalderaFace"..k,x+nx*59,89,z+nz*59,71,178,116,
      k%3==0 and ash or basalt,{0,yaw,0},"Basalt","Wedge")
     part("CalderaApron"..k,x+nx*104,19,z+nz*104,83,38,56,
      k%3==0 and oxide or ash,{0,yaw,0},"Ground","Wedge")
    end
   end
  else
  for layer=0,4 do
   local r=124-layer*21;local h=28+layer*39
   for k=0,7 do
    local a=math.rad(k*45);local side=math.cos(a);local front=math.sin(a)
    if k~=5 and k~=6 then
     part('MountainMass'..layer..'_'..k,x+side*r*.47,h/2,z+front*r*.47,r*.95,h,r*.72,(k+layer)%2==0 and basalt or ash,{0,k*45,0},'Slate')
    end
   end
  end
  for k=0,7 do
   if k~=5 and k~=6 then
    local a=math.rad(k*45)
    part('MountainSlope'..k,x+math.cos(a)*57,72,z+math.sin(a)*57,61,144,93,k%2==0 and ash or basalt,{0,90-k*45,0},'Slate','Wedge')
   end
  end
  -- Broad asymmetric mountain skirt spreads into the available quadrant instead
  -- of leaving a tower-sized rock pile in an empty square. All pieces overlap
  -- the core or neighboring skirt; none enter the arterial/perimeter corridors.
  for i,b in ipairs({
   {82,166,106,62,166,0},{272,174,137,76,174,180},
   {180,77,218,52,99,0},{183,263,208,66,78,180},
   {86,83,100,43,104,0},{279,85,112,45,104,90},
   {86,257,108,40,94,270},{278,257,120,49,96,180},
  })do
   part('MountainSkirt'..i,b[1],b[4]/2,b[2],b[3],b[4],b[5],i%2==0 and ash or basalt,nil,'Slate','Wedge')
   -- Fitted dark-red mineral ribs break the large facets without disconnected lava.
   part('SkirtMineral'..i,b[1],b[4]*.22,b[2],b[3]*.62,3,b[5]*.34,oxide,nil,'Slate')
  end
  end
  for k=0,5 do
   local a=math.rad(k*60);local px=x+math.cos(a)*27;local pz=z+math.sin(a)*27
   part('CraterTooth'..k,px,193+(k%2)*9,pz,25,52+(k%2)*18,22,basalt,{0,k*60,0},'Slate','Wedge')
  end
  -- A broad stepped molten cleavage is fitted between dark broken rock cheeks.
  for j=0,5 do
   local py=13+j*29;local pz=63+j*16
   part('MoltenCleavage'..j,x-12,py,pz,27-j*2,5,29,j%2==0 and hot or lava,nil,'Neon')
   for side=-1,1,2 do
    part('CleavageCheek'..j..side,x-12+side*(26-j),py-3,pz,13,26,32,side<0 and basalt or oxide,{0,side*12,0},'Slate')
   end
  end
  -- Continuous solid molten ribbon joins the stepped ledges into one readable rift.
  part('ContinuousLavaFall',x-12,88,104,21,3,169,lava,{-61.1,0,0},'Neon')
  inlay('LavaDelta',139,65,104,41,lava,-12)
  for j=0,6 do inlay('LavaBranch'..j,72+j*17,43+j*3,8,33,hot,-25) end
  -- Secondary black fortress at the opposite corner, distinct lower skyline.
  local fx,fz=-166,-160
  part('FortressKeep',fx,38,fz,126,76,105,basalt,nil,'Basalt')
  part('KeepCornice',fx,78,fz,138,8,116,oxide,nil,'Slate')
  for side=-1,1,2 do
   part('FortressTower'..side,fx+side*68,56,fz,34,112,40,ash,nil,'Slate')
   part('FortressCrown'..side,fx+side*68,116,fz,41,8,47,basalt,nil,'Slate')
   part('FortressFurnace'..side,fx+side*34,43,fz-53,13,35,2,lava,nil,'Neon')
  end
  for i=0,6 do part('KeepMerlon'..i,fx-57+i*19,88,fz-52,10,15,10,basalt,nil,'Slate') end
  -- Lower broken ridge field and quarry monuments: foreground/intermediate scale.
  for k=0,11 do
   local px=-260+(k%4)*52;local pz=78+math.floor(k/4)*61;local h=18+(k%5)*10
   part('RiftOutcrop'..k,px,h/2,pz,35,h,38,k%2==0 and ash or basalt,{0,k*17,0},'Slate','Wedge')
   part('OreSeam'..k,px,h*.55,pz-19.5,9,3,1,oxide,nil,'Slate')
  end
  for j=0,5 do
   part('ForgePillar'..j,72+j*37,22,-165,15,44,18,basalt,nil,'Slate')
   part('ForgeLantern'..j,72+j*37,47,-165,10,6,10,hot,nil,'Neon')
  end
  part('ForgeBeam',165,48,-165,213,12,22,ash,nil,'Metal')
  for j=0,4 do part('ForgeAnvil'..j,78+j*40,7,-110,25,14,23,metal,nil,'Metal') end
 elseif id=='08' then
  local pale={148,127,181};local crystal={157,86,209};local deep={42,28,65}
  -- One dominant citadel gateway across the northern half. The main lane passes
  -- through a genuine 112-stud opening beneath an 80+stud clear high lintel.
  for side=-1,1,2 do
   local x=side*91;local z=157
   part('CitadelFoot'..side,x,12,z,65,24,95,dark,nil,'Slate')
   part('CitadelPier'..side,x,84,z,42,144,57,deep,nil,'Slate')
   part('CitadelFlute'..side,x+side*23,90,z,9,148,63,violet,nil,'Slate')
   part('CitadelCrown'..side,x,160,z,64,18,75,pale,nil,'Slate')
   part('CitadelSpire'..side,x,205,z,43,76,43,crystal,{0,side*25,0},'Glass','Wedge')
   part('CitadelRune'..side,x,102,z-29,7,72,2,cyan,nil,'Neon')
   for j=0,4 do part('PierBand'..side..j,x,30+j*25,z,48,4,64,stone,nil,'Slate') end
  end
  part('VoidHighArch',0,139,157,220,30,64,deep,nil,'Slate')
  part('VoidArchCrown',0,159,157,232,10,76,violet,nil,'Slate')
  part('VoidKeystone',0,186,157,36,45,45,crystal,nil,'Glass','Wedge')
  part('VoidEye',0,151,119,3,94,94,{24,12,44},{0,90,0},'SmoothPlastic','Cylinder')
  for k=0,11 do
   local a=math.rad(k*30)
   part('VoidAureole'..k,52*math.cos(a),151+52*math.sin(a),116,28,6,8,k%3==0 and cyan or pale,{0,0,k*30+90},k%3==0 and 'Neon' or 'Metal')
  end
  part('VoidPupil',0,151,114,2,28,28,crystal,{0,90,0},'Neon','Cylinder')
  -- Subordinate tethered masonry islands/needles are deliberately unequal.
  for i,p in ipairs({{-210,-170,132},{170,-160,158},{-225,165,46},{225,162,54}})do
   local x,z,h=p[1],p[2],p[3];local r=i<=2 and 68 or 37
   disk('SatelliteDais'..i,x,5,z,r,10,dark,'Slate')
   disk('SatelliteRim'..i,x,12,z,r*.8,4,pale,'Slate')
   part('NeedleRoot'..i,x,25,z,i<=2 and 42 or 28,26,i<=2 and 42 or 28,deep,nil,'Slate')
   part('NeedleShaft'..i,x,35+h/2,z,i<=2 and 29 or 19,h,i<=2 and 29 or 19,violet,nil,'Slate')
   part('NeedleCrown'..i,x,40+h,z,i<=2 and 38 or 26,i<=2 and 54 or 36,i<=2 and 38 or 26,crystal,{0,i*37,0},'Glass','Wedge')
   for side=-1,1,2 do
    part('NeedleBrace'..i..side,x+side*21,24,z,8,35,26,stone,nil,'Slate')
    part('NeedleSignal'..i..side,x+side*21,43,z,5,3,12,cyan,nil,'Neon')
   end
  end
  -- Sculpted ruin shoulders anchor the foreground towers to the court. These
  -- ground-grown buttresses and stepped plinths are real collision, not floating islands.
  for side=-1,1,2 do
   for j=0,2 do
    local x=side*(85+j*54);local z=-227+j*10;local h=18+j*13
    part('AstralRuinSkirt'..side..j,x,h/2,z,58,h,76,deep,nil,'Slate','Wedge')
    part('AstralRuinCrest'..side..j,x,h+3,z+22,44,6,19,pale,nil,'Slate')
   end
   -- Sculpted connecting buttress toward the great portal, outside the route.
   part('OrbitalFoundation'..side,side*204,11,82,116,22,80,stone,nil,'Slate')
   part('OrbitalFoundationFacet'..side,side*210,30,94,70,38,56,violet,nil,'Slate','Wedge')
  end
  -- Front ritual court: broken obelisks and gold tether drums frame a clear entry.
  for side=-1,1,2 do
   for j=0,3 do
    local x=side*(65+j*48);local z=-75-(j%2)*25
    part('CourtObelisk'..side..j,x,15+j*4,z,14,30+j*8,17,deep,{0,side*j*12,0},'Slate')
    part('CourtCrown'..side..j,x,36+j*8,z,18,12,21,pale,nil,'Slate','Wedge')
    inlay('CourtGlyph'..side..j,x,z+25,12,2,cyan,0)
   end
  end
  for side=-1,1,2 do
   for j=0,4 do
    part('CitadelButtress'..side..j,side*(54+j*43),18,244,16,36,25,stone,nil,'Slate')
    part('CitadelGoldCap'..side..j,side*(54+j*43),39,244,19,6,28,brass,nil,'Metal')
   end
  end
 end
 assert(count<=260,'east district budget '..id..':'..count)
 return count
end
