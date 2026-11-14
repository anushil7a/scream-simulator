-- Disposable Studio UI fixture; copy alongside production CityMap, then remove after Play.
local M=require(script.Parent:WaitForChild("CityMap"))
local g=Instance.new("ScreenGui");g.Name="CityMapReview";g.Parent=game.Players.LocalPlayer.PlayerGui
local result={}
for i,width in ipairs({648,270}) do
 local holder=Instance.new("Frame");holder.Size=UDim2.fromOffset(width,274);holder.Position=UDim2.fromOffset(40+(i-1)*700,150);holder.BackgroundColor3=Color3.fromRGB(19,32,40);holder.Parent=g
 local view=M.create(holder)
 M.update(view,{Position=Vector3.new(-600,0,210),CFrame=CFrame.lookAt(Vector3.zero,Vector3.new(1,0,0))})
 game:GetService("RunService").RenderStepped:Wait()
 assert(math.abs(view.map.AbsoluteSize.X/view.map.AbsoluteSize.Y-1.2)<.02,"Map proportions")
 assert(math.abs(view.dot.Position.X.Scale-1/12)<.0001,"Player x")
 assert(math.abs(view.dot.Position.Y.Scale-.675)<.0001,"Player z")
 assert(math.abs(view.arrow.Rotation-90)<.001,"East heading")
 M.update(view,nil);assert(not view.dot.Visible,"Missing root hidden")
 M.update(view,{Position=Vector3.new(-600,0,210),CFrame=CFrame.new()})
 assert(view.dot.Visible,"Root restored")
 table.insert(result,{width=width,checks=6,mapWidth=view.map.AbsoluteSize.X,mapHeight=view.map.AbsoluteSize.Y})
end
g:SetAttribute("Result",game:GetService("HttpService"):JSONEncode(result))
