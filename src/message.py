import pyxel as px
import const as G_

class MessageManager:
    def __init__(self):
        self.message_list = []
        self.timer_message = 0

    def update(self):
        self.timer_message += 1

    def clear_message(self):
        self.message_list.clear()

    def add_message(self, message_text:str, textcolor:int=7):
        self.message_list.append([self.timer_message, message_text, textcolor])
        while len(self.message_list) > 10:
            self.message_list.pop(0)

    def countdown_message(self):
        self.update()
        for i,msg in enumerate(self.message_list):
            if self.timer_message - msg[0] > 5*G_.GAME_FPS:
                self.message_list.pop(i)

    def get_message(self, index:int):
        return self.message_list[index]
    
    def draw_window(self):
        px.bltm(G_.P_MESG_WND[0],G_.P_MESG_WND[1], 7, 
                0,G_.P_MESG_WND[1], G_.P_MESG_WND[2],G_.P_MESG_WND[3], colkey=7)
        
        #角は画像反転で描画
        px.blt(G_.P_MESG_WND[0], G_.P_MESG_WND[1], 0,
                96,0, 8,8, colkey=7)
        px.blt(G_.P_MESG_WND[0]+G_.P_MESG_WND[2]-8, G_.P_MESG_WND[1], 0,
                96,0, -8,8, colkey=7)
        px.blt(G_.P_MESG_WND[0], G_.P_MESG_WND[1]+G_.P_MESG_WND[3]-8, 0,
                96,0, 8,-8, colkey=7)
        px.blt(G_.P_MESG_WND[0]+G_.P_MESG_WND[2]-8, G_.P_MESG_WND[1]+G_.P_MESG_WND[3]-8, 0,
                96,0, -8,-8, colkey=7)

    def draw_message(self):
        #メッセージエリア枠線描画
        self.draw_window()
        line = 6
        for msgdata in self.message_list:
            px.text(G_.P_MESG_WND[0]+5,G_.P_MESG_WND[1]+line, msgdata[1], msgdata[2], G_.JP_FONT)
            line += 14

    