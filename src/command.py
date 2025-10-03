import pyxel as px
import pickle
import gzip
from pathlib import Path
import const as G_
import common_func as comf
import menu, item, sound
import hashlib


class Commands:
    def __init__(self, x=0, y=0):
        self.msg_window = None
        self.data = None
        self.is_finished = False
        self.is_disp_finished = False
        self.message = []
        
    def keycheck(self):
        btn = comf.get_button_state()
        if btn["a"]:
            px.play(3,G_.SNDEFX["pi"], resume=True)
            return True
        if btn["b"]:
            return False
        return None
    
    def update(self):
        self.is_finished = True
        return self.keycheck()
    
    def draw(self):
        raise NotImplementedError
    
    def exec(self):
        raise NotImplementedError


class CommandStatus(Commands):
    def __init__(self, x, y, user):
        super().__init__(self)
        self.user = user
        self.param1_window = menu.Window(x, y, G_.P_CHIP_SIZE*36,G_.P_CHIP_SIZE*14,0)
        self.param2_window = menu.Window(x, y+107, G_.P_CHIP_SIZE*36,G_.P_CHIP_SIZE*10,0)
        self.param3_window = menu.Window(x, y+182, G_.P_CHIP_SIZE*36,G_.P_CHIP_SIZE*6,0)

    def update(self):
        if not self.is_finished:
            spellname = []
            for _spell_id in self.user.spellbook:
                if _spell_id is False:
                    spellname.append("なし")
                else:
                    spellname.append(item.get_item_info(_spell_id)[1])

            equip_name = []
            for name in (self.user.weapon.name, self.user.armor.name, self.user.shield.name, self.user.magic.name):
                strlen_ = len(name)*2
                equip_name.append(name + " " * (13 - strlen_))
            for name in (spellname[0], spellname[1], spellname[2], spellname[3]):
                strlen_ = len(name)*2
                equip_name.append(name + " " * (11 - strlen_))
            _strength = min(255,self.user.strength*2) if self.user.is_str_up else self.user.strength
            _agility = min(255,self.user.agility*2) if self.user.is_agi_up else self.user.agility
            _intelligence = min(255,self.user.intelligence*2) if self.user.is_int_up else self.user.intelligence
            self.data1 = [
                f"レベル　　  ：{self.user.level: >9}　　　筋力度 ：{_strength: >4}",
                f"最大ＨＰ　  ：{self.user.maxhp: >9,.0f}　　　器用度 ：{self.user.dexterity: >4}",
                f"攻撃力　　  ：{self.user.attack: >9,.0f}　　　敏捷度 ：{_agility: >4}",
                f"防御力　　  ：{self.user.defend: >9,.0f}　　　知性度 ：{_intelligence: >4}",
                f"魔法攻撃力  ：{self.user.magic_power: >9,.0f}　　　賢明度 ：{self.user.wisdom: >4}",
                f"魔法防御力  ：{self.user.magic_defend: >9,.0f}　　　抵抗度 ：{self.user.magicregistance: >4}",
            ]
            self.data2 = [
                f"武器　　　  ：（{G_.ITEM_TYPE[self.user.weapon.item_type]}）　{equip_name[0]}　{self.user.exp_weapon:06.2f}％",
                f"防具　　　  ：（{G_.ITEM_TYPE[self.user.armor.item_type]}）{equip_name[1]}　{self.user.exp_armor:06.2f}％",
                f"盾　　　　  ：（{G_.ITEM_TYPE[self.user.shield.item_type]}）{equip_name[2]}　{self.user.exp_shield:06.2f}％",
                f"魔法　　　  ：（{G_.ITEM_TYPE[self.user.magic.item_type]}）{equip_name[3]}　{self.user.exp_magic[self.user.equip_magic_index]:06.2f}％",
            ]
            self.data3 = [
                f"火){equip_name[4]}{self.user.exp_magic[0]:06.2f}％ 氷){equip_name[5]}{self.user.exp_magic[1]:06.2f}％",
                f"風){equip_name[6]}{self.user.exp_magic[2]:06.2f}％ 土){equip_name[7]}{self.user.exp_magic[3]:06.2f}％",
                ]
            self.is_finished = True
        return self.keycheck()

    def draw(self, P_adrCursor):
        if self.is_finished:
            self.param1_window.draw()
            self.param1_window.drawText(self.param1_window.x + 8 ,self.param1_window.y + 8, self.data1)
            self.param2_window.draw()
            self.param2_window.drawText(self.param2_window.x + 8 ,self.param2_window.y + 8, self.data2)
            self.param3_window.draw()
            self.param3_window.drawText(self.param3_window.x + 8 ,self.param3_window.y + 8, self.data3)


