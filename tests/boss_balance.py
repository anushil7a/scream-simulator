"""Use the actual authored balance catalog and active layout with Roblox module/vector doubles."""
from pathlib import Path
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
shared=ROOT/'src/ReplicatedStorage/Shared'
base=(ROOT/'tests/fixtures/BossBalance.luau').read_text(encoding='utf-8').split('\n',1)[1]
code='''local Vector3={new=function(x,y,z)return {X=x,Y=y,Z=z} end}
local Color3={fromRGB=function(...)return {...} end}
local nativeRequire=require
local Layout=(function()
'''+(shared/'CompactLayout.luau').read_text(encoding='utf-8')+'''
end)()
local script={Parent={CompactLayout="CompactLayout"}}
local function require(name)
 if name=="CompactLayout" then return Layout end
 return nativeRequire(name)
end
local Catalog=(function()
'''+(shared/'BossCatalog.luau').read_text(encoding='utf-8')+'\nend)()\n'+base
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='tmp_boss_balance_',dir=ROOT/'tests',delete=False,encoding='utf-8') as handle:
    handle.write(code)
    path=Path(handle.name)
try:
    subprocess.run(['luau',str(path)],cwd=ROOT,check=True)
finally:
    path.unlink()
