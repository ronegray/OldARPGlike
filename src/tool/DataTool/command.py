import pyxel as px
import sys
import os
import pickle
import gzip
import tarfile
from pathlib import Path
import hashlib
import const as G_
import common_func as comf
import menu


class Commands:
    def __init__(self, x=0, y=0):
        self.msg_window = None
        self.data = None
        self.is_finished = False
        self.is_disp_finished = False
        self.message = []
        
    def keycheck(self):
        btn = comf.get_button_state()
        if btn["a"]:
            px.play(3,G_.SNDEFX["pi"], resume=True)
            return True
        if btn["b"]:
            return False
        return None
    
    def update(self):
        self.is_finished = True
        return self.keycheck()
    
    def draw(self):
        raise NotImplementedError
    
    def exec(self):
        raise NotImplementedError

class CommandBuy(Commands):
    def __init__(self, x=0, y=0):
        super().__init__(x, y)

class CommandQuit(Commands):
    def __init__(self):
        pass

    def exec(self):
        px.quit()

class CommandBackup(Commands):
    def __init__(self):
        super().__init__(self)
        self.messege_window = menu.Window(16,88,px.width - (G_.P_CHIP_SIZE*2*2),(1+1*2+1)*G_.P_CHIP_SIZE,1)

    def exec(self):
        if not self.is_finished:
            #パス情報の生成
            target = Path(px.user_data_dir("moq","OldARPGlike"))
            if getattr(sys, 'frozen', False):
                # exeとして実行されている場合
                destination = Path(sys.executable).parent
            else:
                # 通常のPythonスクリプトとして実行されている場合 (.pyファイル)
                # __file__ は現在のスクリプトのパスを指します。
                destination = Path(__file__).parent

            tmpfile = destination / "tmp.tar"
            outfile = destination / "OldARPGlike.bin"

            #バックアップ対象データから一時アーカイブ生成
            with tarfile.open(tmpfile, "w") as tmp:
                for file in sorted(target.glob("*.bin")):
                    tmp.add(file, arcname=file.name)

            #一時アーカイブを暗号化
            encrypted = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(tmpfile.read_bytes()))

            #データヘッダを付与して暗号化済一時アーカイブ変数と共に本アーカイブへ書き出し
            with open(outfile, "wb") as f:
                f.write(G_.DATA_HEADER + encrypted)
            #一時アーカイブ削除
            tmpfile.unlink(missing_ok=True)

            px.play(3, G_.SNDEFX["save"], resume=True)
            px.flip()
            self.is_finished=True
    
    def draw(self, P_adrCursor=None):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["バックアップが完了しました"])


class CommandRestore(Commands):
    def __init__(self):
        super().__init__(self)
        self.messege_window = menu.Window(16,88,px.width - (G_.P_CHIP_SIZE*2*2),(1+1*2+1)*G_.P_CHIP_SIZE,1)
        self.is_nofile = False
        self.menu_datalist = None

    def exec(self):
        #パス情報の生成
        destination = Path(px.user_data_dir("moq","OldARPGlike"))
        if getattr(sys, 'frozen', False):
            # exeとして実行されている場合
            target = Path(sys.executable).parent
        else:
            # 通常のPythonスクリプトとして実行されている場合 (.pyファイル)
            # __file__ は現在のスクリプトのパスを指します。
            target = Path(__file__).parent

        tmpfile = target / "tmp.tar"
        inpfile = target / "OldARPGlike.bin"

        print([target,tmpfile])
        #バックアップが無い場合
        if inpfile.exists() is False:
            self.is_nofile = True
            return False

        if not self.is_finished:
            #バックアップファイルの読み出し
            with open(inpfile, "rb") as f:
                archive = f.read()

            #アーカイブヘッダが異常な場合
            if not archive.startswith(G_.DATA_HEADER):
                comf.error_message(["Invalid archive data"])

            #データヘッダを除き、暗号化を解除して一時アーカイブのバイト列を取得
            encrypted = archive[len(G_.DATA_HEADER):]
            compressed = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(encrypted))
            #一時アーカイブバイトデータをファイルへ書き出し
            tmpfile.write_bytes(compressed)

            #一時アーカイブファイルからバックアップデータを展開
            with tarfile.open(tmpfile, "r") as tmp:
                for file in tmp.getmembers():
                    tmp.extract(file, destination)
                    restore_path = destination / file.name
                    if restore_path.exists():
                        os.utime(restore_path, (file.mtime, file.mtime))

            #一時アーカイブ削除
            tmpfile.unlink(missing_ok=True)

            self.menu_datalist = menu.MenuSavedata(0,0,None,6)
            messages = []
            for msg in self.menu_datalist.menu_items:
                messages += msg
            self.datalist_window = menu.Window(64,128,200,80)
            self.datalist_window.message_text = messages

            px.play(3, G_.SNDEFX["load"])
            px.flip()
            self.is_finished = True
    
        return True

    def draw(self,P_adrcursor=None):
        if self.is_nofile:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["バックアップが存在しません"])
            self.is_disp_finished = True
            return
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["リストアが完了しました"])
            self.datalist_window.draw()
            self.datalist_window.draw_message()