class CommandInventory(Commands):
    def __init__(self, x, y, user):
        super().__init__(self)
        self.user = user
        self.data = [f" アイテム　 個数　 熟練度"]
        
        for item_ in self.user.inventory:
            mark_in_effect = " "
            if item_[0] in (31,32,33):
                continue
            name = item.get_item_info(item_[0])[1]
            strlen_ = len(name)*2
            name = name + " " * (9 - strlen_)
            if (item_[0] == 10 and user.timer_item[0] > 0) or \
                    (item_[0] == 11 and user.timer_item[1] > 0) or \
                    (item_[0] == 12 and user.timer_item[2] > 0) or \
                    (item_[0] == 13 and user.timer_item[3] > 0) or \
                    (item_[0] == 14 and user.timer_item[4] > 0) or \
                    (item_[0] == 15 and user.timer_item[5] > 0) or \
                    (item_[0] == 16 and user.timer_item[6] > 0) or \
                    (item_[0] == 17 and user.timer_item[7] > 0) or \
                    (item_[0] == 18 and user.timer_item[8] > 0) :
                mark_in_effect = "*"

            self.data.append(f"{mark_in_effect}{name}　({int(item_[1]):>2})　 {item_[2]:>06.2f}％")
        self.is_finished = True
        self.msg_window = menu.Window(x, y, G_.P_CHIP_SIZE*23,G_.P_CHIP_SIZE*(len(self.data)*2+2),0)

    def update(self):
        return self.keycheck()
    
    def draw(self, P_adrCursor):
        if self.is_finished:
            self.msg_window.draw()
            self.msg_window.drawText(P_adrCursor[0] + 8 ,P_adrCursor[1] + 16, self.data)


class CommandQuit(Commands):
    def __init__(self):
        pass

    def exec(self):
        px.quit()


class CommandCharaSelect(Commands):
    def __init__(self, x, y, select_index, fnc_init_user):
        super().__init__(x,y)
        self.select_index = select_index
        self.fnc_init_user = fnc_init_user

    def exec(self):
        self.fnc_init_user(self.select_index)
        px.cls(0)
        return
    
    def draw(self):
        pass


class CommandBuy(Commands):
    def __init__(self, x, y, insW, iteminfo, user):
        super().__init__(self)
        self.messege_window=insW
        self.user = user
        self.iteminfo = iteminfo

        self.is_bought   = False

    def exec(self):
        if self.user.gold < self.iteminfo[2]:
            self.msg = ["所持金不足ですね。どうぞお引き取りを。"]
            self.is_finished = True

        if not self.is_finished:
            item.pick_item(self.iteminfo[0], self.iteminfo[3], self.user)

            self.user.gold -= self.iteminfo[2]
            self.msg = ["お買い上げありがとうございます！"]
            px.play(2, G_.SNDEFX["buy"], resume=True)
            self.is_finished = True

        if self.keycheck() != None:
            return True
        
        return None

    def draw(self):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x +8 ,self.messege_window.y + 8, self.msg)
            self.is_disp_finished = True


class CommandInn(Commands):
    def __init__(self, x, y, user, fee, insW = None):
        super().__init__(self)
        if isinstance(insW,menu.Window):
            self.messege_window=insW
        else:
            self.messege_window = menu.Window(x, y, G_.P_CHIP_SIZE*13*2,G_.P_CHIP_SIZE*8,0)
        self.user = user
        self.is_stay = False
        self.fee = fee

    def exec(self):
        self.msg = ""
        if self.user.gold < self.fee:
            self.msg = ["所持金が足りないようです。","お帰りはあちらですよ？"]
            self.is_finished = self.is_stay = True

        if self.is_stay is False:
            self.user.hp = self.user.maxhp
            self.user.timer_fire = 0
            self.user.timer_ice = 0
            self.user.timer_wind = 0
            self.user.gold -= self.fee
            self.msg = ["ゆっくり休息して","完全に回復した"]
            self.is_finished = self.is_stay = True

        if self.keycheck() != None:
            return True
        return None

    def draw(self):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x +8 ,self.messege_window.y + 8, self.msg)
            self.is_stay = False


