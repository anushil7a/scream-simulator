-- Original Zone05 playtest geometry. Explicit Build only; never required by production.
-- Reference: MAP-05 Tidal Bell-Foundry image; vault flow/landmark/clear-lane guidance.
local Geometry={}
local S={}
local cream={215,199,161};local pale={237,221,183};local stone={158,145,119}
local dark={61,68,63};local bronze={101,78,48};local brass={179,140,72};local teal={65,110,113}
local function box(id,pos,size,color,solid,rot,material,tags,shape)
 table.insert(S,{id=id,position=pos,size=size,color=color,collidable=solid==true,
 rotation=rot or {0,0,0},material=material or "Sandstone",tags=tags or {},shape=shape or "Block"})
end
local function disk(id,x,y,z,r,h,color,solid,material,tags)
 box(id,{x,y,z},{h,r*2,r*2},color,solid,{0,0,90},material,tags,"Cylinder")
end
local function ramp(id,a,b,width)
 local dx,dy,dz=b[1]-a[1],b[2]-a[2],b[3]-a[3];local h=math.sqrt(dx*dx+dz*dz);local l=math.sqrt(h*h+dy*dy)
 local normal={-dy*dx/(l*h),h/l,-dy*dz/(l*h)}
 local p={};for i=1,3 do p[i]=(a[i]+b[i])/2-normal[i]*1.5 end
 box(id,p,{width,3,l},pale,true,{-math.deg(math.atan2(dy,h)),math.deg(math.atan2(dx,dz)),0},"Sandstone",{"WalkableRoute"})
end
local function trim(id,a,b,width,height,color,y,material)
 local dx,dz=b[1]-a[1],b[2]-a[2]
 box(id,{(a[1]+b[1])/2,y,(a[2]+b[2])/2},{width,height,math.sqrt(dx*dx+dz*dz)},color,false,{0,math.deg(math.atan2(dx,dz)),0},material)
end
-- Full masonry podium14..48, partitioned around south ramp notch. No overlapping tops.
box("PlatformWest",{238,31,-680},{316,34,520},cream,true)
box("PlatformEast",{602,31,-680},{316,34,520},cream,true)
box("PlatformMiddle",{420,31,-704},{48,34,472},cream,true)
-- Bands only on vertical exterior faces, never layered over walking floor.
for _,side in ipairs({-1,1}) do
 local x=420+side*340
 box("SidePlinth"..side,{x,18,-680},{1,6,520},stone,false)
 box("SideCornice"..side,{x,44,-680},{1.3,3,520},pale,false)
 for j=0,9 do box("SideQuoin"..side.."_"..j,{x,31,-914+j*52},{2,27,5},pale,false) end
end
for _,z in ipairs({-940,-420}) do
 for _,span in ipairs({{80,396},{444,760}}) do
  box("EndBand"..z.."_"..span[1],{(span[1]+span[2])/2,44,z},{span[2]-span[1],3,1.3},pale,false)
 end
end
-- Clear190-stud circular arena; no collision sheet over existing podium.
disk("FoundryArena",420,48.045,-680,95,.09,{181,170,142},false,"Concrete",{"ArenaFloor"})
for i=0,31 do
 local a=i*math.pi/16;local b=(i+1)*math.pi/16
 trim("ArenaInlay"..i,{420+94*math.cos(a),-680+94*math.sin(a)},{420+94*math.cos(b),-680+94*math.sin(b)},.9,.08,brass,48.13,"Metal")
end
-- Eight intentional static cover pillars: exact diameter8, height20, circle75.
for i=0,7 do
 local a=i*math.pi/4;local x,z=420+75*math.cos(a),-680+75*math.sin(a)
 disk("ArenaPillar"..(i+1),x,58,z,4,20,stone,true,"Sandstone",{"ArenaPillar","ArenaPillar"..(i+1),"StaticCover","BeamCover"})
 disk("PillarFootTrim"..i,x,49,z,4.35,1.4,pale,false)
 disk("PillarCapital"..i,x,67.1,z,4.4,1.5,pale,false)
