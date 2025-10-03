import json
import random
import pytest
import common_func as comf

# --- stage.py から必要なデータを引用 ---
# 各ステージのフィールド画面サイズ（縦、横）
_size_stage_map = ((4, 4), (5, 5), (8, 8), (6, 6), (9, 9), (7, 7))
# 各ステージのダンジョンの部屋数（画面数）
_info_dungeon_rooms = ((7, 1, 1), (12, 2, 2), (18, 2, 1), (33, 3, 2), (26, 4, 2), (44, 4, 1),)

def read_json_from_file(filepath: str):
    """
    指定されたJSONファイルを読み込んで内容を返すヘルパー関数。
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"エラー: ファイルが見つかりません - {filepath}")
        return None
    except json.JSONDecodeError:
        print(f"エラー: JSONの解析に失敗しました - {filepath}")
        return None

def calculate_stage_experience(stage_id: int):
    """
    指定されたステージの総経験値をシミュレーション計算する関数。
    monster.pyとstage.pyのロジックを模倣しています。
    """
    # 1. ステージの総画面数を計算
    field_screens = _size_stage_map[stage_id][0] * _size_stage_map[stage_id][1]
    dungeon_screens = _info_dungeon_rooms[stage_id][0]
    total_screens = field_screens + dungeon_screens

    # 2. 対応するステージのモンスターデータを読み込む
    monster_data = read_json_from_file(f"assets/data/stage{stage_id}.json")
    if monster_data is None:
        return 0

    stage_monster_id_list = comf.generate_random_iterater(min(monster_data)[0],max(monster_data)[0]+1,
                                                            len(monster_data))

    # モンスターのIDリストと、IDからデータを高速に引くための辞書を作成
    monster_id_list = [data[0] for data in monster_data]
    monster_dict = {data[0]: data for data in monster_data}

    total_experience = 0
    total_gold = 0
    total_food = 0


    # 3. 全画面についてループ
    for _ in range(total_screens):
        # この画面に出現するモンスターの種類をランダムに決定
        # assigned_monster_id = random.choice(monster_id_list)
        try:
            assigned_monster_id = next(stage_monster_id_list)
        except StopIteration:
            stage_monster_id_list = comf.generate_random_iterater(min(monster_data)[0],max(monster_data)[0]+1,
                                                        len(monster_data))
            assigned_monster_id = next(stage_monster_id_list)
    
        monster_info = monster_dict[assigned_monster_id]

        # 4. モンスターの再配置（4グループ分）についてループ
        for group_id in range(4):
            treasuregold = 0
            treasurefood = 0
            # 5. 出現するモンスターの数をランダムに決定 (1〜9匹)
            num_monsters = random.randint(1, 9)

            # 6. JSONからモンスター1匹あたりの経験値を取得
            # monster_info[3] -> パラメータリスト
            # [group_id]      -> 4つの再配置グループのいずれか
            # [14]            -> experience（リストの15番目の要素）
            try:
                experience_per_monster = monster_info[3][group_id][15]
                if monster_info[3][group_id][17]==30:
                    treasuregold = monster_info[3][group_id][18]
                if monster_info[3][group_id][17]==31:
                    treasurefood = monster_info[3][group_id][18]
                gold_per_monster = (stage_id + 1)**2 * random.randint(1, 10)
                
            except IndexError:
                print(f"警告: ステージ{stage_id}のモンスターID {assigned_monster_id} に不正なデータ構造があります。")
                experience_per_monster = 0

            # 7. このグループで得られる経験値を加算
            total_experience += num_monsters * experience_per_monster
            total_gold += num_monsters * gold_per_monster + treasuregold
            total_food += treasurefood
            
    return [total_experience, total_gold, total_food]

# Pytestのテスト関数
def test_total_experience_calculation():
    """
    ステージ0から5までの累計獲得経験値を計算し、結果を出力するテスト。
    """
    # シードを固定することで、毎回同じランダム結果を生成し、テストの再現性を確保します。
    # random.seed(123) 

    print("\n--- 各ステージの累計獲得経験値のシミュレーション結果 ---")
    
    grand_total_experience = 0
    grand_total_gold = 0
    grand_total_food = 0
    cumlative_exp = 0
    cumlative_gold = 0
    cumlative_food = 0
    
    all_stage_results = []

    for stage_id in range(6):
        stage_exp,stage_gold,stage_food = calculate_stage_experience(stage_id)
        grand_total_experience += stage_exp
        grand_total_gold += stage_gold
        grand_total_food += stage_food
        cumlative_exp += stage_exp
        cumlative_gold += stage_gold
        cumlative_food += stage_food

        all_stage_results.append(stage_exp)
        print(f"ステージ {stage_id}: {stage_exp:13,} EXP {stage_gold:13,} GP  {stage_food:13,}food   累計 {cumlative_exp:11,}EP {cumlative_gold:11,}GP {cumlative_food:11,}food")
    
    print("----------------------------------------------------")
    print(f"全ステージ合計: {grand_total_experience:13,} EXP  {grand_total_gold:13,} EXP")
    
    # テストとして、計算結果が0より大きいことを確認
    assert grand_total_experience > 0
    # 各ステージの結果も0以上であることを確認
    for result in all_stage_results:
        assert result >= 0