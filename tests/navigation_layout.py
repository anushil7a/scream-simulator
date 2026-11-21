"""Actual guide layout sizing and wiring. Not native UI or text-raster evidence."""
from pathlib import Path
import subprocess
import tempfile

root=Path(__file__).resolve().parents[1]
s=(root/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
a=s.index('function academy.trackerLayout(');b=s.index('local function menuKey()',a)
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
for _,view in ipairs({{541,239},{567,241},{567,280},{600,314},{784,296}})do
 local width,height=view[1],view[2]
 local left,top,cardWidth,cardHeight=academy.trackerLayout({X=width,Y=height},true,160)
 check(left>=math.ceil(width*.4)+8,'Tracker enters thumbstick lane')
 check(left+cardWidth<=width-103,'Tracker enters Jump lane')
 check(top>=height-91,'Tracker enters combat lane')
 check(top+cardHeight<=height-12,'Tracker crosses bottom safe margin')
 check(cardWidth>=212 and cardHeight==60,'Compact objective has no room for timer/Guide')
end
for _,view in ipairs({{388,704,true,160},{567,315,true,160},{1024,768,false,64},{320,240,true,160}})do
 local left,top,w,h=academy.trackerLayout({X=view[1],Y=view[2]},view[3],view[4])
 check(left==16 and top==view[4] and w==290 and h==50,'Layout changed outside verified compact lane')
end
print('PASS '..checks..' navigation layout checks; no native rendering claim')
'''
def run(payload):
    with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',prefix='tmp_layout_',dir=root/'tests',delete=False) as f:
        f.write(payload)
        temp=Path(f.name)
    try:return subprocess.run(['luau',str(temp)],cwd=root,capture_output=True,text=True)
    finally:temp.unlink()
result=run(code)
assert result.returncode==0,result.stderr
print(result.stdout.strip())
for old,new,reason in [
    ('math.ceil(w*.4)+8','16','Tracker enters thumbstick lane'),
    ('w-103','w-80','Tracker enters Jump lane'),
    ('math.max(defaultY,h-91)','defaultY','Tracker enters combat lane'),
]:
    assert code.count(old)==1,old
    result=run(code.replace(old,new))
    assert result.returncode and reason in result.stderr,result.stderr
print('PASS 3 tracker lane negative controls')
assert 'or noticeView:Overlaps(passive,gui,talkButton)' in s and 'meter,academy.guidePanel}' in s
assert 'if academy.guideText.Text~=text' in s
