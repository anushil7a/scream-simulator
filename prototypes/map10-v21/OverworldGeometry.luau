local Geometry={}
local EDGE_HEIGHT=6
local INSET=22
local CHAMFER={["01"]=52,["02"]=44,["03"]=44,["04"]=52,["06"]=54,["07"]=52,["08"]=43,["10"]=58}
local function stripShape(w,h,r)
 local n=5
 local out={}
 if r==0 then return {{-h/2,h/2,w}} end
 for j=0,n-1 do
  local a=-h/2+j*r/n
  table.insert(out,{a,a+r/n,w-2*r*(1-j/n)})
 end
 table.insert(out,{-h/2+r,h/2-r,w})
 for j=0,n-1 do
  local a=h/2-r+j*r/n
  table.insert(out,{a,a+r/n,w-2*r*(j+1)/n})
 end
 return out
end
local palettes={
 ["01"]={{200,174,132},{239,219,172}},["02"]={{161,138,115},{195,166,131}},
 ["03"]={{138,107,84},{156,109,69}},["04"]={{115,152,85},{190,178,138}},
 ["06"]={{103,94,127},{121,112,145}},["07"]={{65,58,63},{125,103,101}},
 ["08"]={{112,95,143},{137,119,159}},["10"]={{142,150,125},{165,173,144}},
}
local function paddedOpenings(layout,id,d)
 local x,_,z=table.unpack(d.center);local w,h=table.unpack(d.size)
 local sides={W={},E={},N={},S={}}
 local gates={}
 for _,link in ipairs(layout.plannedZone09Links) do
  local ends=layout.worldLinks[table.concat(link,"-")]
  local p=link[1]==id and ends[1] or link[2]==id and ends[#ends] or nil
  if p then
   local side=p[1]==x-w/2 and "W" or p[1]==x+w/2 and "E" or p[3]==z-h/2 and "N" or "S"
   local axis=(side=="W" or side=="E") and 3 or 1
   table.insert(sides[side],{p[axis]-16.02,p[axis]+16.02})
   table.insert(gates,{side=side,p=p,link=link})
  end
 end
 if id=="05" then
  table.insert(sides.E,{-666.02,-633.98}) -- lighthouse causeway
  table.insert(sides.S,{395.98,444.02}) -- south dock notch
 end
 return sides,gates
end
local function border(builder,id,d,sides)
 local x,y,z=table.unpack(d.center);local w,h=table.unpack(d.size)
 local color=(palettes[id] or {{170,151,121}})[1]
 for _,side in ipairs({"W","E","N","S"}) do
  local vertical=side=="W" or side=="E"
  local fixed=vertical and x+(side=="W" and -w/2 or w/2) or z+(side=="N" and -h/2 or h/2)
  if side=="W" or side=="N" then fixed-=.65 else fixed+=.65 end
  local low,high=vertical and z-h/2 or x-w/2,vertical and z+h/2 or x+w/2
  local cap=CHAMFER[id] or 0
  local trim=cap*1.2
  low+=trim;high-=trim
  local cuts=sides[side]
  table.sort(cuts,function(a,b)return a[1]<b[1] end)
  table.insert(cuts,{high,high})
  local last=low
  for i,cut in ipairs(cuts) do
   if cut[1]-last>.01 then
    local mid=(cut[1]+last)/2
    local long=cut[1]-last
    local p=vertical and {fixed,y+EDGE_HEIGHT/2,mid} or {mid,y+EDGE_HEIGHT/2,fixed}
    local size=vertical and {1.3,EDGE_HEIGHT,long} or {long,EDGE_HEIGHT,1.3}
    builder:part("Parapet_"..side..i,p,size,color,true,nil,"Slate",{"GateRail"})
   end
   last=math.max(last,cut[2])
  end
 end
 local chamfer=CHAMFER[id] or 0
 if chamfer>0 then
  -- One diagonal parapet per chamfer, drawn one strip inset so its whole
  -- length stays over physical support; the exposed earth outside is geology.
  local run=chamfer*1.2
  for _,sx in ipairs({-1,1}) do for _,sz in ipairs({-1,1}) do
   local ox,oz=x+sx*(w/2+.65),z+sz*(h/2+.65)
   local ax,az=ox-sx*run,oz
   local bx,bz=ox,oz-sz*run
   local yaw=math.deg(math.atan2(bx-ax,bz-az))
   builder:part("ChamferRail_"..sx.."_"..sz,{(ax+bx)/2,y+3,(az+bz)/2},
    {1.3,EDGE_HEIGHT,math.sqrt(2)*run+1.3},color,true,{0,yaw,0},"Slate",{"GateRail"})
  end end
 end
end
local function base(builder,id,d)
 local x,y,z=table.unpack(d.center);local w,h=table.unpack(d.size)
 local bottom=math.max(-6,y-math.min(y+6,50))
 local p=palettes[id]
 for i,strip in ipairs(stripShape(w,h,CHAMFER[id] or 0)) do
  local lo,hi,width=table.unpack(strip)
  builder:part("DistrictGround_"..i,{x,(y+bottom)/2,z+(lo+hi)/2},{width,y-bottom,hi-lo},p[1],true,nil,(id=="01" or id=="04" or id=="07") and "SmoothPlastic" or "Slate",{"GroundSurface"})
 end
 -- Material changes read as paving rather than luminous paint. The four
 -- arms terminate at an inset octagonal plaza with no coplanar overlap.
 local center=35
 builder:disk("CenterPaving",x,y+.042,z,center,.08,p[2],false,id=="01" and "SmoothPlastic" or "Cobblestone",{"CosmeticDetail"})
 for j,dir in ipairs({{1,0},{-1,0},{0,1},{0,-1}}) do
  local dx,dz=table.unpack(dir);local radius=dx~=0 and w/2 or h/2
  local last=radius-9
  local length=last-center
  local width=id=="03" and 22 or id=="04" and 24 or 20
  local along=(center+last)/2
  local q={x+dx*along,y+.046,z+dz*along}
  builder:part("Paving_"..j,q,dx~=0 and {length,.08,width} or {width,.08,length},
    p[2],false,nil,(id=="01" or id=="03") and "SmoothPlastic" or "Concrete",{"CosmeticDetail"})
 end
end
local function gatesTest(builder,id,d,gates)
 -- Assert support and head clearance from gate to the interior perimeter and along
 -- that perimeter to the central axis. Later room-style entrances are separate.
 local x,y,z=table.unpack(d.center);local w,h=table.unpack(d.size)
 for i,g in ipairs(gates) do
  local a=g.p;local b,c
  if g.side=="W" or g.side=="E" then
   b={a[1]+(g.side=="W" and INSET or -INSET),y,a[3]}
   c={b[1],y,z}
  else
   b={a[1],y,a[3]+(g.side=="N" and INSET or -INSET)}
   c={x,y,b[3]}
  end
  -- Studio rays can miss an exact edge shared by two solids (platform strip
  -- and a sloped deck). A narrow, visible metal threshold makes the joint
  -- continuous even under engine float tolerances. Max step is 0.10 studs.
  local parallelZ=g.side=="W" or g.side=="E"
  builder:part("GateThreshold_"..i,{a[1],y-.045,a[3]},
    parallelZ and {.45,.29,32} or {32,.29,.45},
    {113,121,123},true,nil,"Metal",{"WalkableRoute"})
  builder:route(id.."_GateApproach"..i,a,b,28,"main")
  if id~="05" and (b[1]~=c[1] or b[3]~=c[3]) then
   builder:route(id.."_GatePerimeter"..i,b,c,16,"secondary")
  end
 end
 if id~="05" then
  builder:route(id.."_MainX",{x-w/2+INSET,y,z},{x+w/2-INSET,y,z},40,"main")
  builder:route(id.."_MainZ",{x,y,z-h/2+INSET},{x,y,z+h/2-INSET},40,"main")
 end
end
local function foundry(builder,old)
 for _,p in ipairs(old.GetSpecs()) do
  local id=p.id
  local exclude=id=="Beacon" or id:match("^Bell%d+Shell")~=nil
  -- The arc from Boardwalk enters at x=80,z=-800. Remove the visual edge
  -- cliff masses in this portal, instead of leaving a walkthrough cliff.
  local westCliff=id:match("^BackCliff") or id:match("^CliffTalus")
  if westCliff and math.abs(p.position[3]+800)<(p.size[3]*.5+27) then exclude=true end
  if not exclude then
   -- Preserve physical silhouettes for reachable parts, including bell shells and
   -- any architecture a future climb/jump route might approach. Optical trim,
   -- foam/spray, lawn and flush markers remain deliberately nonphysical.
   local physical=p.collidable or westCliff~=nil or id:match("^Bell%d+Shell")~=nil
     or id:match("^Bell%d+Yoke")~=nil or id:match("^Bell%d+Crown")~=nil
     or id:match("^Bell%d+Clapper")~=nil or id:match("^Gantry%d+Crossbeam")~=nil
   for _,prefix in ipairs({"IslandRock","NorthRetainingBlock","NorthRetainingCoping","HarborLantern",
      "DockCapstan","BellShell","GantryCrossbeam","BellCrown","BellClapper","WorkshopRoof",
      "LighthouseShaft","LighthousePlinth","LanternColumn","LanternGallery","LanternCrown","ArchStone"}) do
    if id:sub(1,#prefix)==prefix then physical=true;break end
   end
   local tags=table.clone(p.tags)
   if p.collidable and (id:match("^Platform") or id:match("^DockUpper") or id:match("^DockLower") or id=="LighthouseIsland") then
    table.insert(tags,"GroundSurface")
   end
   builder:part(id,p.position,p.size,p.color,physical,p.rotation,p.material,tags,p.shape)
  end
 end
 for _,route in ipairs(old.Routes) do builder:route("05_"..route.id,route.a,route.b,route.width,"secondary") end
end
function Geometry.Compose(builder,layout,arteries,west,coast,east,originalFoundry)
 local names={["09"]="Zone09_TransitArteries",["00"]="OceanBase"}
 for id,d in pairs(layout.districts) do
  names[id]="Zone"..id.."_"..d.name:gsub("[^%w]","")
  builder.zone=id
  local openings,gates=paddedOpenings(layout,id,d)
  if id=="05" then foundry(builder,originalFoundry) else
   base(builder,id,d)
   if id=="01" or id=="02" or id=="04" then west(builder,id,d)
   elseif id=="03" or id=="10" then coast(builder,id,d)
   else east(builder,id,d) end
  end
  border(builder,id,d,openings)
  gatesTest(builder,id,d,gates)
 end
 arteries.Build(builder,layout)
 builder.zone="00"
 builder:part("Sea",{0,-2.2,0},{4200,4,4200},{23,124,154},false,nil,"SmoothPlastic",{"WaterVisual"})
 -- Restrained nearshore water strokes. Unwalkable and non-queryable, no per-frame animation.
 local foam={
  {236,-411,4,16,2},{459,-231,-14,17,2},{657,-401,13,22,2},{842,-579,-11,9,2},{913,-660,75,10,2},
  {-1028,925,-14,22,3},{-819,948,4,28,3},{-526,931,12,18,2},{-1125,519,79,20,3},
  {-387,-1001,7,37,4},{-721,-1005,0,29,4},{-1437,-690,89,31,4},{-1122,-921,-9,24,3},
 }
 for i,wave in ipairs(foam) do
  local fx,fz,yaw,length,count=table.unpack(wave)
  local a=math.rad(yaw)
  for i2=1,count do
   local coast=(i2-1)*5
   builder:part("HarborFoam"..i.."_"..i2,{fx+math.sin(a)*coast,.065+i2*.008,fz+math.cos(a)*coast},
    {length+i2*4,.07,1.15+i2*.42},i2==1 and {130,209,201} or {58,169,180},
    false,{0,yaw+(-1)^i2*4,0},"SmoothPlastic",{"WaterVisual"})
  end
 end
 return names
end
return Geometry
