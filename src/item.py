import pyxel as px
import const as G_

#ID:(type,Name,price,value)
ITEMS={
"0":(17,"金床",0,1), #STRが10増える
"1":(17,"手袋",0,1), #DEXが10増える
"2":(17,"粉薬",0,1), #AGLが10増える
"3":(17,"書物",0,1), #INTが10増える
"4":(17,"十字架",0,1), #WISが10増える
"5":(17,"手鏡",0,1), #MGRが10増える
"6":(17,"宝珠",0,1), #HPが5%増える
"10":(18,"松明",0,1), #暗い場所を照らす
"11":(18,"砂時計",0,1), #モンスターの完全停止
"12":(18,"隠れ蓑",0,1), #モンスターから近付かれない、攻撃されない（魔法ふくめ）
"13":(18,"着ぐるみ",0,1), #モンスターから物理攻撃されない、物理攻撃できない
"14":(18,"紅玉石",0,1), #STRが倍になる
"15":(18,"飲み薬",0,1), #INTが倍になる
"16":(18,"天馬の羽",0,1), #AGLが倍になる
"17":(18,"護り札",0,1), #魔法被ダメージが半分になる
"18":(18,"翼の長靴",0,1), #デバフ床の効果を受けなくなる
"20":(19,"鍵束",0,1), #マップ内の扉を全て開く
"21":(19,"鶴嘴",0,1), #ヒビの入った岩を壊せる
"22":(19,"傷薬",0,1), #HPを回復する（熟練100＝50％、WIS200＝50％）＝MAXHP*(熟練//2+WIS//4)
"30":(17,"お金",1,1), #おかねが1ふえる
"31":(20,"食料",1,10), #FOODが10ふえる
"32":(20,"鍵",100,1), #扉を開く
"33":(21,"霊薬",0,1), #一回復活
}

WEAPONS={
"40":(0,"樫の杖",0,1),
"41":(0,"樫の堅杖",1000,4),
"42":(0,"紫檀の杖",3200,9),
"43":(0,"紫檀の錫杖",7500,24),
"44":(0,"黒曜の杖",15800,54),
"45":(0,"黒曜の棒杖",33600,110),
"46":(0,"氷晶の杖",72000,235),
"47":(0,"氷晶の魔杖",148000,490),
"48":(0,"鳳珠の杖",320000,990),
"49":(0,"カドゥケウス",0,1),

"50":(1,"短刀",0,7),
"51":(1,"良い短刀",1000,12),
"52":(1,"短剣",3200,23),
"53":(1,"鋭い短剣",7500,47),
"54":(1,"長剣",15800,99),
"55":(1,"厚い長剣",33600,205),
"56":(1,"段平",72000,425),
"57":(1,"長い段平",148000,890),
"58":(1,"両手剣",320000,1780),
"59":(1,"カラドボルグ",0,712),

"60":(2,"短槍",0,5),
"61":(2,"上等な短槍",1000,8),
"62":(2,"槍",3200,15),
"63":(2,"上質な槍",7500,31),
"64":(2,"長槍",15800,69),
"65":(2,"良質な長槍",33600,175),
"66":(2,"騎兵槍",72000,365),
"67":(2,"豪華な騎兵槍",148000,790),
"68":(2,"斧槍",320000,1580),
"69":(2,"ゲイボルグ",0,632),

"70":(3,"手斧",0,9),
"71":(3,"薪割斧",1000,16),
"72":(3,"伐採斧",3200,31),
"73":(3,"鉞",7500,63),
"74":(3,"大工斧",15800,119),
"75":(3,"楔斧",33600,240),
"76":(3,"戦斧",72000,525),
"77":(3,"重戦斧",148000,1040),
"78":(3,"両刃斧",320000,1980),
"79":(3,"ミョルニル",0,792),
}

