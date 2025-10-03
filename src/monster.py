import pyxel as px
import const as G_
import common_func as comf
import character, item

class MonsterManager:
    def __init__(self, map_address:tuple, stage_id:int, user, message_manager):
        self.ref_user = user #ユーザインスタンスへの参照
        self.message_manager = message_manager #メッセージ管理インスタンスへの参照
        self.mobgroup = [] #出現アドレス,グループID,モンスターID,モンスターオブジェクトのリスト
        self.treasure_list = [] #宝箱オブジェクト(出現マップアドレス、設置済フラグ、開封済フラグ、出現アドレス、アイテムID、個数)のリスト
        self.mobgroup_index = 0

        monster_list = comf.read_json(f"assets/data/stage{stage_id}.json")
        stage_monster_id_list = comf.generate_random_iterater(min(monster_list)[0],max(monster_list)[0]+1,
                                                              len(monster_list))
        for address in map_address:
            try:
                self.mobgroup.append([address, 0,next(stage_monster_id_list),None])
            except StopIteration:
                stage_monster_id_list = comf.generate_random_iterater(min(monster_list)[0],max(monster_list)[0]+1,
                                                                    len(monster_list))
                self.mobgroup.append([address, 0,next(stage_monster_id_list),None])
            self.treasure_list.append(None)

        for i,mobs in enumerate(self.mobgroup):
            self.mobgroup_index = i
            self.generate_monsters(stage_id, mobs)

    def generate_monsters(self, stage_id, mobs=None):
        if mobs is None: #引数無し時は設定済変数からデータ取得
            mobs = self.mobgroup[self.mobgroup_index]

        if mobs[1] <= 3: #最大出現は４グループ（index 0~3）
            pass
        else:
            mobs[1] = 5
            return

        if self.treasure_list[self.mobgroup_index] is not None:
            if self.treasure_list[self.mobgroup_index].is_placed and \
                    self.treasure_list[self.mobgroup_index].is_opened is False:
                        return
        mobs[3] = self.generate_monster(stage_id, mobs[2], mobs[1],)
        self.treasure_list[self.mobgroup_index] = (item.TreasureBox(mobs[0],[0,0],
                                                                    mobs[3][0].drop_item_id,mobs[3][0].drop_number))
        mobs[1] += 1

    def generate_monster(self, stage_id, monster_id, group_id):
        monsters = []
        monster_list = comf.read_json(f"assets/data/stage{stage_id}.json")
        for data in monster_list:
            if data[0] == monster_id:
                break
        name = data[1]
        image_source = data[2]
        monster_parameter = data[3][group_id]
        
        _q = G_.P_MAIN_WND[2]//4
        _address_list = ([_q*2,_q*2],[_q*1,_q*2],[_q*3,_q*2],
                         [_q*2,_q*3],[_q*2,_q*1],[_q*1,_q*3],
                         [_q*3,_q*1],[_q*3,_q*3],[_q*1,_q*1])
        _address_list = ([_q*2,_q*2],[_q*1.5,_q*2],[_q*2.5,_q*2],
                         [_q*2,_q*2.5],[_q*2,_q*1.5],[_q*1.5,_q*2.5],
                         [_q*2.5,_q*1.5],[_q*2.5,_q*2.5],[_q*1.5,_q*1.5])

        for i in range(px.rndi(1,9)):
            monsters.append(Monster(stage_id, name, image_source, _address_list[i],
                                    *monster_parameter, self.message_manager))
        return monsters

    def get_living_monsters(self):
        return sum([1 for mob in self.mobgroup[self.mobgroup_index][3] if mob.is_dead is False])

    def set_mobgroup_index(self, now_view):
        for i,data in enumerate(self.mobgroup):
            if data[0] == tuple(now_view):
                self.mobgroup_index = i
                break

    def update(self):
        for i, mob in enumerate(self.mobgroup[self.mobgroup_index][3]):
            if mob.is_dead:
                pass
            elif mob.hp < 0:
                mob.is_dead = True
                self.treasure_list[self.mobgroup_index].address = mob.address
            else:
                mob.update(self.ref_user)
        
        if  self.get_living_monsters() == 0:
            if self.treasure_list[self.mobgroup_index].map_address == self.mobgroup[self.mobgroup_index][0]:
                if self.treasure_list[self.mobgroup_index].is_placed is False:
                    if self.ref_user.is_clear:
                        self.treasure_list[self.mobgroup_index].is_placed = True
                        self.treasure_list[self.mobgroup_index].is_opened = True
                        self.treasure_list[self.mobgroup_index].rate_open = 100
                        item.pick_item(self.treasure_list[self.mobgroup_index].item_id,
                                       self.treasure_list[self.mobgroup_index].num_item, self.ref_user)
                        self.message_manager.add_message(
                            f"{item.get_item_info(self.treasure_list[self.mobgroup_index].item_id)[1]} {self.treasure_list[self.mobgroup_index].num_item}獲得")
                    else:
                        self.treasure_list[self.mobgroup_index].is_placed = True

    def draw(self, scene):
        if self.treasure_list[self.mobgroup_index].map_address == self.mobgroup[self.mobgroup_index][0]:
            self.treasure_list[self.mobgroup_index].draw()

        for mob in self.mobgroup[self.mobgroup_index][3]:
            if mob.is_dead:
                if mob.dead_dither > 0:
                    px.dither(mob.dead_dither)
                    px.blt(mob.address[0]-8, mob.address[1]-8, G_.IMGIDX["MOB"], 
                        mob.image_source[0] + 16*mob.image_position, mob.image_source[1],
                        mob.image_source[2] * mob.image_mirror, mob.image_source[3], colkey=3)
                    px.dither(1)
                    mob.dead_dither -= 0.025
            else:
                mob.draw(scene)


