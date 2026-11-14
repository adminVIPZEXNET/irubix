"""Native Shad account client for IRubix."""
from __future__ import annotations
import asyncio, base64, inspect, json, logging, random, re, string
from datetime import datetime
from pathlib import Path
from typing import Any
import aiohttp
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15
from Crypto.Util.Padding import pad, unpad

PLATFORMS = {
 "shad_web": ("Web", "web.shad.ir", "https://web.shad.ir", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"),
 "shad_pwa": ("PWA", "my.shad.ir", "https://my.shad.ir", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0 Safari/537.36"),
 "shad_android": ("Android", "ir.medu.shad", None, "okhttp/3.12.1"),
}
class ShadError(Exception): pass
class ShadAuthError(ShadError): pass
class ShadAPIError(ShadError): pass

class ShadEvent:
 def __init__(self, data: dict[str, Any], client: "Shad"):
  self.original_data=data; self.client=client; self.text=data.get("text") or data.get("message",{}).get("text","")
  self.message_id=data.get("message_id"); self.chat_id=data.get("object_guid") or data.get("chat_id")
  self.sender_id=data.get("author_object_guid") or data.get("user_guid"); self.raw=data
 async def reply(self, text: str):
  if not self.chat_id: raise ShadAPIError("شناسه گفتگو در رویداد موجود نیست.")
  return await self.client.send_message(self.chat_id,text,reply_to_message_id=self.message_id)

class Shad:
 """Independent Shad user client. Requires an existing API v6 session."""
 PLATFORMS=tuple(PLATFORMS)
 def __init__(self, session: str|None=None, *, auth: str|None=None, private_key: str|bytes|None=None,
              platform: str="shad_web", timeout: float=30, proxy: str|None=None, api_version: int=6,
              max_retries: int=3, logger: logging.Logger|None=None, **options):
  if platform not in PLATFORMS: raise ValueError(f"platform باید یکی از این موارد باشد: {', '.join(PLATFORMS)}")
  if api_version != 6: raise ValueError("در حال حاضر فقط API نسخه 6 پشتیبانی می‌شود.")
  self.platform=platform; self.platform_name,self.package,self.origin,self.user_agent=PLATFORMS[platform]
  self.timeout=float(timeout)
  if self.timeout<=0: raise ValueError("timeout باید بزرگ‌تر از صفر باشد.")
  self.proxy=proxy; self.max_retries=max(0,int(max_retries)); self.logger=logger or logging.getLogger("irubix.shad")
  self.session_path=Path(session) if session else None; self.auth=auth
  self.private_key=private_key.decode() if isinstance(private_key,bytes) else private_key
  self.guid=None; self._http=None; self._api_url=None; self._ws_url=None; self._handlers=[]; self._running=False
  if self.session_path and self.session_path.exists():
   try:
    saved=json.loads(self.session_path.read_text(encoding="utf-8"))
    self.auth=self.auth or saved.get("auth"); self.private_key=self.private_key or saved.get("private_key"); self.guid=saved.get("guid")
   except (OSError,json.JSONDecodeError) as exc: raise ShadAuthError(f"فایل نشست قابل خواندن نیست: {exc}") from exc
  if self.auth and not re.fullmatch(r"[a-z]{32}",self.auth): raise ShadAuthError("auth باید شامل ۳۲ حرف کوچک انگلیسی باشد.")
  if bool(self.auth)!=bool(self.private_key): raise ShadAuthError("برای ورود API v6 باید auth و private_key را با هم بدهید.")
  if not self.auth: raise ShadAuthError("نشست معتبر یا هر دو مقدار auth و private_key لازم است.")
  try: RSA.import_key(self.private_key.encode())
  except (ValueError,TypeError) as exc: raise ShadAuthError("کلید خصوصی RSA معتبر نیست.") from exc
  self.decode_auth=self._decode_auth(self.auth); self.key=self._passphrase(self.auth)

 @staticmethod
 def _decode_auth(auth):
  low=str.maketrans(string.ascii_lowercase,"".join(chr((32-(ord(c)-97))%26+97) for c in string.ascii_lowercase))
  upp=str.maketrans(string.ascii_uppercase,"".join(chr((29-(ord(c)-65))%26+65) for c in string.ascii_uppercase))
  dig=str.maketrans("0123456789","".join(chr((13-i)%10+48) for i in range(10)))
  return auth.translate(low).translate(upp).translate(dig)
 @staticmethod
 def _passphrase(auth):
  chunks=re.findall(r"\S{8}",auth)
  return "".join(chr((ord(c)-97+9)%26+97) for c in chunks[2]+chunks[0]+chunks[3]+chunks[1])
 @staticmethod
 def _encrypt(data,key):
  aes=AES.new(key.encode(),AES.MODE_CBC,iv=b"\0"*16)
  return base64.b64encode(aes.encrypt(pad(json.dumps(data,separators=(",",":")).encode(),16))).decode()
 @staticmethod
 def _decrypt(data,key):
  aes=AES.new(key.encode(),AES.MODE_CBC,iv=b"\0"*16)
  return json.loads(unpad(aes.decrypt(base64.b64decode(data)),16).decode())

 async def connect(self):
  if self._http and not self._http.closed: return self
  headers={"content-type":"application/json","user-agent":self.user_agent}
  if self.origin: headers.update({"origin":self.origin,"referer":self.origin+"/"})
  self._http=aiohttp.ClientSession(headers=headers,timeout=aiohttp.ClientTimeout(total=self.timeout))
  try:
   async with self._http.get("https://shgetdcmess.iranlms.ir/",proxy=self.proxy) as res:
    res.raise_for_status(); payload=await res.json()
  except Exception:
   await self.close(); raise
  data=payload.get("data") or {}; apis=data.get("API") or {}; sockets=data.get("socket") or {}
  order=list(data.get("default_apis") or []); default=data.get("default_api")
  if default is not None: order=[default]+[x for x in order if x!=default]
  order += [x for x in apis if x not in order]
  self._api_url=next((apis.get(str(x)) for x in order if apis.get(str(x))),None)
  self._ws_url=sockets.get(data.get("default_socket"))
  if not self._api_url or not self._ws_url:
   await self.close(); raise ShadAPIError("سرور شاد نشانی API یا WebSocket معتبر برنگرداند.")
  return self
 async def close(self):
  if self._http and not self._http.closed: await self._http.close()
  self._http=None
 async def request(self,method,input=None):
  if not self._http or self._http.closed: await self.connect()
  client={"app_name":"Main","app_version":datetime.now().strftime("%y.%m.%d"),"platform":self.platform_name,"package":self.package,"lang_code":"fa"}
  encrypted=self._encrypt({"method":method,"input":input or {},"client":client},self.key)
  signature=pkcs1_15.new(RSA.import_key(self.private_key.encode())).sign(SHA256.new(encrypted.encode()))
  payload={"api_version":"6","auth":self.decode_auth,"data_enc":encrypted,"sign":base64.b64encode(signature).decode()}
  last=None
  for attempt in range(self.max_retries+1):
   try:
    async with self._http.post(self._api_url,json=payload,proxy=self.proxy) as res:
     res.raise_for_status(); result=await res.json()
    enc=result.get("data_enc"); result=self._decrypt(enc,self.key) if enc else result
    if result.get("status")=="OK" and result.get("status_det")=="OK": return result.get("data") or {}
    raise ShadAPIError(f"{result.get('status_det') or result.get('status')}: {result}")
   except (aiohttp.ClientError,asyncio.TimeoutError) as exc:
    last=exc
    if attempt<self.max_retries: await asyncio.sleep(min(2**attempt,8))
  raise ShadAPIError(f"ارتباط با سرور شاد ناموفق بود: {last}")
 async def get_me(self):
  data=await self.request("getUserInfo",{}); user=data.get("user") or data
  self.guid=user.get("user_guid") or self.guid
  return data
 async def send_message(self,chat,text,reply_to_message_id=None):
  if not isinstance(text,str) or not text.strip(): raise ValueError("متن پیام نمی‌تواند خالی باشد.")
  if len(text)>4096: raise ValueError("حداکثر طول پیام ۴۰۹۶ نویسه است.")
  target=self.guid if chat.lower() in {"me","self","myself","cloud"} else chat
  if not target: raise ShadAPIError("شناسه گفتگو مشخص نیست.")
  data={"object_guid":target,"text":text.strip(),"rnd":random.randint(100000,999999)}
  if reply_to_message_id: data["reply_to_message_id"]=reply_to_message_id
  return await self.request("sendMessage",data)
 def on_new_message(self,*filters):
  def decorator(func): self._handlers.append((func,filters)); return func
  return decorator
 async def _dispatch(self,update):
  data=update.get("message") if isinstance(update.get("message"),dict) else update
  event=ShadEvent(data,self)
  for func,filters in tuple(self._handlers):
   accepted=True
   for condition in filters:
    result=condition(event)
    if inspect.isawaitable(result): result=await result
    if not result: accepted=False; break
   if accepted:
    result=func(event)
    if inspect.isawaitable(result): await result
 async def run_async(self):
  await self.connect(); await self.get_me(); self._running=True
  while self._running:
   try:
    async with self._http.ws_connect(self._ws_url,proxy=self.proxy) as ws:
     await ws.send_json({"method":"handShake","auth":self.auth,"api_version":"6","data":""})
     async for msg in ws:
      if msg.type==aiohttp.WSMsgType.TEXT:
       packet=msg.json(); enc=packet.get("data_enc") or packet.get("messenger")
       updates=enc if isinstance(enc,dict) else (self._decrypt(enc,self.key) if enc else {})
       for name,items in updates.items():
        if name in {"MessageUpdates","message_updates"} and isinstance(items,list):
         for item in items:
          if item.get("action") in {"New","new"}: await self._dispatch(item)
      elif msg.type in {aiohttp.WSMsgType.CLOSED,aiohttp.WSMsgType.ERROR}: break
   except (aiohttp.ClientError,asyncio.TimeoutError) as exc:
    self.logger.warning("اتصال شاد قطع شد؛ تلاش مجدد: %s",exc); await asyncio.sleep(3)
  await self.close()
 def run(self):
  """Run the client; returns a task when called inside an active event loop."""
  try: loop=asyncio.get_running_loop()
  except RuntimeError: return asyncio.run(self.run_async())
  return loop.create_task(self.run_async())
 def stop(self): self._running=False
