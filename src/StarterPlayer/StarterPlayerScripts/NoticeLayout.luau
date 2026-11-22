-- Bounded notice geometry; coordinates share the existing HUD ScreenGui inset.
local Layout={}
function Layout.Get(width,height,touch,map,testTools,talkVisible,statusPosition,statusSize,objectiveBottom)
 local right=width-14
 if map and map.available then right=math.min(right,width-map.width-22) end
 if testTools then right=math.min(right,width-(width<432 and 100 or 126)-8) end
 local bottom=height-(touch and 203 or 110)
 local h=math.floor(math.min(height*.35,bottom-66))
 local w=math.floor(math.min(640,right-14))
 local result={x=14,y=66,width=math.max(0,w),height=math.max(0,h),available=w>=120 and h>=44 and (not touch or width>=312)}
 local status=statusPosition and {x=statusPosition.X,y=statusPosition.Y,width=statusSize.X,height=statusSize.Y}
 if status and result.available and Layout.Overlaps(result,status) then
  -- Keep health and progress readable while a notice is on screen.
  local beside=math.ceil(status.x+status.width+8)
  if right-beside>=120 then
   result.x=beside;result.width=math.floor(math.min(640,right-beside))
  else
   result.y=math.ceil(math.max(status.y+status.height,objectiveBottom or 0)+8)
   result.height=math.max(0,math.floor(math.min(height*.35,bottom-result.y)))
   result.available=result.height>=44
  end
 end
 if not touch and talkVisible then
  local talkX=width/2-60
  local lastX=width-274-8-120 -- leave space to the left of the combat controls
  if talkX>lastX then
   local topX=(width<380 and 190 or 243)+8
   local topWidth=height<156 and 84 or 120
   if height>=150 and height<318 and topX+topWidth<=right then
    -- The bottom lane crosses the status and quest rail at this height.
    result.baseTalkX=topX;result.baseTalkY=12;result.baseTalkWidth=topWidth
   elseif lastX>=14 then
    result.baseTalkX=lastX;result.baseTalkY=height-108
   end
  end
 end
 if touch and talkVisible then
  local navRight=width<380 and 190 or 243
  local x=navRight+8
  local talk={x=width/2-60,y=height-249,width=120,height=44}
  -- The short safe area can put the default target above the HUD or on the launchers.
  -- Move above the action row when the top lane fits between the nav and right column.
  if (talk.y<0 or (talk.y<56 and talk.x<navRight)) and x+talk.width<=right and height>=239 then
   talk.x=x;talk.y=math.min(14,height-239)
   result.baseTalkX=talk.x;result.baseTalkY=talk.y
  end
  if Layout.Overlaps(result,talk) or status and Layout.Overlaps(status,talk) then
   -- Never move TALK into the native bottom-left thumbstick exclusion zone.
   if x+120<=right then result.moveTalk=true;result.talkX=x;result.talkY=14 else result.available=false end
  end
 end
 return result
end
function Layout.Modal(width,height,shortLandscape)
 if shortLandscape then
  local menuWidth=math.min(720,width-24)
  local w=menuWidth-70
  return {x=(width-menuWidth)/2+8,y=8,width=math.max(0,w),height=44,available=w>=120 and height>=128}
 end
 local w=math.min(640,width-28)
 return {x=(width-w)/2,y=8,width=math.max(0,w),height=48,available=w>=120 and height>=128}
end
function Layout.Overlaps(a,b)
 return a.x<b.x+b.width and b.x<a.x+a.width and a.y<b.y+b.height and b.y<a.y+a.height
end
return Layout
