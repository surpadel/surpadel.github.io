"""Baja la locución v3 del homenaje a Lamperti (ElevenLabs) al repo."""
import pathlib, urllib.request
AQUI = pathlib.Path(__file__).resolve().parent
URL = ("https://elevenlabsusercontent.com/database/workspace/616874bc8ff04f49a33e0fd2b53295f7/content_generation/"
       "Tgi7K8kClB2XgjoV98SF/P3NHvHxSyrEuUKfDxMOC/content.mp3?Expires=1795586400&KeyName=assets-cdn-key-1&Signature=gDTp3Inx4kNquujBlmOAkd8-I3M=")
req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
(AQUI / "lamperti-voz-v3.mp3").write_bytes(urllib.request.urlopen(req, timeout=60).read())
print("ok")
