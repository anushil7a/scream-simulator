-- Bounded notice geometry; coordinates share the existing HUD ScreenGui inset.
local Layout={}
function Layout.Get(width,height,touch,map,testTools,talkVisible)
 local right=width-14
 if map and map.available then right=math.min(right,width-map.width-22) end
 if testTools then right=math.min(right,width-(width<432 and 100 or 126)-8) end
 local bottom=height-(touch and 203 or 110)
 local h=math.floor(math.min(height*.35,bottom-66))
 local w=math.floor(math.min(640,right-14))
 local result={x=14,y=66,width=math.max(0,w),height=math.max(0,h),available=w>=120 and h>=44 and (not touch or width>=312)}
 if touch and talkVisible and Layout.Overlaps(result,{x=width/2-60,y=height-249,width=120,height=44}) then
  -- Never move TALK into the native bottom-left thumbstick exclusion zone.
  local x=(width<380 and 190 or 243)+8
  if x+120<=right then result.moveTalk=true;result.talkX=x;result.talkY=14 else result.available=false end
 end
 return result
end
function Layout.Modal(width,height)
 local w=math.min(640,width-28)
 return {x=(width-w)/2,y=8,width=math.max(0,w),height=48,available=w>=120 and height>=128}
end
function Layout.Overlaps(a,b)
 return a.x<b.x+b.width and b.x<a.x+a.width and a.y<b.y+b.height and b.y<a.y+a.height
end
return Layout
