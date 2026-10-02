-- Original wearable geometry; gameplay power remains server-calculated in VoiceCombat.
local Equipment={}
local function piece(model,torso,name,size,offset,color,shape)
 local part=Instance.new("Part");part.Name=name;part.Size=size;part.Color=color;part.Material=Enum.Material.SmoothPlastic
 part.CanCollide=false;part.CanTouch=false;part.CanQuery=false;part.Massless=true;part.CFrame=torso.CFrame*offset
 if shape then part.Shape=shape end
 part.Parent=model
 local weld=Instance.new("WeldConstraint");weld.Part0=torso;weld.Part1=part;weld.Parent=part
 return part
end
function Equipment.Sync(player,equipped)
 local character=player.Character;if not character then return end
 local existing=character:FindFirstChild("MicroSpeakerAccessory")
 if not equipped then if existing then existing:Destroy() end;return end
 if existing then return end
 local torso=character:FindFirstChild("UpperTorso") or character:FindFirstChild("Torso");if not torso then return end
 local model=Instance.new("Model");model.Name="MicroSpeakerAccessory"
 local back=torso.Size.Z/2+.24
 piece(model,torso,"Enclosure",Vector3.new(.95,1.2,.4),CFrame.new(.3,0,back),Color3.fromRGB(38,56,62))
 piece(model,torso,"GoldTrim",Vector3.new(.84,1.08,.06),CFrame.new(.3,0,back+.23),Color3.fromRGB(232,186,92))
 piece(model,torso,"SpeakerGrille",Vector3.new(.72,.93,.07),CFrame.new(.3,0,back+.27),Color3.fromRGB(36,42,47))
 for i=-2,2 do piece(model,torso,"GrilleSlot",Vector3.new(.6,.035,.03),CFrame.new(.3,i*.15,back+.32),Color3.fromRGB(98,117,120)) end
 piece(model,torso,"StatusLight",Vector3.new(.1,.1,.06),CFrame.new(.6,.43,back+.33),Color3.fromRGB(119,233,182),Enum.PartType.Ball).Material=Enum.Material.Neon
 model.Parent=character
end
return Equipment
