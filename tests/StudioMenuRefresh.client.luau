-- Append to Client in an unpublished Studio copy. Synthetic state, real GUI instances.
task.spawn(function()
 task.wait(6)
 local original=data
 data=table.clone(data);data.quests=table.clone(data.quests)
 selected="Screams";modal.Visible=true;render();task.wait(.2)
 local checks=0
 local function check(ok,message) assert(ok,message);checks+=1 end
 local first=content:FindFirstChild("Card")
 content.CanvasPosition=Vector2.new(0,650)
 local scroll=content.CanvasPosition.Y
 data.xp+=1;render()
 check(content:FindFirstChild("Card")==first,"XP rebuilt scream cards")
 check(string.find(subtitle.Text,tostring(data.xp).." /",1,true)~=nil,"XP subtitle stale")
 data.quests.fixture={progress=1};render()
 check(content:FindFirstChild("Card")==first,"Quest progress rebuilt screams")
 check(content.CanvasPosition.Y==scroll,"Unrelated update moved scroll")
 data.level=math.min(300,data.level+5);render();task.wait(.2)
 check(content:FindFirstChild("Card")~=first,"Level did not update cards")
 check(math.abs(content.CanvasPosition.Y-scroll)<1,"Level reset scroll")
 selected="Settings";render();task.wait(.2)
 check(content.CanvasPosition.Y==0,"Tab switch retained prior scroll")
 first=content:FindFirstChild("Card");data.xp+=1;render()
 check(content:FindFirstChild("Card")==first,"XP rebuilt settings")
 data.settings=table.clone(data.settings);data.settings.reducedShake=not data.settings.reducedShake;render()
 check(content:FindFirstChild("Card")~=first,"Settings failed to refresh")
 data=original;modal.Visible=false;renderedMenuKey=nil
 workspace:SetAttribute("MenuRefreshResult",tostring(checks).." checks passed")
 print("Menu refresh: "..checks.." checks passed")
end)
