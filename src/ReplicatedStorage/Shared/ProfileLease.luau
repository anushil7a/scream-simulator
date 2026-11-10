-- Pure lease checks used inside atomic UpdateAsync callbacks.
local Lease={Duration=180}
function Lease.CanAcquire(record,owner,now,token)
 if type(record)~="table" or type(record._lease)~="table" then return true end
 local lease=record._lease
 if lease.owner==owner and (token==nil or lease.token==token) then return true end
 return type(lease.expires)~="number" or lease.expires~=lease.expires or lease.expires<=now
end
function Lease.Owns(record,owner,token)
 return type(record)=="table" and type(record._lease)=="table" and record._lease.owner==owner and (token==nil or record._lease.token==token)
end
function Lease.Stamp(record,owner,now,token)
 record._lease={owner=owner,token=token,expires=now+Lease.Duration}
 return record
end
return Lease
