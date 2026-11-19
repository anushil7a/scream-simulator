-- Adds HP to existing boss plates and enables the engine's remote-player health strip.
-- No screen-space enemy HUD, damage estimates, remote sends or gameplay mutations.
local stopped=false
local playersController
local connections,records={},{}
local bossIds={metronome=true,golem=true,ignis=true,leviathan=true,conductor=true}
local recordCount=0
local worldConnections,folderConnections={},{}
local function clearConnections(list)
 for _,connection in ipairs(list) do connection:Disconnect() end;table.clear(list)
end
local function remove(model)
 local record=records[model];if not record then return end
 if record.view then record.view:Destroy() end
 clearConnections(record.connections);records[model]=nil;recordCount-=1
end
local function clearBosses()
 local pending={};for model in pairs(records) do table.insert(pending,model) end
 for _,model in ipairs(pending) do remove(model) end
end
local function stop()
 if stopped then return end;stopped=true
 clearConnections(connections);clearConnections(worldConnections);clearConnections(folderConnections)
 clearBosses();if playersController then playersController:Destroy() end
end
connections[#connections+1]=script.Destroying:Connect(stop)
local Presentation=require(script.Parent:WaitForChild("HealthBarPresentation"))
if stopped then return end
local Players=game:GetService("Players")
playersController=Presentation.Players(Players,Players.LocalPlayer,workspace)
local function add(model)
 if stopped or not model:IsA("Model") or not bossIds[model.Name] or recordCount>=5 or records[model] then return end
 local record={connections={}};records[model]=record;recordCount+=1
 local function reconcile()
  if stopped or records[model]~=record then return end
  local core=model:FindFirstChild("Core")
  local board=core and core:FindFirstChild("BossNameplate")
  local label=board and board:FindFirstChild("NameAndLevel")
  if not board or not board:IsA("BillboardGui") or not label or not label:IsA("TextLabel") then board=nil;label=nil end
  if record.board==board and record.label==label then return end
  if record.view then record.view:Destroy();record.view=nil end
  record.board,record.label=board,label
  if board then record.view=Presentation.Boss(model,board,label) end
 end
 record.connections[#record.connections+1]=model.DescendantAdded:Connect(reconcile)
 record.connections[#record.connections+1]=model.DescendantRemoving:Connect(function(item)
  if item==record.board or item==record.label or item.Name=="Core" then
   if record.view then record.view:Destroy();record.view=nil end;record.board=nil;record.label=nil
  end
 end)
 reconcile()
end
local bindFolder,bindWorld
bindFolder=function(folder)
 clearConnections(folderConnections);clearBosses()
 if not folder then return end
 folderConnections[#folderConnections+1]=folder.ChildAdded:Connect(add)
 folderConnections[#folderConnections+1]=folder.ChildRemoved:Connect(remove)
 for _,model in ipairs(folder:GetChildren()) do add(model) end
end
bindWorld=function(world)
 clearConnections(worldConnections);bindFolder(nil)
 if not world then return end
 worldConnections[#worldConnections+1]=world.ChildAdded:Connect(function(child)if child.Name=="BossEncounters" then bindFolder(child) end end)
 worldConnections[#worldConnections+1]=world.ChildRemoved:Connect(function(child)if child.Name=="BossEncounters" then bindFolder(nil) end end)
 bindFolder(world:FindFirstChild("BossEncounters"))
end
connections[#connections+1]=workspace.ChildAdded:Connect(function(child)if child.Name=="ScreamSimulatorWorld" then bindWorld(child) end end)
connections[#connections+1]=workspace.ChildRemoved:Connect(function(child)if child.Name=="ScreamSimulatorWorld" then bindWorld(nil) end end)
bindWorld(workspace:FindFirstChild("ScreamSimulatorWorld"))
