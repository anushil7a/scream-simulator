-- Maps source specs into ordinary Roblox parts. No external content or game-state bindings.
local Builder={}
Builder.__index=Builder
local function copy(t) return table.clone(t or {}) end
function Builder.new()
 return setmetatable({parts={},routes={},zone=nil,names={}},Builder)
end
function Builder:part(id,position,size,color,solid,rotation,material,tags,shape)
 assert(self.zone and not self.names[self.zone.."/"..id], "duplicate or ungrouped part: "..id)
 assert(size[1]>0 and size[2]>0 and size[3]>0,"nonpositive part size")
 tags=copy(tags)
 local role
 if solid then
  role="Solid"
  if not table.find(tags,"WalkableRoute") and not table.find(tags,"GroundSurface") then
   table.insert(tags,"SolidObstacle")
  end
 elseif table.find(tags,"WaterVisual") then role="NonPhysical"
 elseif table.find(tags,"CosmeticDetail") or size[2]<=.45 then role="Decorative"
 else role="Decorative"; table.insert(tags,"Scenery") end
 local spec={id=id,position=position,size=size,color=color,rotation=rotation or {0,0,0},
  collidable=solid==true,queryable=solid==true,collisionRole=role,zone=self.zone,
  material=material or "SmoothPlastic",tags=tags,shape=shape or "Block"}
 self.names[self.zone.."/"..id]=true
 table.insert(self.parts,spec)
 return spec
end
function Builder:disk(id,x,y,z,r,h,color,solid,material,tags)
 return self:part(id,{x,y,z},{h,r*2,r*2},color,solid,{0,0,90},material,tags,"Cylinder")
end
function Builder:route(id,a,b,width,kind,link)
 table.insert(self.routes,{id=id,a=a,b=b,width=width,class=kind,link=link})
end
function Builder:Build(parent,groupNames)
 local service=game:GetService("CollectionService")
 local groups={}
 for id,name in pairs(groupNames) do
  local m=Instance.new("Model")
  m.Name=name;m:SetAttribute("ZoneId",id);m.Parent=parent;groups[id]=m
 end
 for _,p in ipairs(self.parts) do
  local wedge=p.shape=="Wedge"
  local item=Instance.new(wedge and "WedgePart" or "Part");item.Name=p.id;item.Anchored=true
  item.Size=Vector3.new(table.unpack(p.size));item.Color=Color3.fromRGB(table.unpack(p.color))
  item.Material=Enum.Material[p.material]
  if p.shape=="Ball" and not p.collidable and not p.queryable and p.zone=="01" then
   -- The soft canopy and inset trim use their authored ellipsoid proportions.
   local mesh=Instance.new("SpecialMesh");mesh.MeshType=Enum.MeshType.Sphere;mesh.Parent=item
  elseif not wedge then item.Shape=Enum.PartType[p.shape] end
  item.CanCollide=p.collidable;item.CanQuery=p.queryable;item.CanTouch=false
  local significant=math.max(table.unpack(p.size))>=8
  item.CastShadow=p.material~="Neon" and (p.collidable and significant or table.find(p.tags,"HeroLandmark")~=nil)
  item.TopSurface=Enum.SurfaceType.Smooth;item.BottomSurface=Enum.SurfaceType.Smooth
  local r=p.rotation
  item.CFrame=CFrame.new(table.unpack(p.position))*CFrame.Angles(0,math.rad(r[2]),0)*CFrame.Angles(math.rad(r[1]),0,math.rad(r[3]))
  item:SetAttribute("ZoneId",p.zone);item:SetAttribute("CollisionRole",p.collisionRole)
  for _,tag in ipairs(p.tags) do service:AddTag(item,tag) end
  item.Parent=groups[p.zone]
 end
 return groups
end
return Builder
