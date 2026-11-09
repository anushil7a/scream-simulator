-- Test-fixture statistics, not production telemetry. Nearest-rank percentiles.
return function(samples)
 local values={};local sum,slow=0,0
 for _,dt in ipairs(samples) do
  if type(dt)=='number' and dt==dt and dt>0 and dt<math.huge then
   table.insert(values,dt);sum+=dt;if dt>.05 then slow+=1 end
  end
 end
 table.sort(values)
 if #values==0 then return {samples=0} end
 return {samples=#values,meanMs=sum/#values*1000,p95Ms=values[math.ceil(#values*.95)]*1000,
  maxMs=values[#values]*1000,over50ms=slow}
end
