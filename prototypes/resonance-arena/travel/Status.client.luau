local player=game:GetService("Players").LocalPlayer
local gui=Instance.new("ScreenGui")
gui.Name="TravelReview";gui.ResetOnSpawn=false;gui.Parent=player:WaitForChild("PlayerGui")
local label=Instance.new("TextLabel")
label.Size=UDim2.new(.8,0,0,58);label.Position=UDim2.new(.1,0,0,10)
label.BackgroundColor3=Color3.fromRGB(22,34,44);label.TextColor3=Color3.fromRGB(234,248,248)
label.Font=Enum.Font.GothamBold;label.TextSize=16;label.TextWrapped=true;label.Parent=gui
local function refresh()
 label.Text="STUDIO TRAVEL TEST\n"..(player:GetAttribute("TravelStatus") or "Use the portal prompt.")
end
player:GetAttributeChangedSignal("TravelStatus"):Connect(refresh)
refresh()
