-- Pass the actual ScreamEffects module in a disposable local Client Play session.
return function(Effects)
 assert(game:GetService("RunService"):IsRunning() and game.PlaceId==0)
 for _,family in ipairs({"Pulse","Echo","Feathers","Quake","Storm","Nova"}) do
  Effects.Render(family,Vector3.new(0,20,0),Vector3.yAxis,30,4,Color3.new(1,.8,.3),false,5)
 end
 for _,part in ipairs(workspace:GetChildren()) do if part.Name=="ScreamVisual" then
  for _,n in ipairs({part.CFrame:GetComponents()}) do assert(n==n and math.abs(n)<math.huge,"Invalid vertical-aim transform") end
 end end
 for i=1,24 do Effects.Render("Storm",Vector3.new(i*2,20,0),Vector3.zAxis,50,7,Color3.new(.2,.8,1),false,10) end
 local busy=Effects.Budget();assert(busy.core<=busy.coreLimit and busy.detail<=busy.detailLimit)
 task.wait(.8)
 local idle=Effects.Budget();assert(idle.core==0 and idle.detail==0)
 Effects.Render("Nova",Vector3.new(0,20,0),Vector3.yAxis,30,4,Color3.new(1,1,1),true,1)
 local reduced=Effects.Budget();assert(reduced.core==2 and reduced.detail==0)
 task.wait(.5)
 local final=Effects.Budget();assert(final.core==0 and final.detail==0)
 return {passed=true,busy=busy,idle=idle,reduced=reduced,final=final}
end
