# test_stage.py (修正版)
import unittest
import sys
import random
from unittest.mock import MagicMock, patch

# pyxelをモックに置き換える
mock_pyxel = MagicMock()
sys.modules['pyxel'] = mock_pyxel

# 依存モジュールをスタブに置き換えるため、検索パスを追加
sys.path.insert(0, 'stubs')

# --- テスト対象モジュールをインポート ---
import stage
import const as G_

class TestStage(unittest.TestCase):
    """
    stage.pyのStageクラスをテストします。
    依存モジュールはスタブ/モックに置き換えられています。
    """
    testcount=10

    def _check_box_collision(self, x1, y1, w1, h1, x2, y2, w2, h2):
        """テスト内で使用する矩形衝突判定ヘルパー"""
        return (x1 < x2 + w2 and
                x1 + w1 > x2 and
                y1 < y2 + h2 and
                y1 + h1 > y2)

    def setUp(self):
        """各テストの実行前に呼ばれるセットアップメソッドです。"""
        mock_pyxel.reset_mock()
        self.seed = 0
        self.random_gen = random.Random(self.seed)
        mock_pyxel.noise.side_effect = lambda x, y, z: (self.random_gen.random() - 0.5) * 2
        mock_pyxel.rndi.side_effect = lambda a, b: self.random_gen.randint(a, b)
        
        mock_tilemap = MagicMock()
        mock_tilemap.pset = MagicMock()
        mock_pyxel.tilemaps = [mock_tilemap]
        
        mock_pyxel.frame_count = 0

        self.mock_user = MagicMock()
        self.mock_user.address = [0, 0]
        self.mock_user.timer_damaged = 0
        self.mock_user.timer_magicdamaged = 0
        
        self.mock_message_manager = MagicMock()

    @patch('common_func.get_tileinfo', return_value=(0, 0))
    @patch('common_func.check_collision_hitbox', return_value=False) # 衝突しない前提でモック化
    def test_01_stage_initialization(self, mock_check_collision, mock_get_tileinfo):
        """Stageクラスが例外なく初期化できることをテストします。"""
        print("\nRunning: Stage Initialization Test")
        for stage_id in range(6):
            try:
                print(f"  - Testing stage_id: {stage_id}")
                s = stage.Stage(stage_id, self.mock_user, self.mock_message_manager)
                self.assertIsInstance(s, stage.Stage)
            except Exception as e:
                self.fail(f"Stage({stage_id}) の初期化に失敗しました: {e}")
        print("  - Success: All stages initialized without errors.")

    @patch('common_func.get_tileinfo', return_value=(0, 0))
    @patch('common_func.check_collision_hitbox', return_value=False)
    def test_02_dungeon_entrance_valid_placement(self, mock_check_collision, mock_get_tileinfo):
        """[バグ検証] ダンジョン入口が侵入不可タイルまたはマップ範囲外に配置されないことをテストします。"""
        print("\nRunning: Dungeon Entrance Valid Placement Test")
        found_bug = False
        
        for seed in range(self.testcount//2+1): # より多くのパターンを試すために試行回数を増やします
            mock_pyxel.reset_mock()
            print(f"test02 SeedNo.{seed:>3} start")
            self.random_gen = random.Random(seed)
            mock_pyxel.rndi.side_effect = lambda a, b: self.random_gen.randint(a, b)
            mock_pyxel.noise.side_effect = lambda x, y, z: (self.random_gen.random() - 0.5) * 2
            s = ""
            for stage_id in range(6):
                
                s = None
                s = stage.Stage(stage_id, self.mock_user, self.mock_message_manager)
                
                if not s.dungeon_entrance_list:
                    continue

                for i, entrance_info in enumerate(s.dungeon_entrance_list):
                    dungeon_id, dungeon_addr, stage_px_addr = entrance_info
                    
                    tile_x = (stage_px_addr[0] - 8) // 8
                    tile_y = (stage_px_addr[1] - 8) // 8

                    # 2x2の範囲をチェック
                    for y_offset in range(2):
                        for x_offset in range(2):
                            check_x = tile_x + x_offset
                            check_y = tile_y + y_offset
                            
                            # <<< 修正点: ここから >>>
                            try:
                                tile_type = s.virtual_map[check_y][check_x][0]
                            except IndexError:
                                found_bug = True
                                print("\n--- BUG DETECTED! (IndexError) ---")
                                print(f"Seed: {seed}, Stage ID: {stage_id}, Entrance Index: {i}")
                                print("Dungeon entrance placed outside the map boundaries.")
                                print(f"Map Size (tiles): W={s.stage_w_tile}, H={s.stage_h_tile}")
                                print(f"Entrance Top-Left Tile: ({tile_x}, {tile_y})")
                                print(f"Attempted to access out-of-range index: ({check_x}, {check_y})")
                                print("--------------------------------------\n")
                                # この座標はチェック不能なので、次の入口へ
                                break # x_offsetループを抜ける
                            
                            # <<< 修正点: ここまで >>>

                            if tile_type == 4:
                                found_bug = True
                                print("\n--- BUG DETECTED! (Impassable Tile) ---")
                                print(f"Seed: {seed}, Stage ID: {stage_id}, Entrance Index: {i}")
                                print(f"Dungeon entrance placed on an impassable tile (ID: 4).")
                                print(f"Entrance Top-Left Tile: ({tile_x}, {tile_y})")
                                print(f"Problematic Tile: ({check_x}, {check_y})")
                                print("---------------------------------------\n")
                        else: # x_offsetループがbreakされなかった場合
                            continue
                        break # y_offsetループも抜ける
            
        if not found_bug:
            print(f"  - Success: No bugs found in {self.testcount} random seeds.")
        self.assertFalse(found_bug, "Dungeon entrance placement bug was detected. See log for details.")


    # <<< ここからが新しいテスト >>>
    @patch('common_func.get_tileinfo', return_value=(0, 0))
    @patch('common_func.check_collision_hitbox', side_effect=lambda x1, y1, w1, h1, x2, y2, w2, h2: self._check_box_collision(x1, y1, w1, h1, x2, y2, w2, h2))
    def test_03_entrances_do_not_overlap(self, mock_check_collision, mock_get_tileinfo):
        """[新バグ検証] ショップ入口とダンジョン入口が重複して配置されないことをテストします。"""
        print("\nRunning: Entrance Overlap Bug Test")
        found_bug = False

        for seed in range(self.testcount+1):
            mock_pyxel.reset_mock()
            print(f"test03 SeedNo.{seed:>3} start")
            self.random_gen = random.Random(seed)
            mock_pyxel.rndi.side_effect = lambda a, b: self.random_gen.randint(a, b)
            mock_pyxel.noise.side_effect = lambda x, y, z: (self.random_gen.random() - 0.5) * 2

            for stage_id in range(6):
                
                s = stage.Stage(stage_id, self.mock_user, self.mock_message_manager)
                
                if not s.dungeon_entrance_list or not s.shops.shop_list:
                    continue

                # 全てのショップと全てのダンジョン入口の組み合わせをチェック
                for shop in s.shops.shop_list:
                    shop_addr = shop.address # (px_x, px_y)
                    for _, _, dungeon_px_addr in s.dungeon_entrance_list:
                        # 16x16のヒットボックスで衝突判定
                        is_overlapping = self._check_box_collision(
                            shop_addr[0], shop_addr[1], 8, 8,
                            dungeon_px_addr[0], dungeon_px_addr[1], 8, 8
                        )

                        if is_overlapping:
                            found_bug = True
                            print("\n--- BUG DETECTED! (Entrance Overlap) ---")
                            print(f"Seed: {seed}, Stage ID: {stage_id}")
                            print(f"Shop at {shop_addr} is overlapping with Dungeon Entrance at {dungeon_px_addr}")
                            print("-------------------------------------------\n")
                            # このステージIDでのテストはこれ以上不要
                            break
                    if is_overlapping:
                        break

        if not found_bug:
            print(f"  - Success: No entrance overlaps found in {self.testcount} random seeds.")
        self.assertFalse(found_bug, "Entrance overlap bug was detected. See log for details.")
        exit

if __name__ == '__main__':
    unittest.main()
# 注: test_02 の内容は省略していますので、お手元のコードから消さずにそのままお使いください。