class CommandSystemData(Commands):
    def __init__(self):
        super().__init__(self)
        self.filename = ".sysdat.bin"
        self.path = Path(px.user_data_dir("moq","OldARPGlike")+f"{self.filename}")
        self.system_data = {}
        if self.path.exists() is False:
            self.system_data["key"] = G_.ENCRYPT_KEY
            self.system_data["clear"] = False
            self.system_data["alert_key"] = False
            self.system_data["alert_LvUp"] = False
            self.system_data["alert_gold"] = False
            self.system_data["alert_group"] = False
            self.system_data["alert_map"] = False
            self.system_data["alert_torch"] = False
            self.system_data["alert_zone"] = False
            self.system_data["alert_mattock"] = False
            self.write_systemdata()
        else:
            self.system_data = self.load()
            self.system_data.setdefault("clear", False)
            self.system_data.setdefault("alert_key",False)
            self.system_data.setdefault("alert_LvUp",False)
            self.system_data.setdefault("alert_gold",False)
            self.system_data.setdefault("alert_group",False)
            self.system_data.setdefault("alert_map",False)
            self.system_data.setdefault("alert_torch",False)
            self.system_data.setdefault("alert_zone",False)
            self.system_data.setdefault("alert_mattock",False)
            self.write_systemdata()

    def write_systemdata(self):
        raw = pickle.dumps(self.system_data)
        compressed = gzip.compress(raw)
        hash_value = hashlib.sha256(compressed).digest()  # 新形式: ハッシュ計算
        hashed_data = hash_value + compressed  # 新形式: ハッシュ + 圧縮データ
        try:
            with open(self.path, "wb") as f:
                f.write(hashed_data + G_.DATA_HEADER)
        except Exception:
            comf.error_message(["Couldn't save system data"])
            px.quit()
        return True

    def load(self):
        try:
            with open(self.path, "rb") as f:
                savedata = f.read()
        except Exception:
            comf.error_message(["Couldn't load system data"])
            px.quit()
        if not savedata.endswith(G_.DATA_HEADER):
            comf.error_message(["Invalid system data"])
            px.quit()
        encrypted_or_hashdata = savedata[:-len(G_.DATA_HEADER)]  # HEADER除去後のデータ
        # 新形式（ハッシュ）試行
        hash_value = encrypted_or_hashdata[:32]  # SHA-256ハッシュ
        savedata_body = encrypted_or_hashdata[32:]
        if hashlib.sha256(savedata_body).digest() == hash_value:  # ハッシュ一致
            raw = gzip.decompress(savedata_body)
            self.system_data = pickle.loads(raw)
            if self.system_data["key"] != G_.ENCRYPT_KEY:  # 元のkey検証（互換性で残す）
                comf.error_message(["Invalid system data"])
            return self.system_data  # 成功: 新形式ロード
        else:
        # 旧形式（XOR）試行
            savedata_body = bytes(b ^ G_.ENCRYPT_KEY[i % len(G_.ENCRYPT_KEY)] for i, b in enumerate(encrypted_or_hashdata))  # XORデクリプト
            raw = gzip.decompress(savedata_body)
            self.system_data = pickle.loads(raw)
            if self.system_data["key"] != G_.ENCRYPT_KEY:
                comf.error_message(["Invalid system data"])
                px.quit()
            return self.system_data  # 成功: 旧形式ロード


class CommandDeleteSystem(Commands):
    def __init__(self):
        super().__init__(self)
        self.messege_window = menu.Window(16,88,px.width - (G_.P_CHIP_SIZE*2*2),(1+1*2+1)*G_.P_CHIP_SIZE,1)
        self.is_nofile = False
        self.system_data = {}
        self.filename = ".sysdat.bin"
        self.path = Path(px.user_data_dir("moq","OldARPGlike")+f"{self.filename}")

    def exec(self):
        if not self.is_finished:
            if self.path.exists() is False:
                self.is_nofile = True
                return False

            self.system_data["key"] = G_.ENCRYPT_KEY
            self.system_data["clear"] = False
            self.system_data["alert_key"] = False
            self.system_data["alert_LvUp"] = False
            self.system_data["alert_gold"] = False
            self.system_data["alert_group"] = False
            self.system_data["alert_map"] = False
            self.system_data["alert_torch"] = False
            self.system_data["alert_zone"] = False
            self.system_data["alert_mattock"] = False
            self.system_data["Encyclopedia"] = []

            raw = pickle.dumps(self.system_data)
            compressed = gzip.compress(raw)
            hash_value = hashlib.sha256(compressed).digest()  # 新形式: ハッシュ計算
            hashed_data = hash_value + compressed  # 新形式: ハッシュ + 圧縮データ
            try:
                with open(self.path, "wb") as f:
                    f.write(hashed_data + G_.DATA_HEADER)
            except Exception:
                comf.error_message(["Couldn't save system data"])
                px.quit()

            px.play(3, G_.SNDEFX["save"], resume=True)
            px.flip()
            self.is_finished=True
    
    def draw(self, P_adrCursor=None):
        if self.is_finished:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["初期化が完了しました"])
        if self.is_nofile:
            self.messege_window.draw()
            self.messege_window.drawText(self.messege_window.x + 8 ,self.messege_window.y + 8, ["データが存在しません"])
            self.is_disp_finished = True
            return