-- Lower connected geology under the inhabited terraces. Kept out of navigation
-- envelopes; these are unreachable visual slopes except if a player falls.
-- Every bulk form collides and is tagged for safe return from an off-route fall.
return function(b)
 local old=b.zone
 local sand={{123,118,94},{153,141,111},{176,160,124}}
 local moss={{116,132,86},{92,114,76},{125,141,91}}
 local function mass(n,x,y,z,sx,sy,sz,angle,color,material,shape)
  b:part("Ridge_"..n,{x,y,z},{sx,sy,sz},color,true,{0,angle,0},material,{"CliffReturn"},shape)
 end
 local function bank(id,spec,tone)
  b.zone=id
  local seq={0,12,-16,9,-6,19,-9,15}
  for i,p in ipairs(spec) do
   local x,top,z,w,d,angle=table.unpack(p)
   if b.compact then
    -- Low horizontal beds follow the shoulder of the road. Their exposed edges
    -- share the same lithology as the intertidal ledges on the district coast.
    local length,width=w*1.14,d*1.03
    mass("ShoreBed"..i,x,(top-6)/2,z, length,top+6,width,angle,sand[tone],"Limestone","Ball")
    mass("ShoreCap"..i,x,top*.74,z,length*.83,top*.45,width*.79,angle,
     i%3==0 and moss[2] or sand[3],i%3==0 and "Ground" or "Sandstone","Ball")
    continue
   end
   -- Massive voxels deliberately overlap well below useable surfaces. Wedge
   -- wings feather the contour toward water instead of exposed box ends.
   local height=top+3
   mass("Bed"..i,x,(top-3)/2,z,w,height,d,angle,sand[tone],"Rock","Block")
   for j=1,4 do
    local t=math.rad(angle+(j-1)*90)
    local rx=x+math.cos(t)*w*.43;local rz=z+math.sin(t)*d*.44
    local hh=height*(.50+j*.055)
    mass("Wing"..i.."_"..j,rx,hh/2-2.4,rz,w*.51,hh,d*.52,angle+(-1)^j*29,sand[1+(i+j)%3],"Slate","Wedge")
   end
   for j=1,3 do
    local a=math.rad(j*110+angle)
    local px=x+math.cos(a)*w*(.22+j*.035);local pz=z+math.sin(a)*d*(.25+j*.026)
    local h=5+(j%2)*2.1
    mass("Heather"..i.."_"..j,px,top+h*.21,pz,w*.36,h,d*.35,angle+seq[(i+j)%8+1],moss[1+(i+j)%3],"Grass","Ball")
   end
  end
 end
 -- Below the gardens and Foundry approaches, fit a layered headland with a
 -- narrow ravine towards the coast. Its west end meets the Academy shoulder.
 bank("04",{
  {-620,18,95,186,155,17},{-522,24,77,170,192,-12},{-461,25,-86,177,207,14},
  {-352,20,-153,181,176,-16},{-258,23,-190,149,176,15},
  {-158,28,-154,180,140,-15},{-89,29,-105,154,153,10},{31,21,-106,145,123,-18}
 },2)
 -- Lower dark ledges straddle the magma foothills without bridging any
 -- navigable water or hiding the suspended Astral underside.
 bank("07",{{574,29,-169,135,112,19},{649,31,-136,155,131,-12},{691,30,-96,148,129,25}},1)
 b.zone=old
end
