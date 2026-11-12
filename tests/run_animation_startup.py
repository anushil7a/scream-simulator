"""Whole RunAnimation script, mocked signals/yielding dependencies; no native scheduling claim."""
from pathlib import Path
import ast,subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1];P='src/StarterPlayer/StarterPlayerScripts/RunAnimation.client.luau'
tree=ast.parse((R/'tests/animation_lifecycle.py').read_text())
setup=next(ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='setup' for t in n.targets))
extra=r'''
local pauseAt=PAUSE;local waits=0;local imports=0
services.ReplicatedStorage.WaitForChild=function(_,name)waits+=1;if pauseAt=='Shared' then coroutine.yield()end;return shared end
shared.WaitForChild=function(_,name)waits+=1;if pauseAt=='Config' then coroutine.yield()end;return 'config' end
require=function(name)assert(name=='config');imports+=1;if pauseAt=='require' then coroutine.yield()end;return {}end
local co=coroutine.create(function()
'''
checks=r'''
end)
local ok,err=coroutine.resume(co);assert(ok,err)
if pauseAt~='normal' then
 check(coroutine.status(co)=='suspended','Dependency did not yield')
 script.Destroying:Fire();local beforeWaits=waits;local beforeImports=imports
 ok,err=coroutine.resume(co);assert(ok,err);drain()
 check(waits==beforeWaits and imports==beforeImports,'Dependency continued after destruction')
 check(players.PlayerAdded:Count()==0 and players.PlayerRemoving:Count()==0 and run.PreAnimation:Count()==0 and run.PreSimulation:Count()==0,'Late gameplay subscription after destroyed startup')
 check(initial.CharacterAdded:Count()==0 and initial.CharacterRemoving:Count()==0 and initial.Character.DescendantAdded:Count()==0,'Late rig subscription')
else
 drain();check(players.PlayerAdded:Count()==1 and run.PreSimulation:Count()==1,'Normal startup disabled')
 check(initial.Character.DescendantAdded:Count()==1,'Normal rig missing')
 script.Destroying:Fire();drain()
 check(players.PlayerAdded:Count()==0 and run.PreSimulation:Count()==0 and initial.Character.DescendantAdded:Count()==0,'Normal cleanup failed')
end
print('PASS '..checks..' startup checks '..pauseAt)
'''
def run(source,stage):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(setup+extra.replace('PAUSE',repr(stage))+source+checks);p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],capture_output=True,text=True,timeout=20)
 finally:p.unlink()
def builder_contract(source):
 # Extract actual resolver only; importing the builder would emit unrelated harnesses.
 tree=ast.parse((R/'tests/build_studio_harness.py').read_text())
 function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='inline')
 regex=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='REQUIRE' for t in n.targets))
 import re
 ns={'re':re,'client':R/'src/StarterPlayer/StarterPlayerScripts','MODULES':{'Config':R/'src/ReplicatedStorage/Shared/Config.luau'}}
 exec(compile(ast.Module(body=[regex,function],type_ignores=[]),'actual_harness_resolver','exec'),ns)
 class Input:
  def __init__(self,text,name='RunAnimation.client.luau'):self.text=text;self.name=name
  def read_text(self):return self.text
  def resolve(self):return (ns['client']/self.name).resolve()
 result=ns['inline'](Input(source))
 assert 'local Config=modules.Config' in result and 'require(' not in result
 assert 'WaitForChild("Shared")' not in result and 'WaitForChild("Config")' not in result
 assert result.index('script.Destroying:Connect')<result.index('local Config=modules.Config')
 invalid=[source.replace('WaitForChild("Shared")','WaitForChild("Wrong")'),source.replace('WaitForChild("Config")','WaitForChild("Other")'),source.replace('require(configModule)','require(otherModule)'),source.replace('local configModule=shared:','local configModule=elsewhere:'),source.replace('local Config=require(configModule)','configModule=other;local Config=require(configModule)')]
 for mutant in invalid:
  try:ns['inline'](Input(mutant))
  except RuntimeError:pass
  else:raise AssertionError('Unknown alias binding accepted')
 try:ns['inline'](Input(source,'Other.client.luau'))
 except RuntimeError:pass
 else:raise AssertionError('Alias exception escaped RunAnimation')
 ns['MODULES']={}
 try:ns['inline'](Input(source))
 except RuntimeError:pass
 else:raise AssertionError('Missing bundled Config accepted')
 print('PASS 10 actual harness resolver contract assertions (including seven rejected bindings)')

if __name__=='__main__':
 source=(R/P).read_text()
 if '--baseline' in sys.argv:
  source=subprocess.check_output(['git','show','927ee47:'+P],cwd=R).decode()
  for stage in ['Shared','Config','require']:
   r=run(source,stage);assert r.returncode and ('Dependency continued after destruction' in r.stderr or 'Late gameplay subscription' in r.stderr),r.stdout+r.stderr
  print('PASS historical whole-script late-startup reproduction at all three yields')
 else:
  builder_contract(source)
  for stage in ['Shared','Config','require','normal']:
   r=run(source,stage);assert r.returncode==0,r.stdout+r.stderr;print(r.stdout,end='')
  if '--negative-controls' in sys.argv:
   for statement,stage in [('local shared=replicated:WaitForChild("Shared");if destroyed then return end','Shared'),('local configModule=shared:WaitForChild("Config");if destroyed then return end','Config'),('local Config=require(configModule);if destroyed then return end','require')]:
    assert statement in source
    r=run(source.replace(statement,statement.split(';')[0]),stage);assert r.returncode and ('Dependency continued after destruction' in r.stderr or 'Late gameplay subscription' in r.stderr),r.stdout+r.stderr
   hook='script.Destroying:Connect(function() destroyed=true end)'
   assert source.count(hook)==1
   r=run(source.replace(hook,''),'Shared')
   assert r.returncode and 'Dependency continued after destruction' in r.stderr,r.stdout+r.stderr
   print('PASS 4 negative controls: three dependency fences and early teardown hook')
