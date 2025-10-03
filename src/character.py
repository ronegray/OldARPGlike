import pyxel as px
import const as G_, common_func as comf
import item


class Character:
    def __init__(self, move_type:int, address:list, image_source:list, name:str, 
                 maxhp:int, strength:int, dexterity:int, agility:int, intelligence:int, wisdom:int,
                 magicregistance:int):
        #引数で設定
        self.move_type = move_type #キャラの移動タイプ 0ユーザ操作、1ランダム、2近付く、3逃げる、4移動しない、5ワープ
        self.address = address #キャラのマップ上座標（Block）
        self.image_source = image_source #画像リソース情報
        self.name = name #名前
        self.maxhp = maxhp #最大HP
        self.strength = strength #腕力
        self.dexterity = dexterity #器用さ
        self.agility = agility #敏捷性
        self.intelligence = intelligence #魔力
        self.wisdom = wisdom #賢さ
        self.magicregistance = magicregistance #魔法抵抗力
        #他パラメータから算出
        self.hp = maxhp #現在HP
        self.attack = 0 #攻撃力
        self.defend = 0 #防御力
        self.magic_power = 0 #魔法攻撃力
        self.magic_defend = 0 #魔法防御力
        #ゲーム状況に合わせて変化
        self.experience = 0 #経験値
        self.gold = 0 #所持金
        self.image_position = 0 #スプライトのアニメーション用。0⇔1切替
        self.is_dead = False #死亡フラグ
        self.exp_weapon = 0 #装備武器熟練度
        self.exp_armor = 0 #装備鎧熟練度
        self.exp_shield = 0 #装備盾熟練度
        self.exp_magic = [0,0,0,0] #魔法属性別熟練度　火氷風土
        self.equip_magic_index = 0 #装備中の魔法属性　0火 1氷 2風 3土
        self.direction = 0 #キャラの向き（CHARA_DIRのインデックス,0~3）
        self.timer_action = 0 #行動時間タイマー
        self.timer_attack = 0 #攻撃時間タイマー
        self.timer_spellcast = 0 #魔法詠唱中タイマー（移動不可）
        self.timer_fire = 0 #デバフ（炎）タイマー
        self.effect_fire = None #デバフ効果
        self.timer_ice = 0 #デバフ（氷）タイマー
        self.effect_ice = None #デバフ効果
        self.timer_wind = 0 #デバフ（風）タイマー
        self.effect_wind = None #デバフ効果
        self.timer_damaged = 0 #ダメージエフェクト表示中タイマー　連続ダメージ防止を兼ねる
        self.timer_magicdamaged = 0 #魔法ダメージエフェクト表示中タイマー　連続ダメージ防止を兼ねる
        #バフアイテム効果中フラグ
        self.is_str_up = False
        self.is_int_up = False
        self.is_agi_up = False
        self.is_regist_up = False
        #実行間隔　この値がタイマーにセットされ、1/1フレーム毎減算
        self.action_waittime = self.set_action_waittime() #aglが変化した際に実行し、行動待ち時間を再設定する
        self.attack_waittime = self.set_attack_waittime() #dex,武器が変化した際に実行し、攻撃待ち時間を再設定する
        self.movespeed = 2 #移動速度　防具やデバフ、アイテム効果等で変化

    #行動速度（間隔）
    def set_action_waittime(self):
        _agility = min(255,self.agility*2) if self.is_agi_up else self.agility
        if _agility >= 245:
            return 0
        elif _agility >= 225:
            return 1
        elif _agility >= 195:
            return 2
        elif _agility >= 145:
            return 3
        elif _agility >= 85:
            return 4
        elif _agility >= 55:
            return 5
        elif _agility >= 30:
            return 6
        else:
            return 7

    #攻撃速度（間隔）
    def set_attack_waittime(self):
        base = G_.GAME_FPS//10
        if self.dexterity >= 250:
            return int(base*2)
        elif self.dexterity >= 230:
            return int(base*2.5)
        elif self.dexterity >= 195:
            return int(base*3)
        elif self.dexterity >= 160:
            return int(base*3.5)
        elif self.dexterity >= 110:
            return int(base*4)
        elif self.dexterity >= 80:
            return int(base*4.5)
        elif self.dexterity >= 60:
            return int(base*5)
        elif self.dexterity >= 40:
            return int(base*5.5)
        elif self.dexterity >= 20:
            return int(base*6)
        else:
            return G_.GAME_FPS

    #アドレス移動
    def move_address(self):
        if px.frame_count%16 in (0,1,2,3):
            self.image_position = 1 - self.image_position
        self.address = [self.address[0] + (G_.CHARA_DIR[self.direction][0]*(self.movespeed)),
                        self.address[1] + (G_.CHARA_DIR[self.direction][1]*(self.movespeed))]
        return True

    #ステータス計算
    def calc_status(self, base_value:float, rate_exp:float, related_param:int=100):
        return float(base_value*(min(500,rate_exp*(related_param/100))))

    #ノックバックによる移動処理
    def move_knockback(self, move_length, target, direction):
        corners = [(-3,0), #左上
                   (3,0), #右上
                   (-3,6), #左下
                   (3,6), #右下
        ]
        match direction:
            case 0:
                offset1 = corners[2]
                offset2 = corners[3]
            case 1:
                offset1 = corners[0]
                offset2 = corners[2]
            case 2:
                offset1 = corners[1]
                offset2 = corners[3]
            case 3:
                offset1 = corners[0]
                offset2 = corners[0]

        rightlimit = G_.P_MAIN_WND[2]
        if target.move_type == 0 and target.user_scene in (70,75):
            rightlimit = px.width
        for _ in range(int(move_length)):
            destination = [target.address[0]+G_.CHARA_DIR[direction][0],\
                    target.address[1]+G_.CHARA_DIR[direction][1]]
            if target.move_type == 0:
                scene = target.user_scene
            else:
                scene = self.user_scene
            if scene == 30:
                fencesize = 10
            elif scene == 40:
                fencesize = 25
            elif scene in (70,75):
                fencesize = 8
            if target.address[0] <= fencesize and direction == 1:
                break
            if target.address[0] >= (rightlimit-fencesize) and direction == 2:
                break
            if target.address[1] <= fencesize and direction == 3:
                break
            if target.address[1] >= (G_.P_MAIN_WND[3]-fencesize) and direction == 0:
                break
            if target.move_type == 0:
                if target.user_scene == 30:
                    layer = 0
                    if comf.get_tileinfo(destination[0]+offset1[0],
                                         destination[1]+offset1[1],layer)[0] == 4:
                        break
                    if comf.get_tileinfo(destination[0]+offset2[0],
                                         destination[1]+offset2[1],layer)[0] == 4:
                        break
                elif target.user_scene == 40:
                    layer = 6
                    checklist = [(19,30),(19,31),(20,30),(20,31)]
                    if comf.get_tileinfo(destination[0]+offset1[0],
                                         destination[1]+offset1[1],layer) in checklist:
                        break
                    if comf.get_tileinfo(destination[0]+offset2[0],
                                         destination[1]+offset2[1],layer) in checklist:
                        break
                elif target.user_scene in (70,75):
                    layer = 1
                    if comf.get_tileinfo(destination[0]+G_.CHARA_DIR[direction][0],
                                         destination[1]+G_.CHARA_DIR[direction][1],layer) == (8,1):
                        break
                    if comf.get_tileinfo(destination[0]+offset1[0],
                                         destination[1]+offset1[1],layer) == (8,1):
                        break
                    if comf.get_tileinfo(destination[0]+offset2[0],
                                         destination[1]+offset2[1],layer) == (8,1):
                        break
            target.address = destination

    #物理攻撃処理
    def proc_attack_physical(self, target, knockback_length:int=1):
        #対象が被ダメージから一定時間内は連続ダメージを受けない
        if target.timer_damaged > 0:
            return -1
        #ノックバック関連処理
        try:
            knockback_reduse = target.shield.rate_knockback
        except AttributeError:
            knockback_reduse = 100
        final_knockback_length = (self.strength//16 + 8) * knockback_length * (knockback_reduse/100)
        self.move_knockback(final_knockback_length, target, self.direction)
        #ダメージ計算
        damage = max(0,
                     int(px.rndf(self.attack*0.9,self.attack*1.2) - target.defend))
        
        #ダメージ量に応じた成長計算
        if damage > 0:
            target.timer_damaged = G_.GAME_FPS
            self.grow_weapon()
            target.grow_armor()
            px.play(3, G_.SNDEFX["damage"], resume=True)
            target.hp -= int(damage)
        else:
            target.timer_damaged = G_.GAME_FPS//3
            upper = 80 if self.exp_weapon > 50 else 32 if self.exp_weapon > 30 else 8
            if px.rndi(1,upper) <= 4:
                self.grow_weapon()
            upper = 80 if target.exp_armor > 50 else 32 if target.exp_armor > 30 else 8
            if px.rndi(1,upper) <= 4:
                target.grow_armor()
        return int(damage)

    #魔法攻撃処理
    def proc_attack_spell(self, spell_type:int, target, knockback_length=1):
        #対象が被ダメージから一定時間内は連続ダメージを受けない
        if target.timer_magicdamaged > 0:
            return -1
        #魔法は基本的にノックバック無し
        _elemental_reduce = 1 - (target.get_elemental_reduce(spell_type)/100)

        #防具の種類に応じて魔法ダメージ減衰
        try:
            damagerate = self.armor.rate_magicpower/100
        except AttributeError:
            damagerate = 1
        #ダメージ計算
        damage = max(0,int((px.rndf(self.magic_power*0.9,self.magic_power*1.1) * damagerate) 
                             * _elemental_reduce - target.magic_defend)
                    )
        if target.is_regist_up:
            damage /= 2
        
        #ダメージ量に応じた成長計算
        if damage > 0:
            target.timer_magicdamaged = G_.GAME_FPS
            self.grow_magic()
            target.grow_shield()
            px.play(3, G_.SNDEFX["damage"], resume=True)
            target.hp -= int(damage)
        else:
            target.timer_magicdamaged = G_.GAME_FPS//3
            upper = 80 if self.exp_magic[self.equip_magic_index] > 30 else 24
            if px.rndi(1,upper) <= 6:
                self.grow_magic()
            upper = 80 if target.exp_shield > 30 else 24
            if px.rndi(1,upper) <= 6:
                target.grow_shield()

        #デバフ抵抗判定
        if target.move_type != 0 and (_elemental_reduce <= 0 or target.is_boss): #ボスにはデバフ無効
            pass
        else:
            caster = (self.wisdom/8) * (self.magic.rate_effect/100) + (self.exp_magic[self.equip_magic_index]*0.1)
            register = (target.magicregistance/8) + px.rndi(-8,8)
            if caster > register:
                target.timer_magicdamaged = G_.GAME_FPS
                _intelligence = min(255,self.intelligence*2) if self.is_int_up else self.intelligence
                match spell_type:
                    case 12:
                        target.timer_fire = min(255, target.timer_fire + int(_intelligence * (px.rndi(2,12)/100) +0.5))
                        target.effect_fire = self.magic.func_effect
                    case 13:
                        target.timer_ice = min(255, target.timer_ice + int(_intelligence * (px.rndi(2,12)/100) +0.5))
                        if target.effect_ice is None: #減少効果は重複発動しない
                            item.effect_type_13(target)
                            target.effect_ice = self.magic.func_effect
                    case 14:
                        target.timer_wind = min(255, target.timer_wind + int(_intelligence * (px.rndi(2,12)/100) +0.5))
                        if target.effect_wind is None: #減少効果は重複発動しない
                            item.effect_type_14(target)
                            target.effect_wind = self.magic.func_effect
                    case 15:
                        self.move_knockback(self.intelligence//8+32, target,
                                            self.magic.spell.direction)
        return int(damage)

    #オーバーライド用
    def grow_weapon(self):
        pass

    def grow_armor(self):
        pass

    def grow_magic(self):
        pass

    def grow_shield(self):
        pass

    def cast_spell(self):
        pass

    def get_elemental_reduce(self, spell_type:int):
        return 0

    def cast_spell_common(self):
        if self.magic.item_type == 12:
            image_source = [24,88,24,24]
        elif self.magic.item_type == 15:
            image_source = [0,88,8,8]
        else:
            image_source = [0,0,0,0]
        if self.magic.item_type == 14:
            self.timer_action += G_.GAME_FPS
        return image_source

    #ユーザ・モンスター共通タイマー減算処理
    def common_timer_decrement(self):
        #カウンタ減算
        self.timer_action = max(0, self.timer_action-1)
        self.timer_attack = max(0, self.timer_attack -1)
        self.timer_spellcast = max(0, self.timer_spellcast -1)
        self.timer_damaged = max(0, self.timer_damaged-1)
        self.timer_magicdamaged = max(0, self.timer_magicdamaged-1)
        if px.frame_count%G_.GAME_FPS == 0:
            self.decrement_fire()
            self.decrement_ice()
            self.decrement_wind()
        return

    def decrement_fire(self, is_equip=False):
        if self.effect_fire is not None:
            if self.timer_fire > 0:
                if is_equip is False:
                    self.effect_fire(self)
                try:
                    dec = 2 if self.is_clear else 1
                except AttributeError:
                    dec = 1
                self.timer_fire = max(0, self.timer_fire-dec)
            if self.timer_fire == 0:
                self.effect_fire = None

    def decrement_ice(self, is_equip=False):
        if self.effect_ice is not None:
            if self.timer_ice > 0:
                if is_equip is False:
                    self.hp = int(self.hp - self.hp*0.001)
                try:
                    dec = 2 if self.is_clear else 1
                except AttributeError:
                    dec = 1
                self.timer_ice = max(0, self.timer_ice-dec)
            if self.timer_ice == 0:
                self.effect_ice = None
                try:
                    self.calc_movespeed()
                except AttributeError:
                    self.movespeed = 2

    def decrement_wind(self):
        if self.effect_wind is not None:
            if self.timer_wind > 0:
                try:
                    dec = 2 if self.is_clear else 1
                except AttributeError:
                    dec = 1
                self.timer_wind = max(0, self.timer_wind-dec)
            if self.timer_wind == 0:
                self.effect_wind = None
                self.attack_waittime = self.set_attack_waittime()


    def update(self):
        raise NotImplementedError

    def draw_damage_effect(self):
        if self.timer_damaged%5 in (1,3):
            px.circ(*self.address, 9, 10)
        if self.timer_magicdamaged%5 in (2,4):
            px.circ(*self.address, 9, 8)

    def draw_cast_effect(self):
        if self.timer_spellcast > 0:
            px.blt(self.address[0]-8,self.address[1]-8, G_.IMGIDX["CHIP"],
                    0+((px.frame_count//(G_.GAME_FPS//5))%3*16),192, 16,16, colkey=0)


class UserCharacter(Character):
    def __init__(self, move_type, address, image_source, name, maxhp, 
                 strength, dexterity, agility, intelligence, wisdom, magicregistance,
                 experience = 0):
        super().__init__(move_type, address, image_source, name, maxhp,
                         strength, dexterity, agility, intelligence, wisdom, magicregistance)
        self.is_clear = False
        self.level = 1
        self.key = 5
        self.elixer = 3
        self.user_scene = G_.SCENE["Title"]
        self.food = 1000
        self.gold = 0
        self.experience = 0
        #キャラ選択に応じた初期パラメータ＆装備
        if self.name == "戦士型":
            self.equip_id = [70,120,160,220,22]
            self.equip_magic_index = 2
        elif self.name == "魔法使い型":
            self.equip_id = [40,100,140,230,22]
            self.equip_magic_index = 3
        elif self.name == "バランス型":
            self.equip_id = [60,110,150,210,22]
            self.equip_magic_index = 1
        self.magic = None
        self.spellbook = [False,False,False,False] #火術、氷術、風術、土術の装備品
        self.add_spellbook(self.equip_id[3])
        if self.name == "魔法使い型":
            self.add_spellbook(200)
            self.add_spellbook(210)
            self.add_spellbook(220)
        self.exp_weapon = self.exp_armor = self.exp_shield = 10
        for id in self.equip_id:
            self.equip_item(id)
        self.inventory=[]
        item.pick_item(22,5,self)
        item.pick_item(21,2,self)
        item.pick_item(10,1,self)
        self.reset_state()
        self.inventory.sort(key = lambda row: row[0])

    #ユーザテンポラリ情報の初期化
    def reset_state(self):
        self.address = [G_.P_MAIN_WND[2]//4,G_.P_MAIN_WND[3]//4]
        self.direction = 0
        self.hp = self.maxhp

        self.weapon.is_attacking = False
        self.weapon.motion_counter = 0
        self.magic.spell = None

        self.timer_action = 0
        self.timer_attack = 0
        self.timer_spellcast = 0
        self.timer_damaged = 0
        self.timer_magicdamaged = 0
        self.timer_fire = 0 #デバフ（炎）タイマー
        self.effect_fire = None #デバフ効果
        self.timer_ice = 0 #デバフ（氷）タイマー
        self.effect_ice = None #デバフ効果
        self.timer_wind = 0 #デバフ（風）タイマー
        self.effect_wind = None #デバフ効果

        self.timer_selectmagic = 0
        self.timer_selectitem = 0
        self.timer_food = 8 * G_.GAME_FPS
        self.timer_ontrap = 0
        self.timer_item = [0,0,0,0,0,0,0,0,0,]
        self.is_str_up = False
        self.is_agi_up = False
        self.is_int_up = False
        self.is_regist_up = False

        self.image_position = 0
        self.is_dead = False
        self.is_use_item20 = False
        self.is_use_item21 = False
        self.is_use_item = False
        self.is_use_item_block = False
        self.is_use_item_miss = False
        self.is_ontrap = False

        self.calc_attack()
        self.defend = self.calc_status(self.armor.value, self.exp_armor)
        self.calc_magic_power()
        self.calc_magic_defend()
        self.calc_movespeed()

        self.action_waittime = self.set_action_waittime() #aglが変化した際に実行し、行動待ち時間を再設定する
        self.attack_waittime = self.set_attack_waittime() #dex,武器が変化した際に実行し、攻撃待ち時間を再設定する

    #移動速度算出
    def calc_movespeed(self):
        agiup = 1 if self.is_agi_up else 0
        bonus = 1 if self.is_clear else 0
        self.movespeed = self.armor.movespeed + agiup + bonus
        if self.timer_ice > 0:
            self.movespeed = self.movespeed//2
            
    #攻撃力算出
    def calc_attack(self):
        _strength = min(255,self.strength*2) if self.is_str_up else self.strength
        self.attack = self.calc_status(self.weapon.value, self.exp_weapon, _strength)

    #魔法攻撃力算出
    def calc_magic_power(self):
        _intelligence = min(255,self.intelligence*2) if self.is_int_up else self.intelligence
        magicvaluerate = 1
        if self.weapon.item_type == 0:
            magicvaluerate += (int(self.weapon.id) - 39)/12
        self.magic_power = int(self.calc_status(self.magic.value * magicvaluerate,
                                                self.exp_magic[self.equip_magic_index],_intelligence))
    #魔法防御算出
    def calc_magic_defend(self):
        self.magic_defend = self.calc_status(self.shield.value, self.exp_shield, self.magicregistance)

    #アイテム装備処理
    def equip_item(self, item_id):
        item_type = item.get_item_info(item_id)[0]
        #武器
        if item_type in (0,1,2,3):
            now_equip_type = item.get_item_info(self.equip_id[0])[0]
            self.equip_id[0] = item_id
            self.weapon = item.Weapon(self.equip_id[0])
            self.exp_weapon = 5+self.exp_weapon*0.5 if self.weapon.item_type == now_equip_type else 10
            self.calc_attack()
            #杖を装備した場合は魔法攻撃力が変化する
            if isinstance(self.magic, item.Magic):
                self.calc_magic_power()
        #防具
        elif item_type in (4,5,6,7):
            now_equip_type = item.get_item_info(self.equip_id[1])[0]
            self.equip_id[1] = item_id
            self.armor = item.Armor(self.equip_id[1])
            self.exp_armor = 5+self.exp_armor*0.5 if self.armor.item_type == now_equip_type else 10
            self.defend = self.calc_status(self.armor.value, self.exp_armor)
            #防具を装備した場合は見た目と移動速度が変化する（ダメージ減衰は攻撃ルーチン内で処理）
            self.image_source[1] = item_type%4*16
            self.calc_movespeed()
        #盾
        elif item_type in (8,9,10,11):
            now_equip_type = item.get_item_info(self.equip_id[2])[0]
            self.equip_id[2] = item_id
            self.shield = item.Shield(self.equip_id[2])
            self.exp_shield = 5+self.exp_shield*0.5 if self.shield.item_type == now_equip_type else 10
            self.calc_magic_defend()
        #魔法
        elif item_type in (12,13,14,15):
            self.equip_id[3] = item_id
            self.magic = item.Magic(self.equip_id[3])
            match item_type:
                case 12:
                    self.equip_magic_index = 0
                case 13:
                    self.equip_magic_index = 1
                case 14:
                    self.equip_magic_index = 2
                case 15:
                    self.equip_magic_index = 3
            self.calc_magic_power()
        elif item_type in (18,19):
            self.equip_id[4] = item_id

    #所有魔法の書き換え
    def add_spellbook(self, item_id):
        item_type = item.get_item_info(item_id)[0]
        _magic_index = int(item_type - 12)
        if self.spellbook[_magic_index]:
            self.exp_magic[_magic_index] = max(10, self.exp_magic[_magic_index]*0.75)
        else:
            self.exp_magic[_magic_index] = 10
        self.spellbook[_magic_index] = item_id

    #熟練度上昇
    def grow_exp(self, exp):
        bonus = 3 if self.is_clear else 1
        if exp < 255:
            if exp < 30:
                exp += 5 * bonus
            elif exp < 50:
                exp += 2.17 * bonus
            elif exp < 70:
                exp += 0.79 * bonus
            elif exp < 100:
                exp += 0.42 * bonus
            elif exp < 128:
                exp += 0.21 * bonus
            elif exp < 144:
                exp += 0.13 * bonus
            elif exp < 160:
                exp += 0.04 * bonus
            else:
                if px.rndi(64,128) >= exp//2:
                    exp += 0.03 * bonus
            exp = min(255,exp)
        return exp

    #武器熟練上昇
    def grow_weapon(self):
        self.exp_weapon = self.grow_exp(self.exp_weapon)
        self.calc_attack()

    #魔法熟練上昇
    def grow_magic(self):
        self.exp_magic[self.equip_magic_index] = self.grow_exp(self.exp_magic[self.equip_magic_index])
        self.calc_magic_power()

    #防具熟練上昇
    def grow_armor(self):
        self.exp_armor = self.grow_exp(self.exp_armor)
        self.defend = int(self.calc_status(self.armor.value, self.exp_armor))

    #盾熟練上昇
    def grow_shield(self):
        self.exp_shield = self.grow_exp(self.exp_shield)
        self.calc_magic_defend()

    #アイテム熟練上昇
    def grow_item(self, inventory_index):
        bonus = 1.5 if self.is_clear else 1
        if self.inventory[inventory_index][2] < 100:
            if self.inventory[inventory_index][2] < 25:
                self.inventory[inventory_index][2] += 5 * bonus
            elif self.inventory[inventory_index][2] < 50:
                self.inventory[inventory_index][2] += 3.97 * bonus
            elif self.inventory[inventory_index][2] < 70:
                self.inventory[inventory_index][2] += 2.94 * bonus
            elif self.inventory[inventory_index][2] < 85:
                self.inventory[inventory_index][2] += 1.91 * bonus
            elif self.inventory[inventory_index][2] < 95:
                self.inventory[inventory_index][2] += 0.88 * bonus
            else:
                self.inventory[inventory_index][2] += 0.33 * bonus
            self.inventory[inventory_index][2] = min(100,self.inventory[inventory_index][2])

    #魔法詠唱（スペル効果インスタンス生成）
    def cast_spell(self):
        image_source = self.cast_spell_common()
        _intelligence = min(255,self.intelligence*2) if self.is_int_up else self.intelligence
        return Spell(self.magic, self.address, self.direction, image_source, _intelligence, self.wisdom)

    #入力キーチェック
    def check_inputkey(self):
        _return_code = None
        btn = comf.get_button_state()
    #タイマーに関係なく実行できる操作(ただしボス戦中は魔法選択のみ、呼び出し元で制御)
        #魔法選択メニュー
        if btn["L"]:
            _return_code = 8
        #アイテム選択メニュー
        elif btn["R"]:
            _return_code = 9
        #メニュー表示
        elif btn["b"]:
            px.play(3, [G_.SNDEFX["po"]], resume=True)
            _return_code =  7
        #図鑑表示
        elif btn["E"]:
            _return_code = 10
    #攻撃タイマー中は攻撃不可
        #攻撃
        elif btn["a"]:
            if self.timer_attack > 0:
                return _return_code
            elif self.timer_item[3] > 0: #着ぐるみ中は物理攻撃不可
                return _return_code
            else:
                self.weapon.is_attacking = True
                self.timer_attack = int(G_.GAME_FPS//20
                                        + (self.attack_waittime
                                            * self.weapon.attack_speed
                                            * ((200-self.shield.rate_attackspeed)/100)))
                self.weapon.motion_frames = self.timer_attack
            _return_code = 4
    #行動タイマー中は以下の行動不可
        elif self.timer_action > 0 or self.timer_spellcast > 0:
            return _return_code
        else:
            #魔法詠唱
            if btn["x"]:
                if self.timer_spellcast > 0:
                    pass
                else:
                    self.magic.spell = self.cast_spell()
                    self.timer_spellcast = self.magic.spell.casttime
                _return_code =  5
            #アイテム使用
            elif btn["y"]:
                if self.timer_action > 0:
                    pass
                elif self.user_scene != G_.SCENE["BossBattle"] and self.user_scene != G_.SCENE["LastBoss"]:
                    rc = item.use_item(self.equip_id[4], self)
                    if rc == 0:
                        self.is_use_item_miss = True
                    elif rc == 1:
                        self.is_use_item_block = True
                    self.timer_action = G_.GAME_FPS // 8
                _return_code =  6
            elif self.timer_attack > 0:
                return _return_code
            else:
                #移動は攻撃タイマ―中も不可
                to_dir = 9
                if btn["u"]:
                    to_dir = 3
                elif btn["l"]:
                    to_dir = 1
                elif btn["d"]:
                    to_dir = 0
                elif btn["r"]:
                    to_dir = 2
                if to_dir != 9:
                    self.direction = to_dir
                    _return_code =  self.direction
    
            if _return_code is not None:
                self.timer_action += self.action_waittime

        return _return_code

    #ユーザ専用カウンタ減算
    def user_timer_decrement(self):
        self.common_timer_decrement()
        self.timer_selectmagic = max(0, self.timer_selectmagic-1)
        self.timer_selectitem = max(0, self.timer_selectitem-1)
        self.timer_food = max(0, self.timer_food-1)
        self.timer_ontrap = max(0, self.timer_ontrap-1)
        #アイテムタイマー減算
        for i,t in enumerate(self.timer_item):
            self.timer_item[i] = max(0, t-1)
        #デバフタイマー２
        if px.frame_count%G_.GAME_FPS == G_.GAME_FPS//2:
            if self.equip_magic_index == 0:
                self.decrement_fire(True)
            if self.equip_magic_index == 1:
                self.decrement_ice(True)
            if self.equip_magic_index == 2:
                self.decrement_wind()

    def move_address(self, scene:int=0, move_length:int=1):
        self.image_position = 1 - self.image_position
        if scene == 30:
            layer = 0
            checklist = [4]
            checktype = True
        elif scene == 40:
            layer = 6
            checklist = [(19,30),(20,30),
                         (19,31),(20,31)]
            checktype = None
        elif scene in (70,75):
            layer = 1
            checklist = [(8,1)]
            checktype = None

        for _ in range(move_length):
            destination = [self.address[0] + (G_.CHARA_DIR[self.direction][0]),
                           self.address[1] + (G_.CHARA_DIR[self.direction][1])]
            if comf.check_hit_tile(self, layer, checklist, checktype):
                px.play(3,G_.SNDEFX["don"], resume=True)
                break
            self.address = destination
        return

    def update(self):
        self.image_source[0] = self.direction*32 + 16*self.image_position

        #食料消費と回復（フィールドとダンジョンのみ）
        if self.user_scene in (30,40) and self.timer_food <= 0:
            bonus = 3 if self.is_clear else 1
            self.timer_food = 8 * G_.GAME_FPS * bonus
            item.func_effect_item31(self)

        #攻撃モーション
        if self.weapon.is_attacking:
            self.weapon.update()

        #詠唱呪文のインスタンス削除はインスタンス外部から実行
        if isinstance(self.magic.spell, Spell):
            self.magic.spell.update()
            if self.magic.spell.timer_remain == 0:
                self.magic.spell = None

        #タイマーアイテム効果消失
        if self.is_str_up and self.timer_item[4] == 0:
            self.is_str_up = False
            self.calc_attack()
        if self.is_int_up and self.timer_item[5] == 0:
            self.is_int_up = False
            self.calc_magic_power()
        if self.is_agi_up and self.timer_item[6] == 0:
            self.is_agi_up = False
            self.calc_movespeed()
            self.action_waittime = self.set_action_waittime()
        if self.is_regist_up and self.timer_item[7] == 0:
            self.is_regist_up = False

    def draw(self):
        if isinstance(self.magic.spell, Spell):
            self.magic.spell.draw(self.user_scene)

        if self.is_dead:
            return
        if self.is_use_item:
            px.play(3, G_.SNDEFX["item"], resume=True)
            px.cls(7)
            self.is_use_item = False

        #ユーザキャラ
        if self.timer_item[3] > 0:
            imagesource_type = item.func_effect_item13(self)
        elif self.timer_item[2] > 0:
            imagesource_type = item.func_effect_item12(self)
        else:
            imagesource_type = self.image_source[1]

        x,y = self.address[0]-8, self.address[1]-8
        if self.timer_item[8] > 0:
            v = (px.frame_count%G_.GAME_FPS)/G_.GAME_FPS
            y += -2.0+8.0*v if v < 0.5 else 2.0-8.0*(v-0.5)
        if self.weapon.is_attacking or self.timer_spellcast > 0:
            px.blt(x, y, G_.IMGIDX["CHAR"],
                128+self.direction*16,imagesource_type, self.image_source[2],self.image_source[3],
                colkey=3)
        else:
            px.blt(x, y, G_.IMGIDX["CHAR"],
                self.image_source[0],imagesource_type, self.image_source[2],self.image_source[3],
                colkey=3)
        self.draw_damage_effect()

        if self.weapon.is_attacking:
            if self.weapon.motion_counter == 1:
                px.play(3, G_.SNDEFX["attack"], resume=True)
            self.weapon.func_attackmotion(self.weapon, *self.address, self.direction)

        self.draw_cast_effect()


class Spell(Character):
    def __init__(self, magic, address, direction, image_source, intelligence, wisdom):
        self.magic = magic
        self.casttime = 0
        self.spell_type = self.magic.item_type
        super().__init__(self.spell_type, [int(address[0]),int(address[1])], image_source, "","",0,0,0,intelligence,wisdom,0)
        match self.spell_type:
            case 12:
                self.timer_remain = intelligence // 6
                self.movespeed = 1.6
                self.casttime = int(max(0, G_.GAME_FPS*1.34 - self.wisdom/5))
            case 13:
                self.timer_remain = intelligence // 12
                self.movespeed = 0
                self.casttime = int(max(0, G_.GAME_FPS*1.74 - self.wisdom/5))
            case 14:
                self.timer_remain = intelligence // 16
                self.movespeed = 0
                self.casttime = int(max(0, G_.GAME_FPS*2.14 - self.wisdom/5))
            case 15:
                self.timer_remain = intelligence // 6
                self.movespeed = 1
                self.casttime = int(max(0, G_.GAME_FPS*1.5 - self.wisdom/5))
        self.timer_remain += G_.GAME_FPS
        self.direction = direction
        self.address[0] += G_.CHARA_DIR[self.direction][0]*2
        self.address[1] += G_.CHARA_DIR[self.direction][1]*2
        px.play(3, G_.SNDEFX["spell"], resume=True)

    def update(self):
        if self.spell_type in (12,15): #火術と土術は投射体あり
            self.move_address()

        #持続時間
        self.timer_remain -= 1

    def draw(self, scene=0):
        if scene not in (30,40,70,75):
            return
        if self.spell_type in (12,15): #火術と土術は投射体あり
            px.blt(self.address[0]-self.image_source[2]//2, self.address[1]-self.image_source[3]//2,
                   G_.IMGIDX["CHIP"], *self.image_source, colkey=0, rotate=px.frame_count%180)
        elif self.spell_type == 13:
            for i, rect in enumerate(self.magic.func_attackrange(*self.address, self.direction)):
                if px.frame_count%3 != i:
                    continue
                px.blt(rect[0]-(rect[2]//2),rect[1]-(rect[3]//2), G_.IMGIDX["CHIP"], 48,88,rect[2],rect[3], colkey=0)

        elif self.spell_type == 14:
            areawidth = G_.P_MAIN_WND[2]
            if scene in (70,75):
                areawidth += G_.P_SUB_WND[2]
            for _ in range(5):
                px.blt(px.rndi(0,areawidth), px.rndi(0,G_.P_MAIN_WND[3]),
                       G_.IMGIDX["CHIP"], 72,232, 8,8, colkey=0)
                px.blt(px.rndf(areawidth*0.33,areawidth*0.66),
                       px.rndf(G_.P_MAIN_WND[3]*0.33,G_.P_MAIN_WND[3]*0.66),
                       G_.IMGIDX["CHIP"], 72,232, -8,8, colkey=0)
                px.blt(px.rndf(areawidth*0.475,areawidth*0.525),
                       px.rndf(G_.P_MAIN_WND[3]*0.475,G_.P_MAIN_WND[3]*0.525),
                       G_.IMGIDX["CHIP"], 72,232, 8,-8, colkey=0)