import pyxel as px
import const as G_
from random import choice as random_choice
import common_func as comf
import item


class Dungeon:
    def __init__(self, num_rooms:int, num_entrance:int, stage_id:int):
        self.stage_id = stage_id
        #扉管理配列
        self.door_lock = [[[0,0],[False,False,False,False]],]
        self.is_door_event = [[[0,0],[False,False,False,False]],]
        self.is_ondoor = False
        #宝物設置用最終配置部屋情報
        self.treasure_cache = [(0,0),0,False] #room address, item_id, is_picked
        #一般設置アイテム情報
        self.item_list = [int(key) for key in item.ITEMS.keys() if 10 <= int(key) <= 22]
        self.treasure_list = [] #room address, item_id, is_picked
        #最終装備情報
        self.final_equip_cache = [(0,0),0,False] #room address, item_id, is_picked
        #ダンジョン生成
        self.room_address = self.generate_dungeon(num_rooms, num_entrance)
        self.set_tilemap_dungeon()
        self.dungeon_id = 0
        #モンスター生成（ダンジョン）
        self.monsters = None

    def generate_dungeon(self, num_rooms:int, num_entrance:int):
        dungeon_rooms = [(0, 0)]
        new_block = (0, 0)
        self.entrance_address = [(0, 0),]
        self.now_room_address = self.entrance_address[0]
        #num_roomに応じて部屋(new_block)の追加
        while len(dungeon_rooms) < num_rooms:
            base_x, base_y = random_choice(dungeon_rooms)
            dx, dy = random_choice(G_.CHARA_DIR)
            new_block = (base_x + dx, base_y + dy)
            if new_block not in dungeon_rooms:
                dungeon_rooms.append(new_block)
                self.door_lock.append([list(new_block),[]])
                self.is_door_event.append([list(new_block),[False,False,False,False]])
                self.treasure_list.append([new_block,self.item_list[px.rndi(0,len(self.item_list)-1)],False])
        #扉フラグマップの情報を追加
        for room in self.door_lock:
            door0,door1,door2,door3 = False,False,False,False
            if (room[0][0], room[0][1] + 1) in dungeon_rooms:
                door0 = self.set_door_lock_status()
            if (room[0][0] - 1, room[0][1]) in dungeon_rooms:
                door1 = self.set_door_lock_status()
            if (room[0][0] + 1, room[0][1]) in dungeon_rooms:
                door2 = self.set_door_lock_status()
            if (room[0][0], room[0][1] - 1) in dungeon_rooms:
                door3 = self.set_door_lock_status()
            room[1] = [door0,door1,door2,door3]
        #最後に追加した部屋を宝物部屋に指定
        self.treasure_cache[0] = new_block
        #最終ステージでは最強装備ボックスを設置
        if self.stage_id == 5:
            self.final_equip_cache[0] = new_block
        #num_entranceに応じて入口アドレスの追加
        while len(self.entrance_address) < num_entrance:
            new_address = random_choice(dungeon_rooms)
            if new_address not in self.entrance_address:
                self.entrance_address.append(new_address)
        
        return dungeon_rooms
    
    #鍵付き扉の初期状態設定（一定確率で非設置、ステージ0なら15%）
    def set_door_lock_status(self):
        return px.rndi(-33,6) <= self.stage_id

    def move_room(self, direction:int):
        destination_address = (self.now_room_address[0] + G_.CHARA_DIR[direction][0],
                               self.now_room_address[1] + G_.CHARA_DIR[direction][1])
        if destination_address in self.room_address:
            self.now_room_address = destination_address
            self.set_tilemap_dungeon()
            self.monsters.set_mobgroup_index(self.now_room_address)
            if self.monsters.get_living_monsters() == 0:
                self.monsters.generate_monsters(self.stage_id)
            self.is_ondoor = True
        else:
            px.play(3,G_.SNDEFX["don"], resume=True)
            return False

    #ダンジョン用タイルマップ　床塗りつぶし＋外壁（隣室有なら空きブロック設定）
    def set_tilemap_dungeon(self, tilemap_id:int=6):
        #床
        _tile_width = G_.P_MAIN_WND[2]//8
        _tile_height = G_.P_MAIN_WND[3]//8
        for dy in range(0, _tile_width, 2):
            for dx in range(0, _tile_height, 2):
                tile_id = ((21,30),(21,31),(22,30),(22,31))
                px.tilemaps[tilemap_id].pset(dx, dy, tile_id[0])
                px.tilemaps[tilemap_id].pset(dx, dy+1, tile_id[1])
                px.tilemaps[tilemap_id].pset(dx+1, dy, tile_id[2])
                px.tilemaps[tilemap_id].pset(dx+1, dy+1, tile_id[3])
        #壁
        x,y = self.now_room_address
        tile_id = ((19,30),(19,31),(20,30),(20,31))
        dx, dy = 0, 0
        for dx in range(0, _tile_width, 2):
            if (x, y - 1) in self.room_address and dx == _tile_width//2-1:
                pass
            else:
                px.tilemaps[tilemap_id].pset(dx, 0, tile_id[0])
                px.tilemaps[tilemap_id].pset(dx, 1, tile_id[1])
                px.tilemaps[tilemap_id].pset(dx+1, 0, tile_id[2])
                px.tilemaps[tilemap_id].pset(dx+1, 1, tile_id[3])
            if (x, y + 1) in self.room_address and dx == _tile_width//2-1:
                pass
            else:
                px.tilemaps[tilemap_id].pset(dx, _tile_height-2, tile_id[0])
                px.tilemaps[tilemap_id].pset(dx, _tile_height-1, tile_id[1])
                px.tilemaps[tilemap_id].pset(dx+1, _tile_height-2, tile_id[2])
                px.tilemaps[tilemap_id].pset(dx+1, _tile_height-1, tile_id[3])
        for dy in range(0, G_.P_MAIN_WND[2]//8, 2):
            if (x - 1, y) in self.room_address and dy == _tile_height//2-1:
                pass
            else:
                px.tilemaps[tilemap_id].pset(0, dy, tile_id[0])
                px.tilemaps[tilemap_id].pset(0, dy+1, tile_id[1])
                px.tilemaps[tilemap_id].pset(1, dy, tile_id[2])
                px.tilemaps[tilemap_id].pset(1, dy+1, tile_id[3])
            if (x + 1, y) in self.room_address and dy == _tile_height//2-1:
                pass
            else:
                px.tilemaps[tilemap_id].pset(_tile_width-2, dy, tile_id[0])
                px.tilemaps[tilemap_id].pset(_tile_width-2, dy+1, tile_id[1])
                px.tilemaps[tilemap_id].pset(_tile_width-1, dy, tile_id[2])
                px.tilemaps[tilemap_id].pset(_tile_width-1, dy+1, tile_id[3])
        #階段
        if self.now_room_address in self.entrance_address:
            tile_id = ((9,30),(9,31),(10,30),(10,31))
            px.tilemaps[tilemap_id].pset(_tile_width//4, _tile_height//4, tile_id[0])
            px.tilemaps[tilemap_id].pset(_tile_width//4, _tile_height//4+1, tile_id[1])
            px.tilemaps[tilemap_id].pset(_tile_width//4+1, _tile_height//4, tile_id[2])
            px.tilemaps[tilemap_id].pset(_tile_width//4+1, _tile_height//4+1, tile_id[3])
        return

    def open_all_doors(self):
        for door_index,room in enumerate(self.door_lock):
            if room[0] == list(self.now_room_address):
                break
        is_open = False
        for i in range(4):
            if self.door_lock[door_index][1][i]:
                is_open = True
                self.door_lock[door_index][1][i] = False
                self.is_door_event[door_index][1][i] = True
        return is_open


    def unlock_door(self, door_index, direction):
        if not self.is_ondoor:
            if self.monsters.ref_user.key <= 0:
                px.play(3, G_.SNDEFX["don"], resume=True)
                self.monsters.ref_user.address[0] -= (G_.CHARA_DIR[self.monsters.ref_user.direction][0]
                                                      *self.monsters.ref_user.movespeed*2)
                self.monsters.ref_user.address[1] -= (G_.CHARA_DIR[self.monsters.ref_user.direction][1]
                                                      *self.monsters.ref_user.movespeed*2)
            else:
                self.monsters.ref_user.key -= 1
                self.is_door_event[door_index][1][direction] = True

    def update(self, scene=40):
        #モンスター行動
        self.monsters.update()

        #扉接触判定
        is_touch_door = False
        for door_index,state in enumerate(self.door_lock):
            if state[0] == list(self.now_room_address):
                break
        is_door0,is_door1,is_door2,is_door3 = self.door_lock[door_index][1]
        if is_door0: #下
            if comf.check_collision_hitbox(self.monsters.ref_user.address[0],self.monsters.ref_user.address[1]+2,12,12,
                                           G_.P_MAIN_WND[2]//2,G_.P_MAIN_WND[3]-8,15,15):
                is_touch_door = True
                self.unlock_door(door_index, 0)
        if is_door1: #左
            if comf.check_collision_hitbox(self.monsters.ref_user.address[0],self.monsters.ref_user.address[1]+2,12,12,
                                           8,G_.P_MAIN_WND[3]//2,15,15):
                is_touch_door = True
                self.unlock_door(door_index, 1)
        if is_door2: #右
            if comf.check_collision_hitbox(self.monsters.ref_user.address[0],self.monsters.ref_user.address[1]+2,12,12,
                                           G_.P_MAIN_WND[2]-8,G_.P_MAIN_WND[3]//2,15,15):
                is_touch_door = True
                self.unlock_door(door_index, 2)
        if is_door3: #上
            if comf.check_collision_hitbox(self.monsters.ref_user.address[0],self.monsters.ref_user.address[1]+2,12,12,
                                           G_.P_MAIN_WND[2]//2,8,15,15):
                is_touch_door = True
                self.unlock_door(door_index, 3)
        self.is_ondoor = is_touch_door


    def draw(self, scene=40):
        #マップ描画
        dx = dy = 0
        if scene == 40:
            if self.monsters.ref_user.timer_damaged > G_.GAME_FPS*0.75 or\
                self.monsters.ref_user.timer_magicdamaged > G_.GAME_FPS*0.75:
                dx = px.rndi(-1,1)
                dy = px.rndi(-1,1)
        px.bltm(dx,dy, 6, 0,0, G_.P_MAIN_WND[2],G_.P_MAIN_WND[3], colkey=0)
        #砂時計の効果エフェクト
        if scene == 40:
            item.func_effect_item11(self.monsters.ref_user)

        #タイル上に扉描画
        doorstate = [state[1] for state in self.door_lock if state[0] == list(self.now_room_address)]
        is_door0,is_door1,is_door2,is_door3 = doorstate[0]
        eventstate = [state[1] for state in self.is_door_event if state[0] == list(self.now_room_address)]
        is_open0,is_open1,is_open2,is_open3 = eventstate[0]
        if is_door0 and is_open0 is False: #下
            px.blt(G_.P_MAIN_WND[2]//2-8,G_.P_MAIN_WND[3]-16, G_.IMGIDX["CHIP"], 216,240,16,16, colkey=0)
        if is_door1 and is_open1 is False: #左
            px.blt(0,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"], 216,240,16,16, colkey=0)
        if is_door2 and is_open2 is False: #右
            px.blt(G_.P_MAIN_WND[2]-16,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"], 216,240,16,16, colkey=0)
        if is_door3 and is_open3 is False: #上
            px.blt(G_.P_MAIN_WND[2]//2-8,0, G_.IMGIDX["CHIP"], 216,240,16,16, colkey=0)

        #松明が無い時は暗がり（当たり判定の為タイルマップの後に消す）
        item.func_effect_item10(self.monsters.ref_user)

        #設置トレジャー
        #最終部屋ステータスアイテム
        if self.treasure_cache[2] is False and self.treasure_cache[0] == self.now_room_address:
            px.blt(G_.P_MAIN_WND[2]*0.75,G_.P_MAIN_WND[3]*0.75, G_.IMGIDX["CHIP"],
                   144+16*self.treasure_cache[1],224, 16,16, colkey=0)
        #各部屋ランダムボックス
        for treasure in self.treasure_list:
            if treasure[2] is False and treasure[0] == self.now_room_address:
                px.blt(G_.P_MAIN_WND[2]//2-8,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"],
                       96,224,16,16, colkey=0)
        #最終装備ボックス
        if self.stage_id == 5 and \
                self.final_equip_cache[2] is False and self.final_equip_cache[0] == self.now_room_address:
            px.blt(G_.P_MAIN_WND[2]*0.25,G_.P_MAIN_WND[3]*0.75, G_.IMGIDX["CHIP"],
                   96,224, 16,16, colkey=0)

        #モンスター描画
        self.monsters.draw(scene)