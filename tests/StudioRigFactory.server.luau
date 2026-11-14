-- Append to Bootstrap in disposable Studio together with the RunAnimation fixture.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 for _,kind in ipairs({Enum.HumanoidRigType.R6,Enum.HumanoidRigType.R15}) do
  local description=Instance.new("HumanoidDescription")
  local model=game.Players:CreateHumanoidModelFromDescriptionAsync(description,kind);description:Destroy()
  model.Name="PoseRig"..kind.Name
  local animate=model:FindFirstChild("Animate");if animate then animate.Disabled=true end
  model.Parent=workspace
  model:PivotTo(CFrame.new(kind==Enum.HumanoidRigType.R6 and -5 or 5,6,560))
  model.HumanoidRootPart.Anchored=true
 end
end)
