import pyxel as px
import const as G_
import common_func as comf, drawevent as evt
import character, stage, sound, message, item, menu, monster, command


class App():
    #アプリケーション固有情報初期化
    def init_app(self):
        px.init(G_.P_MAIN_WND[2]+G_.P_SUB_WND[2], G_.P_MAIN_WND[3],
                title="Old ARPG like", fps=G_.GAME_FPS, quit_key=99999)
        G_.JP_FONT = px.Font(G_.FONTFILE)
        px.load(G_.ASSET_FILE, excl_images=True, excl_tilemaps=True)
        px.images[0].load(0, 0, "assets/image/0.chip.bmp")
        px.images[1].load(0, 0, "assets/image/1.chara.bmp")
        self.message_manager = message.MessageManager()
        self.build_window_frame()
        self.encyclopedia = Encyclopedia()
        #システムデータ情報設定
        self.is_clear_user = False
        cmd = command.CommandSystemData()
        systemdata = cmd.load()
        self.is_clear = systemdata["clear"]
        self.is_alert_key = systemdata["alert_key"]
        self.is_alert_LvUp = systemdata["alert_LvUp"]
        self.is_alert_gold = systemdata["alert_gold"]
        self.is_alert_group = systemdata["alert_group"]
        self.is_alert_map = systemdata["alert_map"]
        self.is_alert_torch = systemdata["alert_torch"]
        self.is_alert_zone = systemdata["alert_zone"]
        self.is_alert_mattock = systemdata["alert_mattock"]

    #ゲーム実行状況リセット
    def reset_parameter(self):
        self.message_window = menu.Window(16,px.height//2-12, px.width-(16*2),8*6, 1,150)
        self.message_manager.message_list = []
        self.background_drawer = None
        self.is_menu = False
        self.is_gameover = False
        self.counter = 0
        self.minimap_spot = []
        self.eventstep = 0
        self.is_nextstage = False
        self.is_kill = False
    
    #熟練度アップ情報更新
    def update_levelup_info(self):
        self.now_user_exp = {
            "weapon":self.user.exp_weapon,
            "armor":self.user.exp_armor,
            "shield":self.user.exp_shield,
            "fire":self.user.exp_magic[0],
            "ice":self.user.exp_magic[1],
            "wind":self.user.exp_magic[2],
            "earth":self.user.exp_magic[3],
        }

    #熟練度アップ情報生成
    def reset_levelup_info(self):
        self.update_levelup_info()
        self.prev_user_exp = self.now_user_exp.copy()
        self.levelup_effects = []

    #熟練度アップチェック・表示オブジェクト生成
    def check_levelup(self):
        for i, (key, val) in enumerate(self.now_user_exp.items()):
            if int(val // 10) > int(self.prev_user_exp[key] // 10):
                self.levelup_effects.append({
                    "x": self.user.address[0]-12+i*3,
                    "y": self.user.address[1]-7-i,
                    "color": G_.LEVELUP_COLOR[0][i],
                    "type": G_.LEVELUP_COLOR[1][i],
                    "frame": 0,
                })
            self.prev_user_exp[key] = val

    #サブウインドウフレーム用タイルマップ生成
    def build_window_frame(self):
        layer = 7
        #ステータスウインドウ
        size = [G_.P_STAT_WND[2]//8, G_.P_STAT_WND[3]//8]
        comf.fill_tilemap(layer, (31,31),size[0]-1,size[1]-1,1,1)
        i = 0
        for y in range(size[1]):
            for x in range(size[0]):
                if y == 0 or y == size[1]-1:
                    px.tilemaps[layer].pset(x, y, (8+i,0))
                    i = 1 - i
                elif x == 0 or x == size[0]-1:
                    px.tilemaps[layer].pset(x, y, (8+i,0))
            i = 1 - i
        #メッセージウインドウ
        size2 = [G_.P_MESG_WND[2]//8,G_.P_MESG_WND[3]//8]
        comf.fill_tilemap(layer, (31,31),size2[0],size[1]+size2[1],0,size[1])
        for y in range(size2[1]):
            for x in range(size2[0]):
                if y == 0:
                    px.tilemaps[layer].pset(x, size[1]+ y, (11,0))
                elif y == size2[1]-1:
                    px.tilemaps[layer].pset(x, size[1]+ y, (15,0))
                elif x == 0:
                    px.tilemaps[layer].pset(x, size[1]+ y, (10,0))
                elif x == size2[0]-1:
                    px.tilemaps[layer].pset(x, size[1]+ y, (16,0))

    #ユーザキャラ情報初期化
    def init_user(self,index:int=9):
        if isinstance(self.user, character.UserCharacter):
            self.user.reset_state()
        else:
            match index:
                case 0:
                    self.user = character.UserCharacter(0,[G_.P_MAIN_WND[2]//4,G_.P_MAIN_WND[3]//4],[0,0,16,16],
                                                        "戦士型",1500,70,50,50,10,15,5)
                case 1:
                    self.user = character.UserCharacter(0,[G_.P_MAIN_WND[2]//4,G_.P_MAIN_WND[3]//4],[0,0,16,16],
                                                        "魔法使い型",1500,0,20,20,70,50,40)
                case 2:
                    self.user = character.UserCharacter(0,[G_.P_MAIN_WND[2]//4,G_.P_MAIN_WND[3]//4],[0,0,16,16],
                                                        "バランス型",1500,40,30,40,35,30,25)

    #ステージ情報初期化・生成
    def init_stage(self, stage_id:int=0):
        self.stage = stage.Stage(stage_id, self.user, self.message_manager)
        self.reset_stage_parameter()

    #ステージ状態パラメタの初期化
    def reset_stage_parameter(self):
        self.is_skip_update = False
        self.is_onstair = False
        self.is_onshop = False
        self.shop_index = 0
        self.dungeon_index = 0
        self.is_boss = False
        self.user_hp_window = None
        self.boss_hp_window = None

    #タイトル画面描画準備
    def prepare_title(self):
        px.dither(1)
        px.cls(0)
        for _ in range(1000):
            pass
        self.user = None
        self.reset_parameter()
        self.stage_id = 0
        px.images[2].cls(0)
        if self.is_clear:
            px.images[2].load(0, 0, "assets/image/title2.bmp")
        else:
            px.images[2].load(0, 0, "assets/image/title.bmp")

        self.now_scene = G_.SCENE["Title"]
        self.menu = menu.MenuTitle(self.now_scene, self)
        sound.load_sounds(self.now_scene)

    #Pyxel アプリケーション起動
    def __init__(self):
        self.init_app()
        self.prepare_title()
        px.run(self.update, self.draw)

    #階段接触チェック
    def check_touch_stair(self):
        is_touch_stair = False
        match self.now_scene:
            #フィールド⇒ダンジョン
            case 30:
                for i,[_dungeon_index,(dungeon_room_x,dungeon_room_y),(field_address_x,field_address_y)] in \
                        enumerate(self.stage.dungeon_entrance_list):
                    if comf.check_collision_hitbox(
                            self.stage.now_view[0]*G_.P_MAIN_WND[2] + self.user.address[0],
                            self.stage.now_view[1]*G_.P_MAIN_WND[3] + self.user.address[1] + 2, 12,12,
                            field_address_x,field_address_y, 15,15):
                        is_touch_stair = True

                        if not self.is_onstair:
                            px.stop()
                            px.play(3,G_.SNDEFX["stair"])
                            while px.play_pos(3) is not None:
                                pass
                            px.flip()
                            self.user.magic.spell = None

                            #連結先チェック
                            self.dungeon_index = _dungeon_index
                            self.stage.dungeon_list[self.dungeon_index].now_room_address = dungeon_room_x, dungeon_room_y
                            self.user.address = [G_.P_MAIN_WND[2]/4, G_.P_MAIN_WND[3]/4]
                            self.stage.dungeon_list[self.dungeon_index].set_tilemap_dungeon()
                            self.stage.dungeon_list[self.dungeon_index].monsters.set_mobgroup_index(
                                    self.stage.dungeon_list[self.dungeon_index].now_room_address)
                            self.background_drawer = self.stage.dungeon_list[self.dungeon_index].draw
                            if self.stage.dungeon_list[self.dungeon_index].monsters.get_living_monsters() == 0:
                                self.stage.dungeon_list[self.dungeon_index].monsters.generate_monsters(self.stage_id)
                            self.now_scene = self.user.user_scene = G_.SCENE["Dungeon"]
                            sound.load_sounds(self.now_scene)
                        break
            #ダンジョン⇒フィールド
            case 40:
                if self.stage.dungeon_list[self.dungeon_index].now_room_address in \
                        self.stage.dungeon_list[self.dungeon_index].entrance_address:
                    if comf.check_collision_hitbox(self.user.address[0], self.user.address[1] + 2, 12,12,
                                                   G_.P_MAIN_WND[2]//4+6,G_.P_MAIN_WND[3]//4+6, 15,15):
                        is_touch_stair = True

                        if not self.is_onstair:
                            px.stop()
                            px.play(3,G_.SNDEFX["stair"])
                            while px.play_pos(3) is not None:
                                pass
                            px.flip()
                            self.user.magic.spell = None

                            #連結先チェック
                            for i,[_dungeon_index,(dungeon_room_x,dungeon_room_y),(field_address_x,field_address_y)] in enumerate(self.stage.dungeon_entrance_list):
                                if _dungeon_index == self.stage.dungeon_list[self.dungeon_index].dungeon_id and \
                                        (dungeon_room_x,dungeon_room_y) == self.stage.dungeon_list[self.dungeon_index].now_room_address:
                                    self.stage.now_view = [field_address_x//G_.P_MAIN_WND[2], field_address_y//G_.P_MAIN_WND[3]]
                                    self.user.address = [field_address_x - (self.stage.now_view[0]*G_.P_MAIN_WND[2]),
                                                            field_address_y - (self.stage.now_view[1]*G_.P_MAIN_WND[3])]
                                    self.stage.set_tilemap()
                                    self.stage.monsters.set_mobgroup_index(self.stage.now_view)
                                    if self.stage.monsters.get_living_monsters() == 0:
                                        self.stage.monsters.generate_monsters(self.stage_id)
                                    self.stage.update_reached_map()
                                    self.background_drawer = self.stage.draw
                                    self.now_scene = self.user.user_scene = G_.SCENE["Field"]
                                    sound.load_sounds(self.now_scene)
                                    break
        self.is_onstair = is_touch_stair
        return is_touch_stair

    #ショップ接触チェック
    def check_entry_shop(self):
        is_entry_shop = False
        self.shop = self.stage.shops.check_enter(self.user,self.stage.now_view)

        if isinstance(self.shop, menu.Shop):
            is_entry_shop = True

            if not self.is_onshop:
                px.stop()
                px.play(3,G_.SNDEFX["stair"])
                while px.play_pos(3) is not None:
                    pass
                px.flip()
                self.now_scene = G_.SCENE["Shop"]
                match self.shop.shoptype:
                    case 0|1:
                        sound.load_sounds(self.now_scene)
                    case 2:
                        sound.load_sounds(self.now_scene+1)
                    case 3:
                        sound.load_sounds(self.now_scene+2)
                        #初回神殿入場時のレベルアップアラート
                        if self.stage_id == 0 and self.is_alert_LvUp is False:
                            cmd = command.CommandSystemData()
                            systemdata = cmd.load()
                            systemdata.setdefault("alert_LvUp", False)
                            if systemdata["alert_LvUp"] is False:
                                self.now_scene = 32 #アラートウインドウ処理用                                

        self.is_onshop = is_entry_shop
        return is_entry_shop

    #モンスター死亡時のメッセージと報酬獲得
    def kill_monster(self, mob):
        self.message_manager.add_message(f"{mob.name}撃退")
        self.user.experience += mob.experience
        bonus = 2.5 if self.user.is_clear else 1
        getgold = int(mob.gold * bonus)
        self.user.gold += getgold
        self.message_manager.add_message(f"獲得EX{mob.experience: >5}/G{getgold: >5}")
        self.is_kill = True

    #物理攻撃処理
    def attack_physical(self, mobgroup):
        if self.user.weapon.item_type == 3 and \
                self.user.weapon.motion_counter > self.user.weapon.motion_frames//2:
            return
        _attackrange_weapon = self.user.weapon.func_attackrange(*self.user.address,self.user.direction)
        is_hit_weapon = False

        #物理攻撃実行中の処理
            #画面内全モンスターに対する処理
            #宝箱の損傷
        for _attackrange in _attackrange_weapon: #武器の攻撃判定は複数ボックスで構成の場合あり
            for mob in mobgroup:
                if mob.is_dead or mob.is_warp:
                    continue                    
                if comf.check_collision_hitbox(*_attackrange,
                                               *mob.address, mob.image_source[2]-8,mob.image_source[3]-8):
                    is_hit_weapon = True
                if is_hit_weapon:
                    if mob.timer_damaged == 0: #１回の攻撃がフレーム毎に連続ヒットしない為のタイマ
                        damage = self.user.proc_attack_physical(mob,self.user.weapon.knockback_length)
                        if damage > 0:
                            self.message_manager.add_message(f"攻撃！ {damage}", 10)
                            if not mob.is_dead and mob.hp < 0:
                                self.kill_monster(mob)
                                self.is_kill = True
                        elif damage == 0:
                            self.message_manager.add_message(f"防御された…", 12)
                is_hit_weapon = False

    #魔法攻撃処理
    def attack_magic(self, mobgroup, treasure):
        _attackrange_magic = self.user.magic.func_attackrange(*self.user.magic.spell.address,
                                                        self.user.magic.spell.direction)
        is_hit_spell = False
        #魔法攻撃実行中の処理
            #画面内全モンスターに対する処理
            #宝箱の損傷
        for _attackrange in _attackrange_magic:
            for mob in mobgroup:
                if mob.is_dead or mob.is_warp:
                    continue
                if comf.check_collision_hitbox(*_attackrange,
                                               *mob.address, mob.image_source[2]-8,mob.image_source[3]-8):
                    is_hit_spell = True
                if is_hit_spell:
                    damage = self.user.proc_attack_spell(self.user.magic.item_type,mob)
                    if damage > 0:
                        self.message_manager.add_message(f"呪文！ {damage}", 10)
                    elif damage == 0:
                        self.message_manager.add_message(f"抵抗された…", 12)
                    if not mob.is_dead and mob.hp < 0:
                        self.kill_monster(mob)
                        self.is_kill = True
                    #魔法が命中したらインスタンスは消える（ダメージタイマ中は阻害しない）
                    if self.user.magic.spell.spell_type == 12 and \
                            mob.timer_magicdamaged in (0,G_.GAME_FPS//3,G_.GAME_FPS): 
                        self.user.magic.spell = None
                        return
                is_hit_spell = False

            if treasure.is_placed and treasure.is_opened is False:
                if comf.check_collision_hitbox(*_attackrange, *treasure.address, 16,16) and \
                        self.user.magic.spell.timer_remain >= G_.GAME_FPS//2:
                    self.message_manager.add_message(f"宝箱が壊れた…", 12)
                    px.play(3, G_.SNDEFX["miss"], resume=True)
                    treasure.is_opened = True
                    if self.user.magic.spell.spell_type in (12,15): #魔法が命中したらインスタンスは消える
                        self.user.magic.spell = None
                        return

    #宝箱の開錠・内容入手
    def pick_treasurebox(self, box):
        if comf.check_collision_hitbox(self.user.address[0], self.user.address[1] + 2, 12,12,
                                    box.address[0],box.address[1],15,15):
            dir_map = {0:3, 1:2, 2:1, 3:0}
            direction = dir_map[self.user.direction]
            self.user.move_knockback(self.user.movespeed, self.user, direction)
            if box.challenge_open(self.stage.stage_id, self.user.dexterity):
                item.pick_item(box.item_id, box.num_item, self.user)
                self.message_manager.add_message("宝箱の開錠に成功", 3)
                self.message_manager.add_message(f"{item.get_item_info(box.item_id)[1]} {box.num_item}獲得")
                #初回宝箱入手時の所持金アラート
                if self.stage_id == 0 and self.is_alert_gold is False and box.item_id == 30 and box.num_item >= 100:
                    cmd = command.CommandSystemData()
                    systemdata = cmd.load()
                    systemdata.setdefault("alert_gold", False)
                    if systemdata["alert_gold"] is False:
                        self.now_scene = 33
    #ボス戦準備
    def prepare_bossbattle(self):
        self.is_boss = False
        self.user.is_ontrap = False
        self.stage.func_trap_tile(self.user, False)
        comf.fill_tilemap(1, (8,1), (G_.P_MAIN_WND[2]+G_.P_SUB_WND[2])//8, G_.P_MAIN_WND[3]//8)
        comf.fill_tilemap(1, (9,1), 48,33, 1,10)
        BOSS_LIST=comf.read_json("assets/data/boss.json")
        self.boss = monster.BossMonster(*BOSS_LIST[self.stage_id],self.message_manager)
        self.user.address = [24,256]
        self.user_hp_window = menu.Window(24,16, 160,48, 9)
        self.boss_hp_window = menu.Window(216,16, 160,48, 9)
        self.background_drawer = stage.draw_boss_stage
        self.now_scene = self.user.user_scene = G_.SCENE["BossBattle"]
        #ボス戦では攻撃抑止系アイテム無効
        for i in range(1,4):
            self.user.timer_item[i] = 0 #0松明,1砂時計,2隠れ蓑,3着ぐるみ,4宝石,5飲み薬,6天馬の羽,7護り札,8翼の長靴
        #ラスボス戦では能力強化アイテムも無効、最終武器／鎧以外は大幅弱体化
        if self.stage_id == 5:
            for i in range(4,9):
                self.user.timer_item[i] = 0
            if self.user.equip_id[0] in (49,59,69,79):
                self.user.weapon.value *= 1.5
                # self.user.calc_attack()
            else:
                self.user.weapon.value //= 255
            self.user.calc_attack()
            if self.user.equip_id[0] != 49:
                self.user.exp_magic[0] = 0
                self.user.exp_magic[1] = 0
                self.user.exp_magic[2] = 0
                self.user.exp_magic[3] = 0
            self.user.calc_magic_power()
            if self.user.equip_id[1] not in (109,119,129,139):
                self.user.armor.value //= 128
            self.user.calc_status(self.user.armor.value, self.user.exp_armor)
            if self.user.equip_id[2] not in (149,159,169,179):
                self.user.shield.value //= 128
            self.user.calc_magic_defend()
            self.now_scene = self.user.user_scene = G_.SCENE["LastBoss"]
        sound.load_sounds(self.now_scene)

    #共通更新処理１（複数フレーム継続処理）
    def update_phase1(self, area):
        #更新中に毎フレーム行う処理
            #メッセージ消去カウントダウン
            self.message_manager.countdown_message()
            #ユーザ情報更新（タイマー減算）
            self.user.user_timer_decrement()
        #継続動作の処理（主に当たり判定　
            #宝箱情報（攻撃時の当たり判定が発生する為ここで取得）
            box = area.monsters.treasure_list[area.monsters.mobgroup_index]
            if self.now_scene in (G_.SCENE["BossBattle"], G_.SCENE["LastBoss"]):
                #物理攻撃処理
                if self.user.weapon.is_attacking:
                    self.attack_physical([self.boss])
                #魔法攻撃処理
                if isinstance(self.user.magic.spell, character.Spell):
                    self.attack_magic([self.boss], box)
            else:
                #物理攻撃処理
                if self.user.weapon.is_attacking:
                    self.attack_physical(area.monsters.mobgroup[area.monsters.mobgroup_index][3])
                #魔法攻撃処理
                if isinstance(self.user.magic.spell, character.Spell):
                    self.attack_magic(area.monsters.mobgroup[area.monsters.mobgroup_index][3], box)
            if self.is_kill:
                self.encyclopedia.add_list(area.monsters.mobgroup[area.monsters.mobgroup_index][2],
                                           area.monsters.mobgroup[area.monsters.mobgroup_index][1]-1)
                self.is_kill = False
            #宝箱開錠判定実行
            if self.user.timer_action == 0 and box.is_placed and box.is_opened is False:
                self.pick_treasurebox(box)

    #共通更新処理２（キー入力反応）
    def update_phase2(self, area):    
        #入力キーチェック（関数内で処理するものもあり）
        _return_code = self.user.check_inputkey()
        #移動時はタイルチェック
        if _return_code in (0,1,2,3):
            self.user.move_address(self.now_scene, int(self.user.movespeed))
        elif _return_code == 8:                    
            if self.user.timer_selectmagic == 0:
                self.menu = menu.MenuSelectMagic(self.user)
                self.now_scene = G_.SCENE["Menu"]
        elif self.now_scene in (G_.SCENE["Field"], G_.SCENE["Dungeon"]):
            if _return_code == 7:                    
                if self.user.timer_selectitem == 0:
                    self.menu = menu.Menu(10,10, [1,6], G_.MENU_ITEM, 6, parent=self, user=self.user)
                    self.now_scene = G_.SCENE["Menu"]
            elif _return_code == 9:                    
                if self.user.timer_selectitem == 0:
                    self.menu = menu.MenuSelectItem(self.user)
                    self.now_scene = G_.SCENE["Menu"]
            elif _return_code == 6:
                if self.user.is_use_item_miss:
                    self.message_manager.add_message("所持数が足りない", 8)
                    self.user.is_use_item_miss = False
                elif self.user.is_use_item_block:
                    self.message_manager.add_message("今は使えない", 8)
                    self.user.is_use_item_block = False
                elif item.get_item_info(self.user.equip_id[4])[0] == 18:
                    self.message_manager.add_message(f"持続時間 {self.user.timer_item[self.user.equip_id[4]-10]//G_.GAME_FPS:3>}秒")
            elif _return_code == 10:
                self.menu = menu.MenuMonsterList(self.encyclopedia.get_list())
                self.now_scene = G_.SCENE["MobList"]
    #その他ユーザ状態更新
        self.user.update()
        self.update_levelup_info()
        self.check_levelup()
        #レベルアップ表示関連
        for eff in self.levelup_effects:
            eff["frame"] += 1
            eff["y"] -= 0.2  # 上に浮く
        self.levelup_effects = [e for e in self.levelup_effects if e["frame"] < G_.GAME_FPS]
    #ステージ状態更新（主にモンスターの行動）
        if self.user.user_scene in (G_.SCENE["Field"], G_.SCENE["Dungeon"]):
            area.update(self.now_scene)
        else:
            self.boss.update(self.user)
        #モンスター行動の結果死亡した
        if self.user.hp <= 0:
            self.user.hp = 0
            self.user.is_dead = True
    #モンスター辞書　ドロップアイテム登録
        box = area.monsters.treasure_list[area.monsters.mobgroup_index]
        if box.is_placed and box.rate_open>=100 and area.monsters.mobgroup[area.monsters.mobgroup_index][1] <= 4:
            self.encyclopedia.update_chest(
                    area.monsters.mobgroup[area.monsters.mobgroup_index][2],
                    area.monsters.mobgroup[area.monsters.mobgroup_index][1]-1)
            box.rate_open = -1
    #モンスター辞書データ更新（１分毎）
        self.encyclopedia.timer_save -= 1
        if self.encyclopedia.timer_save == 0:
            self.encyclopedia.save_list(self)
            self.message_manager.add_message("<system autosave>")

    #Pyxel Update処理
    def update(self):
        try:
            match self.now_scene:
            #タイトル画面
                case 0:
                    self.menu.update()
                    return
            #キャラ選択
                case 10:
                    if not self.menu.update():
                        self.message_window = menu.Window(16,224,G_.P_MAIN_WND[2]+G_.P_SUB_WND[2]-32,48, 1,50)
                        px.images[2].cls(0)
                        px.images[2].load(0, 0, "assets/image/op.png")
                        px.dither(0)
                        self.counter = 0
                        self.user.is_clear = self.is_clear_user
                        self.now_scene = self.user.user_scene = G_.SCENE["Opening"]
                    return
            #オープニング
                case 15:
                    self.counter += 0.01
                    px.dither(self.counter)
                    if self.counter > 1:
                        next_ = self.message_window.update()
                        if self.is_nextstage:
                            self.counter = 0
                            self.menu = menu.MenuNameEntry()
                            self.now_scene = self.user.user_scene = G_.SCENE["NameEntry"]
                        elif next_ is False:
                            self.message_window.close_counter = 0
                            self.eventstep += 1
                    return
            #名前入力
                case 20:
                    if not self.menu.update():
                        self.user.name = self.menu.input_name_string
                        if self.user.is_clear:
                            self.user.elixer = 10
                            self.user.food = 5000
                            self.user.strength += 5
                            self.user.dexterity += 5
                            self.user.agility += 5
                            self.user.intelligence += 5
                            self.user.wisdom += 5
                            self.user.magicregistance += 5
                            self.user.inventory=[]
                            item.pick_item(10,6,self.user)
                            item.pick_item(11,6,self.user)
                            item.pick_item(12,6,self.user)
                            item.pick_item(13,6,self.user)
                            item.pick_item(14,6,self.user)
                            item.pick_item(15,6,self.user)
                            item.pick_item(16,6,self.user)
                            item.pick_item(17,6,self.user)
                            item.pick_item(18,6,self.user)
                            item.pick_item(20,6,self.user)
                            item.pick_item(21,6,self.user)
                            item.pick_item(22,6,self.user)
                        self.now_scene = self.user.user_scene = G_.SCENE["StagePrepare"]
                    return
            #フィールド準備
                case 25:
                    self.reset_parameter()
                    self.user.reset_state()
                    self.reset_levelup_info()
                    self.init_stage(self.stage_id) #ステージ、ダンジョンおよび付随モンスターの生成
                    self.background_drawer = self.stage.draw
                    px.images[2].cls(0)
                    px.images[2].load(0, 0, f"assets/image/stage{self.stage_id}.bmp")
                    self.message_window.message_text = evt.stage_prelude(self.stage_id)
                    self.now_scene = self.user.user_scene = G_.SCENE["StageStart"]
                    return
            #ステージ開始
                case 29:
                    if self.user.is_clear:
                        pass
                    else:
                        px.stop()
                        for ch, sound_ in enumerate(comf.read_json("assets/sound/ed0.intro.json")):
                            px.sounds[ch].set(*sound_)
                            px.play(ch, ch)
                        while px.play_pos(0) is not None:
                            pass

                    px.flip()
                    self.now_scene = self.user.user_scene = G_.SCENE["Field"]
                    sound.load_sounds(self.now_scene)
                    return
            #フィールド
                case 30:
                    #更新スキップに優先して実行する処理
                    #初回敵全滅時のアラート
                    if self.stage_id == 0 and self.is_alert_group is False:
                        if self.stage.monsters.mobgroup[self.stage.monsters.mobgroup_index][1] >=4 and \
                                self.stage.monsters.get_living_monsters() == 0:
                            cmd = command.CommandSystemData()
                            systemdata = cmd.load()
                            systemdata.setdefault("alert_group", False)
                            if systemdata["alert_group"] is False:
                                self.now_scene = 34 #アラートウインドウ処理用
                                return
                    #初回デバフ床進入時の鍵アラート
                    if self.stage_id == 0 and self.is_alert_map and self.is_alert_zone is False and self.user.timer_ontrap > 0:
                        cmd = command.CommandSystemData()
                        systemdata = cmd.load()
                        systemdata.setdefault("alert_zone", False)
                        if systemdata["alert_zone"] is False:
                            self.now_scene = 37 #アラートウインドウ処理用
                            return
                    #初回掘り出しポイント接近時のアラート
                    if self.stage_id == 0 and self.is_alert_map and self.is_alert_mattock is False and self.stage.search_treasure() is not None:
                        cmd = command.CommandSystemData()
                        systemdata = cmd.load()
                        systemdata.setdefault("alert_mattock", False)
                        if systemdata["alert_mattock"] is False:
                            self.now_scene = 38 #アラートウインドウ処理用
                            return
                    if self.is_boss: #ボス戦準備
                        if isinstance(self.message_window, menu.Window) and \
                                self.message_window.update() is False:
                            self.message_window = None
                            self.prepare_bossbattle()
                        return
                    #更新状況に関わらず毎フレーム実行する処理
                        #現時点で無し
                    #処理待ちによる更新のスキップ
                    if self.is_skip_update: #処理待ち中は更新スキップフラグON
                        return
                    #共通更新処理１
                    self.update_phase1(self.stage)
                    if self.now_scene != 30:
                        return
                    #ボス召喚オーブ接触
                    if self.stage.now_view == self.stage.boss_orb.map_address and self.stage.boss_orb.is_placed:
                        if comf.check_collision_hitbox(*self.user.address,16,16, *self.stage.boss_orb.address,16,16):
                            if self.stage_id == 5:
                                self.message_window = menu.Window(16,G_.P_MAIN_WND[3]//2+16,
                                                                (1+18*2+1)*8, 16*6, 1, 240)
                                if self.user.weapon.id%10 == 9:
                                    if self.user.is_clear:
                                        self.message_window.message_text = [
                                            "輝く宝珠に近付くと、どこからか声が響いてきた",
                                            "何？何故このような場所に居る？",
                                            "そのような導きは与えておらぬはずだが・・・",
                                            "もしや邪悪なる逃亡者共に唆されたか",
                                            "ならば我自らの手で引導を渡してやろう！！"]
                                    else:
                                        self.message_window.message_text = [
                                            "輝く宝珠に近付くと、どこからか声が響いてきた",
                                            "とうとうここまで辿り着いてしまったか・・・",
                                            "",
                                            "まあ、よいだろう",
                                            "愚かな旅人よ　何も知らぬまま　果てるがいい！"]
                                else:
                                    self.message_window.message_text = [
                                        "輝く宝珠に近付くと、どこからか声が響いてきた",
                                        "",
                                        "とうとうここまで辿り着いたか・・・しかし",
                                        "その貧弱な武器では我が身に傷一つ付けられまい！",
                                        "自らの愚かさを悔いるがいい！！"]
                            else:
                                self.message_window = menu.Window(16,G_.P_MAIN_WND[3]//2+16,
                                                                  G_.P_MAIN_WND[2]-(16*2),16*4,1,120)
                                match self.stage_id:
                                    case 0:
                                        hint_message = ["草原の先から巨大な猪が突進してくる！！",
                                                        "・・・獣なら火に驚くだろうか？"]
                                    case 1:
                                        hint_message = ["沼の中から巨大な蛇が鎌首をもたげる！！",
                                                        "変温動物なら冬眠させてやれば！"]
                                    case 2:
                                        hint_message = ["翼のはためきと共に巨大な鷲が飛来する！",
                                                        "風が荒れれば自由に飛べぬはず！"]
                                    case 3:
                                        hint_message = ["見上げる程の氷の巨人が地響きを立てる！",
                                                        "氷なら当然…だが武器は？叩き割れるか？"]
                                    case 4:
                                        hint_message = ["深淵から現れた巨大な竜が咆哮をあげる！",
                                                        "剣や槍では竜鱗を貫けそうにない！！"]
                                self.message_window.message_text = ["輝く宝珠を手にすると・・・"] + hint_message
                            self.is_boss = True
                            return
                    #掘り出し物ポイント接触＆鶴嘴使用
                    if self.user.is_use_item21: #鶴嘴
                        result = self.stage.trove_treasure()
                        if result is None:
                            self.message_manager.add_message("何も見つからない", 12)
                        else:
                            for i,item_ in enumerate(self.user.inventory):
                                if item_[0] == 21:
                                    break
                            self.user.inventory[i][1] -= 1
                            item.pick_item(result[0], result[1], self.user)
                            px.play(3,G_.SNDEFX["pick"], resume=True)
                            self.message_manager.add_message("何か埋まっていた", 3)
                            self.message_manager.add_message(f"{item.get_item_info(result[0])[1]} {result[1]}獲得")
                        self.user.is_use_item21 = False
                        return
                    #画面遷移オブジェクト
                    if self.check_touch_stair() and self.now_scene != G_.SCENE["Field"]: # toダンジョン
                        self.user.is_ontrap = False
                        self.stage.func_trap_tile(self.user, False)
                        return
                    if self.check_entry_shop() and self.now_scene != G_.SCENE["Field"]: #全ショップループチェック
                        return
                    #トラップタイル 着ぐるみ、翼の長靴時は発動しない
                    if self.user.timer_item[3] <= 0 and self.user.timer_item[8] <= 0:
                        if comf.get_tileinfo(self.user.address[0],self.user.address[1]+6, 0)[0] == 3:
                            if self.user.timer_ontrap == 0:
                                trapmessage = self.stage.func_trap_tile(self.user, True)
                                self.message_manager.add_message(trapmessage, 8)
                                self.user.timer_ontrap = G_.GAME_FPS
                        else:
                            self.stage.func_trap_tile(self.user, False)
                    #共通更新処理２
                    self.update_phase2(self.stage)
                    return
                case 31|32|33|34|35|36|37|38:
                    if self.message_window.update() is False:
                        cmd = command.CommandSystemData()
                        match self.now_scene:
                            case 31:
                                self.is_alert_key = True
                            case 32:
                                self.is_alert_LvUp = True
                            case 33:
                                self.is_alert_gold = True
                            case 34:
                                self.is_alert_group = True
                            case 35:
                                self.is_alert_map = True
                                self.generate_minimap()
                                return
                            case 36:
                                self.is_alert_torch = True
                            case 37:
                                self.is_alert_zone = True
                            case 38:
                                self.is_alert_mattock = True
                        cmd.save(self)
                        if self.now_scene == 32:
                            sound.load_sounds(G_.SCENE["Field"])
                        self.now_scene = self.user.user_scene

            #ダンジョン
                case 40:
                    #初回ダンジョン進入時の鍵アラート
                    if self.stage_id == 0 and self.is_alert_key is False:
                        cmd = command.CommandSystemData()
                        systemdata = cmd.load()
                        systemdata.setdefault("alert_key", False)
                        if systemdata["alert_key"] is False:
                            self.now_scene = 31 #アラートウインドウ処理用
                            return
                    #初回松明消灯時のアラート
                    if self.stage_id == 0 and self.is_alert_torch is False:
                        if self.user.timer_item[0] <= 0 and self.user.inventory[0][2]>5:
                            cmd = command.CommandSystemData()
                            systemdata = cmd.load()
                            systemdata.setdefault("alert_torch", False)
                            if systemdata["alert_torch"] is False:
                                self.now_scene = 36 #アラートウインドウ処理用
                                return
                    #コードが長くなる為エイリアス名で処理
                    alias = self.stage.dungeon_list[self.dungeon_index]
                    #更新状況に関わらず毎フレーム実行する処理
                        #現時点で無し
                    #処理待ちによる更新のスキップ
                    if self.is_skip_update: #処理待ち中は更新スキップフラグON
                        return
                    #共通更新処理１
                    self.update_phase1(alias)
                    if self.user.is_use_item20:
                        if alias.open_all_doors():
                            for i,item_ in enumerate(self.user.inventory):
                                if item_[0] == 20:
                                    break
                            self.user.inventory[i][1] -= 1
                        self.user.is_use_item20 = False
                    #ダンジョンアイテム獲得
                    if alias.treasure_cache[2] is False and alias.treasure_cache[0] == alias.now_room_address:
                        if comf.check_collision_hitbox(self.user.address[0],self.user.address[1]+2,12,12,
                                                    G_.P_MAIN_WND[2]*0.75+8,G_.P_MAIN_WND[3]*0.75+8,15,15):
                            item.pick_item(alias.treasure_cache[1], 1, self.user)
                            px.play(3,G_.SNDEFX["pick"], resume=True)
                            self.message_manager.add_message(f"{item.get_item_info(alias.treasure_cache[1])[1]} 獲得")
                            alias.treasure_cache[2] = True
                    #ダンジョン宝箱獲得
                    for treasure in alias.treasure_list:
                        if treasure[2] is False and treasure[0] == alias.now_room_address:
                            if comf.check_collision_hitbox(self.user.address[0],self.user.address[1]+2,12,12,
                                                        G_.P_MAIN_WND[2]//2,G_.P_MAIN_WND[3]//2,15,15):
                                item.pick_item(treasure[1], 1, self.user)
                                px.play(3,G_.SNDEFX["pick"], resume=True)
                                self.message_manager.add_message(f"{item.get_item_info(treasure[1])[1]} 獲得")
                                treasure[2] = True
                    #最終装備獲得
                    if self.stage_id == 5 and \
                            alias.final_equip_cache[2] is False and alias.final_equip_cache[0] == alias.now_room_address:
                        if comf.check_collision_hitbox(self.user.address[0],self.user.address[1]+2,12,12,
                                                    G_.P_MAIN_WND[2]*0.25+8,G_.P_MAIN_WND[3]*0.75+8,15,15):
                            match alias.dungeon_id:
                                case 0:
                                    final_equip_id = self.user.weapon.item_type*10 + 49
                                case 1:
                                    final_equip_id = self.user.armor.item_type*10 + 69
                                case 2:
                                    final_equip_id = self.user.shield.item_type*10 + 69
                                case 3:
                                    final_equip_id = 20
                            item.pick_item(final_equip_id, 1, self.user)
                            px.play(3,G_.SNDEFX["pick"], resume=True)
                            self.message_manager.add_message("神秘的な宝箱から…", 15)
                            self.message_manager.add_message(f"{item.get_item_info(final_equip_id)[1]} 獲得")
                            alias.final_equip_cache[2] = True
                    if self.check_touch_stair() and self.now_scene != G_.SCENE["Dungeon"]:
                        pass
                    #共通更新処理２
                    self.update_phase2(alias)
                    return
            #ショップ
                case 50:
                    if self.shop.menu.update() is False:
                        self.now_scene = self.user.user_scene
                        if self.shop.shoptype == 3:
                            self.stage.shops.shop_list[1].price_hike_keys(self.user, self.stage_id)
                            self.stage.shops.shop_list[2].menu = menu.MenuInn(2, self.stage_id, self.user)
                        sound.load_sounds(self.now_scene)
                    return
            #メニュー
                case 60:
                    if self.menu.update() is False:
                        if self.menu.is_map:
                            if self.user.user_scene == G_.SCENE["Dungeon"]:
                                self.message_manager.add_message("地上でのみ表示可能", 8)
                                px.play(3, G_.SNDEFX["miss"], resume=True)
                                self.menu.is_map = False
                                self.menu = None
                                self.now_scene = self.user.user_scene
                                return

                            self.generate_minimap()
                            return
                        self.menu = None
                        self.now_scene = self.user.user_scene
                    return
            #マップ表示
                case 65:
                    if px.frame_count > self.counter + (G_.GAME_FPS//2):
                        pushed = comf.get_button_state()
                        if pushed["a"] or pushed["b"]:
                            self.menu = None
                            self.counter = 0
                            self.now_scene = self.user.user_scene
                    return
            #敵リスト
                case 66:
                    if self.menu.update() is False:
                        self.menu = None
                        px.images[G_.IMGIDX["MOB"]].load(0, 0, f"assets/image/stage{self.stage_id}.bmp")
                        self.now_scene = self.user.user_scene
                    return
            #ボス戦 #ラスボス戦
                case 70 | 75:
                    #処理待ちによる更新のスキップ
                    if self.is_skip_update: #処理待ち中は更新スキップフラグON
                        return
                    #更新スキップに優先して実行する処理
                    if self.user.is_dead:
                        self.now_scene = G_.SCENE["GameOver"]
                        return
                    if self.boss.is_dead:
                        grpid = 3 if self.user.is_clear else 1
                        self.encyclopedia.add_list(self.boss.stage_id+80, grpid)
                        self.encyclopedia.save_list(self)
                        if isinstance(self.user.magic.spell, character.Spell):
                            self.user.magic.spell = None
                        if self.stage_id == 5 and isinstance(self.boss.magic.spell, character.Spell):
                            self.boss.magic.spell = None
                        self.user.weapon.is_attacking = False
                        if self.boss.is_broken:
                            self.now_scene = self.user.user_scene = G_.SCENE["Ending"] if self.now_scene == 75 \
                                                                                        else G_.SCENE["StageClear"] 
                            self.message_window = menu.Window(32,32, px.width-32-32,px.height-32-32, 1, 300)
                            sound.load_sounds(self.now_scene)
                            return
                        elif self.boss.is_defeat:
                            if px.play_pos(3) is None:
                                self.boss.is_broken = True
                            return
                        else:
                            self.counter += 1
                            return
                    #更新状況に関わらず毎フレーム実行する処理
                        #現時点で無し
                    #処理待ちによる更新のスキップ
                    if self.is_skip_update: #処理待ち中は更新スキップフラグON
                        self.is_skip_update = self.message_window.update()
                        return
                    #共通更新処理１
                    self.update_phase1(self.stage)
                    if self.boss.hp < 0:
                        self.boss.is_dead = True
                        self.counter = 0
                        return
                    #共通更新処理２
                    self.update_phase2(self.stage)
                    return
            #ステージクリアイベント
                case 80:
                    next_ = self.message_window.update()
                    match self.stage_id:
                        case 0:
                            if self.is_nextstage:
                                self.stage_id += 1
                                self.now_scene = self.user.user_scene = G_.SCENE["StagePrepare"]
                            elif next_ is False:
                                self.message_window.close_counter = 0
                                self.eventstep += 1
                        case _:
                            if self.is_nextstage:
                                self.stage_id += 1
                                self.now_scene = self.user.user_scene = G_.SCENE["StagePrepare"]
                            elif next_ is False:
                                self.message_window.close_counter = 0
                                self.eventstep += 1
                    return
            #エンディング1（メッセージウインドウ）
                case 90:
                    next_ = self.message_window.update()
                    if self.is_nextstage:
                        self.stage_id += 1
                        self.now_scene = 91
                        self.counter = 1
                    elif next_ is False:
                        self.message_window.close_counter = 0
                        self.eventstep += 1
                    return
            #エンディング2（テキストスクロール準備）
                case 91:
                    self.counter -= 0.01
                    if self.counter < 0:
                        self.stars = []
                        self.spawn_timer = 0
                        self.ending_messages = comf.read_json("assets/data/messages_u.json") \
                                                if self.user.is_clear else comf.read_json("assets/data/messages.json")
                        self.scroll_y = G_.P_MAIN_WND[3]
                        px.dither(1)
                        self.now_scene = 92
                        cmd = command.CommandSystemData()
                        self.is_clear = True
                        cmd.save(self)
                        cmd = None
                    return
            #エンディング3（テキストスクロール、スタッフロール）
                case 92:
                    # 流れ星生成
                    self.spawn_timer -= 1
                    if self.spawn_timer <= 0:
                        self.stars.append(evt.ShootingStar())
                        self.spawn_timer = px.rndi(5, 15)
                    # 流れ星更新
                    self.stars = [s for s in self.stars if not s.update()]
                    # メッセージスクロール
                    if self.scroll_y > -5198:
                        self.scroll_y -= 0.2
                    #エンディングスキップ
                    if self.scroll_y < 200 and self.counter <= 0:
                        state = comf.get_button_state()
                        if state["a"] or state["b"]:
                            self.counter = 1
                    if self.counter >= (G_.GAME_FPS*8):
                        px.dither(1)
                        self.prepare_title()
                    elif self.counter >= 1:
                        self.counter += 1
                    return
            #ゲームオーバー
                case 99:
                    if self.is_gameover:
                        if self.message_window.update() is False:
                            self.prepare_title()
                    else:
                        if self.user.user_scene in (30,40):
                            menuwidth = G_.P_MAIN_WND[2]//4
                        else:
                            menuwidth = (G_.P_MAIN_WND[2]+G_.P_SUB_WND[2])//4
                        self.message_window = menu.Window(menuwidth, G_.P_MAIN_WND[3]//2+16,
                                                            (1+9*2+1)*G_.P_CHIP_SIZE, (1+2*3+1)*G_.P_CHIP_SIZE, 1, 300)
                        self.is_gameover = True
                        self.counter = px.frame_count
                    return
        except Exception as e:
            comf.error_message(["",f"更新処理で予期せぬ例外が発生しました","",f"情報：",f"{e}",""])
            self.prepare_title()

    def generate_minimap(self):
        minimap_address = menu.generate_minimap(self.stage)
        self.counter = px.frame_count
        self.minimap_spot = [[False for _ in range(3)] for _ in range(3)]
        for spot in self.stage.treasure_spot:
            for y in range(-1,2):
                for x in range(-1,2):
                    if minimap_address[y+1][x+1] == (-1,-1):
                        pass
                    elif (self.stage.now_view[0]+x,self.stage.now_view[1]+y) == spot[0]:
                        self.minimap_spot[y+1][x+1] = spot[1]
        self.now_scene = G_.SCENE["Map"]

    #ユーザステータスウインドウ描画
    def draw_status(self):
        #サブウインドウ枠線描画
        px.bltm(G_.P_STAT_WND[0],G_.P_STAT_WND[1], 7, 
            0,G_.P_STAT_WND[1], G_.P_STAT_WND[2],G_.P_STAT_WND[3], colkey=7)
        _draw_data = [
            f"{self.user.name}",
            f"{int(self.user.hp):>11,}",
            f"{int(self.user.food):>11,}",
            f"{self.user.experience:>11,}",
            f"{self.user.gold:>11,}",
            f"{self.user.magic.name}",
            f"{item.ITEMS[str(self.user.equip_id[4])][1]}",
        ]
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 1*13, 0, 0,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 2*13, 0, 8,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 3*13, 0, 16,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 4*13, 0, 24,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 5*13, 0, 32,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 6*13, 0, 88,232, 8,8, 0)
        px.blt(G_.P_SUB_WND[0]+10+74, G_.P_SUB_WND[1]+11 + 5*13, 0, 40,232, 8,8, 0)
        px.text(G_.P_SUB_WND[0]+10+83, G_.P_SUB_WND[1]+8+ 5*13, f"{self.user.key:>3}", 7, font=G_.JP_FONT)
        px.blt(G_.P_SUB_WND[0]+10+74, G_.P_SUB_WND[1]+11 + 6*13, 0, 48,232, 8,8, 0)
        px.text(G_.P_SUB_WND[0]+10+83, G_.P_SUB_WND[1]+8+ 6*13, f"{self.user.elixer:>3}", 7, font=G_.JP_FONT)
        if self.user.timer_fire > 0:
            px.blt(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+11 + 7*13, 0, 56+(0*8),232, 8,8, 0)
            px.text(G_.P_SUB_WND[0]+18, G_.P_SUB_WND[1]+8 + 7*13, f"{self.user.timer_fire}s", 7, font=G_.JP_FONT)
        if self.user.timer_ice > 0:
            px.blt(G_.P_SUB_WND[0]+44, G_.P_SUB_WND[1]+11 + 7*13, 0, 56+(1*8),232, 8,8, 0)
            px.text(G_.P_SUB_WND[0]+52, G_.P_SUB_WND[1]+8 + 7*13, f"{self.user.timer_ice}s", 7, font=G_.JP_FONT)
        if self.user.timer_wind > 0:
            px.blt(G_.P_SUB_WND[0]+76, G_.P_SUB_WND[1]+11 + 7*13, 0, 56+(2*8),232, 8,8, 0)
            px.text(G_.P_SUB_WND[0]+86, G_.P_SUB_WND[1]+8 + 7*13, f"{self.user.timer_wind}s", 7, font=G_.JP_FONT)

        for i, text in enumerate(_draw_data):
            if i == 0:
                px.text(G_.P_SUB_WND[0]+10, G_.P_SUB_WND[1]+8 + i*13, text, 7, font=G_.JP_FONT)
            else:
                px.text(G_.P_SUB_WND[0]+20, G_.P_SUB_WND[1]+8 + i*13, text, 7, font=G_.JP_FONT)

    #スクロール方向算出
    def get_scroll_direction(self, offset):
        scroll_dir = 9
        if self.user.address[0] < offset:
            scroll_dir = 1
        elif self.user.address[0] > G_.P_MAIN_WND[2] - offset:
            scroll_dir = 2
        elif self.user.address[1] < offset:
            scroll_dir = 3
        elif self.user.address[1] > G_.P_MAIN_WND[2] - offset:
            scroll_dir = 0
        return scroll_dir

    #ボス戦描画
    def draw_bossbattle(self):
        #背景描画共通呼び出し
        self.background_drawer()
        #HPウインドウ
        self.user_hp_window.draw()
        self.user_hp_window.drawText(self.user_hp_window.x+8, self.user_hp_window.y+8,
                                        [self.user.name, f"{int(self.user.hp):>11,}"])
        self.boss_hp_window.draw()
        self.boss_hp_window.drawText(self.boss_hp_window.x+8, self.boss_hp_window.y+8,
                                        [self.boss.name,f"{int(self.boss.hp):>11,}"])
        self.user.draw()
        self.boss.draw()
        #ボス死亡時エフェクト
        if self.boss.is_dead and self.boss.is_defeat is False:
            self.boss.is_defeat = evt.defeat_boss(self.boss, self.counter)

    #共通描画処理
    def draw_common(self):
        #背景・モンスター描画共通呼び出し
        self.background_drawer()
        #ユーザ死亡時はエリクサーがあれば復活
        if self.user.is_dead:
            self.user.timer_damaged = self.user.timer_magicdamaged = G_.GAME_FPS*2
            if self.user.elixer >= 1:
                self.is_skip_update = evt.use_elixer(self.user)
                if self.is_skip_update is False:
                    sound.load_sounds(self.user.user_scene)
            else:
                self.now_scene = G_.SCENE["GameOver"]
        self.user.draw()
        for eff in self.levelup_effects:
            col = eff["color"] if px.frame_count%8 < 7 else 7
            px.text(int(eff["x"]), int(eff["y"]), f"{eff["type"]}UP", col)
        self.draw_status()
        self.message_manager.draw_message()

    #Pyxel draw処理
    def draw(self):
        try:
            match self.now_scene:
            #タイトル画面
                case 0:
                    if self.menu.is_newgame:
                        if self.menu.cnt <= 0:
                            px.dither(1)
                            self.menu = menu.MenuSelectCharacter(self.init_user)
                            self.now_scene = G_.SCENE["SelectChara"]
                            sound.load_sounds(self.now_scene)
                    self.menu.draw( )
            #キャラ選択
                case 10:
                    self.menu.draw()
            #オープニング
                case 15:
                    px.blt(68,0, 2, 0,0, 256,256, colkey=0)
                    if self.user.is_clear:
                        self.is_nextstage = evt.opening_u(self.message_window, self.eventstep)
                    else:
                        self.is_nextstage = evt.opening(self.message_window, self.eventstep)
                    self.message_window.draw()
                    self.message_window.draw_message()
            #名前入力
                case 20:
                    self.menu.draw()
            #フィールド準備
                case 25:
                    if isinstance(self.message_window, menu.Window):
                        self.message_window.draw()
                        self.message_window.draw_message()
            #ステージ開始
                case 29:
                    #背景描画共通呼び出し
                    self.background_drawer()
                    self.draw_status()
                    self.message_manager.draw_window()
                    self.message_window.draw()
                    self.message_window.draw_message()
            #フィールド
                case 30:
                    #ボス出現（＝召喚アイテム接触）時
                    if self.is_boss:
                        self.message_window.draw()
                        self.message_window.drawText(self.message_window.x+8,self.message_window.y+8,
                                                    self.message_window.message_text)
                        return
                    #マップスクロール
                    _scroll_offset = 0
                    scroll_dir = self.get_scroll_direction(_scroll_offset)
                    if scroll_dir in (0,1,2,3):
                        if self.stage.scroll_counter == 0:
                            self.is_skip_update = True
                            #画面切替時は魔法効果中止
                            if isinstance(self.user.magic.spell, character.Spell):
                                self.user.magic.spell = None
                            if self.stage.prepare_scroll_map(scroll_dir) is False:
                                self.is_skip_update = False
                                return
                        if evt.scroll_map(self.stage):
                            match scroll_dir:
                                case 0:
                                    self.user.address = [self.user.address[0], _scroll_offset]
                                case 1:
                                    self.user.address = [G_.P_MAIN_WND[2] - _scroll_offset, self.user.address[1]]
                                case 2:
                                    self.user.address = [_scroll_offset, self.user.address[1]]
                                case 3:
                                    self.user.address = [self.user.address[0], G_.P_MAIN_WND[3] - _scroll_offset]
                            self.is_skip_update = False
                            #初回画面切り替え時のミニマップアラート
                            if self.stage_id == 0 and self.is_alert_map is False:
                                cmd = command.CommandSystemData()
                                systemdata = cmd.load()
                                systemdata.setdefault("alert_map", False)
                                if systemdata["alert_map"] is False:
                                    self.now_scene = 35 #アラートウインドウ処理用
                                    return
                        return
                    #共通描画処理
                    self.draw_common()
                case 31|32|33|34|35|36|37|38:
                    #チュートリアル／アラート
                    self.message_window.draw()
                    match self.now_scene:
                        case 31:
                            self.message_window.message_text = [
                                "　鍵は十分持っているか？上手く動けば少なく済むが・・・",
                                "　ここは浅そうだ、１５個もあれば足りるだろう"]
                        case 32:
                            self.message_window.message_text = [
                                "　レベルが上がるにつれ鍵と宿代、食糧消費が増えてゆく",
                                "　まずは熟練度を積み上げての強さを求めなされ"]
                        case 33:
                            self.message_window.message_text = [
                                "　宝箱には纏まった額のお金が入っていた",
                                "　闇雲に敵を倒すより宝箱の方が余程稼げそうだ"]
                        case 34:
                            self.message_window.message_text = [
                                "　４度目の戦いの後、敵の気配が感じられなくなった",
                                "　このエリアの敵は全て倒してしまったようだ"]
                        case 35:
                            self.message_window.message_text = [
                                "　未知のエリアへ辿り着いた",
                                "　踏破済エリアなら、現在地と周辺の地形が確認できる"]
                        case 36:
                            self.message_window.message_text = [
                                "　松明は燃え尽き、辺りは闇に閉ざされる",
                                "　複数使う事で、灯りが長持ちしそうだ"]
                        case 37:
                            self.message_window.message_text = [
                                "　足元に生い茂る草木が絡みついてくる",
                                "　悪影響を防ぐ道具は持っていただろうか"]
                        case 38:
                            self.message_window.message_text = [
                                "　何か埋まっているのか、地面がキラキラ光っている",
                                "　鶴嘴を使えば掘り出せそうだ"]
                    self.message_window.draw_message()

            #ダンジョン
                case 40:
                    #マップ切替
                    _scroll_offset = 4
                    scroll_dir = self.get_scroll_direction(_scroll_offset)
                    if scroll_dir in (0,1,2,3):
                        #画面切替時は魔法効果中止
                        if isinstance(self.user.magic.spell, character.Spell):
                            self.user.magic.spell = None
                        self.is_skip_update = True
                        self.stage.dungeon_list[self.dungeon_index].move_room(scroll_dir)
                        match scroll_dir:
                            case 0:
                                self.user.address = [self.user.address[0], _scroll_offset]
                            case 1:
                                self.user.address = [G_.P_MAIN_WND[2] - _scroll_offset, self.user.address[1]]
                            case 2:
                                self.user.address = [_scroll_offset, self.user.address[1]]
                            case 3:
                                self.user.address = [self.user.address[0], G_.P_MAIN_WND[3] - _scroll_offset]
                        self.is_skip_update = False
                        self.background_drawer()
                    #共通描画処理
                    self.draw_common()
                    #ドアオープン
                    for i,doorevent in enumerate(self.stage.dungeon_list[self.dungeon_index].is_door_event):
                        if doorevent[0] == list(self.stage.dungeon_list[self.dungeon_index].now_room_address):
                            if doorevent[1][0]:
                                result = evt.open_door(0, self.counter)
                                self.stage.dungeon_list[self.dungeon_index].door_lock[i][1][0] = result
                                self.stage.dungeon_list[self.dungeon_index].is_door_event[i][1][0] = result
                                self.counter = 0 if result is False else self.counter + 1
                                self.is_skip_update = result
                            if doorevent[1][1]:
                                result = evt.open_door(1, self.counter)
                                self.stage.dungeon_list[self.dungeon_index].door_lock[i][1][1] = result
                                self.stage.dungeon_list[self.dungeon_index].is_door_event[i][1][1] = result
                                self.counter = 0 if result is False else self.counter + 1
                                self.is_skip_update = result
                            if doorevent[1][2]:
                                result = evt.open_door(2, self.counter)
                                self.stage.dungeon_list[self.dungeon_index].door_lock[i][1][2] = result
                                self.stage.dungeon_list[self.dungeon_index].is_door_event[i][1][2] = result
                                self.counter = 0 if result is False else self.counter + 1
                                self.is_skip_update = result
                            if doorevent[1][3]:
                                result = evt.open_door(3, self.counter)
                                self.stage.dungeon_list[self.dungeon_index].door_lock[i][1][3] = result
                                self.stage.dungeon_list[self.dungeon_index].is_door_event[i][1][3] = result
                                self.counter = 0 if result is False else self.counter + 1
                                self.is_skip_update = result
                            break
            #ショップ
                case 50:
                    #背景描画共通呼び出し
                    self.background_drawer(self.now_scene)
                    self.draw_status()
                    self.message_manager.draw_window()
                    match self.shop.shoptype:
                        case 0:
                            px.text(G_.P_MESG_WND[0]+13,G_.P_MESG_WND[1]+26, "装備品の店",
                                    7, G_.JP_FONT)
                            px.text(G_.P_MESG_WND[0]+22,G_.P_MESG_WND[1]+50, "『ボッタクル』",
                                    7, G_.JP_FONT)
                        case 1:
                            px.text(G_.P_MESG_WND[0]+13,G_.P_MESG_WND[1]+26, "日用品の店",
                                    7, G_.JP_FONT)
                            px.text(G_.P_MESG_WND[0]+22,G_.P_MESG_WND[1]+50, "『ぎんぎん』",
                                    7, G_.JP_FONT)
                        case 2:
                            px.text(G_.P_MESG_WND[0]+13,G_.P_MESG_WND[1]+26, "旅人の宿屋",
                                    7, G_.JP_FONT)
                            px.text(G_.P_MESG_WND[0]+22,G_.P_MESG_WND[1]+50, "『十三番』",
                                    7, G_.JP_FONT)
                        case 3:
                            px.text(G_.P_MESG_WND[0]+13,G_.P_MESG_WND[1]+26, "巡礼者の聖殿",
                                    7, G_.JP_FONT)
                            px.text(G_.P_MESG_WND[0]+22,G_.P_MESG_WND[1]+50, "『紫龍牙』",
                                    7, G_.JP_FONT)
                    self.shop.menu.draw()
            #メニュー
                case 60|66:
                    #背景描画共通呼び出し
                    self.background_drawer(self.now_scene)
                    self.draw_status()
                    self.message_manager.draw_window()
                    self.menu.draw()
            #マップ表示
                case 65:
                    #外枠
                    px.rectb(33,33,206,206,0)
                    px.rectb(32,32,208,208,10)
                    px.rectb(31,31,210,210,8)
                    #縮小タイルマップ
                    px.bltm(-68,-68,5, 0,0,  272,272,colkey=0,scale=0.25)
                    px.bltm(-68,  0,5, 272,0,  272,272,colkey=0,scale=0.25)
                    px.bltm(-68, 68,5, 544,0,  272,272,colkey=0,scale=0.25)
                    px.bltm(  0,-68,5, 0,272,  272,272,colkey=0,scale=0.25)
                    px.bltm(  0,  0,5, 272,272,  272,272,colkey=0,scale=0.25)
                    px.bltm(  0, 68,5, 544,272,  272,272,colkey=0,scale=0.25)
                    px.bltm( 68,-68,5, 0,544,  272,272,colkey=0,scale=0.25)
                    px.bltm( 68,  0,5, 272,544,  272,272,colkey=0,scale=0.25)
                    px.bltm( 68, 68,5, 544,544,  272,272,colkey=0,scale=0.25)
                    #区切り線
                    px.rectb(33+68,33,69,206,12)
                    px.rectb(33,33+68,206,69,12)
                    #採取スポット
                    if self.minimap_spot[0][0] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*3)+self.minimap_spot[0][0][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*3)+self.minimap_spot[0][0][1]*2,1,7)
                    if self.minimap_spot[1][0] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*3)+self.minimap_spot[1][0][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[1][0][1]*2,1,7)
                    if self.minimap_spot[2][0] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*3)+self.minimap_spot[2][0][0]*2,
                                G_.P_MAIN_WND[3]*0.5+(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[2][0][1]*2,1,7)
                    if self.minimap_spot[0][1] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[0][1][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*3)+self.minimap_spot[0][1][1]*2,1,7)
                    if self.minimap_spot[2][1] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[2][1][0]*2,
                                G_.P_MAIN_WND[3]*0.5+(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[2][1][1]*2,1,7)
                    if self.minimap_spot[0][2] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5+(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[0][2][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*3)+self.minimap_spot[0][2][1]*2,1,7)
                    if self.minimap_spot[1][2] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5+(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[1][2][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[1][2][1]*2,1,7)
                    if self.minimap_spot[2][2] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5+(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[2][2][0]*2,
                                G_.P_MAIN_WND[3]*0.5+(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[2][2][1]*2,1,7)
                    if self.minimap_spot[1][1] and px.frame_count%32//2 in (0,1,2,3,4,5,6,7):
                        px.circ(G_.P_MAIN_WND[2]*0.5-(G_.P_MAIN_WND[2]//8*1)+self.minimap_spot[1][1][0]*2,
                                G_.P_MAIN_WND[3]*0.5-(G_.P_MAIN_WND[3]//8*1)+self.minimap_spot[1][1][1]*2,1,7)
                    #自キャラ
                    if px.frame_count%12 in (0,1,2,3,4,5):
                        px.circ(G_.P_MAIN_WND[2]*0.5-G_.P_MAIN_WND[2]//8 + self.user.address[0]*0.25,
                                G_.P_MAIN_WND[3]*0.5-G_.P_MAIN_WND[3]//8 + self.user.address[1]*0.25,px.frame_count%2+1,8)
            #ボス戦 #ラスボス戦
                case 70|75:
                    self.draw_bossbattle()
                    if self.boss.is_anger_event:
                        self.is_skip_update = True
                        if evt.anger_boss(self.counter):
                            self.boss.is_anger_event = False
                            if self.user.is_clear:
                                px.images[2].cls(0)
                                px.images[2].load(0, 0, f"assets/image/stage{self.stage_id}u.bmp")
                                self.boss.hp = self.boss.maxhp
                                self.boss.movespeed += 1
                                self.boss.attack *= 1.2
                                self.boss.magic_defend *= 2
                                self.boss.defend *= 1.1
                            sound.load_sounds(self.now_scene)
                            self.counter = 0
                            self.is_skip_update = False
                            return
                        else:
                            self.counter += 1
                        return
            #ステージクリアイベント
                case 80:
                    if self.user.is_clear:
                        match self.stage_id:
                            case 0:
                                self.is_nextstage = evt.interlude_0_u(self.message_window, self.eventstep)
                            case 1:
                                self.is_nextstage = evt.interlude_1_u(self.message_window, self.eventstep)
                            case 2:
                                self.is_nextstage = evt.interlude_2_u(self.message_window, self.eventstep)
                            case 3:
                                self.is_nextstage = evt.interlude_3_u(self.message_window, self.eventstep)
                            case 4:
                                self.is_nextstage = evt.interlude_4_u(self.message_window, self.eventstep)
                    else:
                        match self.stage_id:
                            case 0:
                                self.is_nextstage = evt.interlude_0(self.message_window, self.eventstep)
                            case 1:
                                self.is_nextstage = evt.interlude_1(self.message_window, self.eventstep)
                            case 2:
                                self.is_nextstage = evt.interlude_2(self.message_window, self.eventstep)
                            case 3:
                                self.is_nextstage = evt.interlude_3(self.message_window, self.eventstep)
                            case 4:
                                self.is_nextstage = evt.interlude_4(self.message_window, self.eventstep)
                    self.message_window.draw()
                    self.message_window.draw_message()
            #エンディング1（メッセージウインドウ）
                case 90:
                    if self.user.is_clear:
                        self.is_nextstage = evt.interlude_5_u(self.message_window, self.eventstep)
                    else:
                        self.is_nextstage = evt.interlude_5(self.message_window, self.eventstep)
                    self.message_window.draw()
                    self.message_window.draw_message()
                    if self.message_window.close_counter >= self.message_window.close_timer//2:
                        if self.is_nextstage is False and px.frame_count//8%2 == 0:
                            px.blt(self.message_window.x+self.message_window.width//2-4,
                                self.message_window.y+self.message_window.height-5, G_.IMGIDX["CHIP"],
                                35,248, 5,8, colkey=0, rotate=90)
            #エンディング2（テキストスクロール準備）
                case 91:
                    px.dither(self.counter)
                    px.cls(0)
                    #背景描画共通呼び出し
                    self.background_drawer()
                    #HPウインドウ
                    self.user_hp_window.draw()
                    self.user_hp_window.drawText(self.user_hp_window.x+8, self.user_hp_window.y+8,
                                                [self.user.name, f"{self.user.hp:>11,}"])
                    self.boss_hp_window.draw()
                    self.boss_hp_window.drawText(self.boss_hp_window.x+8, self.boss_hp_window.y+8,
                                                [self.boss.name,f"{self.boss.hp:>11,}"])
                    #キャラクター描画
                    self.user.draw()
                    self.boss.draw()
                    self.message_window.draw()
                    self.message_window.draw_message()

            #エンディング3（テキストスクロール、スタッフロール）
                case 92:
                    px.cls(0)
                    if self.counter >= 1:
                        px.dither(1-self.counter/(G_.GAME_FPS*8))
                    # 流れ星
                    for s in self.stars:
                        s.draw()
                    # メッセージ（中央寄せ、日本語対応）
                    y = self.scroll_y
                    for line in self.ending_messages:
                        text_w = G_.JP_FONT.text_width(line)
                        px.text(px.width//2 - text_w // 2, int(y), line, 7, font=G_.JP_FONT)
                        if self.scroll_y < 1400:
                            y += 48  # 行間
                    if self.scroll_y <= 200:
                        px.text(375,264,"skip", 13)
            #ゲームオーバー
                case 99:
                    if isinstance(self.message_window, menu.Window):
                        if evt.gameover(self.user, self.counter, self.message_window):
                            self.message_window.draw()
                            self.message_window.draw_message()

        except Exception as e:
            comf.error_message(["",f"描画処理で予期せぬ例外が発生しました","",f"情報：",f"{e}",""])
            self.prepare_title()


class Encyclopedia():
    def __init__(self):
        self.monster_list = [] #[ [モンスターID,最終グループID,[宝箱フラググループ1,2,3,4]],[モンスターID...[]] ]
        self.timer_save = G_.GAME_FPS*60 #1分毎に自動でシステムデータをセーブ
        self.load_list()
    
    def add_list(self, mob_id, last_group_id):
        is_published = False
        for i,listed_mob in enumerate(self.monster_list):
            if listed_mob[0] == mob_id:
                is_published = True
                break
        if is_published:
            if last_group_id > self.monster_list[i][1]:
                self.monster_list[i][1] = last_group_id
        else:
            self.monster_list.append([mob_id, last_group_id, [False,False,False,False]])
            self.monster_list.sort()
        return

    def update_chest(self, mob_id, last_group_id):
        if len(self.monster_list) == 0:
            self.add_list(mob_id, last_group_id)
        for i,listed_mob in enumerate(self.monster_list):
            if listed_mob[0] == mob_id:
                break
        self.monster_list[i][2][last_group_id] = True

    def get_list(self):
        return self.monster_list

    def load_list(self):
        cmd = command.CommandSystemData()
        system_data = cmd.load()
        if system_data is False:
            return
        try:
            self.monster_list = cmd.system_data["Encyclopedia"]
        except KeyError:
            pass
        cmd = None

    def save_list(self,app):
        cmd = command.CommandSystemData()
        cmd.save(app)
        cmd = None
        self.timer_save = G_.GAME_FPS*60 #1分毎に自動でシステムデータをセーブ

#******アプリケーション実行******#
if __name__ == "__main__":
    App()