ARMORS={
"100":(4,"短衣",0,0.1),
"101":(4,"短衣改",400,1),
"102":(4,"外套",1100,7),
"103":(4,"外套改",2850,28),
"104":(4,"祭服",6300,52),
"105":(4,"祭服改",13700,160),
"106":(4,"長衣",29800,270),
"107":(4,"長衣改",62500,420),
"108":(4,"束帯",128000,840),
"109":(4,"パランギーナ",0,400),

"110":(5,"なめし革鎧",0,1),
"111":(5,"なめし革鎧改",800,3),
"112":(5,"重ね革鎧",2200,16),
"113":(5,"重ね革鎧改",5700,59),
"114":(5,"鋲打ち革鎧",12600,104),
"115":(5,"鋲打ち革鎧改",27400,285),
"116":(5,"輪付き革鎧",59600,480),
"117":(5,"輪付き革鎧改",125000,790),
"118":(5,"鱗片鎧",256000,1610),
"119":(5,"カリュドン",0,800),

"120":(6,"鎖帷子",0,3),
"121":(6,"鎖帷子改",800,6),
"122":(6,"長鎖帷子",2200,21),
"123":(6,"長鎖帷子改",5700,74),
"124":(6,"板片鎧",12600,129),
"125":(6,"板片鎧改",27400,365),
"126":(6,"板巻鎧",59600,630),
"127":(6,"板巻鎧改",125000,960),
"128":(6,"真銀帷子",256000,1870),
"129":(6,"ウィガール",0,900),

"130":(7,"鉄の胸甲",0,5),
"131":(7,"鉄の胸甲改",800,10),
"132":(7,"小札鎧",2200,27),
"133":(7,"小札鎧改",5700,93),
"134":(7,"板金鎧",12600,159),
"135":(7,"板金鎧改",27400,470),
"136":(7,"甲冑",59600,790),
"137":(7,"重甲冑",125000,1250),
"138":(7,"溝付甲冑",256000,2130),
"139":(7,"イージス",0,1000),
}

SHIELDS={
"140":(8,"バングル",0,3),
"141":(8,"腕輪＋１",600,5),
"142":(8,"腕輪＋２",1250,14),
"143":(8,"腕輪＋３",2600,23),
"144":(8,"腕輪＋４",5500,52),
"145":(8,"腕輪＋５",11800,90),
"146":(8,"腕輪＋６",24000,240),
"147":(8,"腕輪＋７",52000,400),
"148":(8,"腕輪＋８",108000,800),
"149":(8,"腕輪＋９",0,1200),

"150":(9,"ターゲット",0,2),
"151":(9,"小円盾＋１",1200,3),
"152":(9,"小円盾＋２",2500,9),
"153":(9,"小円盾＋３",5200,16),
"154":(9,"小円盾＋４",11000,39),
"155":(9,"小円盾＋５",23600,70),
"156":(9,"小円盾＋６",48000,180),
"157":(9,"小円盾＋７",104000,300),
"158":(9,"小円盾＋８",216000,600),
"159":(9,"小円盾＋９",0,900),

"160":(10,"カイト",0,1),
"161":(10,"中凧盾＋１",1200,2),
"162":(10,"中凧盾＋２",2500,6),
"163":(10,"中凧盾＋３",5200,11),
"164":(10,"中凧盾＋４",11000,26),
"165":(10,"中凧盾＋５",23600,50),
"166":(10,"中凧盾＋６",48000,120),
"167":(10,"中凧盾＋７",104000,235),
"168":(10,"中凧盾＋８",216000,470),
"169":(10,"中凧盾＋９",0,700),

"170":(11,"タワー",0,0.5),
"171":(11,"巨塔盾＋１",1200,1),
"172":(11,"巨塔盾＋２",2500,3),
"173":(11,"巨塔盾＋３",5200,5),
"174":(11,"巨塔盾＋４",11000,12),
"175":(11,"巨塔盾＋５",23600,35),
"176":(11,"巨塔盾＋６",48000,60),
"177":(11,"巨塔盾＋７",104000,170),
"178":(11,"巨塔盾＋８",216000,340),
"179":(11,"巨塔盾＋９",0,500),
}

MAGICS={
"200":(12,"ファイア",200,7),
"201":(12,"フレイム",3000,60),
"202":(12,"バーン",26800,320),
"203":(12,"ブラスト",108000,950),

"210":(13,"アイス",300,4),
"211":(13,"フロスト",4500,40),
"212":(13,"フリーズ",39800,180),
"213":(13,"ブリザード",162000,540),

"220":(14,"ウインド",500,2),
"221":(14,"ストーム",7500,20),
"222":(14,"サイクロン",66600,90),
"223":(14,"テンペスト",270000,270),

"230":(15,"ストーン",400,11),
"231":(15,"ロック",6000,80),
"232":(15,"ボルダー",54300,450),
"233":(15,"メテオ",216000,1350),
}