class CommandShrine(Commands):
    def __init__(self, x, y, stage_id, user, insW = None):
        super().__init__(self)
        if isinstance(insW,menu.Window):
            self.messege_window=insW
        else:
            self.messege_window = menu.Window(x, y, G_.P_CHIP_SIZE*18*2,G_.P_CHIP_SIZE*6,0)
        self.user = user
        self.stage_id = stage_id
        self.cnt = 0

    def exec(self):
        _level = [_lv for _lv in G_.LEVEL_UP if _lv[1] <= self.user.experience and _lv[0] > self.user.level]
        if _level: #複数レベルアップの場合を考慮してループ処理
            for _ in _level:
                self.user.level += 1
                self.user.maxhp += (self.user.level - self.stage_id -1) * 2000
                self.user.strength = min(255,self.user.strength+5)
                self.user.dexterity = min(255,self.user.dexterity+5)
                self.user.agility = min(255,self.user.agility+5)
                self.user.intelligence = min(255,self.user.intelligence+5)
                self.user.wisdom = min(255,self.user.wisdom+5)
                self.user.magicregistance = min(255,self.user.magicregistance+5)
            self.user.defend = self.user.calc_status(self.user.armor.value, self.user.exp_armor)
            self.user.calc_attack()
            self.user.calc_magic_power()
            self.user.calc_magic_defend()
            self.user.action_waittime = self.user.set_action_waittime()
            self.user.attack_waittime = self.user.set_attack_waittime()
            self.msg = [f"あなたはレベル{self.user.level}になりました！","強きものに祝福を！！"]
        elif self.user.level == 33:
            self.msg = [f"あなたは既に人の高みを極めました。","どうか世の末に導きを…"]
        else:
            _level = [_lv for _lv in G_.LEVEL_UP if _lv[0] == self.user.level + 1]
            self.msg = [f"力を得るには更なる経験が{_level[0][1]-self.user.experience}必要です。",
                        "より一層精進されますように。"]

        if self.keycheck() != None:
            return True
        return None

    def draw(self):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x +8 ,self.messege_window.y + 8, self.msg)
            self.is_finished = False


class CommandSave(Commands):
    def __init__(self, x, y, app, data_no:int):
        super().__init__(self)
        self.messege_window = menu.Window(16,88,px.width - (G_.P_CHIP_SIZE*2*2),(1+1*2+1)*G_.P_CHIP_SIZE,1)
        self.app = app
        self.data_no = data_no
        self.GameData = {}

    def exec(self):
        if not self.is_finished:
            self.GameData["HEADER"] = G_.DATA_HEADER #不正データチェック用
            #アプリケーション固有情報
            self.GameData["now_scene"] = self.app.user.user_scene
            self.GameData["stage_id"] = self.app.stage_id
            #保持すべきステータス
            self.GameData["is_boss"] = self.app.is_boss
            self.GameData["is_skip_update"] = self.app.is_skip_update
            self.GameData["is_onstair"] = self.app.is_onstair
            self.GameData["is_onshop"] = self.app.is_onshop
            self.GameData["dungeon_index"] = self.app.dungeon_index
            #ゲームの中核インスタンス
            self.GameData["message"] = self.app.message_manager
            self.GameData["user"] = self.app.user
            self.GameData["stage"] = self.app.stage
            
            raw = pickle.dumps(self.GameData)
            compressed = gzip.compress(raw)
            # encrypted = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(compressed))
            hash_value = hashlib.sha256(compressed).digest()  # 新形式: ハッシュ計算
            hashed_data = hash_value + compressed  # 新形式: ハッシュ + 圧縮データ
            path = Path(px.user_data_dir("moq","OldARPGlike")+f"savedata{self.data_no}.bin")
            with open(path, "wb") as f:
                # f.write(G_.DATA_HEADER + encrypted)
                f.write(G_.DATA_HEADER + hashed_data)
            #システムデータのセーブ
            self.app.encyclopedia.save_list(self.app)

            px.play(3, G_.SNDEFX["save"], resume=True)
            px.flip()
            self.is_finished=True
    
    def draw(self, P_adrCursor=None):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["セーブが完了しました"])


