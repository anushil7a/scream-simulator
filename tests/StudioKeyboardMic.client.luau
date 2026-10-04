-- Append to Client only in disposable Play, then use Studio keyboard input tools.
-- Fake microphone for input routing; no real voice or physical keyboard claim.
assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
mic={ready=true,power=.6,status="SYNTHETIC INPUT TEST",Cancel=function()end,Begin=function()return true end,Release=function()return .6 end,Check=function()end,Calibrate=function()end}
local screams,dodges=0,0
p:SetAttribute("KeyboardScreams",0);p:SetAttribute("KeyboardDodges",0)
remotes.Effect.OnClientEvent:Connect(function(kind)
 if kind=="Scream" then screams+=1;p:SetAttribute("KeyboardScreams",screams)
 elseif kind=="Dodge" then dodges+=1;p:SetAttribute("KeyboardDodges",dodges) end
end)
