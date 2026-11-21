-- Original handheld amplifier geometry; gameplay power remains server-calculated in VoiceCombat.
local Equipment={}
local function piece(model,torso,name,size,offset,color,shape)
 local part=Instance.new("Part");part.Name=name;part.Size=size;part.Color=color;part.Material=Enum.Material.SmoothPlastic
 part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.Massless=true;part.CFrame=torso.CFrame*offset
 if shape then part.Shape=shape end
 part.Parent=model
 local weld=Instance.new("WeldConstraint");weld.Part0=torso;weld.Part1=part;weld.Parent=part
 return part
end
local function syncAccessory(player,equipped,modelName,build)
 local character=player.Character;if not character then return end
 local existing=character:FindFirstChild(modelName)
 if not equipped then if existing then existing:Destroy() end;return end
 if existing then return end
 local hand=character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm");if not hand then return end
 local model=Instance.new("Model");model.Name=modelName
 -- R15 grips at the palm; R6 grips at the end of its full-length arm.
 local grip=CFrame.new(0,-hand.Size.Y/2+.15,-.25)
 local function add(name,size,offset,color,shape) return piece(model,hand,name,size,grip*offset,color,shape) end
 build(add,hand)
 model.Parent=character
end
function Equipment.Sync(player,equipped)
 syncAccessory(player,equipped,"MicroSpeakerAccessory",function(add)
  add("Grip",Vector3.new(.25,.6,.25),CFrame.new(0,0,0),Color3.fromRGB(46,57,64))
  add("Enclosure",Vector3.new(.72,.78,.5),CFrame.new(0,.42,-.28),Color3.fromRGB(38,56,62))
  add("GoldTrim",Vector3.new(.64,.7,.06),CFrame.new(0,.42,-.56),Color3.fromRGB(232,186,92))
  add("SpeakerGrille",Vector3.new(.54,.58,.06),CFrame.new(0,.42,-.6),Color3.fromRGB(36,42,47))
  for i=-2,2 do add("GrilleSlot",Vector3.new(.43,.025,.02),CFrame.new(0,.42+i*.1,-.64),Color3.fromRGB(98,117,120)) end
  add("StatusLight",Vector3.new(.08,.08,.04),CFrame.new(.23,.7,-.65),Color3.fromRGB(119,233,182),Enum.PartType.Ball).Material=Enum.Material.Neon
  add("PommelCap",Vector3.new(.29,.08,.29),CFrame.new(0,-.32,0),Color3.fromRGB(232,186,92))
  add("GuardCollar",Vector3.new(.34,.08,.32),CFrame.new(0,.22,-.08),Color3.fromRGB(238,230,207))
  add("AcousticCone",Vector3.new(.18,.18,.05),CFrame.new(0,.42,-.64),Color3.fromRGB(232,186,92),Enum.PartType.Ball)
  add("TelemetrySpine",Vector3.new(.22,.56,.06),CFrame.new(0,.42,-.02),Color3.fromRGB(238,230,207))
 end)
end
function Equipment.SyncMegaphone(player,equipped)
 syncAccessory(player,equipped,"AcademyMegaphoneAccessory",function(add,hand)
  local cream,gold,brass=Color3.fromRGB(242,232,206),Color3.fromRGB(224,180,86),Color3.fromRGB(196,148,64)
  local leather,stitch,cavity=Color3.fromRGB(122,74,42),Color3.fromRGB(214,186,140),Color3.fromRGB(48,38,28)
  local rot=CFrame.Angles(0,math.pi/2,0)
  -- Leave .04 studs between the rear collar and the palm while keeping the handle in the grip.
  local forward=math.max(0,hand.Size.Z/2-.02)
  local function horn(z) return CFrame.new(0,.38,z-forward)*rot end
  add("Grip",Vector3.new(.22,.56,.22),CFrame.new(0,0,0),leather)
  add("GripStitch",Vector3.new(.23,.36,.04),CFrame.new(0,0,.09),stitch)
  add("PommelCap",Vector3.new(.26,.08,.26),CFrame.new(0,-.3,0),gold)
  add("WristLoop",Vector3.new(.06,.34,.18),CFrame.new(0,-.46,.04),leather)
  add("MountBracket",Vector3.new(.16,.18,.24+forward),CFrame.new(0,.24,-.04-forward/2),gold)
  add("MouthpieceCollar",Vector3.new(.14,.32,.32),horn(.12),gold,Enum.PartType.Cylinder)
  add("RearCone",Vector3.new(.22,.44,.44),horn(-.04),cream,Enum.PartType.Cylinder)
  add("MidBand",Vector3.new(.06,.58,.58),horn(-.16),gold,Enum.PartType.Cylinder)
  add("MidCone",Vector3.new(.26,.64,.64),horn(-.3),cream,Enum.PartType.Cylinder)
  add("FrontCone",Vector3.new(.28,.86,.86),horn(-.54),cream,Enum.PartType.Cylinder)
  add("BellRim",Vector3.new(.09,.96,.96),horn(-.7),gold,Enum.PartType.Cylinder)
  add("BellCavity",Vector3.new(.04,.76,.76),horn(-.73),cavity,Enum.PartType.Cylinder)
  add("AcousticNose",Vector3.new(.22,.22,.22),horn(-.68),brass,Enum.PartType.Ball)
 end)
end
-- Authored templates are local imported Models in ServerStorage/GearTemplates.
-- No asset IDs, uploads or fake mesh claims. Fallback is explicitly marked.
function Equipment.SyncGear(player,item)
 local character=player.Character;if not character then return end
 local id=item and item.id
 local current=character:FindFirstChild("ProgressionGear")
 if current and current:GetAttribute("GearId")~=id then current:Destroy();current=nil end
 Equipment.Sync(player,false);Equipment.SyncMegaphone(player,false)
 if not item then return end
 if current then return end
 local templates=game:GetService("ServerStorage"):FindFirstChild("GearTemplates")
 local template=templates and templates:FindFirstChild(item.template)
 local mount=item.mount=="back" and (character:FindFirstChild("UpperTorso") or character:FindFirstChild("Torso")) or (character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm"))
 if template and template:IsA("Model") and mount and template:FindFirstChildWhichIsA("BasePart",true) then
  local model=template:Clone();model.Name="ProgressionGear";model:SetAttribute("GearId",id);model:SetAttribute("MountKind",item.mount=="back" and "back" or "hand")
  local offset=item.mount=="back" and CFrame.new(0,0,.8) or CFrame.new(0,-mount.Size.Y/2+.15,-.25)
  model:PivotTo(mount.CFrame*offset)
  for _,part in ipairs(model:GetDescendants()) do
   if part:IsA("BasePart") then
    part.Anchored=false;part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.Massless=true
    local weld=Instance.new("WeldConstraint");weld.Part0=mount;weld.Part1=part;weld.Parent=part
   end
  end
  model.Parent=character
 else
  -- Explicit temporary old art, never presented as an imported Blender model.
  if id=="Megaphone" then Equipment.SyncMegaphone(player,true) else Equipment.Sync(player,true) end
  local model=character:FindFirstChild(id=="Megaphone" and "AcademyMegaphoneAccessory" or "MicroSpeakerAccessory")
  if model then model.Name="ProgressionGear";model:SetAttribute("GearId",id);model:SetAttribute("FallbackVisual",true);model:SetAttribute("MountKind","hand") end
 end
end
return Equipment
