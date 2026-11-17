-- Every road uses axis-aligned landings and an analytically joined swept slab.
local Arteries={}
local RAIL={121,147,153};local DECK={170,175,168};local CAP={136,225,217}
local PAD=16
local MOOD={
 ["01-02"]={{191,170,134},{239,208,151}},["02-10"]={{151,148,120},{136,211,190}},
 ["10-03"]={{135,114,92},{145,211,196}},["03-05"]={{161,137,108},{134,219,204}},
 ["05-07"]={{116,100,99},{255,162,79}},["07-08"]={{103,86,135},{212,142,251}},
 ["08-06"]={{100,89,134},{135,200,253}},["06-01"]={{138,125,147},{167,159,244}},
 ["01-04"]={{157,160,114},{184,210,144}},["04-06"]={{127,136,125},{162,207,195}},
 ["04-05"]={{146,139,113},{150,220,198}},
}
local function makePoint(a,b,f)
 return {a[1]+(b[1]-a[1])*f,a[2]+(b[2]-a[2])*f,a[3]+(b[3]-a[3])*f}
end
local function ramp(builder,id,a,b,width,height,offset,color,solid,material,tags)
 local dx,dy,dz=b[1]-a[1],b[2]-a[2],b[3]-a[3]
 local h=math.sqrt(dx*dx+dz*dz);local length=math.sqrt(h*h+dy*dy)
 local n={-dy*dx/(length*h),h/length,-dy*dz/(length*h)}
 local c={}
 for j=1,3 do c[j]=(a[j]+b[j])/2+n[j]*(offset-height/2) end
 builder:part(id,c,{width,height,length},color,solid,
  {-math.deg(math.atan2(dy,h)),math.deg(math.atan2(dx,dz)),0},material,tags)
end
local function orientation(a,b)
 local dx,dz=b[1]-a[1],b[3]-a[3]
 local h=math.sqrt(dx*dx+dz*dz)
 return dx/h,dz/h
end
local function extrapolate(a,x,z,d)
 return {a[1]+x*d,a[2],a[3]+z*d}
end
local function delta(a,b)
 return {b[1]-a[1],0,b[3]-a[3]}
end
local function openSide(v,x,z)
 return math.sign(v[1])==x and math.sign(v[3])==z
