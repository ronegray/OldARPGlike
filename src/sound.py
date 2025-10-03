import pyxel as px
import common_func as comf

def merge_sound_file(filename, merged):
    append = comf.read_json(filename)
    for i in range(4):
        merged[i][0] += append[i][0]
        merged[i][2] += append[i][2]
    return merged

#******************************************************************************#
# サウンドファイルロード・演奏開始
#******************************************************************************#
def load_sounds(scene):
    px.stop()
    merged_sounds = []
    match scene:
        case 0: # SCENE["Title"]
            merged_sounds = comf.read_json("assets/sound/title.json")
        case 10: # SCENE["CharaSelect"]
            merged_sounds = comf.read_json("assets/sound/field_french.json")
        case 20: # SCENE["NameEntry"]
            merged_sounds = comf.read_json("assets/sound/field_french.json")
        case 30: # SCENE["Field"]
            music1 = comf.read_json("assets/sound/1.A1.json")
            music2 = merge_sound_file("assets/sound/2.A2.json", music1)
            music3 = merge_sound_file("assets/sound/3.B.json", music2)
            music4 = merge_sound_file("assets/sound/4.6.sabiA.json", music3)
            music5 = merge_sound_file("assets/sound/5.sabiB.json", music4)
            music6 = merge_sound_file("assets/sound/4.6.sabiA.json", music5)
            music7 = merge_sound_file("assets/sound/7.sabiC.json", music6)
            music8 = merge_sound_file("assets/sound/8.oosabi.json", music7)
            merged_sounds = merge_sound_file("assets/sound/9.bridge.json", music8)
        case 40: # SCENE["Dungeon"]
            merged_sounds = comf.read_json("assets/sound/dungeon_french.json")
        case 50: # SCENE["Shop"] type 0,1
            merged_sounds = comf.read_json("assets/sound/shop.json")
        case 51: # SCENE["Shop"] type 2
            merged_sounds = comf.read_json("assets/sound/inn.json")
        case 52: # SCENE["Shop"] type 3
            merged_sounds = comf.read_json("assets/sound/shrine.json")
        case 70: # SCENE["BossBattle"]
            music1 = comf.read_json("assets/sound/boss01.json")
            merged_sounds = merge_sound_file("assets/sound/boss02.json", music1)
        case 75: # SCENE["LastBoss"]
            music1 = comf.read_json("assets/sound/LastBoss.json")
            merged_sounds = merge_sound_file("assets/sound/LastBoss2.json", music1)
        case 80: # SCENE["StageClear"]
            merged_sounds = comf.read_json("assets/sound/stageclear.json")
        case 90: # SCENE["Ending"]
            music1 = comf.read_json("assets/sound/ending1.json")
            music2 = merge_sound_file("assets/sound/ending2.json", music1)
            music3 = merge_sound_file("assets/sound/ending3.json", music2)
            music4 = merge_sound_file("assets/sound/ending4.json", music3)
            music5 = merge_sound_file("assets/sound/ending5.json", music4)
            music6 = merge_sound_file("assets/sound/ending6.json", music5)
            music7 = merge_sound_file("assets/sound/ending7.json", music6)
            music8 = merge_sound_file("assets/sound/ending8.json", music7)
            music9 = merge_sound_file("assets/sound/ending9.json", music8)
            music10 = merge_sound_file("assets/sound/ending10.json", music9)
            merged_sounds = merge_sound_file("assets/sound/ending11.json", music10)

    play_sounds(merged_sounds)

#ロードしたBGMファイルを再生
def play_sounds(merged_sounds):
    if px.play_pos(0) is None:
        for ch, sound in enumerate(merged_sounds):
            px.sounds[ch].set(*sound)
            px.play(ch, ch, loop=True)
