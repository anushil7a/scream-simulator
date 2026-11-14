-- Presentation only: accept monotonically increasing, server-confirmed damage.
local Feedback={};Feedback.__index=Feedback
local function number(n)return type(n)=="number" and n==n and math.abs(n)<math.huge end
function Feedback.new()return setmetatable({sequence=0,total=0,expires=0,discardedThrough=0},Feedback)end
function Feedback:Accept(sequence,total,now)
 if not number(sequence) or sequence%1~=0 or sequence<1 or sequence<self.sequence or sequence<=self.discardedThrough
  or not number(total) or total%1~=0 or total<=0 or total>32768 or not number(now) then return false end
 if sequence==self.sequence and total<=self.total then return false end
 self.sequence=sequence;self.total=total;self.expires=now+.7
 return true
end
function Feedback:DiscardThrough(sequence)
 if not number(sequence) or sequence%1~=0 or sequence<0 then return false end
 self.discardedThrough=math.max(self.discardedThrough,self.sequence,sequence)
 self.expires=0
 return true
end
function Feedback:Read(now)
 if now>=self.expires then return nil end
 return self.total
end
return Feedback
