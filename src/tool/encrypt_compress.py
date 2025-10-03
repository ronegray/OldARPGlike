import pyxel as px
import pickle
import gzip
import json
from random import seed, sample
import const as G_

#jsonファイルの暗号圧縮
def encrypt_json(filename:str):
    with open(filename, "rt", encoding="utf-8") as file:
        data = json.loads(file.read())

    raw = pickle.dumps(data)
    compressed = gzip.compress(raw)
    encrypted = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(compressed))
        
    with open(filename+".bin", "wb") as f:
        f.write(G_.DATA_HEADER + encrypted)

    return

# 暗号圧縮
if __name__ == "__main__":
    px.init(120,120,title="common")
    encrypt_json("assets/sound/title.json")
    encrypt_json("assets/sound/field_french.json")
    encrypt_json("assets/sound/ed0.intro.json")
    encrypt_json("assets/sound/1.A1.json")
    encrypt_json("assets/sound/2.A2.json")
    encrypt_json("assets/sound/3.B.json")
    encrypt_json("assets/sound/4.6.sabiA.json")
    encrypt_json("assets/sound/5.sabiB.json")
    encrypt_json("assets/sound/7.sabiC.json")
    encrypt_json("assets/sound/8.oosabi.json")
    encrypt_json("assets/sound/9.bridge.json")
    encrypt_json("assets/sound/dungeon_french.json")
    encrypt_json("assets/sound/shop.json")
    encrypt_json("assets/sound/inn.json")
    encrypt_json("assets/sound/shrine.json")
    encrypt_json("assets/sound/boss01.json")
    encrypt_json("assets/sound/boss02.json")
    encrypt_json("assets/sound/LastBoss.json")
    encrypt_json("assets/sound/LastBoss2.json")
    encrypt_json("assets/sound/stageclear.json")
    encrypt_json("assets/sound/ending1.json")
    encrypt_json("assets/sound/ending2.json")
    encrypt_json("assets/sound/ending3.json")
    encrypt_json("assets/sound/ending4.json")
    encrypt_json("assets/sound/ending5.json")
    encrypt_json("assets/sound/ending6.json")
    encrypt_json("assets/sound/ending7.json")
    encrypt_json("assets/sound/ending8.json")
    encrypt_json("assets/sound/ending9.json")
    encrypt_json("assets/sound/ending10.json")
    encrypt_json("assets/sound/ending11.json")
    encrypt_json("assets/data/letter.json")
    encrypt_json("assets/data/boss.json")
    encrypt_json("assets/data/stage0.json")
    encrypt_json("assets/data/stage1.json")
    encrypt_json("assets/data/stage2.json")
    encrypt_json("assets/data/stage3.json")
    encrypt_json("assets/data/stage4.json")
    encrypt_json("assets/data/stage5.json")
    encrypt_json("assets/data/messages.json")
    encrypt_json("assets/data/messages_u.json")
    px.text(0,0,"encrypt finished. ", 7)
    px.text(0,10,"press ESC key", 7)
    px.show()

    