class CommandLoad(Commands):
    def __init__(self, x, y, app, data_no:int):
        super().__init__(self)
        self.messege_window = menu.Window(16,88,px.width - (G_.P_CHIP_SIZE*2*2),(1+1*2+1)*G_.P_CHIP_SIZE,1)
        self.GameData  = {}
        self.app = app
        self.data_no = data_no
        self.is_nofile = False

    def exec(self):
        path = Path(px.user_data_dir("moq","OldARPGlike")+f"savedata{self.data_no}.bin")
        if path.exists() is False:
            self.is_nofile = True
            return False

        if not self.is_finished:
            self.app.reset_parameter()
            self.app.reset_stage_parameter()

            with open(path, "rb") as f:
                savedata = f.read()

            if not savedata.startswith(G_.DATA_HEADER):
                comf.error_message(["Invalid save data"])
                return False

            savedata_body = savedata[len(G_.DATA_HEADER):]  # HEADER除去後のデータ
            # 新形式（ハッシュ）試行
            hash_value = savedata_body[:32]  # SHA-256ハッシュ（32バイト）
            compressed = savedata_body[32:]
            if hashlib.sha256(compressed).digest() == hash_value:  # ハッシュ一致
                raw = gzip.decompress(compressed)
                self.GameData = pickle.loads(raw)
                if self.GameData["HEADER"] != G_.DATA_HEADER:
                    comf.error_message(["Invalid save data"])
                # 成功: 新形式ロード完了
            else:
                compressed = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(savedata_body))  # XORデクリプト
                raw = gzip.decompress(compressed)
                self.GameData = pickle.loads(raw)
                if self.GameData["HEADER"] != G_.DATA_HEADER:
                    comf.error_message(["Invalid save data"])
                # 成功: 旧形式ロード完了

            #アプリケーション固有情報
            self.app.now_scene = self.GameData["now_scene"]
            self.app.stage_id = self.GameData["stage_id"]
            px.images[2].cls(0)
            px.images[2].load(0, 0, f"assets/image/stage{self.app.stage_id}.bmp")
            #保持すべきステータス
            self.app.is_boss = self.GameData["is_boss"]
            self.app.is_skip_update = self.GameData["is_skip_update"]
            self.app.is_onstair = self.GameData["is_onstair"]
            self.app.is_onshop = self.GameData["is_onshop"]
            self.app.dungeon_index = self.GameData["dungeon_index"]
            #ゲームの中核インスタンス
            self.app.message_manager = self.GameData["message"]
            self.app.user = self.GameData["user"]
            self.app.reset_levelup_info()

            self.app.stage = self.GameData["stage"]
            self.app.stage.message_manager.clear_message()
            self.app.stage.message_manager.timer_message = 0
            self.app.stage.ref_user = self.app.user

            match self.app.now_scene:
                case 30:
                    self.app.background_drawer = self.app.stage.draw
                    self.app.stage.set_tilemap()
                    self.app.stage.monsters.set_mobgroup_index(self.app.stage.now_view)
                case 40:
                    self.app.background_drawer = self.app.stage.dungeon_list[self.app.dungeon_index].draw
                    self.app.stage.dungeon_list[self.app.dungeon_index].set_tilemap_dungeon()
                    self.app.stage.dungeon_list[self.app.dungeon_index].monsters.set_mobgroup_index(
                            self.app.stage.dungeon_list[self.app.dungeon_index].now_room_address)
            px.stop()
            px.cls(0)
            if px.play_pos(3) is None:
                px.play(3, G_.SNDEFX["load"])
                while px.play_pos(3) is not None:
                    pass
                px.flip()

            sound.load_sounds(self.app.now_scene)

            self.is_finished = True
    
        return True

    def draw(self,P_adrcursor=None):
        if self.is_nofile:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["データが存在しません"])
            self.is_disp_finished = True
            return


