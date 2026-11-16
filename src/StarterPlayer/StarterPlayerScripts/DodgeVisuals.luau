-- Client-only Lightning Dash Warp interpretation: two actual-position cyan echoes,
-- angular filaments and thin gold foot sparks. No motion, collision or gameplay authority.
local RunService=game:GetService("RunService")
local Visuals={}
local MAX_CASTS=4
local MAX_BODY_PARTS=16
local SECOND_SAMPLE=.16
local ECHO_LIFETIME=.34
local CAST_LIFETIME=.60
local CYAN=Color3.fromRGB(78,225,255)
local GOLD=Color3.fromRGB(255,208,108)
local BODY={Head=true,Torso=true,UpperTorso=true,LowerTorso=true,
 ["Left Arm"]=true,["Right Arm"]=true,["Left Leg"]=true,["Right Leg"]=true,
 LeftUpperArm=true,LeftLowerArm=true,LeftHand=true,RightUpperArm=true,RightLowerArm=true,RightHand=true,
 LeftUpperLeg=true,LeftLowerLeg=true,LeftFoot=true,RightUpperLeg=true,RightLowerLeg=true,RightFoot=true}
local casts={}
local heartbeat
local function clearCast(cast)
 if cast.root then cast.root:Destroy();cast.root=nil end
 table.clear(cast.echoes)
end
local function stopIfEmpty()
 if #casts==0 and heartbeat then heartbeat:Disconnect();heartbeat=nil end
end
local function filament(parent,from,to,color,width)
 local a=Instance.new("Attachment");a.Position=from;a.Parent=parent
 local b=Instance.new("Attachment");b.Position=to;b.Parent=parent
 local beam=Instance.new("Beam");beam.Name="DashFilament";beam.Attachment0=a;beam.Attachment1=b
 beam.Color=ColorSequence.new(color);beam.Transparency=NumberSequence.new(.25)
 beam.Width0=width;beam.Width1=width*.4;beam.FaceCamera=true;beam.LightEmission=1;beam.Segments=1;beam.Parent=parent
 return beam
end
local function snapshot(cast)
 if not cast.character.Parent or not cast.root then return end
 local echo={age=0,parts={},beams={}}
 local model=Instance.new("Model");model.Name="CyanAfterimage";model.Parent=cast.root;echo.model=model
 for _,body in ipairs(cast.character:GetChildren()) do
  if #echo.parts>=MAX_BODY_PARTS then break end
  if BODY[body.Name] and body:IsA("BasePart") and body.Transparency<1 then
   -- Clone only direct body geometry. Never parent copied scripts, joints or effects.
   local ok,copy=pcall(function() return body:Clone() end)
   if ok and copy then
    copy:ClearAllChildren()
    copy.Name="Echo_"..body.Name;copy.Anchored=true;copy.CanCollide=false;copy.CanTouch=false;copy.CanQuery=false;copy.Massless=true
    copy.CastShadow=false;copy.Material=Enum.Material.Neon;copy.Color=CYAN;copy.Transparency=.72
    if copy:IsA("MeshPart") then copy.TextureID="" end
    copy.CFrame=body.CFrame;copy.Parent=model;table.insert(echo.parts,copy)
    if body.Name=="UpperTorso" or body.Name=="Torso" then
     -- Three angular strokes lie on the sampled torso, not projected ahead through walls.
     local x,y,z=copy.Size.X*.36,copy.Size.Y*.38,-copy.Size.Z*.51
     local points={Vector3.new(-x,y,z),Vector3.new(x*.3,y*.2,z),Vector3.new(-x*.2,-y*.3,z),Vector3.new(x,-y,z)}
     for i=1,3 do table.insert(echo.beams,filament(copy,points[i],points[i+1],CYAN,.045)) end
    elseif body.Name=="LeftFoot" or body.Name=="RightFoot" or body.Name=="Left Leg" or body.Name=="Right Leg" then
     local y=-copy.Size.Y*.48
     for sign=-1,1,2 do
      table.insert(echo.beams,filament(copy,Vector3.new(0,y,0),Vector3.new(sign*copy.Size.X*.4,y+.05,copy.Size.Z*.35),GOLD,.025))
     end
    end
   end
  end
 end
 table.insert(cast.echoes,echo)
end
local function step(dt)
 for i=#casts,1,-1 do
  local cast=casts[i];cast.age+=dt
  if not cast.character.Parent or not cast.root or not cast.root.Parent or cast.age>=CAST_LIFETIME then
   clearCast(cast);table.remove(casts,i)
  else
   for j=#cast.echoes,1,-1 do
    local echo=cast.echoes[j];echo.age+=dt
    if echo.age>=ECHO_LIFETIME then echo.model:Destroy();table.remove(cast.echoes,j)
    else
     local fade=echo.age/ECHO_LIFETIME
     for _,part in ipairs(echo.parts) do part.Transparency=.72+.28*fade end
     for _,beam in ipairs(echo.beams) do beam.Transparency=NumberSequence.new(.25+.75*fade) end
    end
   end
   if not cast.second and cast.age>=SECOND_SAMPLE then
    cast.second=true
    -- If the client stalls, don't create a late echo after the dash is over.
    if cast.age<SECOND_SAMPLE+.1 then snapshot(cast) end
   end
  end
 end
 stopIfEmpty()
end
function Visuals.Play(character,reducedMotion)
 if reducedMotion then return false end
 if typeof(character)~="Instance" or not character:IsA("Model") or not character.Parent then return false end
 if #casts>=MAX_CASTS then clearCast(casts[1]);table.remove(casts,1) end
 local root=Instance.new("Folder");root.Name="LocalDodgeEchoes";root.Parent=workspace
 local cast={character=character,root=root,age=0,second=false,echoes={}}
 table.insert(casts,cast);snapshot(cast)
 if not heartbeat then heartbeat=RunService.Heartbeat:Connect(step) end
 return true
end
function Visuals.Destroy()
 for _,cast in ipairs(casts) do clearCast(cast) end
 table.clear(casts);stopIfEmpty()
end
return Visuals
