import sys
import random
import collections
import pandas as pd

# ----------------------------------------------------------------------
# 1. モックオブジェクトとダミーの定義
# Stageクラスが依存する外部モジュールをシミュレーション用に作成します。
# ----------------------------------------------------------------------

class MockPyxel:
    """pyxelモジュールのダミー"""
    def rndi(self, a, b):
        return random.randint(a, b)
    def noise(self, x, y, z):
        return random.uniform(-0.6, 0.6)
    def pset(self, *args, **kwargs): pass
    def play(self, *args, **kwargs): pass
    # tilemapsプロパティを模倣
    @property
    def tilemaps(self):
        class MockTilemap:
            def pset(self, *args, **kwargs): pass
        return [MockTilemap()] * 3 # tilemaps[0]などでアクセスできるようリストを返す
    def bltm(self, *args, **kwargs): pass

class MockConst:
    """constモジュール(G_)のダミー"""
    P_MAIN_WND = [0, 0, 272, 272]
    CHARA_DIR = [[0, -1], [1, 0], [0, 1], [-1, 0]]
    SNDEFX = {"don": 0}
    GAME_FPS = 30
    IS_DEBUG = False
    JP_FONT=0
    IMGIDX={"CHIP": 0}

class MockCommonFunc:
    """common_funcモジュール(comf)のダミー"""
    def generate_random_iterater(self, start, end, count):
        return iter(random.sample(range(start, end + 1), count))
    def get_tileinfo(self, *args):
        return (0,)
    def check_collision_hitbox(self, *args): return False

class MockItem:
    """itemモジュールのダミー"""
    effect_type_12 = lambda user: None
    effect_type_13 = lambda user: None
    effect_type_14 = lambda user: None
    class BossSummonOrb:
        def __init__(self, *args, **kwargs): pass
        def draw(self, *args, **kwargs): pass

class MockMenu:
    """menuモジュールのダミー"""
    class ShopManager:
        def __init__(self, *args, **kwargs): pass
        def create_shop(self, *args, **kwargs): pass
        def draw(self, *args, **kwargs): pass

class MockMonster:
    """monsterモジュールのダミー"""
    class MonsterManager:
        def __init__(self, *args, **kwargs): pass
        def set_mobgroup_index(self, *args, **kwargs): pass
        def get_living_monsters(self, *args, **kwargs): return 0
        def generate_monsters(self, *args, **kwargs): pass
        def update(self, *args, **kwargs): pass
        def draw(self, *args, **kwargs): pass

class MockDungeon:
    """dungeonモジュールのダミー"""
    class Dungeon:
        def __init__(self, *args, **kwargs):
            self.room_address = []
            self.entrance_address = []
            self.treasure_cache = [0, 0]
            self.monsters = None
            self.dungeon_id = 0

class MockUser:
    """ユーザーインスタンスのダミー"""
    def __init__(self):
        self.address = [80, 60]
        self.direction = 0
        self.timer_action = 0; self.timer_wind = 0; self.effect_wind = None
        self.timer_ice = 0; self.effect_ice = None; self.hp = 100
        self.maxhp = 100; self.timer_fire = 0; self.effect_fire = None
        self.timer_damaged = 0; self.timer_magicdamaged = 0; self.timer_item = [0,0]
        class MockArmor:
            movespeed = 4
        self.armor = MockArmor()
    def calc_movespeed(self): pass

# ----------------------------------------------------------------------
# 2. sys.modules を使ったモジュールのモック化
# stage.py がインポートされる前に、偽のモジュールをシステムに登録します。
# ----------------------------------------------------------------------
sys.modules['pyxel'] = MockPyxel()
sys.modules['const'] = MockConst()
sys.modules['common_func'] = MockCommonFunc()
sys.modules['item'] = MockItem()
sys.modules['menu'] = MockMenu()
sys.modules['monster'] = MockMonster()
sys.modules['dungeon'] = MockDungeon()

# ----------------------------------------------------------------------
# 3. stage.py をインポート
# 上記でモックが登録されたので、stage.pyはエラーなくインポートできます。
# ----------------------------------------------------------------------
from stage import Stage

# ----------------------------------------------------------------------
# 4. シミュレーション実行部 (前回と同様)
# ----------------------------------------------------------------------

def run_treasure_simulation(num_simulations: int):
    """指定された回数だけ掘り出し物配置のシミュレーションを実行し、結果を集計する"""
    
    range_item = [(((1,100),33),), (((1,80),31),((81,100),32)),
                  (((1,12),20),((13,75),21),((76,100),22)),
                  (((1,20),10),((21,40),14),((41,60),15),((61,80),16),((81,100),17)),
                  (((1,1),0),((2,2),1),((3,3),2),((4,4),3),((5,5),4),((6,6),5),((7,12),6),((13,100),30)),]
    all_item_ids = sorted(list(set(item[1] for group in range_item for item in group)))
    
    counts = collections.defaultdict(lambda: collections.defaultdict(int))
    mock_user = MockUser()
    mock_message_manager = None
    
    print(f"{num_simulations}回のシミュレーションを実行します...")
    
    for stage_id in range(6):
        for _ in range(num_simulations):
            stage_instance = Stage(stage_id, mock_user, mock_message_manager)
            for treasure in stage_instance.treasure_spot:
                item_id = treasure[2]
                counts[item_id][stage_id] += 1
                
    print("シミュレーション完了。結果を集計します。")

    # ----- 結果の集計と表示 -----
    # ----- 結果の集計と表示 -----
    df = pd.DataFrame(counts).transpose().fillna(0).astype(int)
    df = df.reindex(sorted(df.columns), axis=1)
    df = df.reindex(all_item_ids)

    total_treasures_per_stage = {
        stage_id: num_simulations * Stage._size_stage_map[stage_id][0]
        for stage_id in range(6)
    }

    df_percent = df.copy()
    for stage_id in range(6):
        if total_treasures_per_stage[stage_id] > 0:
            df_percent[stage_id] = (df[stage_id] / total_treasures_per_stage[stage_id]) * 100

    df_percent['全合計'] = (df.sum(axis=1) / sum(total_treasures_per_stage.values())) * 100
    
    df_percent.index.name = 'アイテムID'
    df_percent.columns.name = 'stage_id'

    pd.set_option('display.float_format', '{:.2f}%'.format)
    print("\n--- 掘り出し物アイテムの平均発生率 ---")
    print(df_percent)


if __name__ == '__main__':
    # 実行前にstage.pyが同じディレクトリにあることを確認してください
    try:
        f = open("stage.py")
        f.close()
    except FileNotFoundError:
        print("エラー: stage.py ファイルが見つかりません。")
        print("このスクリプトと同じディレクトリに stage.py を配置してください。")
        sys.exit(1)

    SIMULATION_COUNT = 1000  # シミュレーションの実行回数
    run_treasure_simulation(SIMULATION_COUNT)