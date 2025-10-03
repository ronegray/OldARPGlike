import sys
import pytest
from unittest.mock import MagicMock, patch

# --- 依存モジュールのモック化 ---
# main.py が import しようとするモジュールを、テスト実行前に偽のモジュールに差し替えます。
# これにより、ファイルが見つからない、pyxelが初期化できない等のエラーを防ぎます。
mock_modules = {
    'pyxel': MagicMock(),
    'const': MagicMock(),
    'common_func': MagicMock(),
    'drawevent': MagicMock(),
    'character': MagicMock(),
    'stage': MagicMock(),
    'sound': MagicMock(),
    'message': MagicMock(),
    'item': MagicMock(),
    'menu': MagicMock(),
    'monster': MagicMock(),
}
sys.modules.update(mock_modules)

# モック化した後で、テスト対象のクラスをインポートします
from main import App

# --- テスト用の設定値 ---
# テストで使う定数をここで定義しておきます (本来は const.py にあるもの)
G_ = mock_modules['const']
G_.P_MAIN_WND = [0, 0, 272, 272] # [x, y, width, height]

@pytest.fixture
def app_instance(mocker):
    """
    各テストの前に実行され、Appクラスのインスタンスを生成・初期化する fixture。
    """
    # Appクラスの __init__ は px.run() を呼び出してテストが終わらなくなるため、一時的に無効化する
    mocker.patch.object(App, "__init__", lambda self: None)
    
    app = App()
    
    # テストに必要な最小限のオブジェクトをモックで作成してセットする
    app.user = MagicMock()
    app.message_manager = MagicMock()
    
    return app

# --- テストケース ---