end
function Arteries.Build(builder,layout)
 builder.zone="09"
 for _,link in ipairs(layout.plannedZone09Links) do
  local id=table.concat(link,"-");local points=layout.worldLinks[id]
  local mood=MOOD[id] or {DECK,CAP};local deck,accent=mood[1],mood[2]
  local highRoute=id=="07-08" or id=="08-06"
  for i=2,#points-1 do
   local p=points[i]
   builder:part(id.."_Turn"..i,{p[1],p[2]-2,p[3]},{32,4,32},deck,true,nil,"Concrete",{"WalkableRoute"})
   local a,b=delta(p,points[i-1]),delta(p,points[i+1])
   for j,d in ipairs({{1,0},{-1,0},{0,1},{0,-1}}) do
    local x,z=table.unpack(d)
    if not openSide(a,x,z) and not openSide(b,x,z) then
     builder:part(id.."_TurnRail"..i.."_"..j,{p[1]+x*16.65,p[2]+2,p[3]+z*16.65},
       {x==0 and 32 or 1.3,4,z==0 and 32 or 1.3},RAIL,true,nil,"Metal",{"GateRail"})
    end
   end
   -- Cross-pad segments, needed to prove flat support up to the next ramp.
   local prevX,prevZ=orientation(p,points[i-1])
   local nextX,nextZ=orientation(p,points[i+1])
   builder:route(id.."_PadIn"..i,extrapolate(p,prevX,prevZ,PAD),p,32,"arterial",link)
   builder:route(id.."_PadOut"..i,p,extrapolate(p,nextX,nextZ,PAD),32,"arterial",link)
  end
  for i=1,#points-1 do
   local a,b=points[i],points[i+1]
   local dx,dz=orientation(a,b)
   local start=extrapolate(a,dx,dz,i==1 and 0 or PAD)
   local finish=extrapolate(b,-dx,-dz,i+1==#points and 0 or PAD)
   local len=math.sqrt((finish[1]-start[1])^2+(finish[3]-start[3])^2)
   local prefix=id.."_Deck"..i
   ramp(builder,prefix,start,finish,32,4,0,deck,true,"Concrete",{"WalkableRoute"})
   -- Inset bronze/colored marker strips follow the native slope, but their
   -- sub-stud height never creates ledges or affects authoritative queries.
   for _,s in ipairs({-1,1}) do
    local aa=extrapolate(start,dz,-dx,11.1*s)
    local bb=extrapolate(finish,dz,-dx,11.1*s)
    ramp(builder,prefix.."_LaneInlay"..s,aa,bb,.62,.085,.09,accent,false,"SmoothPlastic",{"CosmeticDetail"})
    if highRoute then
     ramp(builder,prefix.."_UnderTie"..s,aa,bb,1.2,2.6,-3.2,RAIL,true,"Metal",{"BridgeSupport"})
    end
   end
   for _,side in ipairs({-1,1}) do
    local dy=finish[2]-start[2]
    local trim=math.min(len/5,math.abs(dy)*6.3/math.sqrt(len^2+dy^2)+.12)
    local ua=extrapolate(start,dx,dz,trim);ua[2]+=dy*trim/len
    local ub=extrapolate(finish,-dx,-dz,trim);ub[2]-=dy*trim/len
    local aa=extrapolate(ua,dz,-dx,16.65*side)
    local bb=extrapolate(ub,dz,-dx,16.65*side)
    ramp(builder,prefix.."_Rail"..side,aa,bb,1.3,6,6,RAIL,true,"Metal",{"GateRail"})
    ramp(builder,prefix.."_Trim"..side,aa,bb,.58,.2,6.15,accent,false,"Neon",{"CosmeticDetail"})
    if trim>.7 then
     for k,pt in ipairs({start,finish}) do
      local rail=extrapolate(pt,dz,-dx,16.65*side)
      local post=extrapolate(rail,dx,dz,k==1 and .75 or -.75)
      builder:part(prefix.."_Post"..side.."_"..k,{post[1],post[2]+2.8,post[3]},
       {dx==0 and 1.3 or 1.5,5.6,dz==0 and 1.3 or 1.5},RAIL,true,nil,"Metal",{"GateRail"})
     end
    end
   end
   for j=1,math.floor(len/82) do
    local f=j/(math.floor(len/82)+1)
    local p=makePoint(start,finish,f);local x,y,z=table.unpack(p)
    -- Mark direction and scale with small outer railside lanterns, never on the walkway.
    for _,s in ipairs({-1,1}) do
     local q=extrapolate(p,dz,-dx,16.58*s)
     builder:part(prefix.."_LanternHousing"..j.."_"..s,{q[1],y+6.75,q[3]},
       {1.15,1.3,1.15},RAIL,true,nil,"Metal",{"GateRail"})
     builder:part(prefix.."_LanternLens"..j.."_"..s,{q[1],y+7.42,q[3]},
       {.9,.38,.9},accent,false,nil,"Neon",{"CosmeticDetail"})
    end
    if highRoute and len>=125 then
     -- A tapered cathedral-like rib holds each side of the elevated fantasy span
     -- together below the deck, without a row of steel stilts down to the ocean.
     local body=math.min(25,len*.11)
     local a=extrapolate(p,-dx,-dz,body);a[2]=p[2]-(finish[2]-start[2])*body/len-6
     local b=extrapolate(p,dx,dz,body);b[2]=p[2]+(finish[2]-start[2])*body/len-6
     local keel={p[1],p[2]-body*.72-7,p[3]}
     ramp(builder,prefix.."_KeelIn"..j,a,keel,3.2,3,0,RAIL,true,"Slate",{"BridgeSupport"})
     ramp(builder,prefix.."_KeelOut"..j,keel,b,3.2,3,0,RAIL,true,"Slate",{"BridgeSupport"})
    elseif y>13 and not (x>360 and x<480 and z>-425 and z<-235) then
     local h=y-7
     builder:part(prefix.."_Pier"..j,{x,h/2,z},{13,h,13},deck,true,nil,"Slate",{"BridgeSupport"})
     builder:part(prefix.."_PierCapital"..j,{x,h-2,z},{19,7,19},deck,true,nil,"Concrete",{"BridgeSupport"})
    end
   end
   builder:route(prefix,start,finish,32,"arterial",link)
  end
 end
end
return Arteries
