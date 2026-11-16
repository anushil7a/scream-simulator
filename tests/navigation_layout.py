"""Actual guide layout sizing and wiring. Not native UI or text-raster evidence."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('academy.guideLayout=function(');b=s.index('local function menuKey()',a)
code='local academy={}\n'+s[a:b]+r'''
local checks=0;local function check(v,msg)assert(v,msg);checks+=1 end
for _,viewport in ipairs({{844,390},{667,375},{640,350},{1280,360}})do
 local x,y,w,h,compact=academy.guideLayout({X=viewport[1],Y=viewport[2]},true,160)
 check(compact and x and y and w and h,'short landscape hid navigation status')
 check(x>=264 and x+w<=viewport[1]-182,'landscape overlaps HUD or minimap reserve')
 check(y>=46 and y+h<=math.min(96,viewport[2]-249),'status overlaps top zone or touch TALK lane')
 check(w>=194 and h>=44,'status/clear tap area too small')
end
local x,y,w,h,compact=academy.guideLayout({X=390,Y=844},true,160)
check(x==16 and y==216 and w==290 and h==62 and compact==false,'portrait guide moved')
local a,b,c,d,e=academy.guideLayout({X=1280,Y=720},false,64)
check(a==16 and b==120 and c==290 and d==62 and e==false,'desktop guide moved')
check(not academy.guideLayout({X=320,Y=315},true,160),'cramped viewport should use clear in menu')
print('PASS '..checks..' navigation layout checks; no native rendering claim')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    f.write(code);temp=Path(f.name)
try:subprocess.run(['luau',str(temp)],cwd=root,check=True)
finally:temp.unlink()
assert 'or noticeView:Overlaps(passive,gui,talkButton)' in s and 'meter,academy.guidePanel}' in s
assert 'if academy.guideText.Text~=text' in s
