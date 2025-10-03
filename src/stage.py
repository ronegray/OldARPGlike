import pyxel as px
import const as G_, common_func as comf
import dungeon, monster, menu, item

#トラップゾーン効果
#ステージ0トラップ：行動阻害
def trap_tree(user, efx:bool):
    if efx:
        user.timer_action += G_.GAME_FPS // 4
    return "茂みに足を取られた"


#ステージ1トラップ：移動速度低下
def trap_swamp(user, efx:bool):
    if efx:
        user.movespeed = user.armor.movespeed // 2
    elif efx is False:
        user.calc_movespeed()
    return "沼に足元が埋まった"


#ステージ2トラップ：攻撃速度低下
def trap_blow(user, efx:bool):
    if efx:
        user.timer_wind = min(255, user.timer_wind + 1)
        if user.effect_wind is None:
            user.effect_wind = item.effect_type_14
            user.effect_wind(user)
    return "強風が動きを遮る"


#ステージ3トラップ：氷結デバフ
def trap_ice(user, efx:bool):
    if efx:
        user.timer_ice = min(255, user.timer_ice + 1)
        if user.effect_ice is None:
            user.effect_ice = item.effect_type_13
            user.effect_ice(user)
    return "足元から凍り付く"


#ステージ4トラップ：ダメージ
def trap_pit(user, efx:bool):
    if efx:
        px.play(3, G_.SNDEFX["don"], resume=True)
        user.hp = int(user.hp - user.maxhp * 0.01)
        user.timer_action += G_.GAME_FPS // 3
    return "落とし穴に落ちた"


#ステージ5トラップ：炎上デバフ
def trap_fire(user, efx:bool):
    if efx:
        user.timer_fire = min(255, user.timer_fire + 1)
        if user.effect_fire is None:
            user.effect_fire = item.effect_type_12
            user.effect_fire(user)
    return "炎の罠だ！"


#ボスステージ描画（メニュー表示時背景用の共通化目的で関数化）
def draw_boss_stage(scene=None):
    px.bltm(0,0, 1, 0,0, G_.P_MAIN_WND[2]+G_.P_SUB_WND[2],G_.P_MAIN_WND[3],colkey=0)