class CommandSystemData(Commands):
    def __init__(self):
        super().__init__(self)
        self.filename = ".sysdat.bin"
        self.path = Path(px.user_data_dir("moq","OldARPGlike")+f"{self.filename}")
        self.system_data = {}
        if self.path.exists() is False:
            self.system_data["key"] = G_.ENCRYPT_KEY
            self.system_data["clear"] = False
            self.system_data["alert_key"] = False
            self.system_data["alert_LvUp"] = False
            self.system_data["alert_gold"] = False
            self.system_data["alert_group"] = False
            self.system_data["alert_map"] = False
            self.system_data["alert_torch"] = False
            self.system_data["alert_zone"] = False
            self.system_data["alert_mattock"] = False
            self.write_systemdata()
        else:
            self.system_data = self.load()
            self.system_data.setdefault("clear", False)
            self.system_data.setdefault("alert_key",False)
            self.system_data.setdefault("alert_LvUp",False)
            self.system_data.setdefault("alert_gold",False)
            self.system_data.setdefault("alert_group",False)
            self.system_data.setdefault("alert_map",False)
            self.system_data.setdefault("alert_torch",False)
            self.system_data.setdefault("alert_zone",False)
            self.system_data.setdefault("alert_mattock",False)
            self.write_systemdata()

    def save(self, app):
        self.system_data = self.load()
        self.system_data["Encyclopedia"] = app.encyclopedia.monster_list
        self.system_data["clear"] = app.is_clear
        self.system_data["alert_key"] = app.is_alert_key
        self.system_data["alert_LvUp"] = app.is_alert_LvUp
        self.system_data["alert_gold"] = app.is_alert_gold
        self.system_data["alert_group"] = app.is_alert_group
        self.system_data["alert_map"] = app.is_alert_map
        self.system_data["alert_torch"] = app.is_alert_torch
        self.system_data["alert_zone"] = app.is_alert_zone
        self.system_data["alert_mattock"] = app.is_alert_mattock
        return self.write_systemdata()

    def write_systemdata(self):
        raw = pickle.dumps(self.system_data)
        compressed = gzip.compress(raw)
        hash_value = hashlib.sha256(compressed).digest()  # 新形式: ハッシュ計算
        hashed_data = hash_value + compressed  # 新形式: ハッシュ + 圧縮データ
        try:
            with open(self.path, "wb") as f:
                f.write(hashed_data + G_.DATA_HEADER)
        except Exception:
            comf.error_message(["Couldn't save system data"])
            px.quit()
        return True

    def load(self):
        try:
            with open(self.path, "rb") as f:
                savedata = f.read()
        except Exception:
            comf.error_message(["Couldn't load system data"])
            px.quit()
        if not savedata.endswith(G_.DATA_HEADER):
            comf.error_message(["Invalid system data"])
            px.quit()
        encrypted_or_hashdata = savedata[:-len(G_.DATA_HEADER)]  # HEADER除去後のデータ
        # 新形式（ハッシュ）試行
        hash_value = encrypted_or_hashdata[:32]  # SHA-256ハッシュ
        savedata_body = encrypted_or_hashdata[32:]
        if hashlib.sha256(savedata_body).digest() == hash_value:  # ハッシュ一致
            raw = gzip.decompress(savedata_body)
            self.system_data = pickle.loads(raw)
            if self.system_data["key"] != G_.ENCRYPT_KEY:  # 元のkey検証（互換性で残す）
                comf.error_message(["Invalid system data"])
            return self.system_data  # 成功: 新形式ロード
        else:
        # 旧形式（XOR）試行
            savedata_body = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(encrypted_or_hashdata))  # XORデクリプト
            raw = gzip.decompress(savedata_body)
            self.system_data = pickle.loads(raw)
            if self.system_data["key"] != G_.ENCRYPT_KEY:
                comf.error_message(["Invalid system data"])
                px.quit()
            return self.system_data  # 成功: 旧形式ロード
