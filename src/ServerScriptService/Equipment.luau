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
function Equipment.Sync(player,equipped)
 local character=player.Character;if not character then return end
 local existing=character:FindFirstChild("MicroSpeakerAccessory")
 if not equipped then if existing then existing:Destroy() end;return end
 if existing then return end
 local hand=character:FindFirstChild("RightHand") or character:FindFirstChild("Right Arm");if not hand then return end
 local model=Instance.new("Model");model.Name="MicroSpeakerAccessory"
 -- R15 grips at the palm; R6 grips at the end of its full-length arm.
 local grip=CFrame.new(0,-hand.Size.Y/2+.15,-.25)
 local function add(name,size,offset,color,shape) return piece(model,hand,name,size,grip*offset,color,shape) end
 add("Grip",Vector3.new(.25,.6,.25),CFrame.new(0,0,0),Color3.fromRGB(46,57,64))
 add("Enclosure",Vector3.new(.72,.78,.5),CFrame.new(0,.42,-.28),Color3.fromRGB(38,56,62))
 add("GoldTrim",Vector3.new(.64,.7,.06),CFrame.new(0,.42,-.56),Color3.fromRGB(232,186,92))
 add("SpeakerGrille",Vector3.new(.54,.58,.06),CFrame.new(0,.42,-.6),Color3.fromRGB(36,42,47))
 for i=-2,2 do add("GrilleSlot",Vector3.new(.43,.025,.02),CFrame.new(0,.42+i*.1,-.64),Color3.fromRGB(98,117,120)) end
 add("StatusLight",Vector3.new(.08,.08,.04),CFrame.new(.23,.7,-.65),Color3.fromRGB(119,233,182),Enum.PartType.Ball).Material=Enum.Material.Neon
 model.Parent=character
end
return Equipment
