-- Original physical terrain, generated from the v2.1 district envelopes.
-- Reference IMG_1526 + DEB21437 gap review: irregular coastal mass, not pad stilts.
-- Invoke after ALL routes. Native parts need no external assets/mesh publication.
return function(build,layout)
 local exclusions={};local LIMIT=450;local count=0;local oldZone=build.zone
 local function route(a,b,r)
  table.insert(exclusions,{math.min(a[1],b[1])-r,math.max(a[1],b[1])+r,
   math.min(a[2],b[2])-6,math.max(a[2],b[2])+16,math.min(a[3],b[3])-r,math.max(a[3],b[3])+r})
 end
 for _,points in pairs(layout.worldLinks or {})do for i=1,#points-1 do route(points[i],points[i+1],48)end end
 for _,r in ipairs(build.routes or {})do route(r.a,r.b,math.max(24,(r.width or 32)/2+12))end
 local function intersects(a,b)
  return a[1]<b[2] and a[2]>b[1] and a[3]<b[4] and a[4]>b[3] and a[5]<b[6] and a[6]>b[5]
 end
 local function extents(size,rot)
  local a,b,c=math.rad(rot[1]),math.rad(rot[2]),math.rad(rot[3])
  local ca,sa,cb,sb,cc,sc=math.cos(a),math.sin(a),math.cos(b),math.sin(b),math.cos(c),math.sin(c)
  local m={{cb*cc+sb*sa*sc,-cb*sc+sb*sa*cc,sb*ca},{ca*sc,ca*cc,-sa},{-sb*cc+cb*sa*sc,sb*sc+cb*sa*cc,cb*ca}}
  local e={};for i=1,3 do e[i]=0;for j=1,3 do e[i]+=math.abs(m[i][j])*size[j]/2 end end;return e
 end
 local ids={};for id in pairs(layout.districts)do table.insert(ids,id)end;table.sort(ids)
 local function emit(id,name,x,z,top,size,rot,color,mat,shape,joined)
  if count>=LIMIT then return false end
  local e=extents(size,rot);local y=top-e[2]
  local a={x-e[1],x+e[1],y-e[2],top,z-e[3],z+e[3]}
  for _,r in ipairs(exclusions)do if intersects(a,r)then return false end end
  for other,n in pairs(layout.districts)do
   if other~=id and not (joined and joined[other]) then
    local p,s=n.center,n.size
    -- Preserve other districts including their own foundation/body, not just floor.
    local b={p[1]-s[1]/2-8,p[1]+s[1]/2+8,-32,p[2]+20,p[3]-s[2]/2-8,p[3]+s[2]/2+8}
    if intersects(a,b)then return false end
   end
  end
  build.zone=id;build:part(name,{x,y,z},size,color,true,rot,mat,{"CoastalCliff","PhysicalTerrain"},shape)
  count+=1;return true
 end
 for _,id in ipairs(ids)do
  local s=layout.districts[id];local x,y,z=table.unpack(s.center);local w,d=table.unpack(s.size)
  local volcanic=id=="07";local astral=id=="08"
  local light=volcanic and {95,75,66} or astral and {130,110,156} or {200,177,135}
  local medium=volcanic and {66,60,62} or astral and {93,77,122} or {169,145,108}
  local dark=volcanic and {48,46,52} or astral and {65,57,91} or {130,118,93}
  -- Broad underbody interlocks with slab bottom, eliminates floating-card silhouette.
  -- Astral terminates in a hanging mineral keel rather than reaching the sea.
  local totalDepth=astral and 230 or math.max(30,y+22)
  emit(id,"TerrainCore",x,z,y-7,{w*.96,totalDepth*.76,d*.96},{0,0,0},medium,"Rock","Ball")
  for i=0,3 do
   local a=i*math.pi/2+.3;local r=math.min(w,d)*.21
   emit(id,"TerrainKeel"..i,x+math.cos(a)*r,z+math.sin(a)*r,y-totalDepth*.40,
    {w*.46,totalDepth*.60,d*.44},{i%2*7,i*90+18,180},dark,"Rock","Wedge")
  end
  -- Four continuous scalloped edge bands, independently staggered strata.
  -- All transformed tops remain below walking plane: never ramps/hidden blockers.
  for edge,n in ipairs({{-1,0},{1,0},{0,-1},{0,1}})do
   local nx,nz=n[1],n[2];local length=nx==0 and w or d
   local pieces=5
   for j=0,pieces-1 do
    local phase=j*1.73+edge*.81
    local along=((j+.5)/pieces-.5)*length
    local px=x+nx*(w/2-5+17*math.sin(phase))+(nx==0 and along or 0)
    local pz=z+nz*(d/2-5+17*math.sin(phase))+(nz==0 and along or 0)
    local depth=126+30*math.sin(phase);local span=length/pieces*(1.05+.12*math.cos(phase))
    local top=y-7-3*(j%2)
    local height=astral and 88+(j%3)*18 or math.max(26,y*.64+18+(j%3)*6)
    local yaw=(edge<=2 and 90 or 0)+math.sin(phase)*13
    -- Broad sloping buttress, not a facade texture; completely collidable.
    emit(id,"TerrainRim"..edge.."_"..j,px,pz,top,{span,height,depth},{(j%3-1)*8,yaw,0},j%3==0 and light or medium,"Rock",j%2==0 and "Wedge" or "Block")
    -- Lower talus fan projects unevenly; tapers toward sea or floating underside.
    local spread=astral and -18 or 26+12*math.cos(phase)
    local lowerTop=astral and y-70-(j%3)*11 or math.max(-7,y-height*.55-8)
    local lowerH=astral and 100+(j%2)*25 or math.max(22,lowerTop+19)
    emit(id,"TerrainTalus"..edge.."_"..j,px+nx*spread,pz+nz*spread,lowerTop,
     {span*.91,lowerH,depth*1.15},{0,yaw+17,astral and 180 or 0},dark,"Rock","Wedge")
    -- A few grassy pockets on sheltered sandstone ledges, physical foliage.
    if not volcanic and not astral and j%2==0 and edge%2==1 then
     emit(id,"TerrainShelfGreen"..edge.."_"..j,px+nx*8,pz+nz*8,y-11,
      {span*.58,8,depth*.55},{0,yaw,0},{101,139,78},"Grass","Ball")
    end
   end
  end
 end
 -- Joined terrestrial substrate beneath roads. Preserve sea gutters at reef/coast
 -- and never support Astral from below. These are broad ground masses, not piles.
 local terrestrial={['01-02']=true,['01-04']=true,['04-06']=true,['06-01']=true,['04-05']=true,['05-07']=true}
 for _,link in ipairs(layout.plannedZone09Links or {})do
  local key=table.concat(link,'-');local points=layout.worldLinks[key]
  if terrestrial[key] then
   local joined={[link[1]]=true,[link[2]]=true}
   for i=1,#points-1 do
    local a,b=points[i],points[i+1];local dx,dz=b[1]-a[1],b[3]-a[3]
    local length=math.sqrt(dx*dx+dz*dz);local top=math.min(a[2],b[2])-12
    local depth=math.max(32,top+18);local yaw=math.deg(math.atan2(dx,dz))
    emit(link[1],"JoinedTerrain_"..key.."_"..i,(a[1]+b[1])/2,(a[3]+b[3])/2,top,
     {144,depth,length+72},{0,yaw,0},{156,137,106},"Rock","Ball",joined)
    emit(link[1],"JoinedTalus_"..key.."_"..i,(a[1]+b[1])/2,(a[3]+b[3])/2,math.min(8,top-8),
     {174,30,length+90},{0,yaw+3,0},{137,126,99},"Rock","Wedge",joined)
   end
  end
 end
 build.zone=oldZone
 return count
end
