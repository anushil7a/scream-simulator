-- Cosmetic only. Server beam length/width remain authoritative; no voice recordings.
local Tween=game:GetService("TweenService")
local Effects={}
local limits={core=64,detail=144}
local active={core=0,detail=0}
local pools={core={},detail={}}
local function facing(a,b)
 local direction=(b-a).Unit
 return CFrame.lookAt(a,b,math.abs(direction.Y)>.98 and Vector3.zAxis or Vector3.yAxis)
end
local function particle(kind,cf,size,color,shape,lifetime,goal)
 if active[kind]>=limits[kind] then return end
 local p=table.remove(pools[kind]) or Instance.new("Part")
 p.Name="ScreamVisual";p.Anchored=true;p.CanCollide=false;p.CanQuery=false;p.CanTouch=false;p.CastShadow=false
 p.Material=Enum.Material.Neon;p.Color=color;p.Shape=shape or Enum.PartType.Block
 p.Size=size;p.CFrame=cf;p.Transparency=kind=="core" and .55 or .25;p.Parent=workspace
 active[kind]+=1
 local target=goal or {};target.Transparency=1
 Tween:Create(p,TweenInfo.new(lifetime,Enum.EasingStyle.Quad,Enum.EasingDirection.Out),target):Play()
 task.delay(lifetime+.05,function()
  p.Parent=nil;active[kind]-=1;table.insert(pools[kind],p)
 end)
end
local function line(kind,a,b,thickness,color,lifetime)
 local distance=(b-a).Magnitude;if distance<.01 then return end
 particle(kind,facing((a+b)/2,b),Vector3.new(thickness,thickness,distance),color,nil,lifetime)
end
function Effects.Render(family,origin,direction,length,width,color,reduced,variant)
 if length<=.01 or direction.Magnitude<.01 then return end
 direction=direction.Unit;length=math.clamp(length,.01,110);width=math.clamp(width,1,7)
 local basis=facing(origin,origin+direction)
 local right,up=basis.RightVector,basis.UpVector
 local center=origin+direction*length/2
 -- Separate budgets reserve a readable core even when decoration is saturated.
 particle("core",facing(center,center+direction),Vector3.new(width*.42,width*.42,length),color,nil,.32)
 particle("core",facing(center,center+direction),Vector3.new(.18,.18,length),Color3.fromRGB(255,240,203),nil,.24)
 if reduced then return end
 local rank=math.clamp(tonumber(variant) or 1,1,10)
 local function ring(distance,radius,life)
  local at=origin+direction*distance
  for i=1,8 do
   local a=(i-1)*math.pi/4;local b=i*math.pi/4
   line("detail",at+(right*math.cos(a)+up*math.sin(a))*radius,at+(right*math.cos(b)+up*math.sin(b))*radius,.12+rank*.006,color,life)
  end
 end
 if family=="Echo" then
  for i=1,3 do ring(length*i/4,width*(.3+i*.11),.25+i*.08) end
 elseif family=="Feathers" then
  for i=1,8 do
   local phase=i*math.pi/4;local offset=(right*math.cos(phase)+up*math.sin(phase))*width*.4
   local start=origin+offset
   local cf=facing(start,start+direction)*CFrame.Angles(0,0,phase)
   particle("detail",cf,Vector3.new(.18,.9+rank*.03,.35),color,nil,.45,{Position=origin+direction*length+offset,Orientation=Vector3.new(i*31,i*19,i*43)})
  end
 elseif family=="Quake" then
  -- Jagged ribbons follow the aimed beam, including when aiming upward.
  for _,side in ipairs({-1,1}) do
   local last=origin+right*side*width*.3-up*width*.25
   for i=1,5 do
    local nextPoint=origin+direction*(length*i/5)+right*side*width*(i%2==0 and .45 or .25)-up*width*.25
    line("detail",last,nextPoint,.25,color,.4);last=nextPoint
   end
  end
 elseif family=="Storm" then
  for strand=1,2 do
   local last=origin
   for i=1,7 do
    local offset=(right*math.sin(i*2.4+strand)+up*math.cos(i*1.7+strand))*width*.3
    local nextPoint=origin+direction*(length*i/7)+(i==7 and Vector3.zero or offset)
    line("detail",last,nextPoint,.12,color,.2+strand*.05);last=nextPoint
   end
  end
 elseif family=="Nova" then
  local finish=origin+direction*length
  for i=1,8 do
   local phase=i*math.pi/4;local offset=(right*math.cos(phase)+up*math.sin(phase))*width*.7
   line("detail",finish+offset*.25,finish+offset,.16,color,.35)
  end
  ring(length,width*.45,.4)
 else -- Pulse
  ring(math.min(length,4),width*.4,.3)
 end
end
function Effects.Budget()
 return {core=active.core,detail=active.detail,cachedCore=#pools.core,cachedDetail=#pools.detail,coreLimit=limits.core,detailLimit=limits.detail}
end
return Effects