class TestApp:
    """Appクラスのメソッドをテストするクラス"""

    def test_get_scroll_direction(self, app_instance):
        """
        get_scroll_direction メソッドのテスト。
        機能：ユーザーの座標に応じて正しいスクロール方向(0,1,2,3)または中央(9)を返すか。
        テスト観点：画面の四隅や中央などの境界値で正しく動作するか。
        """
        app = app_instance
        offset = 32 # テスト用のオフセット値

        # (x, y)座標, 期待される返り値
        test_cases = [
            # 正常系（画面中央）
            ((100, 100), 9),
            # 境界値（上方向）
            ((100, offset - 1), 3),
            ((100, offset), 9),
            # 境界値（下方向）
            ((100, G_.P_MAIN_WND[3] - offset), 9),
            ((100, G_.P_MAIN_WND[3] - offset + 1), 0),
            # 境界値（左方向）
            ((offset - 1, 100), 1),
            ((offset, 100), 9),
            # 境界値（右方向）
            ((G_.P_MAIN_WND[2] - offset, 100), 9),
            ((G_.P_MAIN_WND[2] - offset + 1, 100), 2),
            # コーナーケース
            ((offset - 1, offset - 1), 1), # 左が優先される
            ((G_.P_MAIN_WND[2] - offset + 1, offset - 1), 2), # 右が優先される
        ]

        for (user_pos, expected) in test_cases:
            app.user.address = list(user_pos)
            result = app.get_scroll_direction(offset)
            assert result == expected, f"座標 {user_pos} の時、期待値 {expected} ではなく {result} が返された"

    def test_kill_monster(self, app_instance):
        """
        kill_monster メソッドのテスト。
        機能：モンスターを倒した際の報酬（経験値、ゴールド）加算とメッセージ追加が行われるか。
        テスト観点：正常に値が加算されるか、メッセージ関数が正しい引数で呼び出されるか。
        """
        app = app_instance

        # ユーザーの初期状態を設定
        app.user.experience = 1000
        app.user.gold = 500
        
        # 倒されるモンスターのモックを作成
        mock_mob = MagicMock()
        mock_mob.name = "スライム"
        mock_mob.experience = 50
        mock_mob.gold = 20

        # メソッドの実行
        app.stage = MagicMock()
        app.stage.world_timer = 12345 # テスト用のタイマー値
        app.kill_monster(mock_mob)

        # --- 検証 ---
        # 1. 経験値が正しく加算されたか (正常性の確認)
        expected_exp = 1000 + 50
        assert app.user.experience == expected_exp

        # 2. ゴールドが正しく加算されたか (正常性の確認)
        expected_gold = 500 + 20
        assert app.user.gold == expected_gold

        # 3. メッセージ追加メソッドが2回呼び出されたか (正常性の確認)
        assert app.message_manager.add_message.call_count == 2

        # 4. 1回目の呼び出しが正しい引数で行われたか (詳細な振る舞いの確認)
        app.message_manager.add_message.assert_any_call(12345, "スライム撃退")
        
        # 5. 2回目の呼び出しが正しい引数で行われたか (詳細な振る舞いの確認)
        app.message_manager.add_message.assert_any_call(12345, f"獲得EX{50: >5}/G{20: >5}")

    def test_kill_monster_with_zero_reward(self, app_instance):
        """
        kill_monster メソッドの境界値テスト。
        機能：報酬が0のモンスターを倒した場合。
        テスト観点：経験値やゴールドが0でも正しく動作するか。
        """
        app = app_instance
        app.user.experience = 1000
        app.user.gold = 500
        
        mock_mob_zero = MagicMock()
        mock_mob_zero.name = "最弱の敵"
        mock_mob_zero.experience = 0
        mock_mob_zero.gold = 0

        app.stage = MagicMock()
        app.stage.world_timer = 54321
        app.kill_monster(mock_mob_zero)

        # 経験値とゴールドが変わっていないことを確認
        assert app.user.experience == 1000
        assert app.user.gold == 500

        # メッセージは正しく表示されることを確認
        app.message_manager.add_message.assert_any_call(54321, "最弱の敵撃退")
        app.message_manager.add_message.assert_any_call(54321, f"獲得EX{0: >5}/G{0: >5}")

    def test_draw_status_basic_info(self, app_instance, mocker):
        """
        draw_status メソッドの基本情報描画をテストする。
        機能：ユーザーの基本的なステータス（名前、HP、所持金など）を描画関数に渡しているか。
        テスト観点：各ステータスが正しい座標とフォーマットで px.text に渡されているか。
        """
        app = app_instance
        px = mock_modules['pyxel'] # モック化されたpyxelを取得
        
        # モックの返り値をリセット
        px.text.reset_mock()
        px.bltm.reset_mock()

        # 1. テスト用のユーザー状態を設定
        app.user.name = "テスト勇者"
        app.user.hp = 123
        app.user.food = 4567
        app.user.experience = 89012
        app.user.gold = 3456
        app.user.magic.name = "メラ"
        app.user.key = 256
        # アイテム名は item.ITEMS をモックする必要があるため、ここでは固定値で代用
        mocker.patch('item.ITEMS', {"20": [0, "やくそう"]})
        app.user.equip_id = [0, 0, 0, 0, 20] # 装備IDの末尾がアイテム

        # 2. テスト対象メソッドの実行
        app.draw_status()

        # --- 検証 ---
        # 3. 枠線描画が正しい引数で呼び出されたか
        px.bltm.assert_called_once() # 1回だけ呼ばれたか
        
        # 4. 各ステータス表示用の px.text が期待通りに呼び出されたか
        #    assert_any_call を使うと、呼び出し順序に関わらず、その呼び出しがあったかを確認できる
        
        # G_.P_SUB_WND は [G_.P_MAIN_WND[2], 0] = [272, 0] と仮定して座標を計算
        sub_wnd_x = 272
        sub_wnd_y = 0
        
        expected_calls = [
            # 名前
            mocker.call(sub_wnd_x + 10, sub_wnd_y + 8 + 0 * 13, "テスト勇者", 7, font=G_.JP_FONT),
            # HP
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 1 * 13, f"{123: >11,}", 7, font=G_.JP_FONT),
            # Food
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 2 * 13, f"{4567: >11,}", 7, font=G_.JP_FONT),
            # Experience
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 3 * 13, f"{89012: >11,}", 7, font=G_.JP_FONT),
            # Gold
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 4 * 13, f"{3456: >11,}", 7, font=G_.JP_FONT),
            # 魔法名
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 5 * 13, "メラ", 7, font=G_.JP_FONT),
            # アイテム名
            mocker.call(sub_wnd_x + 20, sub_wnd_y + 8 + 6 * 13, "やくそう", 7, font=G_.JP_FONT),
        ]
        
        px.text.assert_has_calls(expected_calls, any_order=True)

    def test_draw_status_conditional_effects(self, app_instance, mocker):
        """
        draw_status メソッドの条件付き描画をテストする。
        機能：タイマーが残っている時だけ、エフェクトアイコンと残り秒数が描画されるか。
        テスト観点：if文の条件分岐（タイマー > 0）が正しく機能しているか。
        """
        app = app_instance
        px = mock_modules['pyxel']

        sub_wnd_x = 272
        sub_wnd_y = 0

        # --- ケース1: タイマーが全て0の場合 ---
        px.blt.reset_mock()
        px.text.reset_mock()
        app.user.timer_fire = 0
        app.user.timer_ice = 0
        app.user.timer_wind = 0
        
        app.draw_status()
        
        # アイコン描画用のpx.bltのうち、エフェクトに関連するものが呼び出されていないことを確認
        # 呼び出し履歴をチェックし、該当座標への描画がないことを確認する
        effect_icon_y = sub_wnd_y + 11 + 7 * 13
        for call in px.blt.call_args_list:
            # call[0] は位置引数のタプル
            y_pos = call[0][1]
            assert y_pos != effect_icon_y, "タイマー0なのにエフェクトアイコンが描画された"

        # --- ケース2: timer_fire > 0 の場合 ---
        px.blt.reset_mock()
        px.text.reset_mock()
        app.user.timer_fire = 99
        app.user.timer_ice = 0
        app.user.timer_wind = 0

        app.draw_status()

        # 火のアイコンと秒数が描画されたことを確認
        px.blt.assert_any_call(sub_wnd_x + 10, effect_icon_y, 0, 56, 232, 8, 8, 0)
        px.text.assert_any_call(sub_wnd_x + 18, sub_wnd_y + 8 + 7 * 13, "99s", 7, font=G_.JP_FONT)

        # --- ケース3: timer_wind > 0 の場合 ---
        px.blt.reset_mock()
        px.text.reset_mock()
        app.user.timer_fire = 0
        app.user.timer_ice = 0
        app.user.timer_wind = 5

        app.draw_status()

        # 風のアイコンと秒数が描画されたことを確認
        px.blt.assert_any_call(sub_wnd_x + 76, effect_icon_y, 0, 56 + (2 * 8), 232, 8, 8, 0)
        px.text.assert_any_call(sub_wnd_x + 86, sub_wnd_y + 8 + 7 * 13, "5s", 7, font=G_.JP_FONT)
        
        # 火と氷のアイコンは描画されていないことを確認
        fire_icon_x = sub_wnd_x + 10
        ice_icon_x = sub_wnd_x + 44
        for call in px.blt.call_args_list:
            x_pos, y_pos = call[0][0], call[0][1]
            if y_pos == effect_icon_y:
                assert x_pos != fire_icon_x, "火タイマー0なのに火アイコンが描画された"
                assert x_pos != ice_icon_x, "氷タイマー0なのに氷アイコンが描画された"
