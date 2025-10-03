import pyxel as px
from pathlib import Path
from datetime import datetime
import const as G_
import common_func as comf
import command, item


class Window:
    def __init__(self, x:int, y:int, width:int, height:int, window_type:int=0, close_timer:int=300):
        self.x = x if x + width <= px.width else px.width - width
        self.y = y
        self.width = width
        self.height= height
        self.window_type = window_type #0:待機メッセージ 1:一時メッセージ
        self.close_timer = close_timer
        self.close_counter = 0
        self.message_text = [""]

    def update(self):
        btn = comf.get_button_state()
        match self.window_type:
            case 0:
                if btn["a"]:
                    px.play(3,G_.SNDEFX["pi"], resume=True)
                    return False
                if btn["b"]:
                    return False
            case 1:
                if self.close_counter >= self.close_timer:
                    self.close_counter = 0
                    return False
                elif self.close_counter >= self.close_timer//2:
                    if btn["a"] or btn["b"]:
                        px.play(3,G_.SNDEFX["pi"], resume=True)
                        self.close_counter = 0
                        return False
                else:
                    self.close_counter += 1
        return True

    def draw(self):
        chip_cnt_w = self.width  // G_.P_CHIP_SIZE 
        chip_cnt_h = self.height // G_.P_CHIP_SIZE

        #枠線
        for Ypos in range(chip_cnt_h):
            for Xpos in range(chip_cnt_w):
                #四隅
                if Ypos == 0 and Xpos == 0:
                    px.blt(self.x, self.y, G_.IMGIDX["CHIP"],
                            0, 240, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0) #左上
                elif Ypos == 0 and Xpos == chip_cnt_w-1:
                    px.blt(self.x + self.width - G_.P_CHIP_SIZE, self.y, G_.IMGIDX["CHIP"],
                            8, 240, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0) #右上
                elif Ypos == chip_cnt_h-1 and Xpos == 0:
                    px.blt(self.x, self.y + self.height - G_.P_CHIP_SIZE, G_.IMGIDX["CHIP"],
                            0, 248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0) #左下
                elif Ypos == chip_cnt_h-1 and Xpos == chip_cnt_w-1:
                    px.blt(self.x + self.width - G_.P_CHIP_SIZE, self.y + self.height - G_.P_CHIP_SIZE,
                           G_.IMGIDX["CHIP"], 8, 248,  G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0) #右下
                #枠線
                elif Ypos == 0: #上端
                    px.blt(self.x + (Xpos*G_.P_CHIP_SIZE), self.y, G_.IMGIDX["CHIP"],
                           16, 248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)
                elif Xpos == 0: #左端
                    px.blt(self.x, self.y + (Ypos*G_.P_CHIP_SIZE), G_.IMGIDX["CHIP"],
                           16, 240, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)
                elif Ypos == chip_cnt_h-1: #下端
                    px.blt(self.x + (Xpos*G_.P_CHIP_SIZE), self.y + self.height - G_.P_CHIP_SIZE, G_.IMGIDX["CHIP"],
                           24, 248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0 )
                elif Xpos == chip_cnt_w-1: #右端
                    px.blt(self.x + self.width - G_.P_CHIP_SIZE, self.y + (Ypos*G_.P_CHIP_SIZE), G_.IMGIDX["CHIP"],
                           24, 240, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0 )
                #塗りつぶし
                else:
                    pass
                    px.blt(self.x + (Xpos*G_.P_CHIP_SIZE), self.y + (Ypos*G_.P_CHIP_SIZE), G_.IMGIDX["CHIP"],
                           32, 240, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE )

        if self.close_counter >= self.close_timer//2:
            if px.frame_count//8%2 == 0:
                px.blt(self.x+self.width//2-4,
                    self.y+self.height-5, G_.IMGIDX["CHIP"],
                    35,248, 5,8, colkey=0, rotate=90)

    @classmethod
    def drawText(self, x:int, y:int, text_list:list):
        for i, text in enumerate(text_list):
            px.text(x, y + (i*16+2), text, 0, font=G_.JP_FONT)
        return
    
    def draw_message(self):
        for i, text in enumerate(self.message_text):
            px.text(self.x+8, self.y+8 + (i*16+2), text, 0, font=G_.JP_FONT)
        return
    

