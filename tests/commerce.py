"""Execute actual receipt handler against a fake atomic store; never Roblox money/saves."""
from pathlib import Path
import subprocess,tempfile
root=Path(__file__).resolve().parents[1]
source=(root/'src/ServerScriptService/Commerce.luau').read_text()
setup='''
local Catalog=require('../src/ReplicatedStorage/Shared/ShopCatalog')
local Ledger=require('../src/ReplicatedStorage/Shared/BoostLedger')
Catalog.Get('XP').id=101;Catalog.Get('Coins').id=102
local raw;local failBefore=false;local ambiguous=false;local studio=false
local player={UserId=7,Parent=true};local live=player;local eligible=true;local notices=0
local market={};local prompts=0
market.PromptProductPurchase=function()prompts+=1 end
market.PromptGamePassPurchase=function()prompts+=1 end
local db={UpdateAsync=function(_,key,transform)
 if failBefore then error('unavailable') end
 -- UpdateAsync may call a transform more than once; only last result commits.
 local returns=table.pack(transform(raw))
 assert(returns.n==1,'UpdateAsync callback returned status as userIds')
 local result=transform(raw)
 if result then raw=result end
 if ambiguous then ambiguous=false;error('write committed but response lost') end
 return result
end}
local services={MarketplaceService=market,Players={GetPlayerByUserId=function()return live end,PlayerRemoving={Connect=function()end}},RunService={IsStudio=function()return studio end},HttpService={GenerateGUID=function()return 'activation-guid' end},DataStoreService={GetDataStore=function()return db end}}
local Config={MovementPassId=0};local Entitlements={HasSpectrum=function()return false end,HasMovement=function()return false end}
local shared={ShopCatalog=Catalog,BoostLedger=Ledger,Config=Config};services.ReplicatedStorage={Shared=shared}
local game={GetService=function(_,name)return services[name]end}
local script={Parent={Entitlements=Entitlements}}
local require=function(module)return module end
local Enum={ProductPurchaseDecision={NotProcessedYet='pending',PurchaseGranted='granted'}}
local task={wait=function()end,spawn=function(fn,...)fn(...)end}
local Commerce=(function()
'''
checks='''
end)()
Commerce.Start(function()return eligible end,function()notices+=1 end)
local n=0;local function check(ok,msg)assert(ok,msg);n+=1 end
local receipt={PlayerId=7,ProductId=101,PurchaseId='r1'}
studio=true;check(market.ProcessReceipt(receipt)=='pending' and raw==nil,'Studio wrote money')
studio=false;live=nil;check(market.ProcessReceipt(receipt)=='pending','Offline receipt consumed')
live=player;eligible=false;check(market.ProcessReceipt(receipt)=='pending','Temporary profile purchased')
eligible=true;failBefore=true;check(market.ProcessReceipt(receipt)=='pending' and raw==nil,'Failed save granted')
failBefore=false;ambiguous=true
check(market.ProcessReceipt(receipt)=='granted' and raw.inventory.xp==1,'Ambiguous commit duplicated/lost receipt')
check(market.ProcessReceipt(receipt)=='granted' and raw.inventory.xp==1,'Repeated receipt duplicated')
Commerce.Load(player);Commerce.Activate(player,'xp')
check(raw.inventory.xp==0 and Commerce.Multiplier(player,'xp')==2,'Durable activation absent')
check(market.ProcessReceipt(receipt)=='granted' and raw.inventory.xp==0,'Old receipt restored consumed token')
local before=raw.ends.xp
Commerce.Activate(player,'bad');check(raw.ends.xp==before,'Unknown activation altered ledger')
receipt.ProductId=999;check(market.ProcessReceipt(receipt)=='pending','Unknown receipt acknowledged')
Catalog.Get('Coins').id=101;receipt.ProductId=101;check(market.ProcessReceipt(receipt)=='pending','Duplicate product IDs granted ambiguous item')
Commerce.Prompt(player,'Spectrum');check(prompts==0,'Unconfigured pass prompted')
print('PASS '..n..' actual commerce handler checks with mocked atomic store')
'''
with tempfile.NamedTemporaryFile(mode='w',suffix='.luau',dir=root/'tests',delete=False) as f:
    path=Path(f.name);f.write(setup+source+checks)
try: subprocess.run(['luau',str(path)],cwd=root,check=True)
finally: path.unlink()
