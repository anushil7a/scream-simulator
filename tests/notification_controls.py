"""Mutation controls for rendered-time queue guarantees; no Roblox services."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
module=(root/'src/StarterPlayer/StarterPlayerScripts/NotificationQueue.luau').read_text()
suite=(root/'tests/notification_queue.luau').read_text().split('\n',1)[1]
cases=[
 ('else table.insert(self.pending,entry) end','else self.active=entry end','Same-frame milestone lost'),
 ('if self.active and priority>self.active.priority then','if false then','Critical failure queued behind routine notice'),
 ('math.clamp(utf8.len(text) or #text,88,264)/22','0.01','Notice overwritten before readable dwell'),
 ('for _,entry in ipairs(self.pending) do if entry.text==text then return end end','','Pending duplicate queued'),
 ('if self.active and self.active.key==key then self.active=table.remove(self.pending,1) end',
  'if self.active and self.active.key==key then self.active=nil end',
  'Keyed normal replacement bypassed waiting critical warning'),
]
for old,new,failure in cases:
 assert module.count(old)==1,old
 source='local Queue=(function()\n'+module.replace(old,new)+'\nend)()\n'+suite
 with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',suffix='.luau',dir=root/'tests',delete=False) as f:
  path=Path(f.name);f.write(source)
 try:
  result=subprocess.run(['luau',str(path)],cwd=root,capture_output=True,text=True,encoding='utf-8')
  assert result.returncode!=0 and failure in result.stderr,result.stdout+result.stderr
  print('PASS queue negative control: '+failure)
 finally:path.unlink()
