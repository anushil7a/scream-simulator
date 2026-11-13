"""Actual collection/copy fragments, mocked UI rectangles; not native text-fit evidence."""
from pathlib import Path
import subprocess,tempfile,sys
R=Path(__file__).resolve().parents[1]
source=(R/'src/StarterPlayer/StarterPlayerScripts/Client.client.luau').read_text()
def build(c):
 a=c.index('  local nextStyle',c.index('title.Text="BEAM COLLECTION"'));collection=c[a:c.index(' elseif selected=="Quests"',a)]
 a=c.index('  local attackHelp');help=c[a:c.index('  info("VOICE SAFETY',a)]
 safety=next(x for x in c.splitlines() if 'info("VOICE SAFETY' in x)
 mic=next(x for x in c.splitlines() if 'info("MICROPHONE' in x)
 return r'''
local Combat=require('../src/ReplicatedStorage/Shared/VoiceCombat')
local checks=0;local function check(v,m)assert(v,m);checks+=1 end
local UDim2={new=function(a,b,c,d)return {a,b,c,d}end,fromOffset=function(x,y)return {0,x,0,y}end}
local Config={VoiceCombat=Combat,Sounds={{id='one',level=1,name='First',description='First sound'},{id='cap',level=100,name='Cap',description='Last sound'}}}
local cards,messages={},{};local sent={};local muted,gold={},{foo=true};local action={FireServer=function(_,verb,id)table.insert(sent,{verb,id})end}
local function card(height)local c={height=height,children={}};table.insert(cards,c);return c end
local function label(c,text,size,pos)table.insert(c.children,{text=text,size=size,pos=pos});table.insert(messages,text);return {}end
local function button(c,id,text,size,pos,callback)table.insert(c.children,{text=text,size=size,pos=pos,button=true,callback=callback});return {}end
local function info(text)table.insert(messages,text)end
local function draw(data,narrow,sustainedRules)
 cards={};messages={}
'''+collection+r'''
end
for _,width in ipairs({288,328,358,592,672})do
 local narrow=width<500
 for _,level in ipairs({1,100})do for _,automatic in ipairs({false,true})do
 table.clear(sent);draw({level=level,sound='one'},narrow,automatic and {} or nil)
 check(#sent==0,'Render emitted equip command')
 local text=table.concat(messages,'\n')
 check(not string.find(text,'SOUND STYLE',1,true),'Repeated style label')
 check(not string.find(text,'Train at the',1,true),'Repeated training direction')
 check(string.find(text,'Now:',1,true) and string.find(text,'CURRENT BEAM',1,true),'Stats removed')
 check(string.find(text,'Sound styles change audio, not damage or range.',1,true),'Shared explanation removed')
 for _,c in ipairs(cards)do
  check(#c.children==(automatic and 2 or 3),'Unexpected description row')
  check(c.height==(automatic and (narrow and 108 or 64) or (narrow and 150 or 76)),'Empty card space retained')
  for _,child in ipairs(c.children)do
   local x=child.pos[1]*width+child.pos[2];local y=child.pos[3]*c.height+child.pos[4]
   local w=child.size[1]*width+child.size[2];local h=child.size[3]*c.height+child.size[4]
   check(x>=0 and x+w<=width and y>=0 and y+h<=c.height,'Card child outside bounds')
  end
  if narrow then local previous=c.children[#c.children-1];check(c.children[#c.children].pos[4]>=previous.pos[4]+previous.size[4]+8,'Button overlaps description')end
  local button=c.children[#c.children];button.callback()
 end
 check(#sent==(level==100 and 2 or 1),'Locked/unlocked callback gate changed')
 check(cards[1].children[#cards[1].children].text=='EQUIPPED','Equipped label lost')
 check(cards[2].children[#cards[2].children].text==(level==100 and 'EQUIP' or 'LEVEL 100'),'Unlock label lost')
 check((string.find(text,'First sound',1,true)~=nil)==not automatic,'Mode description mismatch')
 end end
end
local function settings(touch,sustainedControl)
 messages={};local sustainedRules={MaxDuration=4,Cooldown=5};local mic={status='Microphone ready'}
'''+help+safety+'\n'+mic+r'''
return messages
end
for _,touch in ipairs({false,true})do for _,automatic in ipairs({false,true})do
 local rows=settings(touch,automatic and {} or nil);local all=table.concat(rows,'\n')
 check(rows[#rows]=='MICROPHONE\nMicrophone ready','Microphone status repeats instructions')
 check((string.find(rows[1],'Beams start OFF.',1,true)~=nil)==automatic,'Wrong default OFF mode copy')
 check(string.find(rows[2],'Stopping attacks does not mute voice.',1,true) and string.find(rows[2],"Use Roblox's mic control to mute",1,true),'Voice safety weakened')
 check(string.find(rows[2],'Roblox records voice for moderation.',1,true),'Moderation notice removed')
 if automatic then
  check(string.find(rows[1],'normal speech can fire attacks',1,true) and string.find(rows[1],'Go quiet before each beam.',1,true),'Automatic safety instructions removed')
  check(string.find(rows[1],'voice chat is unchanged',1,true),'OFF voice distinction removed')
 else check(string.find(rows[1],'Hold',1,true) and string.find(rows[1],'release',1,true),'Legacy controls mislabeled')end
end end
print('PASS '..checks..' actual copy/renderer rectangle assertions; no native text fit claim')
'''
def run(c):
 with tempfile.NamedTemporaryFile('w',suffix='.luau',dir=R/'tests',delete=False,encoding='utf8')as f:f.write(build(c));p=Path(f.name)
 try:return subprocess.run(['luau',str(p)],text=True,capture_output=True,timeout=15)
 finally:p.unlink()
out=run(source);print(out.stdout,end='');assert out.returncode==0,out.stderr
if '--negative-controls' in sys.argv:
 cases=[('narrow and 108 or 64','narrow and 194 or 118','Empty card space retained'),('narrow and 60 or 14','narrow and 40 or 14','Button overlaps description'),('Beams start OFF. BEAMS ON:','BEAMS ON:','Wrong default OFF mode copy'),('Stopping attacks does not mute voice.','Stopping attacks mutes voice.','Voice safety weakened'),('label(c,s.description,','label(c,"SOUND STYLE",','Repeated style label')]
 for old,new,message in cases:
  assert old in source
  out=run(source.replace(old,new));assert out.returncode and message in out.stderr,(message,out.stderr)
 out=run(source.replace('if not sustainedRules then\n   label(c,s.description,','if true then\n   label(c,s.description,'));assert out.returncode and 'Unexpected description row' in out.stderr,out.stderr
 print('PASS 6 copy/layout negative controls')