class Monster(character.Character):
    def __init__(self, stage_id, name, image_source, address,
                 maxhp, strength, dexterity, agility, intelligence,wisdom, magicregistance,
                 attack, defend, magic_power, magic_defend, reduce_fire, reduce_ice, reduce_wind, reduce_earth,
                 experience, move_type, drop_item_id, drop_number, magic_id, message_manager):
        super().__init__(move_type, address, image_source,
                         name, maxhp, strength, dexterity, agility, intelligence, wisdom, magicregistance)

        self.message_manager = message_manager
        #モンスター専用属性
        self.experience = experience
        self.reduce_fire = reduce_fire
        self.reduce_ice = reduce_ice
        self.reduce_wind = reduce_wind
        self.reduce_earth = reduce_earth
        self.drop_item_id = drop_item_id
        self.drop_number = drop_number
        self.magic_id = magic_id
        self.is_boss = False
        self.is_warp = False
        self.warp_counter = 0
        self.image_mirror = 1
        self.dead_dither = 1

        #所持金算出
        self.gold = (stage_id + 1)**2 * px.rndi(1,10)

        #モンスターの場合は算出ではなく指定値
        self.attack = attack
        self.defend = defend
        self.magic_power = magic_power
        self.magic_defend = magic_defend
        self.exp_weapon = 100
        self.exp_armor = 100
        self.exp_shield = 100
        self.exp_magic = [100,100,100,100]

        if magic_id is None:
            self.magic = None
        else:
            self.magic = item.Magic(magic_id)

    def get_elemental_reduce(self, spell_type):
        match spell_type:
            case 12:
                return self.reduce_fire
            case 13:
                return self.reduce_ice
            case 14:
                return self.reduce_wind
            case 15:
                return self.reduce_earth

    def cast_spell(self):
        image_source = self.cast_spell_common()
        return character.Spell(self.magic, self.address, self.direction, image_source, self.intelligence, self.wisdom)

    def calc_distance(self, ref_user):
        diff_x = ref_user.address[0] - self.address[0]
        diff_y = ref_user.address[1] - self.address[1]
        threshold = self.image_source[2]*0.75
        return [diff_x, diff_y, threshold]

    def trace_target(self, ref_user):
        diff_x, diff_y, threshold = self.calc_distance(ref_user)
        dx = -1 if diff_x <= -threshold else 1 if diff_x >= threshold else 0
        dy = +3 if diff_y <= -threshold else -3 if diff_y >= threshold else 0
        dir = 5 + dx + dy  # テンキー配置の位置を表す
        # 斜めにいる場合 → ランダムに縦横へ寄せる
        match dir:
            case 1: dir = 4 if px.rndi(0,1) == 0 else 2
            case 3: dir = 6 if px.rndi(0,1) == 0 else 2
            case 7: dir = 4 if px.rndi(0,1) == 0 else 8
            case 9: dir = 6 if px.rndi(0,1) == 0 else 8
        # テンキー方向 → Python版 direction に変換
        dir_map = {2:0, 4:1, 6:2, 8:3}
        if dir in dir_map:
            self.direction = dir_map[dir]
        else:
            # 重なっている場合 → より差分の大きい軸で方向を決定
            if abs(diff_x) > abs(diff_y):
                self.direction = 2 if diff_x > 0 else 1  # 右 or 左
            elif abs(diff_y) > 0:
                self.direction = 0 if diff_y > 0 else 3  # 下 or 上
            else:
                # 完全に同座標 → デフォルトで下を向く（安全策）
                self.direction = 0

    def flee_target(self, ref_user):
        diff_x, diff_y, threshold = self.calc_distance(ref_user)
        dx = -1 if diff_x <= -threshold else 1 if diff_x >= threshold else 0
        dy = +3 if diff_y <= -threshold else -3 if diff_y >= threshold else 0
        dir = 5 - dx - dy  # 追尾の逆
        # 斜め方向なら、前フレームの向きを避けて縦横を選択
        match dir:
            case 1: dir = 4 if px.rndi(0,1) == 1 else 2
            case 3: dir = 6 if px.rndi(0,1) == 1 else 2
            case 7: dir = 4 if px.rndi(0,1) == 1 else 8
            case 9: dir = 6 if px.rndi(0,1) == 1 else 8
        # テンキー方向 → Python版 direction に変換
        dir_map = {2:0, 4:1, 6:2, 8:3}
        if dir in dir_map:
            self.direction = dir_map[dir]

    #詠唱後魔法の独立更新処理
    def spellupdate(self, ref_user):
        if self.magic_id is not None and isinstance(self.magic.spell, character.Spell):
            self.magic.spell.update()
            if self.magic.spell.timer_remain == 0:
                self.magic.spell = None
            else:
                _attackrange_magic = self.magic.func_attackrange(*self.magic.spell.address,
                                                                self.magic.spell.direction)
                for _attackrange in _attackrange_magic:
                    if comf.check_collision_hitbox(*_attackrange, *ref_user.address,16,16):
    
                        damage = self.proc_attack_spell(self.magic.item_type, ref_user)
                        if damage > 0:
                            self.message_manager.add_message(f"被害 {damage}", 8)
                        elif damage == 0:
                            self.message_manager.add_message(f"レジスト成功！", 3)
                        if self.magic.spell.spell_type in (12,15): #魔法が命中したらインスタンスは消える
                            self.magic.spell = None
                            return

    def update(self, ref_user):
        if self.is_dead:
            return
        
        self.common_timer_decrement()

        #詠唱呪文のインスタンス削除はインスタンス外部から実行
        self.spellupdate(ref_user)

        #砂時計、隠れ蓑によるモンスター移動ロジックの一時変更
        if ref_user.timer_item[1] > 0:
            return
        elif ref_user.timer_item[2] > 0:
            movetype = 1
            self.is_warp = False
        else:
            movetype = self.move_type

        if self.timer_action > 0 or self.timer_spellcast > 0:
            return
        else:
            if self.timer_attack > 0:
                return
            elif self.is_warp:
                pass
            elif comf.check_collision_hitbox(*self.address,15,15, *ref_user.address,15,15):
                if ref_user.timer_damaged == 0:
                    if ref_user.timer_item[2] <= 0 and ref_user.timer_item[3] <= 0: #砂時計の場合は処理がここまで来ない
                        damage = self.proc_attack_physical(ref_user)
                        if damage:
                            self.message_manager.add_message(f"被害 {damage}", 8)
                        else:
                            self.message_manager.add_message(f"ガード成功！", 3)
                        self.timer_attack = int(G_.GAME_FPS//8 + self.attack_waittime)
                        return
            if self.magic_id is not None and ref_user.timer_item[2] <= 0 and px.rndi(0,128) < self.wisdom/2:
                if self.is_warp: #ワープ中は当然魔法を撃たない
                    pass
                elif (self.address[0]-8 <= ref_user.address[0] <= self.address[0]+8) or\
                        (self.address[1]-8 <= ref_user.address[1] <= self.address[1]+8):
                    self.trace_target(ref_user)
                    self.magic.spell = self.cast_spell()
                    px.play(3, G_.SNDEFX["spell"], resume=True)
                    # self.timer_action = self.magic.spell.timer_remain
                    self.timer_spellcast = self.magic.spell.casttime
                    return

        is_moved = False
        agility_ = min(255,ref_user.agility*2) if ref_user.is_agi_up else ref_user.agility
        match movetype:
            case 1:
                tmpRnd = px.rndi(0,4)
                if tmpRnd == 4:
                    return
                else:
                    self.direction = tmpRnd
                    is_moved = True
            case 2:
                if px.rndi(0, agility_) < self.agility:
                    self.trace_target(ref_user)
                    is_moved = True
            case 3:
                if px.rndi(0, agility_) < self.agility:
                    self.flee_target(ref_user)
                    is_moved = True
            case 4:
                self.trace_target(ref_user) 
                self.image_position = px.frame_count%32//16
            case 5:
                self.image_position = px.frame_count%32//16
                self.warp_counter = max(0, self.warp_counter - 1)
                if self.warp_counter < self.action_waittime*32:
                    self.is_warp = True
                else:
                    self.is_warp = False
                if self.warp_counter == 0:
                    self.address = [px.rndi(20,G_.P_MAIN_WND[2]-20),px.rndi(20,G_.P_MAIN_WND[3]-20)]
                    self.timer_action = self.action_waittime
                    self.warp_counter = self.action_waittime*64
            case _:
                pass

        if is_moved:
            if ref_user.user_scene == 30:
                fencesize = 10
            elif ref_user.user_scene == 40:
                fencesize = 25
            is_blocked = self.check_fence(fencesize) #フェンス（柵）より外には移動しない
            if is_blocked:
                diff_x = self.address[0] - ref_user.address[0]
                diff_y = self.address[1] - ref_user.address[1]
                match movetype:
                    case 1:
                        self.direction = self.direction + 1 if self.direction != 3 else 0
                    case 2:
                        match self.direction:
                            case 0|3:
                                self.direction = 2 if diff_x > 0 else 1
                            case 1|2:
                                self.direction = 0 if diff_y > 0 else 3
                        if self.check_fence(fencesize):
                            return
                    case 3:
                        # 本来の方向に進めないので「ユーザから遠ざかる反対方向」を再計算
                        match self.direction:
                            case 0: self.direction = 3 if px.rndi(0,1) == 0 else 1 if diff_x < 0 else 2
                            case 1: self.direction = 2 if px.rndi(0,1) == 0 else 3 if diff_y < 0 else 0
                            case 2: self.direction = 1 if px.rndi(0,1) == 0 else 3 if diff_y < 0 else 0
                            case 3: self.direction = 0 if px.rndi(0,1) == 0 else 1 if diff_x < 0 else 2
                        if self.check_fence(fencesize):
                            return
                    # case 4:
                    #   移動しない為このケースは不要
                    # case 5:
                    #   通常移動ロジック内でフェンス内のみ移動する為このケースは不要
            self.move_address()
            self.timer_action = self.action_waittime

    def check_fence(self, fencesize):
        # fencesize = 10
        if (self.address[0] <= fencesize and self.direction == 1) or \
        (self.address[0] >= (G_.P_MAIN_WND[2]-fencesize) and self.direction == 2) or \
        (self.address[1] <= fencesize and self.direction == 3) or \
        (self.address[1] >= (G_.P_MAIN_WND[3]-fencesize) and self.direction == 0):
            return True
        return False

    def draw(self,scene):
        if self.magic_id is not None and isinstance(self.magic.spell, character.Spell):
            self.magic.spell.draw(scene)

        if self.is_warp:
            return

        #HPバー表示
        hpbar = self.hp/self.maxhp*16 #現HP率を16ドット（キャラ幅）に合わせる
        px.rect(self.address[0]-8, self.address[1]-10, 16, 1, 8) #下地の赤
        px.rect(self.address[0]-8, self.address[1]-10, hpbar, 1, 5) #現HPを示す青

        self.draw_damage_effect()
        if self.direction == 2:
            self.image_mirror = -1
        elif self.direction == 1:
            self.image_mirror = 1
        else:
            self.image_mirror = self.image_mirror
        px.blt(self.address[0]-8, self.address[1]-8, G_.IMGIDX["MOB"], 
            self.image_source[0] + 16*self.image_position, self.image_source[1],
            self.image_source[2] * self.image_mirror, self.image_source[3], colkey=3)
        self.draw_cast_effect()
        if self.timer_fire>0:
            px.blt(self.address[0]-12, self.address[1]+4, G_.IMGIDX["CHIP"],
                    56,232, 8,8, colkey=0)
        if self.timer_ice>0:
            px.blt(self.address[0]-4, self.address[1]+4, G_.IMGIDX["CHIP"],
                    64,232, 8,8, colkey=0)
        if self.timer_wind>0:
            px.blt(self.address[0]+4, self.address[1]+4, G_.IMGIDX["CHIP"],
                    72,232, 8,8, colkey=0)


class BossMonster(Monster):
    def __init__(self, stage_id, name, image_source, address,
                 maxhp, strength, dexterity, agility, intelligence, wisdom, magicregistance,
                 attack, defend, magic_power, magic_defend, reduce_fire, reduce_ice, reduce_wind, reduce_earth,
                 experience, move_type, drop_item_id, drop_number, magic_id, message_manager):
        super().__init__(stage_id, name, image_source, address,
                         maxhp, strength, dexterity, agility, intelligence,wisdom, magicregistance,
                         attack, defend, magic_power, magic_defend, reduce_fire, reduce_ice, reduce_wind, reduce_earth,
                         experience, move_type, drop_item_id, drop_number, magic_id, message_manager)
        self.shield = item.Shield(170)
        self.shield.rate_knockback = 0
        self.is_anger = False
        self.is_anger_event = False
        self.is_boss = True
        self.is_defeat = False
        self.is_broken = False
        self.stage_id = stage_id

    def update(self, ref_user):
        if self.is_dead:
            return

        #HP半減で怒りモード
        if self.hp <= self.maxhp//2 and self.is_anger is False:
            self.agility *= 2
            self.movespeed += 1
            self.set_action_waittime()
            self.attack_waittime *= 1.45
            if self.stage_id in (4,5):
                self.defend *= 2
            if self.stage_id == 5:
                self.wisdom /= 3.5
            self.is_anger = True
            self.is_anger_event = True

        self.common_timer_decrement()
        #ボスにデバフは効かない
        self.timer_fire = 0
        self.timer_ice = 0
        self.timer_wind = 0

        self.spellupdate(ref_user)

        #難易度調整の為　5秒に一度短時間硬直
        if px.frame_count%(G_.GAME_FPS*5) < G_.GAME_FPS//4:
            return

        #ステージ別の処理
        match self.stage_id:
            case 0:
                #火術、風術特効
                if self.timer_magicdamaged == 1 and \
                        ref_user.equip_id[3] in (200,201,202,203,220,221,222,223):
                    px.play(0, G_.SNDEFX["critical"], resume=True)
            case 1:
                #氷術特効
                if self.timer_magicdamaged == 1 and \
                        ref_user.equip_id[3] in (210,211,212,213):
                    px.play(0, G_.SNDEFX["critical"], resume=True)
                    self.agility *= 0.95
                    self.action_waittime = self.set_action_waittime()
            case 2:
                #風術特効
                if self.timer_magicdamaged == 1 and \
                        ref_user.equip_id[3] in (220,221,222,223):
                    self.agility *= 0.93
                    self.action_waittime = self.set_action_waittime()
                    px.play(0, G_.SNDEFX["critical"], resume=True)
                if px.frame_count%G_.GAME_FPS == 0:
                    self.agility += 1
                    self.action_waittime = self.set_action_waittime()
            case 3:
                #火術特効
                if self.timer_magicdamaged == 1 and \
                        ref_user.equip_id[3] in (200,201,202,203):
                    self.magic_defend *= 0.97
                    px.play(0, G_.SNDEFX["critical"], resume=True)
                #打撃特効(短時間硬直)
                if self.timer_damaged > G_.GAME_FPS*0.25:
                    return
                elif self.timer_damaged == 1:
                    px.play(0, G_.SNDEFX["critical"], resume=True)
            case 4:
                #斧特効(硬直・防御力減少)
                if ref_user.weapon.item_type == 3:
                    if self.timer_damaged > G_.GAME_FPS*0.4:
                        return
                    elif self.timer_damaged == 1:
                        self.defend *= 0.95
                        px.play(0, G_.SNDEFX["critical"], resume=True)
            case 5:
                #風術特効
                if self.timer_magicdamaged == 1 and \
                        ref_user.equip_id[3] in (220,221,222,223):
                    px.play(0, G_.SNDEFX["critical"], resume=True)
                    self.agility *= 0.98
                    self.action_waittime = self.set_action_waittime()

        if self.timer_action > 0 or self.timer_spellcast > 0:
            return
        else:
            if self.timer_attack > 0:
                return
            elif comf.check_collision_hitbox(*self.address,self.image_source[2]-4,self.image_source[3]-4,
                                             *ref_user.address,15,15):
                if ref_user.timer_damaged == 0:
                    self.proc_attack_physical(ref_user, 8)
                    self.timer_attack = int(G_.GAME_FPS//2 + self.attack_waittime)
                    return
            if self.magic_id is not None and (px.rndi(0,128) < (self.wisdom/2)):
                if (self.address[0]-20 <= ref_user.address[0] <= self.address[0]+20) or\
                        (self.address[1]-20 <= ref_user.address[1] <= self.address[1]+20):
                    self.trace_target(ref_user)
                    self.magic.spell = self.cast_spell()
                    px.play(3, G_.SNDEFX["spell"], resume=True)
                    self.timer_spellcast = self.magic.spell.casttime+self.action_waittime
                    return

        self.trace_target(ref_user)

        #フェンス（柵）より外には移動しない
        fencesize = 40
        if (self.address[0] <= fencesize and self.direction == 1) or \
        (self.address[0] >= (G_.P_MAIN_WND[2]+G_.P_SUB_WND[2]-fencesize) and self.direction == 2) or \
        (self.address[1] <= fencesize and self.direction == 3) or \
        (self.address[1] >= (G_.P_MAIN_WND[3]+G_.P_SUB_WND[3]-fencesize) and self.direction == 0):
            diff_x = self.address[0] - ref_user.address[0]
            diff_y = self.address[1] - ref_user.address[1]
            match self.direction:
                case 0|3:
                    self.direction = 2 if diff_x > 0 else 1
                case 1|2:
                    self.direction = 0 if diff_y > 0 else 3
            if self.check_fence(fencesize):
                return

        self.move_address()
        self.timer_action = self.action_waittime

    def draw(self):
        if self.magic_id is not None and isinstance(self.magic.spell, character.Spell):
            self.magic.spell.draw(70)
        if self.timer_damaged%5 in (1,3):
            px.circ(*self.address, 34, 7)
        if self.timer_magicdamaged%5 in (2,4):
            px.circ(*self.address, 34, 8)
        
        if self.direction == 2:
            self.image_mirror = -1
        elif self.direction == 1:
            self.image_mirror = 1
        else:
            self.image_mirror = self.image_mirror
        if self.is_dead and self.is_defeat:
            px.blt(self.address[0]-32, self.address[1], G_.IMGIDX["MOB"],
                    self.image_source[0], self.image_source[3]*2,
                    self.image_source[2], self.image_source[3]//2, colkey=3)
        else:
            px.blt(self.address[0]-32, self.address[1]-32, G_.IMGIDX["MOB"], 
                self.image_source[0], self.image_source[1] + 64*(px.frame_count%64//32),
                self.image_source[2] * self.image_mirror, self.image_source[3], colkey=3)
        self.draw_cast_effect()