#アイテムIDから辞書情報を取得
def get_item_info(item_id:int):
    _dict = dict(**ITEMS,**WEAPONS,**ARMORS,**SHIELDS,**MAGICS)
    return _dict[str(item_id)]


#アイテム使用（取得即時効果の場合もここ）
def use_item(item_id:int, user):
    item_info = get_item_info(item_id)
    for i,item in enumerate(user.inventory):
        if item[0] == item_id:
            break
    inventory_index = i
    timer_index = None

    if item_info[0] == 17:
        match item_id:
            case 0: #金床
                user.strength = min(255, user.strength+10)
                user.calc_attack()
            case 1: #手袋
                user.dexterity = min(255, user.dexterity+10)
                user.attack_waittime = user.set_attack_waittime()
            case 2: #粉薬
                user.agility = min(255, user.agility+10)
                user.action_waittime = user.set_action_waittime()
            case 3: #書物
                user.intelligence = min(255, user.intelligence+10)
                user.calc_magic_power()
            case 4: #十字架
                user.wisdom = min(255, user.wisdom+10)
            case 5: #手鏡
                user.magicregistance = min(255, user.magicregistance+10)
                user.calc_magic_defend()
            case 6: #宝珠
                user.maxhp *= 1.05
        return
    else:
        if user.inventory[inventory_index][1] <= 0:
            px.play(3, G_.SNDEFX["miss"], resume=True)
            return 0
        else:
            if item_info[0] == 18:
                user.inventory[inventory_index][1] -= 1
                match item_id:
                    case 10: #松明
                        timer_index = 0
                    case 11: #砂時計
                        timer_index = 1
                    case 12: #隠れ蓑
                        timer_index = 2
                    case 13: #着ぐるみ
                        timer_index = 3
                    case 14: #紅玉石
                        user.is_str_up = True
                        user.calc_attack()
                        timer_index = 4
                    case 15: #飲み薬
                        user.is_int_up = True
                        user.calc_magic_power()
                        timer_index = 5
                    case 16: #天馬の羽
                        user.is_agi_up = True
                        user.calc_movespeed()
                        user.action_waittime = user.set_action_waittime()
                        timer_index = 6
                    case 17: #護り札
                        user.is_regist_up = True
                        # user.calc_magic_defend()
                        timer_index = 7
                    case 18: #翼の長靴
                        timer_index = 8
                user.timer_item[timer_index] = min(255 * G_.GAME_FPS,
                                                   user.timer_item[timer_index]
                                                   + int((user.wisdom / 10
                                                          + user.inventory[inventory_index][2]
                                                          ) * G_.GAME_FPS
                                                        )
                                                   )
            elif item_info[0] == 19:
                match item_id:
                    case 20: #鍵束
                        if user.user_scene == 40:
                            user.is_use_item20 = True
                        else:
                            px.play(3, G_.SNDEFX["miss"], resume=True)
                            return 1
                    case 21: #鶴嘴
                        if user.user_scene == 30:
                            user.is_use_item21 = True
                        else:
                            px.play(3, G_.SNDEFX["miss"], resume=True)
                            return 1
                    case 22: #傷薬
                        if user.hp == user.maxhp:
                            px.play(3, G_.SNDEFX["miss"], resume=True)
                            return 1
                        user.inventory[inventory_index][1] -= 1
                        user.hp = min(user.maxhp,
                                      user.hp
                                      + int(
                                          (user.maxhp * (
                                              (min(50, user.inventory[inventory_index][2]/2)
                                               +min(50, user.wisdom/4))
                                               /100)
                                            )))
        #以下は備忘録
        # match item_id:
        # case 31: 食料消費はカウンター処理で直接呼出し func_effect_item31
        #     pass #食料
        # case 32: 鍵消費はダンジョン扉接触イベントで直接呼出し func_effect_item32
        #     pass #鍵
        # case 33: 霊薬消費は死亡時処理で直接呼出し func_effect_item33
        #     pass #霊薬
    user.grow_item(inventory_index)
    user.is_use_item = True