end
-- Low workshops on the west/rear edge leave main lanes and arena unblocked.
for i,t in ipairs({{155,-860,86,58},{155,-720,86,76},{205,-540,130,62}}) do
 local x,z,w,d=table.unpack(t)
 box("Workshop"..i,{x,61,z},{w,26,d},cream,true)
 box("WorkshopCornice"..i,{x,74.2,z},{w+3,2,d+3},pale,false)
 for _,side in ipairs({-1,1}) do
  box("WorkshopRoof"..i.."_"..side,{x+side*w*.24,79,z},{w*.54,3,d+8},teal,false,{0,0,-side*12},"Slate")
 end
 for j=-1,1 do
  box("WorkshopWindow"..i.."_"..j,{x+w/2+.12,63,z+j*d*.27},{.2,11,9},dark,false)
  box("WorkshopWindowSill"..i.."_"..j,{x+w/2+.35,57.2,z+j*d*.27},{.7,.7,11},pale,false)
 end
end
-- Massive bronze industrial frames,45stud tall; bells are segmented open shells.
-- All hanging art is non-queryable; tags identify the exact bell Assembly model.
for i,t in ipairs({{250,-810,24},{420,-840,32},{580,-800,40}}) do
 local x,z,d=table.unpack(t);local half=d/2+11
 for _,side in ipairs({-1,1}) do
  box("Gantry"..i.."Foot"..side,{x+side*half,50,z},{10,4,16},stone,true)
  box("Gantry"..i.."Leg"..side,{x+side*half,70.5,z},{6,45,9},bronze,true,nil,"Metal")
  box("Gantry"..i.."RivetRail"..side,{x+side*half,70,z-4.7},{2,37,.5},brass,false,nil,"Metal")
  for j=0,4 do disk("GantryRivet"..i.."_"..side.."_"..j,x+side*half,55+j*8,z-5,.8,.5,brass,false,"Metal") end
 end
 box("Gantry"..i.."Crossbeam",{x,90,z},{d+30,6,11},bronze,false,nil,"Metal")
 box("Gantry"..i.."BeamLip",{x,93.2,z},{d+34,1.4,13},brass,false,nil,"Metal")
 box("Bell"..i.."Yoke",{x,86,z},{4,8,4},dark,false,nil,"Metal",{"BellAssembly"..i,"ResonanceBell","BeamTarget"})
 local bottom=60;local height=24
 for tier=0,3 do
  local y=bottom+tier*6+3;local radius=d/2*(1-tier*.16)
  for j=0,11 do
   local a=j*math.pi/6
   box("Bell"..i.."Shell"..tier.."_"..j,{x+math.cos(a)*radius,y,z+math.sin(a)*radius},{2*radius*math.tan(math.pi/12)+.2,6,1.6},tier==0 and brass or bronze,false,{0,90-math.deg(a),0},"Metal",{"BellAssembly"..i})
  end
 end
 disk("Bell"..i.."Crown",x,84,z,d*.23,2,brass,false,"Metal",{"BellAssembly"..i})
 disk("Bell"..i.."Clapper",x,62,z,2,7,dark,false,"Metal",{"BellAssembly"..i})
end
-- Tiered dock:48→36→24, both ramps14.04degrees; same clear40stud lane.
ramp("DockUpperRamp",{420,48,-468},{420,36,-420},40)
box("DockUpper",{420,34,-385},{72,4,70},stone,true)
ramp("DockLowerRamp",{420,36,-350},{420,24,-302},40)
box("DockLower",{420,22,-272},{100,4,60},stone,true)
for _,tier in ipairs({{34,-385,70,72},{22,-272,60,100}}) do
 local y,z,length,width=table.unpack(tier)
 for _,side in ipairs({-1,1}) do
  for j=0,2 do
   box("DockSupport"..z.."_"..side.."_"..j,{420+side*(width/2-7),y/2-1,z-length/2+8+j*(length-16)/2},{10,y-2,10},cream,true)
  end
 end
end
-- The acoustic lighthouse sits on its OWN rocky octagonal islet, approached east.
-- Wide continuous causeway top48.12; individual arch voussoirs leave real gaps.
box("LighthouseCauseway",{782,46.12,-650},{44,4,32},pale,true,nil,"Sandstone",{"WalkableRoute"})
for _,cx in ipairs({782}) do
 for _,side in ipairs({-1,1}) do
  box("ArcadePier"..cx.."_"..side,{cx+side*17,22,-650},{7,16,25},cream,true)
 end
 for j=0,8 do
  local a=(j+.5)*math.pi/9
  box("ArchStone"..cx.."_"..j,{cx+17*math.cos(a),27+17*math.sin(a),-650},{6.3,5,25},cream,false,{0,0,math.deg(a)+90})
 end