class Menu:
    rofs    = 4 #文字出力 行間(pixel)
    fw,fh   = 12, 13 #フォント幅高
    rowpad  = 2 #オブジェクト上下間調整
    _padding_left = 2

    def __init__(self, x:int, y:int, menulist_shape:list, menu_items:list,
                 menutext_length:int=6, menu_type:int=0, parent=None, user=None):
        self.user = user
        self.parent = parent    
        self.menu_items = menu_items     #メニュー項目文字列
        self.menu_shape = menulist_shape    #メニュー項目個数　横,縦
        self.menutext_length = menutext_length      #メニュー項目文字長
        self.menu_type = menu_type       #メニュー種別 
        self.cursor_position = [0,0]     #メニューカーソル選択位置
        self.cursor_address = [0,0]     #メニューカーソル描画アドレス
        self.selectitem_text = ""        #選択メニューの文字列
        _window_width = ((1+1+1) + (1+1+self.menutext_length*2)*self.menu_shape[0])*G_.P_CHIP_SIZE
        _window_height = ((1+1)+ (self.menu_shape[1]*2))*G_.P_CHIP_SIZE 
        if (x + _window_width) > px.width:
            x = px.width - _window_width
        self.menu_window = Window(x, y, _window_width, _window_height, 2)
        self.submenu_instance = ""
        self.is_submenu = False
        self.msg_window = ""
        self.is_msg_window = False
        self.answerYN = 0 #MenuYesNoからのリターン
        self.command_instance = None
        self.is_command = False
        self.message_text = ""
        self.is_close_me = False
        self.is_map = False

    def chkCmdRtn(self):
        flgTmp = self.command_instance.update()
        if flgTmp is not None:
            if isinstance(self.command_instance, command.CommandBuy):
                return False
            else:
                self.is_command = False
                if isinstance(self.parent, Menu):
                    self.parent.is_close_me = True
                return False
        return True

    def update(self):
        if self.is_close_me:
            if isinstance(self.parent, Menu):
                self.parent.is_close_me = True
            return False

        if self.is_command:
            return self.chkCmdRtn()
       
        #サブメニュー表示中
        if self.is_submenu:
            self.is_submenu = self.submenu_instance.update()
            return True
        if self.is_msg_window:
            self.is_msg_window = self.msg_window.update()
            return True
        btn = comf.get_button_state()
        #キャンセル
        if btn["b"]:
            return False
        #決定
        if btn["a"]:
            px.play(3,G_.SNDEFX["pi"], resume=True)

            self.selectitem_text = self.menu_items[self.cursor_position[1] % self.menu_shape[1]] [self.cursor_position[0] % self.menu_shape[0]]
            _subwindow_x, _subwindow_y = self.cursor_address[0], self.cursor_address[1] + G_.P_CHIP_SIZE + 2
            match self.menu_type:
                #フィールドメニュー
                case 0:
                    match self.cursor_position:
                        case [0,0]: #パラメータ
                            self.command_instance = command.CommandStatus(_subwindow_x, _subwindow_y, self.user)
                            self.is_command = True
                        case [0,1]: #インベントリ
                            self.command_instance = command.CommandInventory(_subwindow_x, _subwindow_y, self.user)
                            self.is_command = True
                        case [0,2]: #マップ
                            self.is_map = True
                            return False
                        case [0,3]: #セーブ
                            self.submenu_instance = MenuSave(_subwindow_x, _subwindow_y, self.parent)
                            self.is_submenu = True
                        case [0,4]: #ロード
                            self.submenu_instance = MenuLoad(_subwindow_x, _subwindow_y, self.parent)
                            self.is_submenu = True
                        case [0,5]: #ゲーム終了
                            self.command_instance = command.CommandQuit()
                            self.submenu_instance = MenuYesNo(_subwindow_x, _subwindow_y, ["ゲームを終了します"], self.command_instance, self)
                            self.is_submenu = True
                    return True
                #キャラ選択メニュー
                case 1:
                    return self.menuCharaSelect()
                #商店メニュー
                case 2:
                    return self.menuShop()
                #タイトルメニュー
                case 3:
                    return self.menuTitle()
                #名前入力メニュー
                case 4:
                    return self.menuNameEntry()
                #装備アイテム選択メニュー
                case 5:
                    return self.menuSelectItem()
                #データセーブメニュー
                case 6:
                    return self.menuSave()
                #データロードメニュー
                case 7:
                    return self.menuLoad()
                case _:
                    raise SystemError

            return True
        
        self.moveCursor()

        return True

    def moveCursor(self):
        # btn = comf.get_button_state()
        if px.btnp(px.KEY_W) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_UP) or px.btnp(px.KEY_UP):
        # if btn["u"]:
            self.cursor_position[1] = (self.cursor_position[1]-1)%self.menu_shape[1]
        if px.btnp(px.KEY_A) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btnp(px.KEY_LEFT):
        # elif btn["l"]:
            self.cursor_position[0] = (self.cursor_position[0]-1)%self.menu_shape[0]
        if px.btnp(px.KEY_S) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_DOWN) or px.btnp(px.KEY_DOWN):
        # elif btn["d"]:
            self.cursor_position[1] = (self.cursor_position[1]+1)%self.menu_shape[1]
        if px.btnp(px.KEY_D) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btnp(px.KEY_RIGHT):
        # elif btn["r"]:
            self.cursor_position[0] = (self.cursor_position[0]+1)%self.menu_shape[0]

    def draw(self):
        self.drawMenu()

        if self.is_command:
            self.command_instance.draw(self.cursor_address)

        if self.is_submenu:
            self.submenu_instance.draw()

        if self.is_msg_window:
            self.msg_window.draw()
            self.msg_window.drawText(self.cursor_address[0] +8 ,self.cursor_address[1] + 16, self.message_text, G_.JP_FONT)

    def drawMenu(self):
        #メニューウインドウ枠表示
        self.menu_window.draw()
        #メニュー項目文字表示
        for row in range(self.menu_shape[1]):
            for col in range(self.menu_shape[0]):
                for i,_str in enumerate(self.menu_items[row][col]):
                    px.text(self.menu_window.x+(1+((1+1)*col+(self.menutext_length*2)*col)+(1+1+i*2))*G_.P_CHIP_SIZE,
                            self.menu_window.y+(1 + row*2)*G_.P_CHIP_SIZE,
                            _str, 0, G_.JP_FONT)
        #メニューカーソル表示
        #初期状態
        self.cursor_address = [self.menu_window.x + 
                               #メニュー枠+余白+(カーソル位置(項目n番目)ｘ項目長x2)*チップサイズ(8)
                               (1+(((1)*(self.cursor_position[0]+1)+self.cursor_position[0]+(self.menutext_length*2)*self.cursor_position[0])))
                               *G_.P_CHIP_SIZE - 2,
                               self.menu_window.y +
                               (1+(1+(self.cursor_position[1]*2)))*G_.P_CHIP_SIZE - 5]
        px.blt(*self.cursor_address, G_.IMGIDX["CHIP"], 32,248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)

    #オーバーライド用
    def menuCharaSelect(self):
        pass

    def menuShop(self):
        pass

    def menuTitle(self):
        pass

    def menuNameEntry(self):
        pass

    def menuSelectItem(self):
        pass

    def menuSave(self):
        pass

    def menuLoad(self):
        pass


class MenuYesNo(Menu):
    def __init__(self, x, y, msg:list, command_instance, parent):
        super().__init__(x + 2*G_.P_CHIP_SIZE, y + (len(msg)*2+1)*G_.P_CHIP_SIZE , [1,2],  [["はい"],["いいえ"]], 4, 3)
        self.address = [x,y]
        _textlength = 0
        for texts in msg:
            _textlength = max(len(texts),_textlength)
        _msg_window_width = (_textlength*2+2)*G_.P_CHIP_SIZE
        if x + _msg_window_width > px.width:
            x = px.width - _msg_window_width
        self.message_window  = Window(x, y, _msg_window_width, (len(msg)*2+2)*G_.P_CHIP_SIZE, 0)
        self.message = msg
        self.command_instance     = command_instance
        self.parent = parent

    def update(self):
        if self.is_command:
            return self.chkCmdRtn()
        btn = comf.get_button_state()
        if btn["a"]:
            px.play(3,G_.SNDEFX["pi"], resume=True)
            match self.cursor_position[1] % self.menu_shape[1]:
                case 0:
                    self.command_instance.exec()
                    self.is_command = True
                case 1:
                    return False
            return True
        if btn["b"]:
            if self.is_command:
                return True
            else:
                return False

        self.moveCursor()
        return True

    def draw(self):
        if self.is_command:
            self.command_instance.draw()
        else:
            self.message_window.draw()
            self.message_window.drawText(self.address[0]+8,self.address[1]+8, self.message)
            self.drawMenu()


#ショップ管理クラス（画面表示、接触時の表示対象ショップを管理）
class ShopManager:
    def __init__(self):
        self.shop_list = []

    def create_shop(self, map_address:tuple, address:tuple, shoptype:int, stage_id:int, user ):
        self.shop_list.append(Shop(map_address, address, shoptype, stage_id, user))

    def check_enter(self, user, now_view):
        for shop in self.shop_list:
            if shop.enter_shop(user, now_view):
                shop.reset_cursor()
                return shop
        return False

    def draw(self, now_view):
        for shop in self.shop_list:
            shop.draw(now_view)


def calc_keyprice(base,user,stage_id):
    return (base * (user.level + stage_id**2) + (base * (stage_id**2)))


class Shop:
    def __init__(self, map_address:tuple, address:tuple, shoptype:int, stage_id:int, user):
        self.map_address = map_address
        self.address = address
        self.shoptype = shoptype
        if self.shoptype in (0,1):
            self.menu = MenuShop(self.shoptype, stage_id, user)
        elif self.shoptype == 2:
            self.menu = MenuInn(self.shoptype, stage_id, user)
        elif self.shoptype == 3:
            self.menu = MenuShrine(self.shoptype, stage_id, user)

    def price_hike_keys(self, user, stage_id):
        if self.shoptype == 1:
            price_key = item.get_item_info(32)[2]
            self.menu.item_list[0][3][2] = calc_keyprice(price_key, user, stage_id)

    def reset_cursor(self):
        if self.shoptype in (0,1):
            self.menu.itemlist_index = 0
            self.menu.remap_item()

    def enter_shop(self, user, now_view):
        if self.map_address == tuple(now_view):
            if comf.check_collision_hitbox(self.address[0]%G_.P_MAIN_WND[2],self.address[1]%G_.P_MAIN_WND[3],16,16,
                                           user.address[0], user.address[1] + 2, 12,12):
                return True
        return None

    def draw(self, now_view):
        if self.map_address == tuple(now_view):
            px.blt(self.address[0]%G_.P_MAIN_WND[2]-8,
                    self.address[1]%G_.P_MAIN_WND[3]-8, G_.IMGIDX["CHIP"], 56,240, 16,16, colkey=0)
            px.blt(self.address[0]%G_.P_MAIN_WND[2]-8,
                    max(0,self.address[1]%G_.P_MAIN_WND[3]-14), G_.IMGIDX["CHIP"], self.shoptype*16,224, 16,8, colkey=0)


