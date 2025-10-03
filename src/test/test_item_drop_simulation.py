import json
import random
from collections import defaultdict

# --- stage.py から必要なデータを引用 ---
_size_stage_map = ((4, 4), (5, 5), (8, 8), (6, 6), (9, 9), (7, 7))
_info_dungeon_rooms = ((7, 1, 1), (12, 2, 2), (18, 2, 1), (33, 3, 2), (26, 4, 2), (44, 4, 1),)

def read_json_from_file(filepath: str):
    """
    指定されたJSONファイルを読み込んで内容を返すヘルパー関数。
    """
    try:
        with open(filepath, 'r', encoding='utf--8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"エラー: JSONの解析に失敗しました - {filepath}")
        return None

def simulate_stage_item_drops(stage_id: int, monster_data_cache: dict):
    """
    指定されたステージの総アイテムドロップ数をシミュレーション計算する関数。
    戻り値は {アイテムID: 個数} の辞書。
    """
    # 1. ステージの総画面数を計算
    field_screens = _size_stage_map[stage_id][0] * _size_stage_map[stage_id][1]
    dungeon_screens = _info_dungeon_rooms[stage_id][0]
    total_screens = field_screens + dungeon_screens

    # 2. キャッシュからモンスターデータを取得
    monster_data = monster_data_cache[stage_id]
    monster_id_list = [data[0] for data in monster_data]
    monster_dict = {data[0]: data for data in monster_data}

    # アイテムIDごとのドロップ数を格納する辞書
    drop_counts = defaultdict(int)

    # 3. 全画面についてループ
    for _ in range(total_screens):
        assigned_monster_id = random.choice(monster_id_list)
        monster_info = monster_dict[assigned_monster_id]

        # 4. モンスターの再配置（4グループ分）についてループ
        for group_id in range(4):
            # num_monsters = random.randint(1, 9)
            
            # 5. JSONからアイテムIDとドロップ数を取得 (要素番号17, 18 -> インデックス16, 17)
            try:
                drop_item_id = monster_info[3][group_id][17]
                drop_number = monster_info[3][group_id][18]
            except IndexError:
                # データ構造が不正な場合はスキップ
                continue

            # # 6. アイテムIDがあり、個数も定義されている場合のみ集計
            # if drop_item_id is not None and drop_number is not None:
            #     # total_drops = drop_number
            #     # drop_counts[drop_item_id] += total_drops
            drop_counts[drop_item_id] += drop_number
            drop_number = 0
                
    return drop_counts

# Pytestのテスト関数
def test_item_drop_simulation_and_summary():
    """
    全ステージのアイテムドロップ数をシミュレーションし、結果を表形式で出力するテスト。
    """
    # 再現性のために乱数シードを固定
    # random.seed(123)

    # 事前に全ステージのJSONを読み込んでおく
    monster_data_cache = {i: read_json_from_file(f"assets/data/stage{i}.json") for i in range(6)}
    if any(data is None for data in monster_data_cache.values()):
        print("必要なJSONファイルが読み込めなかったため、処理を中断します。")
        assert False, "JSONファイルの読み込みに失敗しました"

    stage_results = []
    all_item_ids = set()
    grand_total_counts = defaultdict(int)

    print("\n--- ステージ別・アイテム別ドロップ数シミュレーション ---")
    for stage_id in range(6):
        # ステージごとのドロップ数を計算
        stage_drops = simulate_stage_item_drops(stage_id, monster_data_cache)
        print(stage_drops)
        stage_results.append(stage_drops)
        
        # 全ステージでドロップするアイテムのIDを収集し、合計を計算
        for item_id, count in stage_drops.items():
            all_item_ids.add(item_id)
            grand_total_counts[item_id] += count
        
        print(f"ステージ {stage_id} のシミュレーション完了...")

    # --- 結果の表形式での表示 ---
    print("\n" + "="*120)
    print("ドロップアイテム数 集計結果")
    print("="*120)

    # ヘッダー作成
    header = f"{'アイテムID':<8}"
    for i in range(6):
        header += f"| {'ステージ ' + str(i):^8}"
    header += f"| {'合計':^15}"
    print(header)
    print("-" * len(header))

    # 各アイテムIDについて行を作成 (アイテムIDでソートして表示)
    sorted_item_ids = sorted(list(all_item_ids))
    for item_id in sorted_item_ids:
        row = f"{item_id:<12}"
        # ステージごとのドロップ数を表示
        for stage_id in range(6):
            count = stage_results[stage_id].get(item_id, 0)
            row += f"| {count:12,}"
        
        # 合計ドロップ数を表示
        total_count = grand_total_counts[item_id]
        row += f"| {total_count:15,}"
        print(row)
    
    print("-" * len(header))
    
    # テストとして、何かしらのアイテムがドロップされていることを確認
    assert len(grand_total_counts) > 0