#アイテム取得
def pick_item(item_id:int, num_item:int, user):
    item_info = get_item_info(item_id)
    if item_info[0] in (0,1,2,3,4,5,6,7,8,9,10,11):
        user.equip_item(item_id)
    elif item_info[0] in (12,13,14,15):
        user.add_spellbook(item_id)
        if item_info[0] == user.equip_magic_index+12:
            user.equip_item(item_id)
    elif item_id == 30: #item_info[0] == 17に該当するが個別で獲得処理
        user.gold += num_item
    elif item_id == 31:
        user.food += num_item
    elif  item_id == 32:
        user.key += num_item
    elif  item_id == 33:
        user.elixer += num_item
    elif item_info[0] in (18,19):
        is_add = False
        for i, item in enumerate(user.inventory):
            if item[0] == item_id:
                user.inventory[i][1] = min(99, user.inventory[i][1] + num_item)
                is_add = True
                break
        if is_add is False:
            user.inventory.append([item_id, num_item, 5])
            user.inventory.sort(key = lambda row: row[0])
    elif item_info[0] == 17:
        use_item(item_id, user)


#ボス召喚アイテム
class BossSummonOrb:
    def __init__(self, map_address_list, virtual_map):
        self.map_address = list(map_address_list[px.rndi(0,len(map_address_list)-1)])
        self.is_placed = False

        tmp_x, tmp_y = G_.P_MAIN_WND[2]//2, G_.P_MAIN_WND[3]//2
        while virtual_map[self.map_address[1]*G_.P_MAIN_WND[3]//8+tmp_y//8]\
                         [self.map_address[0]*G_.P_MAIN_WND[2]//8+tmp_x//8][0] == 4:
            tmp_x = px.rndi(0,G_.P_MAIN_WND[2])
            tmp_y = px.rndi(0,G_.P_MAIN_WND[3])
        self.address = (tmp_x, tmp_y)

    def update(self):
        #接触チェック
        pass
    
    def draw(self, now_view):
        #表示
        if self.is_placed and self.map_address == now_view:
            px.blt(self.address[0]-8, self.address[1]-8, G_.IMGIDX["CHIP"],
                   64,208,16,16, colkey=0)


#モンスタードロップ宝箱
class TreasureBox:
    def __init__(self, map_address, address, item_id, num_item):
        self.map_address = map_address
        self.address = address
        self.item_id = item_id
        self.num_item = num_item
        self.rate_open = 0
        self.is_placed = False
        self.is_opened = False
    
    def challenge_open(self, stage_id, dexterity):
        px.play(3,G_.SNDEFX["unlock"], resume=True)
        DifficultClass = (stage_id+1)*stage_id
        if px.rndf(0, 20 + ((DifficultClass) * 9)) <= dexterity:
            self.rate_open += dexterity/(DifficultClass + 2)
        if self.rate_open >= 100:
            self.is_opened = True
            px.play(3,G_.SNDEFX["open"], resume=True)
            return True
        return False

    def draw(self):
        if self.is_placed and self.is_opened is False:
            px.blt(self.address[0]-8,self.address[1]-8, 0, 96+16*(self.rate_open//45),224, 16,16, colkey=0)


class Item:
    def __init__(self, item_id:int):
        self.id = item_id
        self.item_type, self.name, self.price, self.value = get_item_info(item_id)
        
    def get_info(self, item_type_id):
        raise NotImplementedError


class Armor(Item):
    def __init__(self, item_id):
        super().__init__(item_id)
        self.movespeed, self.rate_magicpower =\
            self.get_info(self.item_type)
    
    def get_info(self, item_type_id):
        match item_type_id:
            case 4:
                return 6, 100
            case 5:
                return 5, 90
            case 6:
                return 4, 70
            case 7:
                return 2, 50
            case _:
                raise IndexError


class Shield(Item):
    def __init__(self, item_id):
        super().__init__(item_id)
        self.rate_attackspeed, self.rate_knockback =\
            self.get_info(self.item_type)
    
    def get_info(self, item_type_id):
        match item_type_id:
            case 8:
                return 100, 100
            case 9:
                return 85, 66
            case 10:
                return 70, 33
            case 11:
                return 55, 1
            case _:
                raise IndexError


class Weapon(Item):
    def __init__(self, item_id):
        super().__init__(item_id)
        self.attack_speed, self.knockback_length, self.func_attackrange, self.func_attackmotion =\
            self.get_info(self.item_type)
        self.motion_counter = 0
        self.motion_frames = -1
        self.is_attacking = False

    def update(self):
        if self.is_attacking:
            self.motion_counter += 1
            if self.motion_counter > self.motion_frames:
                self.is_attacking = False
                self.motion_counter = 0

    def get_info(self, item_type_id):
        match item_type_id:
            case 0:
                return 0.1, 0.4, range_type_0, motion_type_0
            case 1:
                return 0.46, 1.33, range_type_1, motion_type_1
            case 2:
                return 0.67, 0.75, range_type_2, motion_type_2
            case 3:
                return 1.78, 2.0, range_type_3, motion_type_3
            case _:
                raise IndexError


def range_type_0(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]*12
    dy1 = G_.CHARA_DIR[direction][1]*12
    w1 = 8
    h1 = 8
    return [[x+dx1,y+dy1, w1,h1]]


def motion_type_0(cls, x, y, direction):
    self = cls
    u, v = 0, 112
    w, h = 8, 16

    # 攻撃角度 = 45 × (現在フレーム / 最大フレーム)
    swing_angle = 45 * self.motion_counter // self.motion_frames

    if direction == 0:  # 下向き：左→下→右（270〜450）
        origin_x = x
        origin_y = y + 7
        base_angle = -130
        rotate_angle = base_angle - swing_angle
    elif direction == 1:  # 左向き：上→左→下（0〜180）
        origin_x = x - 7
        origin_y = y
        base_angle = -40
        rotate_angle = base_angle - swing_angle
    elif direction == 2:  # 右向き：下→右→上（180〜360）
        origin_x = x + 7
        origin_y = y
        base_angle = 40
        rotate_angle = base_angle + swing_angle
    elif direction == 3:  # 上向き：右→上→左（90〜270）
        origin_x = x
        origin_y = y - 7
        base_angle = -40
        rotate_angle = base_angle + swing_angle

    draw_x = origin_x - w // 2
    draw_y = origin_y - h // 2

    px.blt(draw_x, draw_y, G_.IMGIDX["CHIP"], u, v, w, h, colkey=15, rotate=rotate_angle)


def range_type_1(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]*10
    dy1 = G_.CHARA_DIR[direction][1]*10
    w1 = 36 if dx1 == 0 else 12
    h1 = 36 if dy1 == 0 else 12

    dx2 = G_.CHARA_DIR[direction][0]*20
    dy2 = G_.CHARA_DIR[direction][1]*20
    w2 = 16 if dx2 == 0 else 8
    h2 = 16 if dy2 == 0 else 8

    return [[x+dx1,y+dy1, w1,h1],[x+dx2,y+dy2, w2,h2]]


def motion_type_1(cls, x, y, direction):
    self = cls
    u, v = 8, 112
    w, h = 8, 32

    # 攻撃角度 = 180 × (現在フレーム / 最大フレーム)
    swing_angle = 180 * self.motion_counter // self.motion_frames

    if direction == 0:  # 下向き：左→下→右（270〜450）
        origin_x = x
        origin_y = y + 5
        base_angle = -90
        rotate_angle = base_angle - swing_angle
    elif direction == 1:  # 左向き：上→左→下（0〜180）
        origin_x = x - 5
        origin_y = y
        base_angle = 0
        rotate_angle = base_angle - swing_angle
    elif direction == 2:  # 右向き：下→右→上（180〜360）
        origin_x = x + 5
        origin_y = y
        base_angle = 10
        rotate_angle = base_angle + swing_angle
    elif direction == 3:  # 上向き：右→上→左（90〜270）
        origin_x = x
        origin_y = y - 5
        base_angle = -90
        rotate_angle = base_angle + swing_angle

    draw_x = origin_x - w // 2
    draw_y = origin_y - h // 2

    px.blt(draw_x, draw_y, G_.IMGIDX["CHIP"], u, v, w, h, colkey=15, rotate=rotate_angle)


def range_type_2(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]*34
    dy1 = G_.CHARA_DIR[direction][1]*34
    w1 = 8 if dx1 == 0 else 52
    h1 = 8 if dy1 == 0 else 52

    return [[x+dx1,y+dy1, w1,h1]]


def motion_type_2(cls, x, y, direction):
    self = cls
    u, v = 16, 112
    w, h = 8, 64

    # 攻撃突き出し距離
    if self.motion_counter <= self.motion_frames//3:
        thrust = int(50 * self.motion_counter / (self.motion_frames // 3))
    else:
        thrust = int(50 * (self.motion_frames - self.motion_counter) / (self.motion_frames * 2 // 3))   

    if direction == 0:  # 下向き：左→下→右（270〜450）
        draw_x = x - w // 2 - 5
        draw_y = y + 10 - h + thrust
        rotate_angle = 180
    elif direction == 1:  # 左向き：上→左→下（0〜180）
        draw_x = x - 8 - thrust + 24
        draw_y = y - h // 2 + 2
        rotate_angle = -90
    elif direction == 2:  # 右向き：下→右→上（180〜360）
        draw_x = x + 8 - w + thrust - 24
        draw_y = y - h // 2 + 2
        rotate_angle = 90
    elif direction == 3:  # 上向き：右→上→左（90〜270）
        draw_x = x - w // 2 + 5
        draw_y = y - 10 - thrust
        rotate_angle = 0

    px.blt(draw_x, draw_y, G_.IMGIDX["CHIP"], u, v, w, h, colkey=15, rotate=rotate_angle)


def range_type_3(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]*10
    dy1 = G_.CHARA_DIR[direction][1]*10
    w1 = 52 if dx1 == 0 else 20
    h1 = 52 if dy1 == 0 else 20

    dx2 = G_.CHARA_DIR[direction][0]*24
    dy2 = G_.CHARA_DIR[direction][1]*24
    w2 = 32 if dx2 == 0 else 8
    h2 = 32 if dy2 == 0 else 8

    dx3 = G_.CHARA_DIR[direction][0]*30
    dy3 = G_.CHARA_DIR[direction][1]*30
    w3 = 16 if dx2 == 0 else 4
    h3 = 16 if dy2 == 0 else 4

    return [[x+dx1,y+dy1, w1,h1],[x+dx2,y+dy2, w2,h2],[x+dx3,y+dy3, w3,h3]]


def motion_type_3(cls, x, y, direction):
    self = cls
    u, v = 24, 112
    w, h = 8, 48

    # 攻撃角度 = 180 × (現在フレーム*2 / 最大フレーム) 振り終わりで硬直
    swing_angle = min(180, 180 * self.motion_counter*2 // self.motion_frames)

    if direction == 0:  # 下向き：左→下→右（270〜450）
        origin_x = x
        origin_y = y + 5
        base_angle = 100
        vector = -1
        rotate_angle = base_angle + swing_angle
    elif direction == 1:  # 左向き：上→左→下（0〜180）
        origin_x = x - 5
        origin_y = y
        base_angle = 10
        vector = -1
        rotate_angle = base_angle + swing_angle
    elif direction == 2:  # 右向き：下→右→上（180〜360）
        origin_x = x + 5
        origin_y = y
        base_angle = 10
        vector = 1
        rotate_angle = base_angle + swing_angle
    elif direction == 3:  # 上向き：右→上→左（90〜270）
        origin_x = x
        origin_y = y - 5
        base_angle = -80
        vector = 1
        rotate_angle = base_angle + swing_angle

    draw_x = origin_x - w // 2
    draw_y = origin_y - h // 2

    px.blt(draw_x, draw_y, G_.IMGIDX["CHIP"], u, v, w*vector, h, colkey=15, rotate=rotate_angle)


class Magic(Item):
    def __init__(self, item_id):
        super().__init__(item_id)
        self.rate_effect, self.func_effect, self.func_attackrange =\
            self.get_info(self.item_type)
        self.spell = None
    
    def get_info(self, item_type_id):
        match item_type_id:
            case 12:
                return 25, effect_type_12, range_type_12
            case 13:
                return 75, effect_type_13, range_type_13
            case 14:
                return 50, effect_type_14, range_type_14
            case 15:
                return 100, effect_type_15, range_type_15
            case _:
                raise IndexError


def range_type_12(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]
    dy1 = G_.CHARA_DIR[direction][1]
    w1 = 24
    h1 = 24

    return [[x+dx1,y+dy1, w1,h1]]


def range_type_13(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]*12
    dy1 = G_.CHARA_DIR[direction][1]*12
    w1 = 32 if dx1 == 0 else 8
    h1 = 32 if dy1 == 0 else 8

    dx2 = G_.CHARA_DIR[direction][0]*20
    dy2 = G_.CHARA_DIR[direction][1]*20
    w2 = 48 if dx2 == 0 else 8
    h2 = 48 if dy2 == 0 else 8

    dx3 = G_.CHARA_DIR[direction][0]*36
    dy3 = G_.CHARA_DIR[direction][1]*36
    w3 = 64 if dx2 == 0 else 24
    h3 = 64 if dy2 == 0 else 24

    return [[x+dx1,y+dy1, w1,h1],[x+dx2,y+dy2, w2,h2],[x+dx3,y+dy3, w3,h3]]


def range_type_14(x, y, direction):
    return [[px.width//2,px.height//2, px.width,px.height]]


def range_type_15(x, y, direction):
    dx1 = G_.CHARA_DIR[direction][0]
    dy1 = G_.CHARA_DIR[direction][1]
    w1 = 8
    h1 = 8
    return [[x+dx1,y+dy1, w1,h1]]


#デバフ効果
def effect_type_12(target):
    target.hp = int(target.hp - target.hp*0.02)


def effect_type_13(target):
    try:
        target.movespeed = target.movespeed //2
    except AttributeError:
        target.movespeed /= 2


def effect_type_14(target):
    target.attack_waittime *= 1.75


def effect_type_15():
    #ノックバック
    pass


#アイテム効果
def func_effect_item10(user): #松明
    if user.timer_item[0] <= 0:
        px.rect(*G_.P_MAIN_WND, 0)
    elif user.timer_item[0] <= 5*G_.GAME_FPS:
        if px.frame_count%(G_.GAME_FPS*2)//2 in (0,1,2,3):
            px.rect(*G_.P_MAIN_WND, 0)


#描画処理のみ。モンスター動作変更系はMonsterクラスの処理内で定義
def func_effect_item11(user): #砂時計 (効果の描画のみ)
    if (user.timer_item[1] > G_.GAME_FPS*4 and px.frame_count//(G_.GAME_FPS*2)%2 == 0) or\
       (G_.GAME_FPS*4 > user.timer_item[1] > 0 and px.frame_count%16 in (0,1,2,3,4)):
        px.rectb(1,1, G_.P_MAIN_WND[2]-2,G_.P_MAIN_WND[2]-2, 6)
        px.rectb(3,3, G_.P_MAIN_WND[2]-6,G_.P_MAIN_WND[2]-6, 12)


def func_effect_item12(user): #隠れ蓑
    imagesource_type = 112
    if user.timer_item[2] <= 5*G_.GAME_FPS:
        if px.frame_count%16 in (0,1,2,3):
            imagesource_type = user.image_source[1]
    return imagesource_type


def func_effect_item13(user): #着ぐるみ
    imagesource_type = 96
    if user.timer_item[3] <= 5*G_.GAME_FPS:
        if px.frame_count%16 in (0,1,2,3):
            imagesource_type = user.image_source[1]
    return imagesource_type
#パラメータ向上関連はコード中でフラグON時２倍時の処理を実行
# def func_effect_item14(user): #宝石 
# def func_effect_item15(user): #飲み薬
# def func_effect_item16(user): #風車
# def func_effect_item17(user): #お守り
#item.use_itemの中で直接記述
# def func_effect_item20(): #鍵束
# def func_effect_item21(): #鶴嘴
# def func_effect_item22(): #傷薬 
def func_effect_item31(user): #食料
    comsume = user.maxhp // 1000
    user.food = max(0, user.food - comsume)
    if user.food > 0:
        user.hp = min(user.maxhp, user.hp + comsume)
    else:
        user.hp -= user.maxhp // 100 
# def func_effect_item32(user): #鍵 #ダンジョン扉接触処理にて記述
# def func_effect_item33(user): #霊薬 #死亡時イベントとして実装