import pyxel as px
import const as G_
import common_func as comf
import menu


class App():
    #アプリケーション固有情報初期化
    def init_app(self):
        px.init(G_.P_MAIN_WND[2]+G_.P_SUB_WND[2], G_.P_MAIN_WND[3],
                title="Old ARPG like DataTool", fps=G_.GAME_FPS, quit_key=99999)
        G_.JP_FONT = px.Font(G_.FONTFILE)
        px.load(G_.ASSET_FILE, excl_images=True, excl_tilemaps=True)
        px.images[0].load(0, 0, "assets/image/0.chip.bmp")

    #ゲーム実行状況リセット
    def reset_parameter(self):
        self.message_window = None
        self.is_menu = False
        self.counter = 0
    
    #タイトル画面描画準備
    def prepare_title(self):
        px.dither(1)
        px.cls(0)
        px.images[2].load(0, 0, "assets/image/title.bmp")

        self.now_scene = G_.SCENE["Title"]
        self.menu = menu.Menu(4,4,
                              [1,4], [["バックアップ"],["リストア"],["システム初期化"],["アプリの終了"]], 9,
                              0, self)

    #Pyxel アプリケーション起動
    def __init__(self):
        self.init_app()
        self.prepare_title()
        px.run(self.update, self.draw)

    #Pyxel Update処理
    def update(self):
        try:
            match self.now_scene:
            #タイトル画面
                case 0:
                    if self.menu.update() is False:
                        self.menu.is_close_me = False
                    return
            #メニュー
                case 60:
                    if self.menu.update() is False:
                        self.menu = None
                        self.prepare_title()
                        self.now_scene = 0
                    return
        except Exception as e:
            comf.error_message(["",f"更新処理で予期せぬ例外が発生しました","",f"情報：",f"{e}",""])
            self.prepare_title()

    #Pyxel draw処理
    def draw(self):
        px.cls(0)
        px.blt(px.width-256-8, px.height-180-4, G_.IMGIDX["MOB"], 0, 0, 256, 180)
        try:
            match self.now_scene:
            #タイトル画面
                case 0:
                    self.menu.draw( )
            #メニュー
                case 60|66:
                    #背景描画共通呼び出し
                    self.menu.draw()
        except Exception as e:
            comf.error_message(["",f"描画処理で予期せぬ例外が発生しました","",f"情報：",f"{e}",""])
            self.prepare_title()

#******アプリケーション実行******#
if __name__ == "__main__":
    App()