-- Pure lease checks used inside atomic UpdateAsync callbacks.
local Lease={Duration=180}
function Lease.CanAcquire(record,owner,now)
 if type(record)~="table" or type(record._lease)~="table" then return true end
 local lease=record._lease
 if lease.owner==owner then return true end
 return type(lease.expires)~="number" or lease.expires~=lease.expires or lease.expires<=now
end
function Lease.Owns(record,owner)
 return type(record)=="table" and type(record._lease)=="table" and record._lease.owner==owner
end
function Lease.Stamp(record,owner,now)
 record._lease={owner=owner,expires=now+Lease.Duration}
 return record
end
return Lease
