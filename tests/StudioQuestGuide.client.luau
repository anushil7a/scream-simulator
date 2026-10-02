-- Append to Client with the matching server fixture. Measures rendered tracker text.
task.spawn(function()
 assert(game.PlaceId==0 and game:GetService("RunService"):IsStudio())
 local texts={};local clipped={};local started=os.clock()
 repeat
  task.wait(.1)
  if tracked.Text~="" then texts[tracked.Text]=true;if not tracked.TextFits then clipped[tracked.Text]=true end end
 until workspace:GetAttribute("QuestGuideFixtureDone") or os.clock()-started>30
 local count=0;local completed=false;local delivery=false;local race=false
 for text in texts do count+=1;completed=completed or string.find(text,"claim in Quests",1,true)~=nil;delivery=delivery or string.find(text,"Deliver to the boardwalk music stage",1,true)~=nil;race=race or string.find(text,"Run east along the promenade!",1,true)~=nil end
 local passed=workspace:GetAttribute("QuestGuideFixtureDone")==true and count==18 and completed and delivery and race and next(clipped)==nil
 workspace:SetAttribute("QuestGuideResult",game:GetService("HttpService"):JSONEncode({passed=passed,textVariants=count,clipped=clipped,completion=completed,delivery=delivery,race=race}))
 print("Quest guide",passed,count)
end)
