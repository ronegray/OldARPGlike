###定数ファイル 

#辞書
SNDEFX = {"buy":40,"menu":41,"tdr1":42,"tdr2":43,"save":44,"load":45,"crush":46,"defeat":47,"dead":48, "pick":49,
          "po":50,"stair":51,"open":52,"unlock":53,"item":54,"special":55, "run":56, "pi":57, "spell":58, "damage":59, 
          "miss":60, "critical":61, "attack":62, "don":63}
IMGIDX = {"CHIP":0, "CHAR":1, "MOB":2}
SCENE  = {"Title":0, "SelectChara":10, "Opening":15, "NameEntry":20,"StagePrepare":25,"StageStart":29,
          "Field":30, "Dungeon":40, "Shop":50, "Menu":60, "Map":65, "MobList":66,
          "BossBattle":70, "LastBoss":75, "StageClear":80, "Ending":90,"GameOver":99 }

#リスト／タプル
ITEM_TYPE = ("杖","剣","槍","斧","衣服","軽装","中装","重装","腕輪","小盾","中盾","大盾",
             "火術","氷術","風術","土術","xx","財宝","継続","消費","消耗","霊薬",)
MENU_ITEM = [["パラメータ"],["インベントリ"],["マップ"],["データセーブ"],["データロード"],["ゲーム終了"]]
CHARA_DIR = ((0,1),(-1,0),(1,0),(0,-1))  #キャラの向き 0:下（正面）1:左 2:右 3:上（背面）
LEVEL_UP = ((2,500),(3,1500),(4,3000),(5,5000),(6,8000),(7,12000),(8,18000),(9,26000),(10,37000),
(11,51000),(12,69000),(13,91000),(14,118000),(15,151000),(16,190000),(17,236000),(18,290000),(19,353000),
(20,425000),(21,507000),(22,600000),(23,704000),(24,820000),(25,950000),(26,1094000),(27,1254000),(28,1430000),
(29,1622000),(30,1830000),(31,2054000),(32,2294000),(33,2550000),)
LEVELUP_COLOR = ((5,2,10,8,12,3,4),("Atk","Def","Mdef","Fire","Ice","Wind","Earth"))
P_MAIN_WND = (0,0, 272,272) #x,y, w,h
P_SUB_WND = (272,0,120,272) #x,y, w,h
P_STAT_WND = (272,0, 120,120) #x,y, w,h
P_MESG_WND = (272,120, 120,152) #x,y, w,h

#パラメータ（指定値）
P_CHIP_SIZE = 8 #マップチップサイズ（Pixel）
GAME_FPS = 60
ASSET_FILE = "assets/assets.pyxres"
FONTFILE = "assets/umplus_j12r.bdf"
JP_FONT = ""
ENCRYPT_KEY = b"OAl25XA7HYs26"
DATA_HEADER = b"\x7F\x70\x79\x78"
APP_VERSION = "2.0.0"

#パラメータ（算出）
#対象無し