end
-- Eight sides around an octagonal island support and lighthouse base.
disk("LighthouseIsland",840,31,-650,60,34,stone,true)
for i=0,7 do
 local a=i*math.pi/4
 box("IslandRock"..i,{840+math.cos(a)*48,20,-650+math.sin(a)*48},{36,30,26},stone,false,{i%2*8,90-math.deg(a),i%3*5},"Rock")
end
disk("LighthouseBase",840,54,-650,24,12,pale,true)
disk("LighthousePlinth",840,61,-650,20,2,stone,false)
for tier=0,5 do
 local radius=15-tier*.9;local y=62+tier*19+9.5
 disk("LighthouseShaft"..tier,840,y,-650,radius,19,cream,false,"Sandstone",{"HeroLandmark"})
 disk("LighthouseBand"..tier,840,y+8.8,-650,radius+.6,1.5,pale,false)
end
-- Lantern gallery at176, roof214, needle crystal228. Ground48→top228=180.
disk("LanternGallery",840,179,-650,19,4,pale,false)
for i=0,7 do
 local a=i*math.pi/4
 box("LanternColumn"..i,{840+14*math.cos(a),195,-650+14*math.sin(a)},{2,30,2},bronze,false,nil,"Metal")
end
disk("LanternCrown",840,211,-650,17,4,brass,false,"Metal")
box("Beacon",{840,220,-650},{10,16,10},{0,240,255},false,{0,45,0},"Neon",{"HeroLandmark","AcousticBeacon"})
-- Scalloped coastal rockwork stays below walkable podium and dock approach.
for i=0,8 do
 local x=105+i*75
 if x<370 or x>470 then
  box("CoastalFoot"..i,{x,8,-413},{64,20,28},stone,false,{0,-9+i%3*9,i%2*5},"Rock")
  box("CoastalStratum"..i,{x,25,-419},{67,10,9},cream,false,{0,0,0},"Sandstone")
 end
end
-- Visual readback pass: shape uphill backdrop, separate the trade yards and
-- add cyan wayfinding rhythm. No walking/beam collision was added by this pass.
local moss={111,128,83};local rockA={105,113,102};local rockB={144,143,125}
for i=0,7 do
 local x=105+(i%2)*30; local z=-923+59*i
 local h=({69,92,117,95,82,71,53,34})[i+1]
 box("BackCliffMass"..i,{x-82,24+h/2,z},{85,h,90},i%2==0 and rockA or rockB,false,{i%2*7,i%3*11,-7},"Rock")
 box("BackCliffHeather"..i,{x-82,28+h,z},{61,7,66},moss,false,{i%2*5,i%3*11,-7},"Grass")
 box("CliffTalus"..i,{x-47,54,z+31},{32,17,38},rockB,false,{9,i*16,17},"Rock")
end
for i=0,4 do
 local x=235+i*75
 box("NorthRetainingBlock"..i,{x,57,-929},{72,18,14},stone,false,nil,"Sandstone")
 box("NorthRetainingCoping"..i,{x,66,-929},{74,2,15},pale,false,nil,"Sandstone")
 box("NorthHeatherStrip"..i,{x,67.5,-934},{66,2,9},moss,false,nil,"Grass")
end
-- Thin color bands convey walkable districts without stacking collider floors.
for i=0,2 do
 local x=250+i*165
 box("BellYardInset"..i,{x,48.055,({-810,-840,-800})[i+1]},{116,.11,68},{169,160,139},false,nil,"Cobblestone")
 for j=-1,1,2 do
  box("BellYardEdge"..i.."_"..j,{x+j*59,48.125,({-810,-840,-800})[i+1]},{2.5,.11,70},pale,false)
 end
end
for i=0,8 do
 local x=522+i*25.5
 box("LighthouseWaymarker"..i,{x,48.14,-650},{10,.09,1.45},i%2==0 and teal or brass,false,nil,"Metal")
end
for i=0,4 do
 local z=-365-9*i
 for _,side in ipairs({-1,1}) do
  box("DeckBoard"..i.."_"..side,{420+side*26,36.1,z},{16,.11,7.2},i%2==0 and bronze or dark,false,nil,"WoodPlanks")
 end
end
for i=0,7 do
 local x=106+i*88
 if i~=3 and i~=4 then
  box("SpindriftInner"..i,{x,.15,-389},{52,.13,1.6},{56,163,167},false,{0,4-i%2*8,0},"SmoothPlastic")
  box("SpindriftOuter"..i,{x+9,.14,-378},{36,.12,1.15},{119,193,185},false,{0,-4+i%2*8,0},"SmoothPlastic")
 end