#モジュールメインクラス
class Stage:
    _rate_stage_map_chips=((0.16, 0.46, 0.26, 0.55),
                           (0.10, 0.28, 0.28, 0.51),
                           (0.123, 0.28, 0.28, 0.548),
                           (0.08, 0.18, 0.233, 0.45),
                           (0.12, 0.21, 0.33, 0.57),
                           (0.143, 0.26, 0.315, 0.37),) #各ステージのチップ出現率
    _size_stage_map=((4,4),(5,5),(8,8),(6,6),(9,9),(7,7)) #各ステージの画面サイズ
    _info_dungeon_rooms = ((8,1,1),(13,2,2),(19,2,1),(33,3,2),(26,4,2),(44,4,1),) #[部屋数,各ステージの入口数,(同一ダンジョン内入口数)]

    def __init__(self, stage_id:int, user_instance, message_manager) -> None:
        self.stage_id = stage_id #ステージ番号 0:草原 1:森 2:山 3:雪 4:洞窟 5:城
        self.ref_user = user_instance #ユーザキャラインスタンスへの参照
        self.message_manager = message_manager
        self.scroll_counter = 0
        self.scroll_direction = 0

    #ステージ生成    
        #ステージ情報生成
        self.stage_w = G_.P_MAIN_WND[2] * self._size_stage_map[self.stage_id][0]
        self.stage_h = G_.P_MAIN_WND[3] * self._size_stage_map[self.stage_id][1]
        self.stage_w_tile = self.stage_w//8
        self.stage_h_tile = self.stage_h//8
        self.virtual_map = [[0 for _ in range(self.stage_w_tile)] for _ in range(self.stage_h_tile)]
        self.map_address = tuple([(x,y) for x in range(self._size_stage_map[self.stage_id][0])
                             for y in range(self._size_stage_map[self.stage_id][1])])
        self.now_view = [px.rndi(0,self._size_stage_map[self.stage_id][0]-1),
                         px.rndi(0,self._size_stage_map[self.stage_id][1]-1)]
        self.reached_map_address = []
        self.shops = menu.ShopManager()

        #ステージ情報からタイルマップ生成
        self.generate_tilemap(2)

        #ボス召喚アイテム配置
        self.boss_orb = item.BossSummonOrb(self.map_address, self.virtual_map)

        #掘り出し物配置
        self.treasure_spot = [] #(マップアドレス)、(画面内座標)、アイテムID、
        range_pattern = [(1,1),  (2,25), (26,45), (46,82), (83,100),]
        range_item = [(((1,100),33),),
                      (((1,80),31),((81,100),32)),
                      (((1,12),20),((13,75),21),((76,100),22)),
                      (((1,20),10),((21,40),14),((41,60),15),((61,80),16),((81,100),17)),
                      (((1,1),0),((2,2),1),((3,3),2),((4,4),3),((5,5),4),((6,6),5),((7,12),6),((13,100),30)),
                      ]
        random_index = comf.generate_random_iterater(0,len(self.map_address)-1,len(self.map_address)-1)
        while len(self.treasure_spot) < self._size_stage_map[self.stage_id][0]:
            is_skip = False
            set_mappos = self.map_address[next(random_index)]
            #設置位置決定
            if len(self.treasure_spot) > 0:
                for spot in self.treasure_spot:
                    if set_mappos == spot[0]:
                        is_skip = True
            if is_skip is False:
                map_pos = set_mappos
                temp_vmap = [row[map_pos[0]*G_.P_MAIN_WND[2]//8:map_pos[0]*G_.P_MAIN_WND[2]//8+G_.P_MAIN_WND[2]//8]
                            for row in 
                            self.virtual_map[map_pos[1]*G_.P_MAIN_WND[3]//8:map_pos[1]*G_.P_MAIN_WND[3]//8+G_.P_MAIN_WND[3]//8]]
                set_pos = None
                while set_pos is None:
                    temp_x = px.rndi(0,G_.P_MAIN_WND[2]//8-1)
                    temp_y = px.rndi(0,G_.P_MAIN_WND[3]//8-1)
                    if temp_vmap[temp_x][temp_y][0] == 4:
                        continue
                    if temp_vmap[temp_x][temp_y][0] == 3:
                        set_pos = (temp_y, temp_x)
                #埋葬アイテム決定
                rate_type = px.rndi(1,100)
                for p in range_pattern:
                    if p[0] <= rate_type <= p[1]:
                        treasurelist = range_item[range_pattern.index(p)]
                        rate_item = px.rndi(1,100)
                        for i in treasurelist:
                            if i[0][0] <= rate_item <= i[0][1]:
                                item_id = i[1]
                                if item_id in (30,31):
                                    item_num = ((stage_id + 1)**2 * 10) * px.rndi(16,32)
                                else:
                                    item_num = 1
                self.treasure_spot.append((map_pos,set_pos,item_id,item_num))

    #モンスター生成（フィールド）
        self.monsters = monster.MonsterManager(self.map_address, self.stage_id, self.ref_user, message_manager)
        if self.stage_id == 0:
            self.now_view = [list(groupinfo[0]) for groupinfo in self.monsters.mobgroup if groupinfo[2] == 3][0]
            self.set_tilemap()
        self.monsters.set_mobgroup_index(self.now_view)

        #現在位置確定にて到達済マップの設定
        self.reached_map_address.append(self.now_view)

    #ダンジョン生成
        _num_rooms, _num_entrance, _num_same_entrance = self._info_dungeon_rooms[self.stage_id]
        #定義情報（全部屋数、入口数、同一ダンジョン内入口数）からダンジョン別部屋数その他を算出
        info_dungeon = []
        num_groups = -(-_num_entrance // _num_same_entrance)
        # 平均部屋数
        avg_rooms = _num_rooms // num_groups
        remain_rooms = _num_rooms
        room_allocations = []
        # 最初にランダムに割り当てる
        for i in range(num_groups):
            # 各グループに、±ゆらぎを加えた部屋数を設定（最低2部屋）
            if i < num_groups - 1:
                delta = min(3, avg_rooms - 2)  # ゆらぎの最大幅（調整可）
                rooms = max(2, avg_rooms + px.rndi(-delta, delta))
                room_allocations.append(rooms)
                remain_rooms -= rooms
            else:
                # 最後のグループに残りを全部渡す
                room_allocations.append(remain_rooms)
        # 入口の分配
        base_entrances = _num_entrance // num_groups
        extra_entrances = _num_entrance % num_groups
        for i in range(num_groups):
            entrances = base_entrances + (1 if i < extra_entrances else 0)
            info_dungeon.append([room_allocations[i], entrances])
        #算出した個別ダンジョン情報を元にダンジョンを生成・リスト化
        self.dungeon_list = []
        for _num_drooms, _num_dentrance in info_dungeon:
            d = dungeon.Dungeon(_num_drooms, _num_dentrance, self.stage_id)
            #モンスター生成（ダンジョン）
            d.monsters = monster.MonsterManager(d.room_address, self.stage_id, self.ref_user, message_manager)
            self.dungeon_list.append(d)
            d.dungeon_id = len(self.dungeon_list) - 1
        #ステージ⇔ダンジョン間の階段座標の紐付け
        self.dungeon_entrance_list = []
        dungeon_index = 0
        i = 0
        _treasure_cache_id = ([2],[4],[0,3],[1,5],[2,4],[0,1,3,5],)
        for _dungeon_unit in self.dungeon_list:
            for _address in _dungeon_unit.entrance_address:
                self.dungeon_entrance_list.append([dungeon_index, _address, self._dungeon_entrance_address[i]])
                i += 1
            self.dungeon_list[dungeon_index].treasure_cache[1] = _treasure_cache_id[self.stage_id][dungeon_index]
            dungeon_index += 1
        del self._dungeon_entrance_address
        
    #トラップゾーン効果設定
        match self.stage_id: #デバフタイルを踏んだ時の効果
            case 0:
                self.func_trap_tile = trap_tree
            case 1:
                self.func_trap_tile = trap_swamp
            case 2:
                self.func_trap_tile = trap_blow
            case 3:
                self.func_trap_tile = trap_ice
            case 4:
                self.func_trap_tile = trap_pit
            case 5:
                self.func_trap_tile = trap_fire
            case _:
                raise NotImplementedError

    #ユーザ初期位置変更
        while comf.get_tileinfo(*self.ref_user.address, 0)[0] == 4:
            self.ref_user.address[0] = max(px.rndi(16,G_.P_MAIN_WND[2]//4),
                                           px.rndi(G_.P_MAIN_WND[2]-G_.P_MAIN_WND[2]//4, G_.P_MAIN_WND[2]-16))
            self.ref_user.address[1] = max(px.rndi(16,G_.P_MAIN_WND[3]//4),
                                           px.rndi(G_.P_MAIN_WND[3]-G_.P_MAIN_WND[3]//4, G_.P_MAIN_WND[3]-16))

    #到着済みマップエリアの更新（ミニマップ表示用）
    def update_reached_map(self):
        if self.now_view not in self.reached_map_address:
            self.reached_map_address.append(self.now_view)
            self.reached_map_address.sort

    #画面端での次画面遷移時に現在画面を別レイヤに保存して２画面でスクロールする(chara_dir=)
    def prepare_scroll_map(self, scroll_dir):
        if 0<=self.now_view[0]+G_.CHARA_DIR[scroll_dir][0]<=self._size_stage_map[self.stage_id][0]-1 and\
           0<=self.now_view[1]+G_.CHARA_DIR[scroll_dir][1]<=self._size_stage_map[self.stage_id][1]-1:
            pass
        else:
            px.play(3,G_.SNDEFX["don"], resume=True)
            self.ref_user.address[0] -= G_.CHARA_DIR[self.ref_user.direction][0] * self.ref_user.armor.movespeed
            self.ref_user.address[1] -= G_.CHARA_DIR[self.ref_user.direction][1] * self.ref_user.armor.movespeed
            return False
        #現マップをタイルレイヤ１に、移動先マップをタイルレイヤ２にセット
        self.set_tilemap(1)

        self.now_view = [self.now_view[0] + G_.CHARA_DIR[scroll_dir][0],
                         self.now_view[1] + G_.CHARA_DIR[scroll_dir][1]]
        self.set_tilemap()
        #移動先マップアドレスを踏破済に
        self.update_reached_map()

        #表示モンスターアドレスの変更及び再出現処理
        self.monsters.set_mobgroup_index(self.now_view)
        if self.monsters.get_living_monsters() == 0:
            self.monsters.generate_monsters(self.stage_id)
        #現マップと移動先マップを並べてスクロール（メインエリア外の描画予防のため描画サイズを
        self.scroll_counter = 0
        self.scroll_direction = scroll_dir
        return True

    #仮想マップ配列から現在表示位置を元に必要データを抽出してタイルマップを生成(tilemap_idはスクロール時のみ使用)
    def set_tilemap(self, tilemap_id:int=0):
        try:
            for y in range(G_.P_MAIN_WND[3]//8):
                for x in range(G_.P_MAIN_WND[2]//8):
                    tile_id = self.virtual_map[y+self.now_view[1]*G_.P_MAIN_WND[3]//8][x+self.now_view[0]*G_.P_MAIN_WND[2]//8]
                    px.tilemaps[tilemap_id].pset(x, y, tile_id)
        except Exception as e:
            comf.error_message([f"予期しないエラーが発生しました: {e}"])

    #ランダムポイントが移動不能タイルだった場合のポイント再設定
    def relocate_object(self, cx, cy, ox, oy):
        tile_sx = tmpx = 2 * cx - ox
        tile_sy = tmpy = 2 * cy - oy
        map_location = (tile_sx*8)//G_.P_MAIN_WND[2],(tile_sy*8)//G_.P_MAIN_WND[3]
        while True:
            if (1 <= tmpx <= self.stage_w_tile-2) and  (1 <= tmpy <= self.stage_h_tile-2):
                if self.virtual_map[tmpy][tmpx][0] == 4:
                    pass
                else:
                    tile_sx,tile_sy = tmpx,tmpy
                    return [tile_sx,tile_sy]
            rnd_x = px.rndi(0,G_.P_MAIN_WND[2]//8-1)
            rnd_y = px.rndi(0,G_.P_MAIN_WND[3]//8-1)
            tmpx = map_location[0]*G_.P_MAIN_WND[2]//8+rnd_x
            tmpy = map_location[1]*G_.P_MAIN_WND[3]//8+rnd_y

    def _find_unique_walkable_spot(self, candidate_address, used_addresses):
        """
        指定された候補座標が利用可能かチェックし、
        利用不可の場合は、利用可能な新しいランダム座標を探索して返すヘルパー関数。
        """
        current_pos = list(candidate_address) # 元の引数を変更しないようにコピーを作成

        # 1. 候補地が通行可能か ＆ 2. 既に使用済みでないか をチェック
        is_walkable = self.virtual_map[current_pos[1]][current_pos[0]][0] != 4
        is_used = any(current_pos == used for used in used_addresses)

        # 座標が利用可能であれば、そのまま返す
        if is_walkable and not is_used:
            return current_pos

        # 利用不可の場合、完全にランダムな場所を探し直す
        while True:
            # マップの端（通行不可）を除いた全域からランダムな座標を探索
            rand_x = px.rndi(1, self.stage_w_tile - 2)
            rand_y = px.rndi(1, self.stage_h_tile - 2)
            
            # その座標が通行可能かチェック
            if self.virtual_map[rand_y][rand_x][0] != 4:
                # さらに、そのランダムな座標が既に使用済みでないかチェック
                new_pos = [rand_x, rand_y]
                if not any(new_pos == used for used in used_addresses):
                    # すべての条件をクリアした座標を返す
                    return new_pos

    def generate_tilemap(self, num):
        # パーリンノイズの計算
        z = 0
        _nMin1=[1,[0,0]]; _nMax1=[0,[0,0]]; _nMin2=[1,[0,0]]; _nMax2=[0,[0,0]]
        for y in range(self.stage_h_tile):
            for x in range(self.stage_w_tile):
                n = 0; scale = 0.066; amp = 1
                for i in range(num):
                    n += px.noise(x*scale, y*scale, z*scale) * amp
                    scale *= 2; amp *= 0.5
                rates = self._rate_stage_map_chips[self.stage_id]
                if x == 0 or x == self.stage_w_tile-1 or y == 0 or y == self.stage_h_tile-1:
                    tileNo = 4
                elif rates[0] >= n >= -(rates[0]):
                    tileNo = 0
                    if n < _nMin2[0]: _nMin2[0] = n; _nMin2[1] = [x,y]
                    elif n > _nMax2[0]: _nMax2[0] = n; _nMax2[1] = [x,y]
                elif rates[1] >= n > rates[0]:
                    tileNo = 1
                    if n < _nMin1[0]: _nMin1[0] = n; _nMin1[1] = [x,y]
                    elif n > _nMax1[0]: _nMax1[0] = n; _nMax1[1] = [x,y]
                elif -(rates[0]) > n >= -(rates[2]):
                    tileNo = 2
                elif rates[3] >= n >= -(rates[3]):
                    tileNo = 3
                else:
                    tileNo = 4
                self.virtual_map[y][x] = (tileNo, self.stage_id)

        cx = self.stage_w_tile // 2
        cy = self.stage_h_tile // 2
        used_tile_address = [] # 使用済み座標を記録するリスト

        # ショップ入口設置
        # 装備品
        pos = self._find_unique_walkable_spot(_nMax2[1], used_tile_address)
        used_tile_address.append(pos)
        _map_address = (pos[0]*8+8)//G_.P_MAIN_WND[2], (pos[1]*8+8)//G_.P_MAIN_WND[3]
        self.shops.create_shop(tuple(_map_address), tuple([pos[0]*8+8, pos[1]*8+8]), 0, self.stage_id, self.ref_user)

        # 消耗品
        pos = self._find_unique_walkable_spot(_nMin2[1], used_tile_address)
        used_tile_address.append(pos)
        _map_address = (pos[0]*8+8)//G_.P_MAIN_WND[2], (pos[1]*8+8)//G_.P_MAIN_WND[3]
        self.shops.create_shop(tuple(_map_address), tuple([pos[0]*8+8, pos[1]*8+8]), 1, self.stage_id, self.ref_user)
        
        # 宿屋
        candidate_pos = self.relocate_object(cx, cy, *_nMax2[1])
        pos = self._find_unique_walkable_spot(candidate_pos, used_tile_address)
        used_tile_address.append(pos)
        _map_address = (pos[0]*8+8)//G_.P_MAIN_WND[2], (pos[1]*8+8)//G_.P_MAIN_WND[3]
        self.shops.create_shop(tuple(_map_address), tuple([pos[0]*8+8, pos[1]*8+8]), 2, self.stage_id, self.ref_user)

        # 神殿
        candidate_pos = self.relocate_object(cx, cy, *_nMin2[1])
        pos = self._find_unique_walkable_spot(candidate_pos, used_tile_address)
        used_tile_address.append(pos)
        _map_address = (pos[0]*8+8)//G_.P_MAIN_WND[2], (pos[1]*8+8)//G_.P_MAIN_WND[3]
        self.shops.create_shop(tuple(_map_address), tuple([pos[0]*8+8, pos[1]*8+8]), 3, self.stage_id, self.ref_user)

        # ダンジョン入口設置
        self._dungeon_entrance_address = []
        entrances_to_place = []
        if self._info_dungeon_rooms[self.stage_id][1] >= 1: entrances_to_place.append(_nMax1[1])
        if self._info_dungeon_rooms[self.stage_id][1] >= 2: entrances_to_place.append(_nMin1[1])
        if self._info_dungeon_rooms[self.stage_id][1] >= 3: entrances_to_place.append(self.relocate_object(cx,cy, *_nMax1[1]))
        if self._info_dungeon_rooms[self.stage_id][1] >= 4: entrances_to_place.append(self.relocate_object(cx,cy, *_nMin1[1]))

        for candidate_pos in entrances_to_place:
            # 2x2の領域を確保できるかチェックしながら場所を探す
            while True:
                pos = self._find_unique_walkable_spot(candidate_pos, used_tile_address)
                # 2x2チェックに失敗した場合でも、二度と同じ場所を探さないように
                # チェックする前に「使用済み」として記録する
                used_tile_address.append(pos)
                # 2x2領域のチェック
                if (pos[0] < self.stage_w_tile - 1 and pos[1] < self.stage_h_tile - 1 and
                    self.virtual_map[pos[1] + 1][pos[0]][0] != 4 and
                    self.virtual_map[pos[1]][pos[0] + 1][0] != 4 and
                    self.virtual_map[pos[1] + 1][pos[0] + 1][0] != 4):
                    break # 2x2が確保できたらループを抜ける
                candidate_pos = [0,0] # 失敗時はダミーの候補地を渡して完全ランダム探索に移行

            used_tile_address.append(pos) # 2x2領域の左上を予約
            # 念のため他の3タイルも予約リストに追加
            used_tile_address.append([pos[0]+1, pos[1]])
            used_tile_address.append([pos[0], pos[1]+1])
            used_tile_address.append([pos[0]+1, pos[1]+1])
            
            self._dungeon_entrance_address.append((pos[0]*8+8, pos[1]*8+8))
            self.virtual_map[pos[1]][pos[0]] = (11,30)
            self.virtual_map[pos[1]+1][pos[0]] = (11,31)
            self.virtual_map[pos[1]][pos[0]+1] = (12,30)
            self.virtual_map[pos[1]+1][pos[0]+1] = (12,31)

        self.set_tilemap()
        return

    def search_treasure(self):
        return_param = None
        for i,spot in enumerate(self.treasure_spot):
            if self.now_view == list(spot[0]):
                if comf.check_collision_hitbox(*self.ref_user.address,16,16,
                                               spot[1][0]*8,spot[1][1]*8,18,18):
                    return_param = [spot[2],spot[3],i]
                    break
        return return_param

    def trove_treasure(self):
        return_param = None
        return_param = self.search_treasure()
        if return_param is not None:
            self.treasure_spot.pop(return_param[2])
        return return_param

    def update(self, scene=30):
        #モンスター描画
        self.monsters.update()

        #ボス召喚アイテムの配置
        if self.now_view == self.boss_orb.map_address and\
                self.monsters.mobgroup[self.monsters.mobgroup_index][1] >= 5:
            if self.boss_orb.is_placed is False:
                self.boss_orb.is_placed = True

    def draw(self, scene=30):
        #マップ描画
        dx = dy = 0
        if scene == 30:
            if self.ref_user.timer_damaged > G_.GAME_FPS*0.75 or\
                self.ref_user.timer_magicdamaged > G_.GAME_FPS*0.75:
                dx = px.rndi(-1,1)
                dy = px.rndi(-1,1)
        px.bltm(dx,dy, 0, 0,0, G_.P_MAIN_WND[2],G_.P_MAIN_WND[3], colkey=0)
        #砂時計の効果エフェクト
        if scene == 30:
            item.func_effect_item11(self.ref_user)

        #隠しアイテムのキラキラ
        for spot in self.treasure_spot:
            if self.now_view == list(spot[0]):
                if px.frame_count%(G_.GAME_FPS//3) in (0,1,2,3,4,5):
                    px.blt(spot[1][0]*8+px.rndi(-2,2), spot[1][1]*8+px.rndi(-2,2), G_.IMGIDX["CHIP"], 
                           40,240+8*(px.frame_count%2),8,8, colkey=0)
        #ショップ入口描画
        self.shops.draw(self.now_view)
        #ボス召喚アイテム
        self.boss_orb.draw(self.now_view)
        #モンスター描画
        self.monsters.draw(scene)
