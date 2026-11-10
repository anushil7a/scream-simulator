-- Disposable native geometry/lifetime audit and owner-review showcase.
assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
local Visuals=require(game:GetService("ReplicatedStorage").BeamVisuals)
local Style=require(game:GetService("ReplicatedStorage").Shared.BeamStyle)
local checks=0
local function check(ok,message) assert(ok,message);checks+=1 end
local rigs={}
for i=1,24 do
 local rig=Visuals.Create();table.insert(rigs,rig)
 Visuals.Update(rig,Vector3.zero,Vector3.yAxis,40,7,Color3.fromRGB(70,220,255),100,false)
 Visuals.Animate(rig,1,Vector3.zero,false)
 check(#rig.parts>=5,"Core starved by other beams")
end
check(Visuals.Budget()<=Style.MaxParts,"Exceeded global allocation cap")
for _,rig in ipairs(rigs) do
 for _,part in ipairs(rig.parts) do check(not part.CanCollide and not part.CanQuery and not part.CanTouch,"Cosmetic changed physics") end
 Visuals.Animate(rig,2,Vector3.zero,true)
 check(#rig.parts==4,"Reduced effects retained decoration")
 Visuals.Animate(rig,3,Vector3.new(1000,0,0),false)
 check(#rig.parts==0,"Offscreen distance retained parts")
 Visuals.Destroy(rig);Visuals.Destroy(rig)
end
local allocated,cached=Visuals.Budget();check(allocated==cached,"Rig cleanup leaked")
Visuals.Clear();check(Visuals.Budget()==0,"Final pool cleanup leaked")
print("BEAM_VISUAL_AUDIT_PASS "..checks)
local camera=workspace.CurrentCamera;camera.CameraType=Enum.CameraType.Scriptable
camera.CFrame=CFrame.lookAt(Vector3.new(0,25,76),Vector3.new(0,25,0));camera.FieldOfView=46
local run=game:GetService("RunService")
local showcase={}
for i,level in ipairs({1,10,30,50,80,100}) do
 local origin=Vector3.new(-22,49-i*7,0)
 local rig=Visuals.Create();table.insert(showcase,rig)
 Visuals.Update(rig,origin,Vector3.xAxis,44,4+3*level/100,Color3.fromHSV(.53+(i-1)*.065,.65,1),level,false)
 local anchor=Instance.new("Part");anchor.Anchored=true;anchor.CanCollide=false;anchor.Transparency=1;anchor.Position=origin+Vector3.new(-5,0,0);anchor.Parent=workspace
 local billboard=Instance.new("BillboardGui");billboard.Size=UDim2.fromOffset(90,30);billboard.AlwaysOnTop=true;billboard.Parent=anchor
 local text=Instance.new("TextLabel");text.BackgroundTransparency=1;text.Text="LEVEL "..level;text.Font=Enum.Font.GothamBold;text.TextSize=16;text.TextColor3=Color3.new(1,1,1);text.Size=UDim2.fromScale(1,1);text.Parent=billboard
end
run.RenderStepped:Connect(function()
 camera.CameraType=Enum.CameraType.Scriptable
 camera.CFrame=CFrame.lookAt(Vector3.new(0,25,76),Vector3.new(0,25,0))
 for _,rig in ipairs(showcase) do Visuals.Animate(rig,os.clock(),camera.CFrame.Position,false) end
end)
