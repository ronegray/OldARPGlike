import pyxel as px
from pathlib import Path
from datetime import datetime
import const as G_
import common_func as comf
import command


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
                        case [0,0]: #バックアップ
                            self.datalist = MenuSavedata(0,0,self.parent,6)
                            messages = []
                            for msg in self.datalist.menu_items:
                                messages += msg
                            messages += ["これらのバックアップアーカイブを作成します","データをバックアップしますか？"]
                            self.command_instance = command.CommandBackup()
                            self.submenu_instance = MenuYesNo(self.cursor_address[0],
                                                              self.cursor_address[1] + G_.P_CHIP_SIZE + 2, messages,
                                                              self.command_instance, self)
                            self.is_submenu = True
                        case [0,1]: #リストア
                            self.datalist = MenuSavedata(0,0,self.parent,6)
                            messages = []
                            for msg in self.datalist.menu_items:
                                messages += msg
                            messages += ["リストアすると既存のセーブデータは削除されます","データをリストアしますか？"]
                            self.command_instance = command.CommandRestore()
                            self.submenu_instance = MenuYesNo(self.cursor_address[0],
                                                              self.cursor_address[1] + G_.P_CHIP_SIZE + 2, messages,
                                                              self.command_instance, self)
                            self.is_submenu = True
                        case [0,2]: #システムデータ削除
                            messages = ["初期化すると以下の情報が削除されます"]
                            self.submenu_instance = command.CommandSystemData()
                            systemdata = self.submenu_instance.load()
                            cleard = " True" if systemdata["clear"] else "False"
                            messages += ["＝現在の状態＝"]
                            messages += [f"　クリアフラグ：{cleard} -> False"]
                            messages += [f"　図鑑登録数　：{len(systemdata["Encyclopedia"]):>5} -> 0"]
                            messages += ["","システムを初期化しますか？"]
                            self.command_instance = command.CommandDeleteSystem()
                            self.submenu_instance = MenuYesNo(self.cursor_address[0],
                                                              self.cursor_address[1] + G_.P_CHIP_SIZE + 2, messages,
                                                              self.command_instance, self)
                            self.is_submenu = True
                        case [0,3]: #アプリ終了
                            self.command_instance = command.CommandQuit()
                            self.submenu_instance = MenuYesNo(_subwindow_x, _subwindow_y, ["アプリを終了します"], self.command_instance, self)
                            self.is_submenu = True
                    return True
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
        _msg_window_width = int(_textlength*1.6+2)*G_.P_CHIP_SIZE
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



# class MenuBackup(Menu):
#     def __init__(self, x, y, app):
#         super().__init__(x, y, app, 6)

#     def menuSave(self):
#         self.select_dataslot()
#         self.command_instance = command.CommandBackup(0,0,self.app, self.dataslot)
#         self.submenu_instance = MenuYesNo(self.cursor_address[0], self.cursor_address[1] + G_.P_CHIP_SIZE + 2,
#                                           ["セーブデータのバックアップアーカイブを作成します","データをバックアップしますか？"], self.command_instance, self)
#         self.is_submenu = True
#         return True
    


# class MenuLoad(MenuSavedata):
#     def __init__(self, x, y, app):
#         super().__init__(x, y, app, 7)

#     def menuLoad(self):
#         self.select_dataslot()
#         self.command_instance = command.CommandRestore(0,0,self.app, self.dataslot)
#         self.submenu_instance = MenuYesNo(self.cursor_address[0], self.cursor_address[1] + G_.P_CHIP_SIZE + 2,
#                                           ["データをロードしますか？"], self.command_instance, self)
#         self.is_submenu = True
#         return True