end
for i=0,7 do
 local a=i*math.pi/4+.18
 box("IsletBreaker"..i,{840+72*math.cos(a),.2,-650+72*math.sin(a)},{28,.14,1.6},{116,191,181},false,{0,90-math.deg(a),0},"SmoothPlastic")
end
for i,t in ipairs({{494,48,-549},{578,48,-667},{665,48,-667},{743,48,-667},{769,48.12,-664.5},{795,48.12,-664.5},{391,36,-386},{449,36,-386},{383,24,-278},{457,24,-278}}) do
 local x,y,z=table.unpack(t)
 box("HarborLanternColumn"..i,{x,y+2.8,z},{1.6,5.6,1.6},dark,false,nil,"Metal")
 box("HarborLanternGlow"..i,{x,y+5.7,z},{2.2,1.15,2.2},{66,199,191},false,nil,"Neon")
 box("HarborLanternRoof"..i,{x,y+6.6,z},{2.85,.7,2.85},bronze,false,nil,"Metal")
end
-- Dock capstan silhouettes at the sides, outside the sampled ramp lane.
for i,t in ipairs({{383,-283},{455,-283},{387,-250},{451,-253}}) do
 local x,z=table.unpack(t)
 disk("DockCapstanFoot"..i,x,24.55,z,4.1,1.1,bronze,false,"Metal")
 disk("DockCapstanDrum"..i,x,26.15,z,2.6,3.1,dark,false,"Metal")
 disk("DockCapstanCrown"..i,x,28.4,z,3.65,1.25,brass,false,"Metal")
end
-- Clear nonblocking marker pads for host-owned encounter/spawn/quest integration.
for _,p in ipairs({{"BossHome",420,-680,48},{"Spawn",420,-545,48},{"DockQuest",420,-272,24},{"BellInteract1",250,-775,48},{"BellInteract2",420,-805,48},{"BellInteract3",580,-755,48}}) do
 disk("Marker"..p[1],p[2],p[4]+.1,p[3],3,.12,teal,false,"SmoothPlastic",{"GameplayMarker",p[1]})
end
Geometry.Routes={
 {id="DockUpperRamp",a={420,48,-468},b={420,36,-420},width=40},
 {id="DockLowerRamp",a={420,36,-350},b={420,24,-302},width=40},
 {id="Causeway",a={760,48.12,-650},b={804,48.12,-650},width=32},
}
for i,t in ipairs({{{804,48,-650},{804,48,-686}},{{804,48,-686},{840,48,-690}},{{840,48,-690},{876,48,-686}},{{876,48,-686},{876,48,-650}}}) do
 table.insert(Geometry.Routes,{id="LighthouseLoop"..i,a=t[1],b=t[2],width=8})
end
Geometry.Spawn={420,52,-545}
Geometry.RecoveryBounds={min={60,0,-960},max={910,250,-230}}
function Geometry.GetSpecs()return S end
function Geometry.Build(parent)
 local CollectionService=game:GetService("CollectionService")
 local model=Instance.new("Model");model.Name="Zone05_TidalBellFoundry"
 for _,s in ipairs(S) do
  local p=Instance.new("Part");p.Name=s.id;p.Anchored=true
  p.Size=Vector3.new(table.unpack(s.size));p.Color=Color3.fromRGB(table.unpack(s.color));p.Material=Enum.Material[s.material]
  p.Shape=Enum.PartType[s.shape];p.CanCollide=s.collidable;p.CanQuery=s.collidable;p.CanTouch=false
  p.CastShadow=s.material~="Neon";p.TopSurface=Enum.SurfaceType.Smooth;p.BottomSurface=Enum.SurfaceType.Smooth
  local r=s.rotation;p.CFrame=CFrame.new(table.unpack(s.position))*CFrame.Angles(0,math.rad(r[2]),0)*CFrame.Angles(math.rad(r[1]),0,math.rad(r[3]))
  p:SetAttribute("ZoneId","Zone05");if s.collidable then p:SetAttribute("GroundSurface",true)end
  for _,tag in ipairs(s.tags)do CollectionService:AddTag(p,tag)end
  p.Parent=model
 end
 model:SetAttribute("PreviewOnly",true);model.Parent=parent;return model
end
return Geometry
