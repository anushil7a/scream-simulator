-- The real production mic controller; this lab never synthesizes mic readiness.
local Players=game:GetService("Players")
local UIS=game:GetService("UserInputService")
local Run=game:GetService("RunService")
local p=Players.LocalPlayer
local mic=require(script.Parent:WaitForChild("Microphone")).new()
local remote=game.ReplicatedStorage:WaitForChild("MicLab")
local gui=Instance.new("ScreenGui");gui.Name="MicFeasibilityLab";gui.ResetOnSpawn=false;gui.Parent=p:WaitForChild("PlayerGui")
local panel=Instance.new("ScrollingFrame");panel.CanvasSize=UDim2.fromOffset(0,310);panel.ScrollBarThickness=4;panel.Size=UDim2.new(1,-24,1,-24);panel.Position=UDim2.fromOffset(12,12);panel.BackgroundColor3=Color3.fromRGB(19,32,40);panel.Parent=gui
local sizeLimit=Instance.new("UISizeConstraint");sizeLimit.MaxSize=Vector2.new(680,340);sizeLimit.Parent=panel
local function text(y,height,words)
 local label=Instance.new("TextLabel");label.Position=UDim2.fromOffset(12,y);label.Size=UDim2.new(1,-24,0,height);label.BackgroundTransparency=1;label.TextColor3=Color3.new(1,1,1);label.TextWrapped=true;label.TextSize=16;label.Font=Enum.Font.Gotham;label.Text=words;label.Parent=panel;return label
end
text(8,25,"SCREAM SIMULATOR • MIC FEASIBILITY LAB")
local status=text(36,52,"Checking microphone…")
local meter=text(90,32,"Scream Power: 0%")
local result=text(123,42,"No capture submitted. Live voice uses Roblox proximity audio.")
text(254,48,"Hold E FIRST, speak immediately, then release. No recording or replay. Hear live voice through a SECOND nearby player; no self-playback.")
local function button(name,x,width,words,fn)
 local b=Instance.new("TextButton");b.Name=name;b.Position=UDim2.new(x,8,0,174);b.Size=UDim2.new(width,-16,0,64);b.Text=words;b.TextWrapped=true;b.TextSize=14;b.BackgroundColor3=Color3.fromRGB(63,108,110);b.TextColor3=Color3.new(1,1,1);b.Parent=panel
 if fn then b.Activated:Connect(fn) end;return b
end
local source;local sequence=0;local releaseTime;local cooldown=0;local captureTime=0
local function cancel()
 source=nil;releaseTime=nil;mic:Cancel();remote:FireServer("cancel")
end
local function begin(input)
 if source or releaseTime or os.clock()<cooldown or not mic:Begin() then return end
 sequence+=1;source=input;captureTime=os.clock();remote:FireServer("begin",sequence)
 result.Text="Speak now while holding. Release to send one test pulse."
end
local function finish(input)
 if source~=input then return end
 source=nil;local power,reason=mic:Release();releaseTime=os.clock()
 if power<.08 then releaseTime=nil;remote:FireServer("cancel");result.Text=reason or "No live voice during the capture window. Try again.";return end
 local mouse=p:GetMouse()
 remote:FireServer("release",sequence,power,mouse.Hit.Position);result.Text="Waiting for server acknowledgement…"
end
button("Calibrate",0,.3,"CALIBRATE",function() cancel();mic:Calibrate() end)
button("Retry",.3,.25,"RETRY ACCESS",function() cancel();mic:Check() end)
local capture=button("Capture",.55,.45,"HOLD + VOICE\nRELEASE [E]")
capture.InputBegan:Connect(function(input) if input.UserInputType==Enum.UserInputType.Touch or input.UserInputType==Enum.UserInputType.MouseButton1 then begin(input) end end)
UIS.InputBegan:Connect(function(input,processed) if not processed and input.KeyCode==Enum.KeyCode.E then begin("keyboard") end end)
UIS.InputEnded:Connect(function(input)
 if input.KeyCode==Enum.KeyCode.E then finish("keyboard")
 elseif source==input or (typeof(source)=="Instance" and source.UserInputType==Enum.UserInputType.MouseButton1 and input.UserInputType==Enum.UserInputType.MouseButton1) then finish(source) end
end)
UIS.WindowFocusReleased:Connect(cancel);p.CharacterRemoving:Connect(cancel)
remote.OnClientEvent:Connect(function(message,power,id)
 if id~=sequence or not releaseTime then return end
 if message=="Accepted" then cooldown=os.clock()+4 end
 result.Text=string.format("%s • power %.0f%% • acknowledgement %.0f ms",message,power*100,releaseTime and (os.clock()-releaseTime)*1000 or 0)
 releaseTime=nil
end)
Run.RenderStepped:Connect(function()
 if releaseTime and os.clock()-releaseTime>5 then releaseTime=nil;result.Text="Server acknowledgement timed out. Rejoin and retry." end
 status.Text=mic.status;meter.Text=string.format("LIVE mic: %d%% • %s",math.floor(mic.power*100),source and "attack held" or "hold E before speaking")
 if source and not mic.ready then cancel() end
 if source and os.clock()-captureTime>8 then cancel();result.Text="Capture expired. Hold again and use a fresh live scream." end
 local remaining=math.max(0,cooldown-os.clock())
 local sampling=1.25-(os.clock()-captureTime)
 capture.Text=remaining>0 and string.format("COOLDOWN %.1fs",remaining) or source and (sampling>0 and string.format("SPEAK NOW • %.1fs\nTHEN RELEASE",sampling) or "WINDOW ENDED\nRELEASE TO TEST") or "HOLD + VOICE\nRELEASE [E]"
end)
