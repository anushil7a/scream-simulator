-- Bounded local accents over actual server warning markers, never damage geometry.
local Effects={MaxParts=24,Distance=140,Lifetime=.45}
local colors={metronome=Color3.fromRGB(70,230,225),golem=Color3.fromRGB(194,153,98),ignis=Color3.fromRGB(70,175,255),leviathan=Color3.fromRGB(100,225,235),seagull=Color3.fromRGB(100,225,235),conductor=Color3.fromRGB(190,130,255)}
function Effects.Build(parent,id,markers,impact)
 local folder=Instance.new("Folder");folder.Name="BossAttackAccents";folder.Parent=parent
 local pieces={}
 local function stroke(frame,size,color)
  if #pieces>=Effects.MaxParts then return end
  local p=Instance.new("Part");p.Name="Accent";p.Size=impact and size*1.25 or size;p.CFrame=frame;p.Color=color
  p.Material=id=="golem" and Enum.Material.Slate or Enum.Material.Neon
  p.Anchored=true;p.CanCollide=false;p.CanTouch=false;p.CanQuery=false;p.CastShadow=false;p.Transparency=impact and .25 or .35
  p.Parent=folder;table.insert(pieces,{part=p,frame=frame})
 end
 -- At most six representative markers. Server warning retains the ENTIRE footprint.
 for i=1,math.min(6,#markers) do
  local marker=markers[i];local anchor=CFrame.new(marker.position+Vector3.new(0,.35,0));local color=colors[id] or colors.seagull
  if not marker.disk and marker.frame then anchor=anchor*marker.frame.Rotation end
  for j=1,4 do
   local width=marker.size and marker.size.X or 1
   local length=marker.size and marker.size.Z or 4
   local spread=not marker.disk and (j-2.5)*math.min(math.max(width,length)*.2,5) or 0
   local base=anchor*CFrame.new(width>length and spread or 0,0,width>length and 0 or spread)
   if marker.disk and id=="golem" then
    local a=j*math.pi/2;local radius=length*.3
    base=anchor*CFrame.new(math.sin(a)*radius,0,math.cos(a)*radius)
   end
   if id=="metronome" then
    local angle=j*math.pi/2
    stroke(base*CFrame.Angles(0,angle,0)*CFrame.new(0,.15,-.85),Vector3.new(.18,.18,1.1),color)
   elseif id=="golem" then
    stroke(base*CFrame.Angles(.2*j,j*1.57,.3)*CFrame.new(.5,0,.5),Vector3.new(.85,.65,1.1),color)
   elseif id=="ignis" then
    stroke(base*CFrame.new((j-2.5)*.3,.35+(j%2)*.2,0)*CFrame.Angles(0,0,(j-2.5)*.12),Vector3.new(.22,1.4+(j%2)*.8,.22),color)
   elseif id=="conductor" then
    local angle=j*math.pi/2
    stroke(base*CFrame.Angles(0,angle,0)*CFrame.new(0,.5,-.55)*CFrame.Angles(.35,0,0),Vector3.new(.20,1.4,.20),color)
   elseif (id=="leviathan" or id=="seagull") and width<length then
    -- Narrow twin-siren lanes carry repeated cyan arches, not blade slashes.
    -- Three strokes per arch; two lanes x four arches stays within24 parts.
    local arch=base*CFrame.new(0,.85,0)
    stroke(arch*CFrame.new(-.48,0,0)*CFrame.Angles(0,0,-.5),Vector3.new(.14,1.1,.14),color)
    stroke(arch*CFrame.new(.48,0,0)*CFrame.Angles(0,0,.5),Vector3.new(.14,1.1,.14),color)
    stroke(arch*CFrame.new(0,.5,0),Vector3.new(.5,.14,.14),color)
   else
    -- Cutlass arc: four angular silver/cyan blade streaks, no ocean serpent motif.
    stroke(base*CFrame.new((j-2.5)*.38,.4+math.sin(j*math.pi/5)*.4,0)*CFrame.Angles(0,0,(2.5-j)*.35),Vector3.new(1.5,.16,.16),j%2==0 and Color3.fromRGB(235,245,250) or color)
   end
  end
 end
 local self={folder=folder,pieces=pieces}
 function self:Step(age)
  if not impact then return end
  local transparency=math.clamp(.1+age/Effects.Lifetime*.9,0,1)
  local rise=Vector3.new(0,math.min(age,Effects.Lifetime)*2,0)
  for _,entry in ipairs(self.pieces) do
   entry.part.Transparency=transparency
   entry.part.CFrame=entry.frame+rise
  end
 end
 function self:Destroy()self.folder:Destroy();table.clear(self.pieces)end
 return self
end
return Effects
