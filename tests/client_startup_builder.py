"""Exact Client startup bundler contracts; no native run or external module access."""
from pathlib import Path
from unittest.mock import patch
R=Path(__file__).resolve().parents[1]
builder=R/'tests/build_studio_harness.py'
source=builder.read_text();namespace={'__file__':str(builder)}
exec(compile(source[:source.index("out=ROOT/'build'")],str(builder),'exec'),namespace)
client=R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau'
original=client.read_text();count=0

def check(value,message):
 global count
 assert value,message;count+=1

bundled=namespace['inline'](client)
check('loadClientDependency' not in bundled and 'require(dependency)' not in bundled,'Loader not resolved')
check('script:IsDescendantOf(game)' in bundled and 'if not clientCheckpoint() then return end' in bundled,'Real-script lifetime check removed')
check('local mic=modules.Microphone;' in bundled and 'mic=mic.new()' in bundled,'Constructor order changed')
check('local shared=RS:WaitForChild("Shared")' not in bundled,'Standalone bundle waits for external Shared')
read=Path.read_text
mutations=[
 ('local value=require(dependency)','local value=require(otherDependency)'),
 ('local dependency\n if direct then','local otherDependency\n if direct then'),
 ('loadClientDependency(script.Parent,"Microphone")','loadClientDependency(script.Parent,"UnknownModule")'),
 ('loadClientDependency(script.Parent,"Microphone")','loadClientDependency(RS.Shared,"Microphone")'),
 ('loadClientDependency(RS.Shared,"AttackAudioConfig",true)','loadClientDependency(RS.Shared,"AttackAudioConfig")'),
 ('loadClientDependency(script.Parent,"Microphone")','loadClientDependency(script.Parent,"Microphone",true)'),
 ('loadClientDependency(script.Parent,"Microphone")','loadClientDependency(somewhere,"Microphone")'),
 ('local shared=RS:WaitForChild("Shared");if not clientCheckpoint() then return end','local shared=RS.Shared'),
]
for old,new in mutations:
 assert original.count(old)==1,old
 changed=original.replace(old,new)
 def mocked_read(path,*args,**kwargs):
  return changed if path.resolve()==client.resolve() else read(path,*args,**kwargs)
 with patch.object(Path,'read_text',mocked_read):
  try:namespace['inline'](client)
  except RuntimeError:check(True,'Rejected changed binding')
  else:raise AssertionError('Unsupported binding accepted: '+new)
preview=(R/'tests/build_ui_preview.py').read_text()
check('ownClient(function() screen:Destroy() end)' in preview and 'ownClient(function() gui:Destroy() end)' in preview,'Synthetic root not owned')
check('script:IsDescendantOf(game)' not in preview,'Preview rewrites real-script ancestry check')
# Execute the exact builder's captured callback instrumentation with Lua doubles.
import ast,subprocess,tempfile
bsource=(R/'tests/build_onboarding_review.py').read_text();tree=ast.parse(bsource)
call=next(node.value for node in tree.body if isinstance(node,ast.Assign) and isinstance(node.value,ast.Call) and getattr(node.value.func,'id',None)=='replace_once' and isinstance(node.value.args[1],ast.Constant) and node.value.args[1].value.startswith('b.Activated:Connect'))
old,new=ast.literal_eval(call.args[1]),ast.literal_eval(call.args[2])
check(original.count(old)==1,'Onboarding callback hook no longer matches exact production')
function=next(node for node in tree.body if isinstance(node,ast.FunctionDef) and node.name=='replace_once')
ns={};exec(compile(ast.Module(body=[function],type_ignores=[]),'<exact-replace>','exec'),ns)
try:ns['replace_once'](old.replace('not clientDestroyed','true'),old,new)
except AssertionError:check(True,'Changed callback rejected')
else:raise AssertionError('Guard change silently accepted')
code="""local clientDestroyed=false;local fixtureCallbacks={};local registered;local calls=0;local sum=0
local name='Test';local b={Activated={Connect=function(_,fn)registered=fn end}}
local callback=function(a,b)calls+=1;sum+=a+b end
local function build()
"""+new+"""
end
build();assert(registered==fixtureCallbacks.Test.callback,'Fixture bypasses registered guard')
registered(2,3);fixtureCallbacks.Test.callback(4,5);assert(calls==2 and sum==14,'Live forwarding changed')
clientDestroyed=true;registered(10,20);fixtureCallbacks.Test.callback(10,20);assert(calls==2,'Captured fixture callback bypasses teardown')
"""
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='.startup-builder-',dir=R/'tests',delete=False) as f:f.write(code);temp=Path(f.name)
try:subprocess.run(['luau',str(temp)],check=True,cwd=R)
finally:temp.unlink()
check(True,'Registered and captured callback use same terminal guard')
print('PASS',count,'exact startup builder contracts; eight rejected dependency mutations, no native execution')
