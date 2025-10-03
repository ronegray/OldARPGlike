import pyxel as px
from random import seed, sample
# import json
import pickle
import gzip
import const as G_
import menu


def array_to_csv(array):
    import csv
    with open("data.csv", "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(array)


#0～numの範囲の整数をランダムに並べ替えた数列イテレータを返却
def generate_random_iterater(start:int, end:int, num:int):
    seed()
    return iter(sample(range(start,end),k=num))


#矩形二つの接触判定(AABB)
def check_collision_hitbox(x1,y1,w1,h1, x2,y2,w2,h2):
    return abs(x1 - x2) <= (w1 + w2) / 2 and abs(y1 - y2) <= (h1 + h2) / 2


#画面内の指定アドレスのタイルマップチップの情報取得
# #type 0:xy指定値(タイル座標) 1:画面座標から変換 2:マップ全体座標から変換
def get_tileinfo(x:float, y:float, layer:int):
    x //= 8
    y //= 8
    return px.tilemaps[layer].pget(x, y)


#移動不可タイルとの接触チェック
def check_hit_tile(target, tilemap_id, check:list, checktype:bool=None): 
    destination_address = [int(target.address[0] + G_.CHARA_DIR[target.direction][0]),
                           int(target.address[1] + G_.CHARA_DIR[target.direction][1])]
    #当たり判定は16ドットキャラの中心ではなく足元寄りの6x6ドット(狭い範囲の通行の為)
    corners = [(destination_address[0]-3,destination_address[1]), #左上
               (destination_address[0]+3,destination_address[1]), #右上
               (destination_address[0]-3,destination_address[1]+6), #左下
               (destination_address[0]+3,destination_address[1]+6), #右下
    ]
    result = False
    for i,[x,y] in enumerate(corners):
        if target.direction == 0 and i in (0,1):
            continue
        elif target.direction == 1 and i in (1,3):
            continue
        elif target.direction == 2 and i in (0,2):
            continue
        elif target.direction == 3 and i in (2,3):
            continue
        tile_x = x // 8
        tile_y = y // 8
        if checktype: #True X軸のみ
            result = result or (px.tilemaps[tilemap_id].pget(tile_x, tile_y)[0] in check)
        elif checktype is False: #False Y軸のみ
            result = result or (px.tilemaps[tilemap_id].pget(tile_x, tile_y)[1] in check)
        else: #None　デフォルト　XY座標
            result = result or (px.tilemaps[tilemap_id].pget(tile_x, tile_y) in check)
    return result


#入力キー情報を取得（複数同時押し可能）
def get_button_state():
    repeat = [int(G_.GAME_FPS//2), int(G_.GAME_FPS//3)]
    btn = {
        "u": px.btn(px.KEY_W) or px.btn(px.GAMEPAD1_BUTTON_DPAD_UP) or px.btn(px.KEY_UP),
        "l": px.btn(px.KEY_A) or px.btn(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btn(px.KEY_LEFT),
        "r": px.btn(px.KEY_D) or px.btn(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btn(px.KEY_RIGHT),
        "d": px.btn(px.KEY_S) or px.btn(px.GAMEPAD1_BUTTON_DPAD_DOWN) or px.btn(px.KEY_DOWN),
        "a": px.btnp(px.KEY_RETURN, *repeat,) or px.btnp(px.GAMEPAD1_BUTTON_A, *repeat,) or px.btnp(px.KEY_Z, *repeat,),
        "b": px.btnp(px.KEY_ESCAPE) or px.btnp(px.GAMEPAD1_BUTTON_B),
        "x": px.btnp(px.KEY_RIGHTBRACKET, *repeat,) or px.btnp(px.GAMEPAD1_BUTTON_X, *repeat,) or px.btnp(px.KEY_X, *repeat,),
        "y": px.btnp(px.KEY_SPACE, *repeat,) or px.btnp(px.GAMEPAD1_BUTTON_Y, *repeat,) or px.btnp(px.KEY_C, *repeat,),
        "L": px.btn(px.KEY_LSHIFT) or px.btn(px.GAMEPAD1_BUTTON_LEFTSHOULDER),
        "R": px.btn(px.KEY_RSHIFT) or px.btn(px.GAMEPAD1_BUTTON_RIGHTSHOULDER),
        "E": px.btn(px.KEY_BACKSPACE) or px.btn(px.GAMEPAD1_BUTTON_BACK),
    }
    return btn


#指定のタイルIDで(width_start,height_start ～ tile_right,tile_under)の範囲でタイルマップを埋める
def fill_tilemap(layer:int, tile:tuple, tile_right:int=256, tile_under:int=256, width_start:int=0, height_start:int=0):
    tilemap = px.tilemaps[layer].data_ptr()
    u, v = tile  # Pyxel Editor上でのタイルID
    for y in range(height_start, tile_under):
        for x in range(width_start, tile_right):
            i = (y * 256 + x) * 2
            tilemap[i] = u      # u座標
            tilemap[i + 1] = v  # v座標


#jsonファイルの読み込み
def read_json(filename:str):
    return decrypt_json(f"{filename}.bin")


#暗号圧縮jsonファイルの読み込み
def decrypt_json(filename:str):
    try:
        with open(filename, "rb") as f:
            data = f.read()

        if not data.startswith(G_.DATA_HEADER):
            error_message(["Invalid json data"])

        encrypted = data[len(G_.DATA_HEADER):]
        compressed = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(encrypted))
        raw = gzip.decompress(compressed)
        json = pickle.loads(raw)
    except Exception:
        error_message(["Invalid json data"])

    return json


def error_message(message:Exception):
    errmsg_window = menu.Window(16,16,px.width-32,px.height-32)
    errmsg_window.message_text = message
    errmsg_window.message_text.append("決定/キャンセルボタンでタイトルに戻ります")
    px.flip()
    while errmsg_window.update():
        px.flip()
        errmsg_window.draw()
        errmsg_window.draw_message()