class MenuInn(MenuYesNo):
    def __init__(self, shoptype, stage_id, user):
        self.fee = int(5*(1.59**user.level)+user.maxhp//1000)

        welcome_message = ["疲れを癒す宿屋へようこそ！","泊って行きますか？",f"お代は {self.fee:,}"]
        _width = (1+len(welcome_message[0])*2+1)*G_.P_CHIP_SIZE
        _height = (1+len(welcome_message)+1)*G_.P_CHIP_SIZE
        _x,_y = G_.P_MAIN_WND[2]//2 - _width//2, G_.P_MAIN_WND[3]//2 - _height//2

        self.inn_command_instance = command.CommandInn(_x+16, _y+16, user, self.fee)
        super().__init__(_x, _y-16, welcome_message, self.inn_command_instance, None)


class MenuShrine(MenuYesNo):
    def __init__(self, shoptype, stage_id, user):
        welcome_message = ["聖なる神殿へよくぞ参られた。","祈りを捧げていきますか？"]
        _width = (1+len(welcome_message[0])*2+1)*G_.P_CHIP_SIZE
        _height = (1+len(welcome_message)+1)*G_.P_CHIP_SIZE
        _x,_y = G_.P_MAIN_WND[2]//2 - _width//2, G_.P_MAIN_WND[3]//2 - _height//2
                
        self.inn_command_instance = command.CommandShrine(_x+16, _y+16, stage_id, user)
        super().__init__(_x, _y-16, welcome_message, self.inn_command_instance, None)


class MenuShop(Menu):
    def __init__(self, shoptype, stage_id, user):
        self.item_list = []
        self.itemlist_index = 0
        self.messege_window = Window(G_.P_MAIN_WND[0], G_.P_MAIN_WND[3]//2-(1+2+1)*G_.P_CHIP_SIZE,
                                     G_.P_MAIN_WND[2], (1+2+1)*G_.P_CHIP_SIZE, 0)
        self.is_push_left = 0
        self.is_push_right = 0
        match shoptype:
            case 0:
                _weaponlist = [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.WEAPONS.items()
                                if _item[0] == 0 and int(_id)%(44+stage_id) >= 40+stage_id]
                _weaponlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.WEAPONS.items()
                                if _item[0] == 1 and int(_id)%(54+stage_id) >= 50+stage_id]
                _weaponlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.WEAPONS.items()
                                if _item[0] == 2 and int(_id)%(64+stage_id) >= 60+stage_id]
                _weaponlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.WEAPONS.items()
                                if _item[0] == 3 and int(_id)%(74+stage_id) >= 70+stage_id]
                self.item_list.append(_weaponlist)

                _armorlist = [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.ARMORS.items()
                                if _item[0] == 4 and int(_id)%(104+stage_id) >= 100+stage_id]
                _armorlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.ARMORS.items()
                                if _item[0] == 5 and int(_id)%(114+stage_id) >= 110+stage_id]
                _armorlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.ARMORS.items()
                                if _item[0] == 6 and int(_id)%(124+stage_id) >= 120+stage_id]
                _armorlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.ARMORS.items()
                                if _item[0] == 7 and int(_id)%(134+stage_id) >= 130+stage_id]
                self.item_list.append(_armorlist)

                _shieldlist = [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.SHIELDS.items()
                                if _item[0] == 8 and int(_id)%(144+stage_id) >= 140+stage_id]
                _shieldlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.SHIELDS.items()
                                if _item[0] == 9 and int(_id)%(154+stage_id) >= 150+stage_id]
                _shieldlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.SHIELDS.items()
                                if _item[0] == 10 and int(_id)%(164+stage_id) >= 160+stage_id]
                _shieldlist += [[int(_id),_item[1],_item[2],_item[3],_item[0]] for _id,_item in item.SHIELDS.items()
                                if _item[0] == 11 and int(_id)%(174+stage_id) >= 170+stage_id]
                self.item_list.append(_shieldlist)

                self.item_list.append([[int(_id),_item[1],_item[2],_item[3],_item[0]]
                                       for _id,_item in item.MAGICS.items()])
                for n,items in enumerate(self.item_list):
                    for i,itemobj in enumerate(items):
                        self.item_list[n][i][1] = f"{G_.ITEM_TYPE[itemobj[4]]}：{self.item_list[n][i][1] }"

                super().__init__(28, 0, [1,len(self.item_list[self.itemlist_index])],
                                 self.item_list[self.itemlist_index], 11, 2, user=user)
            case 1:
                self.item_list = [[[int(_id),_item[1],_item[2],_item[3],_item[0]]
                                  for _id,_item in item.ITEMS.items() if _item[0] == 20]]
                self.item_list[0][1][2] = calc_keyprice(self.item_list[0][1][2], user, stage_id)
                self.item_list[0].insert(-1,[self.item_list[0][0][0],f"{self.item_list[0][0][1]}ｘ１００",
                                          self.item_list[0][0][2]*100,self.item_list[0][0][3]*100,
                                          self.item_list[0][0][4]])
                self.item_list[0].insert(-1,[self.item_list[0][0][0],f"{self.item_list[0][0][1]}ｘ９９９９",
                                          self.item_list[0][0][2]*9999,self.item_list[0][0][3]*9999,
                                          self.item_list[0][0][4]])
                super().__init__(28, px.height//3, [1,len(self.item_list[self.itemlist_index])],
                                 self.item_list[self.itemlist_index], 11, 2, user=user)

    def remap_item(self):
        self.menu_items = self.item_list[self.itemlist_index]
        self.menu_shape[1] = len(self.menu_items)
        self.cursor_position = [0,0]

    def moveCursor(self):
        if px.btnp(px.KEY_W,20,10) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_UP,20,10) or px.btnp(px.KEY_UP,20,10):
            self.cursor_position[1] = (self.cursor_position[1]-1)%self.menu_shape[1]
        if px.btnp(px.KEY_S,20,10) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_DOWN,20,10) or px.btnp(px.KEY_DOWN,20,10):
            self.cursor_position[1] = (self.cursor_position[1]+1)%self.menu_shape[1]
        if len(self.item_list) > 1:
            if px.btnp(px.KEY_A) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btnp(px.KEY_LEFT):
                self.itemlist_index = (self.itemlist_index-1)%4
                self.remap_item()
                self.is_push_left = 1
            if px.btnp(px.KEY_D) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btnp(px.KEY_RIGHT):
                self.itemlist_index = (self.itemlist_index+1)%4
                self.remap_item()
                self.is_push_right = 1

    def menuShop(self):
        _item = self.item_list[self.itemlist_index][self.cursor_position[1]]
        self.Msg = [f"{_item[1]} なら 価格は {_item[2]} です"]
        if len(self.item_list) > 1:
            match self.itemlist_index:
                case 0:
                    now_item_type = self.user.weapon.item_type
                case 1:
                    now_item_type = self.user.armor.item_type
                case 2:
                    now_item_type = self.user.shield.item_type
            if self.itemlist_index == 3:
                if self.user.spellbook[item.get_item_info(_item[0])[0]-12]:
                    self.Msg += ["もう使える属性の魔法だし、すぐに慣れますよ"]
                else:
                    self.Msg += ["初めて使う属性だと、少し慣らしが必要ですね"]
            elif item.get_item_info(_item[0])[0] != now_item_type:
                self.Msg += ["不慣れな武具じゃ素人からやり直しですよ？"]
            else:
                self.Msg += ["買い換えた武具もキチンと慣らして下さいね！"]
            msg_height = G_.P_CHIP_SIZE*5
            self.messege_window.height = (1+4+1)*G_.P_CHIP_SIZE
        else:
            msg_height = G_.P_CHIP_SIZE*3

        self.command_instance = command.CommandBuy(self.messege_window.x, self.messege_window.y, self.messege_window, _item, self.user)
        self.submenu_instance = MenuYesNo(self.cursor_address[0], self.messege_window.y + msg_height, ["購入しますか？"], self.command_instance, self)
        self.is_submenu = True

        return True

    def draw(self):
        self.drawMenu()
        #装備品は左右キーで別リスト展開
        if len(self.item_list) > 1:
            px.blt(self.menu_window.x-(4+16),G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"], 200,240,-16,16,0)
            px.blt(self.menu_window.x+self.menu_window.width+4,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"],
                   200,240,16,16,0)

        if self.is_push_left:
            px.blt(7,G_.P_MAIN_WND[3]//2-10, G_.IMGIDX["CHIP"], 200,240,-16,16,0, scale=2.0)
            self.is_push_left = (self.is_push_left+1)%4
        if self.is_push_right:
            px.blt(self.menu_window.x+self.menu_window.width+9,G_.P_MAIN_WND[3]//2-10,G_.IMGIDX["CHIP"],
                   200,240,16,16,0, scale=2.0)
            self.is_push_right = (self.is_push_right+1)%4

        if self.is_submenu:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8  ,self.messege_window.y + 8, self.Msg)
            self.submenu_instance.draw()

    def drawMenu(self):
        #メニューウインドウ枠表示
        self.menu_window.draw()
        #メニュー項目文字表示
        for row in range(self.menu_shape[1]):
                    _padding = " "*(19-(len(self.menu_items[row][1])*2))
                    _str = f"{self.menu_items[row][1]}{_padding}{self.menu_items[row][2]: >9,.0f}"

                    px.text(self.menu_window.x+(1+1+1)*G_.P_CHIP_SIZE,
                            self.menu_window.y+(1 + row*2)*G_.P_CHIP_SIZE,
                            _str, 0, G_.JP_FONT)
        #メニューカーソル表示
        self.cursor_address = [self.menu_window.x + 
                               #メニュー枠+余白+(カーソル位置(項目n番目)ｘ項目長x2)*チップサイズ(8)
                               (1+(((1)*(self.cursor_position[0]+1)+self.cursor_position[0]+(self.menutext_length*2)*self.cursor_position[0])))
                               *G_.P_CHIP_SIZE - 2,
                               self.menu_window.y +
                               (1+(1+(self.cursor_position[1]*2)))*G_.P_CHIP_SIZE - 5]
        px.blt(*self.cursor_address, G_.IMGIDX["CHIP"], 32,248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)


class MenuNameEntry(Menu):
    def __init__(self):#, Parent):
        self.name_chars = comf.read_json("assets/data/letter.json")
        super().__init__(px.width//2-(376//2), 16, [11,9],  self.name_chars[0], 1 , 4)
        self.prefix     = "名前　：　"
        self.input_name_string  = ""
        self.name_window  = Window(px.width//2 - (G_.P_CHIP_SIZE*(8+5)*2)//2,
                                      px.height//1.5, G_.P_CHIP_SIZE*(8+5)*2, G_.P_CHIP_SIZE*5, 0)
        self.name_string = [self.prefix + self.input_name_string]
        self.msg_window2 = None
        self.is_msg_window2 = False
        self.msg2_string = []
        self.keep_corsor = [0,0]
        self.is_need_redraw = True

    def update(self):
        if self.is_msg_window2:
            self.is_msg_window2 = self.msg_window2.update()
            return True
        btn = comf.get_button_state()
        if btn["a"]:
            self.is_need_redraw = True
            px.play(3,G_.SNDEFX["pi"], resume=True)
            self.selMnu = self.menu_items[self.cursor_position[1]][self.cursor_position[0]]
            match self.selMnu:
                case "ED":
                    if len(self.input_name_string) <= 0:
                        if isinstance(self.msg_window2, Window):
                            del self.msg_window2
                        self.msg_window2 = Window(32,px.height//2-16,
                                                    px.width-64,((1+1+(1*2))*G_.P_CHIP_SIZE), 1,90)
                        self.is_msg_window2 = True
                        self.msg2_string = ["名前が入力されていません"]
                        return True
                    else:
                        return False
                case "片":
                    self.menu_items = self.name_chars[1]
                    return True
                case "英":
                    self.menu_items = self.name_chars[2]
                    return True
                case "平":
                    self.menu_items = self.name_chars[0]
                    return True
            tmpStr = self.input_name_string + self.selMnu
            if len(tmpStr) > 8:
                self.msg_window2 = Window(32,px.height//2-16,
                                            px.width-64,((1+1+(1*2))*G_.P_CHIP_SIZE), 1, 90)
                self.is_msg_window2 = True
                self.msg2_string = ["名前の文字数は８文字が上限です"]
                px.play(3, G_.SNDEFX["don"], resume=True)
                return True
            else:
                self.input_name_string += self.selMnu
        if btn["b"]:
            tmpStr = self.input_name_string[:-1]
            self.input_name_string = tmpStr
            return True
        self.name_string = [self.prefix + self.input_name_string]
        self.moveCursor()
        return True

    def draw(self):
        self.drawMenu() #文字一覧はここで
        self.name_window.draw() #入力名はここ
        self.name_window.drawText(self.name_window.x+8,
                                    self.name_window.y+12, self.name_string)
        if self.is_msg_window2:
            self.msg_window2.draw() #エラーメッセージ用
            self.msg_window2.drawText(self.msg_window2.x+40, self.msg_window2.y+8, self.msg2_string)
        self.is_need_redraw = False


class MenuSelectMagic:
    def __init__(self, user):
        self.user = user
        self.menu_window = Window(10,px.height//2-40, 80,80, 0)
        self.msg_window = Window(self.menu_window.x, self.menu_window.y-32, 
                            self.menu_window.width,32,0)
        self.cursor_position = [0,0]
        self.select_index = self.user.magic.item_type - 12
        match self.select_index:
            case 0:
                self.cursor_position = [0,-1]
            case 1:
                self.cursor_position = [0,1]
            case 2:
                self.cursor_position = [-1,0]
            case 3:
                self.cursor_position = [1,0]
        self.is_map = False

    def update(self):
        _pushed_button = comf.get_button_state()
        if _pushed_button["L"] is False:
            return False
        if _pushed_button["u"]:
            if self.user.spellbook[0]:
                self.cursor_position = [0,-1]
                self.select_index = 0
        elif _pushed_button["d"]:
            if self.user.spellbook[1]:
                self.cursor_position = [0,1]
                self.select_index = 1
        elif _pushed_button["l"]:
            if self.user.spellbook[2]:
                self.cursor_position = [-1,0]
                self.select_index = 2
        elif _pushed_button["r"]:
            if self.user.spellbook[3]:
                self.cursor_position = [1,0]
                self.select_index = 3
        elif _pushed_button["a"]:
            self.user.equip_item(self.user.spellbook[self.select_index])
            self.user.equip_magic_index = self.select_index
            self.user.timer_selectmagic = G_.GAME_FPS//2
            px.play(3, G_.SNDEFX["pi"], resume=True)
            return False
        return True

    def draw(self):
        self.menu_window.draw()
        self.msg_window.draw()
        self.msg_window.drawText(self.msg_window.x+4, self.msg_window.y+8,["魔法属性選択"])
        px.blt(self.menu_window.x+40+self.cursor_position[0]*16-4,
               self.menu_window.y+40+self.cursor_position[1]*16-4,
               G_.IMGIDX["CHIP"], 80,232, 8,8, colkey=0)
        if self.user.spellbook[0]:
            px.blt(self.menu_window.x+32, self.menu_window.y+8, G_.IMGIDX["CHIP"], 0,208, 16,16, colkey=0 )
        if self.user.spellbook[1]:
            px.blt(self.menu_window.x+32, self.menu_window.y+56, G_.IMGIDX["CHIP"], 16,208, 16,16, colkey=0 )
        if self.user.spellbook[2]:
            px.blt(self.menu_window.x+8, self.menu_window.y+32, G_.IMGIDX["CHIP"], 32,208, 16,16, colkey=0 )
        if self.user.spellbook[3]:
            px.blt(self.menu_window.x+56, self.menu_window.y+32, G_.IMGIDX["CHIP"], 48,208, 16,16, colkey=0 )


class MenuSelectItem(Menu):
    def __init__(self, user):
        self.user = user
        self.data = []
        for items in self.user.inventory:
            if items[0] in (31,32,33):
                continue
            if items[1] <= 0:
                continue
            name = item.get_item_info(items[0])[1]
            _strlen = len(name)*2
            name = name+" "*(8-_strlen)
            self.data.append([items[0],f"{name}"])
        self.is_finished = True
        super().__init__(px.width//2, px.height//2-(len(self.data)*G_.P_CHIP_SIZE), [1,len(self.data)],
                         [[_i[1]] for _i in self.data], 5, 5, user = self.user)
        self.msg_window = Window(self.menu_window.x, self.menu_window.y-32, 
                                 self.menu_window.width,32,0)

    def menuSelectItem(self):
        self.user.equip_id[4] = self.data[self.cursor_position[1]][0]
        self.user.timer_selectitem = G_.GAME_FPS//2
        return False
    
    def update(self):
        rc = True
        btn = comf.get_button_state()
        if btn["R"] is False:
            return False
        if btn["b"]:
            return True
        rc = super().update()
        return rc

    def draw(self):
        super().draw()
        self.msg_window.draw()
        self.msg_window.drawText(self.msg_window.x+8,self.msg_window.y+8,["装備アイテム選択"])


def generate_minimap(stage):
    minimap_address = [[(-1,-1),(-1,-1),(-1,-1)],[(-1,-1),stage.now_view,(-1,-1)],[(-1,-1),(-1,-1),(-1,-1)],]
    for map_y in range(0,3):
        for map_x in range(0,3):
            address_x = stage.now_view[0]+map_x-1
            address_y = stage.now_view[1]+map_y-1
            minimap_address[map_y][map_x] = (address_x,address_y) \
                    if [address_x,address_y] in stage.reached_map_address else (-1,-1)
    for map_y in range(0,3):
        for map_x in range(0,3):
            set_tilemap_mini(stage, minimap_address[map_y][map_x], [map_y,map_x], 5)
    return minimap_address

#仮想マップ配列から現在表示位置を元に必要データを抽出してタイルマップを生成(tilemap_idはスクロール時のみ使用)
def set_tilemap_mini(stage, minimap_address_block, offset:list, tilemap_id:int=0):
    shop_x = [-1 for _ in range(4)]
    shop_y = [-1 for _ in range(4)]
    for i,shop in enumerate(stage.shops.shop_list):
        if shop.map_address == tuple(minimap_address_block):
            shop_x[i] = (shop.address[0] - (minimap_address_block[0]*G_.P_MAIN_WND[2])) // 8
            shop_y[i] = (shop.address[1] - (minimap_address_block[1]*G_.P_MAIN_WND[3])) // 8
    boss_x = boss_y = -1
    if stage.boss_orb.is_placed and stage.boss_orb.map_address == list(minimap_address_block):
        boss_x = stage.boss_orb.address[0]// 8
        boss_y = stage.boss_orb.address[1]// 8
    width = G_.P_MAIN_WND[2]//8
    height = G_.P_MAIN_WND[3]//8
    for y in range(height):
        for x in range(width):
            if minimap_address_block[0]<0 or minimap_address_block[1]<0:
                tile_id = (7,1)
            else:
                if x == shop_x[0] - 1 and y == shop_y[0] - 1:
                    tile_id = 10,26
                elif x == shop_x[0] - 1 and y == shop_y[0]:
                    tile_id = 10,27
                elif x == shop_x[0] and y == shop_y[0] - 1:
                    tile_id = 11,26
                elif x == shop_x[0] and y == shop_y[0]:
                    tile_id = 11,27
                elif x == shop_x[1] - 1 and y == shop_y[1] - 1:
                    tile_id = 10,26
                elif x == shop_x[1] - 1 and y == shop_y[1]:
                    tile_id = 10,27
                elif x == shop_x[1] and y == shop_y[1] - 1:
                    tile_id = 11,26
                elif x == shop_x[1] and y == shop_y[1]:
                    tile_id = 11,27
                elif x == shop_x[2] - 1 and y == shop_y[2] - 1:
                    tile_id = 10,26
                elif x == shop_x[2] - 1 and y == shop_y[2]:
                    tile_id = 10,27
                elif x == shop_x[2] and y == shop_y[2] - 1:
                    tile_id = 11,26
                elif x == shop_x[2] and y == shop_y[2]:
                    tile_id = 11,27
                elif x == shop_x[3] - 1 and y == shop_y[3] - 1:
                    tile_id = 10,26
                elif x == shop_x[3] - 1 and y == shop_y[3]:
                    tile_id = 10,27
                elif x == shop_x[3] and y == shop_y[3] - 1:
                    tile_id = 11,26
                elif x == shop_x[3] and y == shop_y[3]:
                    tile_id = 11,27
                elif x == boss_x - 1 and y == boss_y - 1:
                    tile_id = 8,26
                elif x == boss_x - 1 and y == boss_y:
                    tile_id = 8,27
                elif x == boss_x and y == boss_y - 1:
                    tile_id = 9,26
                elif x == boss_x and y == boss_y:
                    tile_id = 9,27
                else:
                    tile_id = stage.virtual_map[minimap_address_block[1]*height + y][minimap_address_block[0]*width + x]
            px.tilemaps[tilemap_id].pset(offset[0]*width+x, offset[1]*height+y, tile_id)


class MenuSelectCharacter(Menu):
    def __init__(self, func_init_user):
        self.func_init_user = func_init_user
        self.item_list = []
        self.itemlist_index = 0
        self.count_push_left = 0
        self.count_push_right = 0
        self.spritedir = [0,1,2,3,6,7,4,5]
        #タイプ、タイプ名、説明、スプライトアドレス(縦位置)
        self.item_list = [[0,["戦士タイプ"],["斧の広範囲攻撃とノックバック距離で敵を蹴散らす",
                                            "重装備の為動きは鈍重で、魔法能力はからっきし",
                                            "",
                                            "初期装備：斧、中装、中盾、ウインド",],2,
                                            ["ＨＰ：１５００",
                                             "筋力度：７０　器用度：５０　敏捷度：５０",
                                             "知性度：１０　賢明度：１５　抵抗度：０５"],"中"],
                          [1,["魔法タイプ"],["魔法の威力を高める杖とストーンの魔法で",
                                            "敵を弾き飛ばす　身軽な分打たれ弱い",
                                            "",
                                            "初期装備：杖、衣服、腕輪、ストーン"],0,
                                            ["ＨＰ：１５００",
                                             "筋力度：００　器用度：２０　敏捷度：２０",
                                             "知性度：７０　賢明度：５０　抵抗度：４０"],"高"],
                          [2,["両道タイプ"],["魔法で足を鈍らせ遠間から槍で串刺しにする",
                                            "武器と魔法でバランスよく戦うタイプ",
                                            "",
                                            "初期装備：槍、軽装、小盾、アイス"],1,
                                            ["ＨＰ：１５００",
                                             "筋力度：４０　器用度：３０　敏捷度：４０",
                                             "知性度：３５　賢明度：３０　抵抗度：２５"],"低"],
        ]
        super().__init__(0,0, [1,9], self.item_list[self.itemlist_index], 16, 2)#, user=user)
        self.menu_window.x = px.width//2 - self.menu_window.width//2
        self.menu_window.y = 24
        self.message_window = Window(self.menu_window.x, self.menu_window.y+self.menu_window.height,
                                     self.menu_window.width, (1+3*2+1)*G_.P_CHIP_SIZE, 0)

    def remap_item(self):
        self.menu_items = self.item_list[self.itemlist_index]

    def moveCursor(self):
        if px.btnp(px.KEY_A) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btnp(px.KEY_LEFT):
            self.itemlist_index = (self.itemlist_index-1)%3
            self.remap_item()
            self.count_push_left = 1
        if px.btnp(px.KEY_D) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btnp(px.KEY_RIGHT):
            self.itemlist_index = (self.itemlist_index+1)%3
            self.remap_item()
            self.count_push_right = 1

    def menuCharaSelect(self):
        self.command_instance = command.CommandCharaSelect(self.message_window.x, self.message_window.y,
                                                           self.itemlist_index, self.func_init_user)
        self.submenu_instance = MenuYesNo(self.menu_window.x+16, self.menu_window.height//2 + G_.P_CHIP_SIZE*3,
                                          [f"{self.menu_items[1][0]}　で　よろしいですか？"], self.command_instance,
                                          self)
        self.is_submenu = True
        return True

    def update(self):
        #サブメニュー表示中
        if self.is_submenu:
            self.is_submenu = self.submenu_instance.update()
            if self.submenu_instance.is_command:
                return False
            return True
        btn = comf.get_button_state()
        #キャンセル
        if btn["b"]:
            px.play(3,G_.SNDEFX["miss"], resume=True)
            return True
        #決定
        if btn["a"]:
            px.play(3,G_.SNDEFX["pi"], resume=True)

            self.menuCharaSelect()
            self.is_submenu = True

            return True
        
        self.moveCursor()

        return True

    def draw(self):
        self.drawMenu()
        #左右キーで別リスト展開
        px.blt(self.menu_window.x-(4+16),self.menu_window.y+self.menu_window.height//2,
               G_.IMGIDX["CHIP"], 200,240,-16,16,0)
        px.blt(self.menu_window.x+self.menu_window.width+4,self.menu_window.y+self.menu_window.height//2,
               G_.IMGIDX["CHIP"], 200,240,16,16,0)
        #左右キー押下時はカーソルを一瞬巨大化
        if self.count_push_left:
            px.blt(self.menu_window.x-24,self.menu_window.y+self.menu_window.height//2, G_.IMGIDX["CHIP"], 200,240,-16,16,0, scale=2.0)
            self.count_push_left = (self.count_push_left+1)%3
        if self.count_push_right:
            px.blt(self.menu_window.x+self.menu_window.width+9,self.menu_window.y+self.menu_window.height//2,G_.IMGIDX["CHIP"],
                   200,240,16,16,0, scale=2.0)
            self.count_push_right = (self.count_push_right+1)%3

        if self.is_submenu:
            self.submenu_instance.draw()

    def drawMenu(self):
        px.cls(0)
        #メニューウインドウ枠表示
        self.menu_window.draw()
        #メニュー項目表示
        header = [str(self.menu_items[1][0])+"(操作難度:"+str(self.menu_items[5])+")"]
        self.menu_window.drawText(self.menu_window.x
                                  +self.menu_window.width//2
                                  -G_.JP_FONT.text_width(str(header))//2
                                  +6,
                                  self.menu_window.y+4, header)
        px.blt(self.menu_window.x+self.menu_window.width//2-8, self.menu_window.y+48, G_.IMGIDX["CHAR"],
               self.spritedir[px.frame_count//32%8]*16, self.menu_items[3]*16,16,16,colkey=3,scale=4.0)
        self.menu_window.drawText(self.menu_window.x+8, self.menu_window.y+90,
                                  self.menu_items[2])
        self.message_window.draw()
        self.message_window.drawText(self.message_window.x+8,self.message_window.y+8,self.menu_items[4])
        px.text(self.message_window.x+32,252, "※初期装備とは異なる装備への買替も可能", 13, font=G_.JP_FONT)



class MenuSavedata(Menu):
    def __init__(self, x, y, app, menu_type):
        slotname = [["データ１"],["データ２"],["データ３"],["データ４"],]
        for i in range(4):
            path = Path(px.user_data_dir("moq","OldARPGlike")+f"savedata{i}.bin")
            if path.exists() is False:
                filedate = "0000/00/00 00:00:00"
            else:
                filedate = f"{datetime.fromtimestamp(path.stat().st_mtime):%Y/%m/%d %H:%M:%S}"
            slotname[i][0] = f"{slotname[i][0]}　{filedate}"

        super().__init__(x, y, [1,4], slotname, 11, menu_type)
        self.app = app
        self.dataslot = 0

    def select_dataslot(self):
        self.dataslot = self.cursor_position[1] % self.menu_shape[1]

    def drawMenu(self):
        #メニューウインドウ枠表示
        self.menu_window.draw()
        #メニュー項目文字表示
        for row in range(self.menu_shape[1]):
            px.text(self.menu_window.x + 3 * G_.P_CHIP_SIZE,
                    self.menu_window.y+(1 + row*2)*G_.P_CHIP_SIZE,
                    self.menu_items[row][0], 0, G_.JP_FONT)
        #メニューカーソル表示
        #初期状態
        self.cursor_address = [self.menu_window.x + 
                               #メニュー枠+余白+(カーソル位置(項目n番目)ｘ項目長x2)*チップサイズ(8)
                               (1+(((1)*(self.cursor_position[0]+1)+self.cursor_position[0]+(self.menutext_length*2)*self.cursor_position[0])))
                               *G_.P_CHIP_SIZE - 2,
                               self.menu_window.y +
                               (1+(1+(self.cursor_position[1]*2)))*G_.P_CHIP_SIZE - 5]
        px.blt(*self.cursor_address, G_.IMGIDX["CHIP"], 32,248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)



class MenuSave(MenuSavedata):
    def __init__(self, x, y, app):
        super().__init__(x, y, app, 6)

    def menuSave(self):
        self.select_dataslot()
        self.command_instance = command.CommandSave(0,0,self.app, self.dataslot)
        self.submenu_instance = MenuYesNo(self.cursor_address[0], self.cursor_address[1] + G_.P_CHIP_SIZE + 2,
                                          ["データをセーブしますか？"], self.command_instance, self)
        self.is_submenu = True
        return True


class MenuLoad(MenuSavedata):
    def __init__(self, x, y, app):
        super().__init__(x, y, app, 7)

    def menuLoad(self):
        self.select_dataslot()
        self.command_instance = command.CommandLoad(0,0,self.app, self.dataslot)
        self.submenu_instance = MenuYesNo(self.cursor_address[0], self.cursor_address[1] + G_.P_CHIP_SIZE + 2,
                                          ["データをロードしますか？"], self.command_instance, self)
        self.is_submenu = True
        return True


class MenuTitle(Menu):
    def __init__(self, now_scene, app):
        if app.is_clear:
            x,y = 112,166
            menushape = [1,6]
            menuitem = [["ニューゲーム"],["ヌルくてニューゲーム"],["データ１をロード"],["データ２をロード"],["データ３をロード"],["データ４をロード"]]
            menulen = 10
        else:
            x,y = 112,174
            menushape = [1,5]
            menuitem = [["ニューゲーム"],["データ１をロード"],["データ２をロード"],["データ３をロード"],["データ４をロード"]]
            menulen = 8
        super().__init__(x,y, menushape, menuitem, menulen, 0)
        self.parent = app
        self.is_clear = app.is_clear
        self.now_scene = now_scene
        self.is_newgame = False
        self.cnt = 1
        self.is_finished = False

    def update(self):
        if self.is_newgame:
            return
        
        if self.is_finished:
            if self.command_instance.update() is not None:
                self.command_instance = None
                self.is_command = self.is_finished = False
                return False

        if self.is_finished is False and self.is_command:
            self.command_instance.exec()
            self.is_finished = True
            if self.command_instance.is_nofile:
                return False
            else:
                return True
        
        if self.is_finished == False:
            btn = comf.get_button_state()
            if btn["a"]:
                px.play(3,G_.SNDEFX["pi"], resume=True)
                cursor_pos = self.cursor_position[1] % self.menu_shape[1]
                if cursor_pos == 0:
                    self.is_finished = self.is_newgame = True
                    self.parent.is_clear_user = False
                    return True
                else:
                    if self.parent.is_clear:
                        cursor_pos -= 1
                    match cursor_pos:
                        case 0:
                            self.is_finished = self.is_newgame = True
                            self.parent.is_clear_user = True
                        case _:
                            self.command_instance = command.CommandLoad(0,0,self.parent, cursor_pos-1)
                            self.is_command = True
                return True
            if btn["b"]:
                return False

        self.moveCursor()

        return None

    def draw(self):
        if self.is_newgame:
            if self.cnt > 0:
                px.dither(self.cnt)
                self.cnt -= 0.01
            else:
               self.parent.is_menu = False
               px.dither(1)

        px.cls(0)
        px.blt(68, 4, G_.IMGIDX["MOB"], 0, 0, 256, 256)
        if self.is_clear:
            #メニュー項目文字表示
            for row in range(self.menu_shape[1]):
                for col in range(self.menu_shape[0]):
                    for i,_str in enumerate(self.menu_items[row][col]):
                        px.text(self.menu_window.x+1
                                +(1+((1+1)*col+(self.menutext_length*2)*col)+(1+1+i*2))*G_.P_CHIP_SIZE,
                                self.menu_window.y+1
                                +(1 + row*2)*G_.P_CHIP_SIZE,
                                _str, 1, G_.JP_FONT)
            #メニュー項目文字表示
            for row in range(self.menu_shape[1]):
                for col in range(self.menu_shape[0]):
                    for i,_str in enumerate(self.menu_items[row][col]):
                        px.text(self.menu_window.x+(1+((1+1)*col+(self.menutext_length*2)*col)+(1+1+i*2))*G_.P_CHIP_SIZE,
                                self.menu_window.y+(1 + row*2)*G_.P_CHIP_SIZE,
                                _str, 7, G_.JP_FONT)

            #メニューカーソル表示
            #初期状態
            self.cursor_address = [self.menu_window.x + 
                                #メニュー枠+余白+(カーソル位置(項目n番目)ｘ項目長x2)*チップサイズ(8)
                                (1+(((1)*(self.cursor_position[0]+1)+self.cursor_position[0]+(self.menutext_length*2)*self.cursor_position[0])))
                                *G_.P_CHIP_SIZE - 2,
                                self.menu_window.y +
                                (1+(1+(self.cursor_position[1]*2)))*G_.P_CHIP_SIZE - 5]
            px.blt(*self.cursor_address, G_.IMGIDX["CHIP"], 32,248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)
        else:
            self.drawMenu()

        px.text(349,264,f"ver.{G_.APP_VERSION}", 13)

        if self.is_command:
            self.command_instance.draw()
            if self.command_instance.is_nofile:
                self.is_newgame = False
                self.cnt = 1


class MenuMonsterList(Menu):
    def __init__(self, monster_list):
        self.monster_list = monster_list
        max_id = max(self.monster_list)[0] if len(monster_list) else 0
        self.item_list = [list(range(j, min(j + 16, max_id + 1))) for j in range(0, max_id + 1, 16)]
        self.itemlist_index = 0

        self.monster_group_index = 0
        self.monster_data = []
        for i in range(6):
            self.monster_data += comf.read_json(f"assets/data/stage{i}.json")
        for boss in comf.read_json(f"assets/data/boss.json"):
            if boss[0] in (4,5):
                anger_def = boss[12]*2
            else:
                anger_def = boss[12]


            self.monster_data.append([boss[0]+80, boss[1], boss[2],[
                                        [boss[4],boss[5],boss[6],boss[7],boss[8],boss[9],"∞",boss[11],
                                        boss[12],boss[13],boss[14],boss[15],boss[16],boss[17],boss[18],
                                        boss[19],boss[20],boss[21],boss[22],boss[23]],

                                        [boss[4],boss[5],boss[6]*0.66,boss[7]*2,boss[8],boss[9],"∞",boss[11],
                                        anger_def,boss[13],boss[14],boss[15],boss[16],boss[17],boss[18],
                                        boss[19],boss[20],boss[21],boss[22],boss[23]],

                                        [boss[4],boss[5],boss[6],boss[7],boss[8],boss[9],"∞",boss[11],
                                        int(boss[12]*1.1),boss[13],boss[14],boss[15],boss[16],boss[17],boss[18],
                                        boss[19],boss[20],boss[21],boss[22],boss[23]],

                                        [int(boss[4]*1.5),boss[5],boss[6]*0.66,boss[7]*2,boss[8],boss[9],"∞",int(boss[11]*1.2),
                                        int(anger_def*1.1),boss[13],int(boss[14]*2),boss[15],boss[16],boss[17],boss[18],
                                        boss[19],boss[20],boss[21],boss[22],boss[23]]
                                        ]
                                    ]
                                   )
        self.detail_monster = []
        self.is_unknown = True
        self.is_group_unknown = True

        self.count_push_left = 0
        self.count_push_right = 0
        self.spritedir = [0,1]
        
        super().__init__(0,0, [1,min(max_id+1,16)], self.item_list[self.itemlist_index], 0, 2)
        self.upper_window = Window(40,0, 232,176, 0)
        self.lower_window = Window(40,176, 232,96, 0)

    def remap_item(self):
        self.menu_items = self.item_list[self.itemlist_index]
        self.menu_shape = [1, len(self.menu_items)]

    def moveCursor(self):
        if px.btnp(px.KEY_W) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_UP) or px.btnp(px.KEY_UP):
            self.cursor_position[1] = (self.cursor_position[1]-1)%self.menu_shape[1]
            return True
        if px.btnp(px.KEY_S) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_DOWN) or px.btnp(px.KEY_DOWN):
            self.cursor_position[1] = (self.cursor_position[1]+1)%self.menu_shape[1]
            return True
        if px.btnp(px.KEY_A) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_LEFT) or px.btnp(px.KEY_LEFT):
            self.itemlist_index = (self.itemlist_index-1)%len(self.item_list)
            self.remap_item()
            self.count_push_left = 1
            self.cursor_position[1] = 0
            return True
        if px.btnp(px.KEY_D) or px.btnp(px.GAMEPAD1_BUTTON_DPAD_RIGHT) or px.btnp(px.KEY_RIGHT):
            self.itemlist_index = (self.itemlist_index+1)%len(self.item_list)
            self.remap_item()
            self.count_push_right = 1
            self.cursor_position[1] = 0
            return True
        return False

    def update(self):
        btn = comf.get_button_state()
        #メニュー終了
        if btn["b"]:
            px.play(3,G_.SNDEFX["miss"], resume=True)
            return False
        #グループ切替
        if len(self.detail_monster): #何も表示していない時は無効
            if px.btnp(px.KEY_LSHIFT) or px.btnp(px.GAMEPAD1_BUTTON_LEFTSHOULDER):
                self.monster_group_index = (self.monster_group_index-1)%4
            if px.btnp(px.KEY_RSHIFT) or px.btnp(px.GAMEPAD1_BUTTON_RIGHTSHOULDER):
                self.monster_group_index = (self.monster_group_index+1)%4
        #カーソル移動＝対象選択
        if self.moveCursor():
            self.monster_group_index = 0

        self.selectitem_text = self.menu_items[self.cursor_position[1] % self.menu_shape[1]]

        self.is_unknown = True
        self.is_group_unknown = True        
        for moblist in self.monster_list:
            if moblist[0] == self.selectitem_text:
                self.is_unknown = False
                if moblist[1] >= self.monster_group_index:
                    self.is_group_unknown = False
                    break
        if self.is_unknown:
            self.detail_monster = []
        else:
            for mobdetail in self.monster_data:
                if mobdetail[0] == self.selectitem_text:
                    self.detail_monster = [mobdetail[1], mobdetail[2], None, moblist[2][self.monster_group_index]]
                    if self.selectitem_text < 8 or self.selectitem_text == 80:
                        fname = "stage0"
                    elif self.selectitem_text < 16 or self.selectitem_text == 81:
                        fname = "stage1"
                    elif self.selectitem_text < 32 or self.selectitem_text == 82:
                        fname = "stage2"
                    elif self.selectitem_text < 48 or self.selectitem_text == 83:
                        fname = "stage3"
                    elif self.selectitem_text < 64 or self.selectitem_text == 84:
                        fname = "stage4"
                    elif self.selectitem_text < 80 or self.selectitem_text == 85:
                        fname = "stage5"

                    if self.is_group_unknown:
                        self.detail_monster[2] = "GROUP UNKNOWN"
                    else:
                        self.detail_monster[2] = mobdetail[3][self.monster_group_index]

                    if self.selectitem_text >= 80 and self.is_group_unknown is False and self.monster_group_index == 3:
                        fname += "u"
                    px.images[G_.IMGIDX["MOB"]].load(0, 0, f"assets/image/{fname}.bmp")

                    break
        return True

    def draw(self):
        self.drawMenu()
        self.upper_window.draw()
        self.lower_window.draw()

        if self.is_unknown:
            px.text(120,112, "UNKNOWN", 0, G_.JP_FONT)
        else:
            if self.selectitem_text >= 80:
                x = 56
                y = 16
                imagescale = 1.25
                imgpos = [self.detail_monster[1][0],
                          self.detail_monster[1][1] + px.frame_count//32%2*self.detail_monster[1][3],]
            else:
                x = 76
                y = 36
                imagescale = 4
                imgpos = [self.detail_monster[1][0] + px.frame_count//32%2*self.detail_monster[1][2],
                          self.detail_monster[1][1],]
            px.blt(x,y, G_.IMGIDX["MOB"], *imgpos,
                # self.detail_monster[1][0] + px.frame_count//32%2*self.detail_monster[1][2], 
                # self.detail_monster[1][1],
                self.detail_monster[1][2], self.detail_monster[1][3], colkey=3,scale=imagescale)
            px.text(128,20, self.detail_monster[0], 0, G_.JP_FONT)
            px.blt(130,50, G_.IMGIDX["CHIP"], 200,240,-16,16,0)
            px.text(130+8,50+5, "L",7)
            px.text(152,52, f"Group{self.monster_group_index+1}", 0, G_.JP_FONT)
            px.blt(193,50, G_.IMGIDX["CHIP"], 200,240,16,16,0)
            px.text(193+6,50+5, "R",7)

        if self.is_group_unknown:
            if self.is_unknown is False:
                px.text(120,112, "GROUP UNKNOWN", 0, G_.JP_FONT)
        else:
            px.text(56,88, "最大ＨＰ　 ： ", 0, G_.JP_FONT)
            px.text(136,88, f"{self.detail_monster[2][0]:9,}", 0, G_.JP_FONT)
            px.text(56,104, "攻撃力　　 ： ", 0, G_.JP_FONT)
            px.text(136,104, f"{self.detail_monster[2][7]:9,}", 0, G_.JP_FONT)
            px.text(56,120, "防御力　　 ： ", 0, G_.JP_FONT)
            px.text(136,120, f"{self.detail_monster[2][8]:9,}", 0, G_.JP_FONT)
            px.text(56,136, "魔法攻撃力 ： ", 0, G_.JP_FONT)
            px.text(136,136, f"{self.detail_monster[2][9]:9,}", 0, G_.JP_FONT)
            px.text(56,152, "魔法防御力 ： ", 0, G_.JP_FONT)
            px.text(136,152, f"{self.detail_monster[2][10]:9,}", 0, G_.JP_FONT)

            px.text(204,88, "魔法減衰率", 0, G_.JP_FONT)
            px.blt(216,103, G_.IMGIDX["CHIP"], 0,208, 16,16, colkey=0, scale=0.75)
            px.text(236,104, f"{self.detail_monster[2][11]:3}%", 0, G_.JP_FONT)
            px.blt(216,119, G_.IMGIDX["CHIP"], 16,208, 16,16, colkey=0, scale=0.75)
            px.text(236,120, f"{self.detail_monster[2][12]:3}%", 0, G_.JP_FONT)
            px.blt(216,135, G_.IMGIDX["CHIP"], 32,208, 16,16, colkey=0, scale=0.75)
            px.text(236,136, f"{self.detail_monster[2][13]:3}%", 0, G_.JP_FONT)
            px.blt(216,151, G_.IMGIDX["CHIP"], 48,208, 16,16, colkey=0, scale=0.75)
            px.text(236,152, f"{self.detail_monster[2][14]:3}%", 0, G_.JP_FONT)

            _agility = self.detail_monster[2][3]
            if _agility >= 245:
                act = "光速"
            elif _agility >= 225:
                act = "音速"
            elif _agility >= 195:
                act = "高速"
            elif _agility >= 145:
                act = "中速"
            elif _agility >= 85:
                act = "低速"
            elif _agility >= 55:
                act = "微速"
            elif _agility >= 30:
                act = "鈍速"
            else:
                act = "最鈍"
            px.text(56,186, f"行動間隔：{act}", 0, G_.JP_FONT)

            _dexterity = self.detail_monster[2][2]
            if _dexterity >= 250:
               spd = "光速"
            elif _dexterity >= 230:
                spd = "音速"
            elif _dexterity >= 195:
                spd = "高速"
            elif _dexterity >= 160:
                spd = "中高"
            elif _dexterity >= 110:
                spd = "中速"
            elif _dexterity >= 80:
                spd = "中低"
            elif _dexterity >= 60:
                spd = "低速"
            elif _dexterity >= 40:
                spd = "微速"
            elif _dexterity >= 20:
                spd = "鈍速"
            else:
                spd = "最鈍"
            px.text(160,186, f"攻撃間隔：{spd}", 0, G_.JP_FONT)

            match self.detail_monster[2][16]:
                case 1: movetype = "彷徨"
                case 2: movetype = "追跡"
                case 3: movetype = "逃走"
                case 4: movetype = "不動"
                case 5: movetype = "転移"
            px.text(56,202, f"移動類型：{movetype}", 0, G_.JP_FONT)

            px.text(160,202, f"弱化抵抗：{self.detail_monster[2][6]:3}", 0, G_.JP_FONT)

            if self.detail_monster[2][19] is None:
                magicname = "なし"
            else:
                magicname = item.get_item_info(self.detail_monster[2][19])[1]
            px.text(56,218, f"使用魔法：{magicname}", 0, G_.JP_FONT)

            px.text(56,234, f"経験値　：{self.detail_monster[2][15]:5,}", 0, G_.JP_FONT)

            if self.detail_monster[3]:
                tresureinfo = f"{item.get_item_info(self.detail_monster[2][17])[1]} x {self.detail_monster[2][18]}"
            else:
                tresureinfo = "不明"
            px.text(56,250, f"宝箱内容：{tresureinfo}", 0, G_.JP_FONT)

    def drawMenu(self):
        #メニューウインドウ枠表示
        self.menu_window.draw()
        #メニュー項目文字表示
        for row in range(self.menu_shape[1]):
            px.text(self.menu_window.x+2*G_.P_CHIP_SIZE,
                    self.menu_window.y+(1 + row*2)*G_.P_CHIP_SIZE,
                    f"{self.menu_items[row]:02}", 0, G_.JP_FONT)
        #メニューカーソル表示
        #初期状態
        self.cursor_address = [self.menu_window.x + G_.P_CHIP_SIZE - 2,
                               self.menu_window.y +
                               (1+(1+(self.cursor_position[1]*2)))*G_.P_CHIP_SIZE - 5]
        px.blt(*self.cursor_address, G_.IMGIDX["CHIP"], 32,248, G_.P_CHIP_SIZE,G_.P_CHIP_SIZE, colkey=0)