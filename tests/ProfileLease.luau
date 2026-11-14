local Lease=require("../src/ReplicatedStorage/Shared/ProfileLease")
local function expect(value) assert(value) end
expect(Lease.CanAcquire(nil,"A",100))
expect(Lease.CanAcquire({level=30},"A",100))
local profile=Lease.Stamp({level=30},"A",100)
expect(Lease.Owns(profile,"A"))
expect(not Lease.CanAcquire(profile,"B",100))
expect(not Lease.CanAcquire(profile,"B",279))
expect(Lease.CanAcquire(profile,"B",280))
Lease.Stamp(profile,"B",281)
expect(not Lease.Owns(profile,"A")) -- stale server's save must cancel
expect(Lease.Owns(profile,"B"))
expect(not Lease.CanAcquire(profile,"A",300))
profile._lease=nil -- release permits immediate reconnect
expect(Lease.CanAcquire(profile,"C",300))
expect(not Lease.Owns(profile,"B"))
expect(Lease.CanAcquire({_lease={owner="A",expires=0/0}},"B",100))
print("PASS 12 session-lease rule checks")
