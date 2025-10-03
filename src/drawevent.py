import pyxel as px
import const as G_


def open_door(direction, step):
    match direction:
        case 0:
            px.blt(G_.P_MAIN_WND[2]//2-8,G_.P_MAIN_WND[3]-16, G_.IMGIDX["CHIP"], 232,240,8,16, colkey=0)
        case 1:
            px.blt(0,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"], 232,240,8,16, colkey=0)
        case 2:
            px.blt(G_.P_MAIN_WND[2]-16,G_.P_MAIN_WND[3]//2-8, G_.IMGIDX["CHIP"], 232,240,8,16, colkey=0)
        case 3:
            px.blt(G_.P_MAIN_WND[2]//2-8,0, G_.IMGIDX["CHIP"], 232,240,8,16, colkey=0)
    if step == 0:
        px.play(3,G_.SNDEFX["unlock"], resume=True)
    elif step == 5:
        px.play(3,G_.SNDEFX["unlock"], resume=True)
    elif step == 10:
        px.play(3,G_.SNDEFX["unlock"], resume=True)
    elif step == 15:
        px.play(3,G_.SNDEFX["open"], resume=True)
        return False
    return True


def use_elixer(user):
    px.stop()
    if user.hp < user.maxhp:
        user.hp = min(user.maxhp, user.hp + user.maxhp//150)
        px.play(3,G_.SNDEFX["unlock"], resume=True)
        #ユーザキャラ
        if user.timer_item[2] > 0:
            imagesource_type = 112
        elif user.timer_item[3] > 0:
            imagesource_type = 96
        else:
            imagesource_type = user.image_source[1]

        px.pal(0,px.frame_count%16)
        px.blt(user.address[0]-8, user.address[1]-8, G_.IMGIDX["CHAR"],
               32*(px.frame_count%16//4),imagesource_type,user.image_source[2],user.image_source[3],
               colkey=3)
    else:
        user.is_dead = False
        user.elixer -= 1
        px.pal()
    return user.is_dead


def gameover(user, counter, window):
    if px.play_pos(0) is not None:
        px.stop()

    if px.play_pos(3) is None and px.frame_count < counter + 1:
        px.play(3, G_.SNDEFX["dead"], loop=False)

    if px.frame_count < counter + 180:
        px.blt(user.address[0]-8, user.address[1]-8, G_.IMGIDX["CHAR"],
               32*(px.frame_count%16//4),user.image_source[1],user.image_source[2],user.image_source[3],
               colkey=3)
    else:
        window.message_text = ["力尽き　倒れた","","　冒険は終わった…"]
        return True
    return False


def anger_boss(counter):
    if counter%32 in (0,3):
        px.rect(0,0,G_.P_MAIN_WND[2]+G_.P_SUB_WND[2],G_.P_MAIN_WND[3]+G_.P_SUB_WND[3], 10)

    match counter:
        case 0:
            px.stop()
            px.play(3, [G_.SNDEFX["tdr2"]], loop=False)
            return False
        case 60:
            while px.play_pos(3) is not None:
                pass
            px.play(3, [G_.SNDEFX["tdr1"]], loop=False)
            return False
        case _:
            if counter > 120:
                while px.play_pos(3) is not None:
                    pass
                return True
            else:
                return False


def defeat_boss(boss, counter):
    if counter < 16:
        px.blt(px.rndi(boss.address[0]-44,boss.address[0]-28), px.rndi(boss.address[1]-44,boss.address[1]-28),
               G_.IMGIDX["CHIP"], 24,88,24,24, colkey=0, scale=0.75, rotate=px.rndi(90,180))
        px.blt(px.rndi(boss.address[0]-44,boss.address[0]-28), px.rndi(boss.address[1],boss.address[1]+20),
               G_.IMGIDX["CHIP"], 24,88,24,24, colkey=0, scale=0.75, rotate=px.rndi(180,360))
        px.blt(px.rndi(boss.address[0],boss.address[0]+20), px.rndi(boss.address[1]-44,boss.address[1]-28),
               G_.IMGIDX["CHIP"], 24,88,24,24, colkey=0, scale=0.75, rotate=px.rndi(0,360))
        px.blt(px.rndi(boss.address[0],boss.address[0]+20), px.rndi(boss.address[1],boss.address[1]+20),
               G_.IMGIDX["CHIP"], 24,88,24,24, colkey=0, scale=0.75, rotate=px.rndi(0,180))
        px.blt(px.rndi(boss.address[0]-28,boss.address[0]+4), px.rndi(boss.address[1]-28,boss.address[1]+4),
               G_.IMGIDX["CHIP"], 24,88,24,24, colkey=0, scale=0.75, rotate=px.rndi(180,270))
        px.play(3, G_.SNDEFX["crush"])
        while px.play_pos(3) is not None:
            pass
        return False
    else:
        px.stop()
        px.play(3,G_.SNDEFX["defeat"], loop=False)
        return True


def scroll_map(stage):
    match stage.scroll_direction:
        case 0:
            px.bltm(0,-stage.scroll_counter, 1, 0,0, G_.P_MAIN_WND[2],G_.P_MAIN_WND[3])
            px.bltm(0,G_.P_MAIN_WND[3]-stage.scroll_counter, 0, 0,0, G_.P_MAIN_WND[2],stage.scroll_counter)
        case 1:
            px.bltm(stage.scroll_counter,0, 1, 0,0, G_.P_MAIN_WND[2]-stage.scroll_counter,G_.P_MAIN_WND[3])
            px.bltm(0,0, 0, G_.P_MAIN_WND[3]-stage.scroll_counter,0, stage.scroll_counter,G_.P_MAIN_WND[3])
        case 2:
            px.bltm(-stage.scroll_counter,0, 1, 0,0, G_.P_MAIN_WND[2],G_.P_MAIN_WND[3])
            px.bltm(G_.P_MAIN_WND[2]-stage.scroll_counter,0, 0, 0,0, stage.scroll_counter,G_.P_MAIN_WND[3])
        case 3:
            px.bltm(0,stage.scroll_counter, 1, 0,0, G_.P_MAIN_WND[2],G_.P_MAIN_WND[3]-stage.scroll_counter)
            px.bltm(0,0, 0, 0,G_.P_MAIN_WND[3]-stage.scroll_counter,G_.P_MAIN_WND[2],stage.scroll_counter)

    stage.scroll_counter += 16
    if stage.scroll_counter >= G_.P_MAIN_WND[2]:
        stage.scroll_counter = 0
        return True
    return False


def stage_prelude(stage_id):
    match stage_id:
        case 0:
            return ["　目の前に広がる見覚えのない景色と生き物達",
                    "　ここは一体…しかし今は生き延びる事が先決だ"]
        case 1:
            return ["　深い森は薄暗く、遠くから何かの叫び声が聞こえる",
                    "　所々に顔を覗かせる沼には気を付けるべきだろう"]
        case 2:
            return ["　むき出しの岩が突き出す間を、時折強い風が吹きすさぶ",
                    "　煽られては身動きが取れなくなりそうだ"]
        case 3:
            return ["　辺り一面凍てついて、足元は磨かれた鏡のようだ",
                    "　寒さに軋む体と心を奮い立たせ、道なき道を往く"]
        case 4:
            return ["　幸いな事に不思議な岩肌が灯り代わりになりそうだ",
                    "　寒さを凌ぐには良さそうだが、不穏な気配が漂う"]
        case 5:
            return ["　洞窟の扉の先には、炎に巻かれた城がそびえ立つ",
                    "　初めて見る筈の光景に、胸の奥で何かが騒いでいる"]


def opening(window, step):
    match step:
        case 0:
            window.message_text = ["眩しい陽射しが瞼越しに、その明るさを伝えてくる",
                                   "どうやら深く眠っていたようだ・・・"]
        case 1:
            window.message_text = ["重く閉じていた目を開き、陽射しに目を凝らす",
                                   "陽の高さから、時間はそろそろ真昼になるだろうか"]
        case 2:
            window.message_text = ["腹も空いているし、なにか軽く食べようか",
                                   "そう考えて固いベッドから起き上がり、事態に気が付いた"]
        case 3:
            window.message_text = ["寝ていた場所はベッドどころか部屋でもない、完全な野外",
                                   "それも、文明らしきものが欠片も見当たらない未開の原野！"]
        case 4:
            window.message_text = ["・・・何故自分はこんな所で寝そべっていたのか？",
                                   "夕べ眠る前、いったい何をしていたのだろうか？！"]
        case 5:
            window.message_text = ["・・・・・・あれ？・・・んんん？？",
                                   "いやまってくれ　そもそも自分は何者なんだ？？？"]
        case 6:
            window.message_text = ["両親の顔、生まれた町、全て思い出せない！",
                                   "呼吸も忘れて思考に沈み、ようやく思い出した名前は・・・"]
        case 7:
            return True
    return False


def interlude_0(window, step):
    match step:
        case 0:
            window.message_text = ["激しい闘いの末、強大な敵を討ち倒すことができた",
                                   "へたりこんで荒く息をついていると、",
                                   "横たわる亡骸がうっすらと光を放っている事に気付く！",
                                   "",
                                   "・・・慌てて距離を取り様子を伺ってみたが、",
                                   "どうやら危険な兆候ではないようだ",
                                   "",
                                   "恐る恐る近付いてみる",
                                   "",
                                   "ゆったりと波打つような光は、",
                                   "とても穏やかなものに見えた"]
        case 1:
            window.message_text = ["",
                                   "休息を終え、次の目的地を目指す",
                                   "視線は草原の向こう、鬱蒼と茂った森へ向いている",
                                   "",
                                   "禍々しい雰囲気の漂う場所だ",
                                   "今までより恐ろしいものと出会うだろう",
                                   "",
                                   "",
                                   "弛緩した気持ちを引き締め、入念に準備を行った",
                                   "",
                                   "",
                                   "　　　亡骸の光は、いつの間にか消えていた"]
        case 2:
            return True
    return False


def interlude_1(window, step):
    match step:
        case 0:
            window.message_text = ["再び激闘を経て、悪夢のような闘いに打ち勝った",
                                   "油断する事なく周囲を警戒する",
                                   "",
                                   "どうやら安全らしいが、それより気を惹くのは",
                                   "また亡骸がうっすら光っていることだ",
                                   "",
                                   "草原で見た光とは少し異なる印象をうけるが、",
                                   "やはり危険よりは穏やかさを感じさせる",
                                   "そっと亡骸に触れてみたが、特に何も起こらない",
                                   "",
                                   "光が納まる気配はなく、何かが寄ってくるでもない",
                                   "ただひっそりと薄明りが森を照らしていた"]
        case 1:
            window.message_text = ["",
                                   "先へ進んでみよう　森の果てはすぐそこだ",
                                   "少し開けてきた頭上から行く先を眺める",
                                   "",
                                   "ゴツゴツとした岩肌が剥き出しの山が見える",
                                   "今度は一体何が待ち受けているのだろうか",
                                   "",
                                   "山へ向かう準備を整えながら、",
                                   "何か予感めいたもので胸がざわついている",
                                   "",
                                   "",
                                   "　　　亡骸は役目を終えたように暗く横たわっている"]
        case 2:
            return True
    return False


def interlude_2(window, step):
    match step:
        case 0:
            window.message_text = ["空を舞う大鷲にとどめの一撃を叩きこむ！",
                                   "無限に続くかのような闘いに、ようやく終止符を打つ",
                                   "亡骸は、思った通りうっすらと光っている",
                                   "",
                                   "これがいったい何を示すのか、全く見当もつかない",
                                   "それとも、意味など無くただそういうものなのか",
                                   "",
                                   "危険はないと感じるが、何かをもたらす訳でもない",
                                   "",
                                   "正体の知れないものが付き纏う気味の悪さは、",
                                   "先行きに小さな不安を感じさせる"]
        case 1:
            window.message_text = ["",
                                   "これ以上考えても仕方あるまい",
                                   "何でもないなら、捨て置けばよいのだろう",
                                   "それよりも行く先を確かめなければ",
                                   "",
                                   "山の向こうは随分北の土地になるようだ",
                                   "白い雪に覆われた大地が眩しく目をうつ",
                                   "",
                                   "凍えてしまわないよう、十分な準備が必要だろう",
                                   "",
                                   "",
                                   "　　　亡骸に灯っていた光は、もう見えない"]
        case 2:
            return True
    return False


def interlude_3(window, step):
    match step:
        case 0:
            window.message_text = ["氷の巨人は、ゆっくりと倒れ込んだ",
                                   "その衝撃が大地を揺らし、周囲の雪や氷まで砕き飛ばす",
                                   "",
                                   "吹きすさぶ雪で視界が悪く、辺りの状況が見渡せない",
                                   "亡骸が光を放っているのかも定かではない",
                                   "",
                                   "そのような場合ではない事に気付く",
                                   "勢いを増す風と切り裂くように打ち付ける氷の礫は",
                                   "もはや吹雪の様相を呈している",
                                   "",
                                   "一刻も早く避難しなければ！"]
        case 1:
            window.message_text = ["",
                                   "・・・",
                                   "方向もほとんど分からないまま、ひたすら前へ",
                                   "",
                                   "いつの間にか目の前には切り立った崖が現れる",
                                   "大きな石でもあれば風が凌げるだろう",
                                   "必死の思いで崖伝いに進んでいくと・・・",
                                   "",
                                   "崖に穿たれた大穴に辿り着いた！",
                                   "ここなら風除けには十分だ",
                                   "風雪からほうほうの体で逃げ出し、休める場所を探す"]
        case 2:
            return True
    return False


def interlude_4(window, step):
    match step:
        case 0:
            window.message_text = ["人知を超えた存在との闘いをからくも制した",
                                   "もはや奇跡だと呼んで差し支えないだろう",
                                   "",
                                   "体中どこと言わず傷だらけのまま、大の字になる",
                                   "もはや指一本動かせそうにない",
                                   "気を抜けば意識を失いそうだ",
                                   "",
                                   "倒した竜がどうなったのか辺りを見回す",
                                   "",
                                   "しかし、あれほどの巨体だったにも関わらず、",
                                   "激しい闘いの相手は影も形も見当たらなかった"]
        case 1:
            window.message_text = ["いったいどういう事だろう",
                                   "いくら目を凝らしても、闘いの痕跡すら見当たらない",
                                   "しかし傷付いた体は先程の闘いが幻では無かったと訴える",
                                   "",
                                   "辺りを見回していると、物陰に小さな扉をみつけた",
                                   "あの竜はこの扉の番人だったのだろうか",
                                   "",
                                   "細く開いた扉はふわふわと揺れ、簡単に開きそうだ",
                                   "あの先はどこへ続いているのだろうか・・・",
                                   "",
                                   "そんな事を考えながら眠りに落ちていった"]
        case 2:
            return True
    return False


def interlude_5(window, step):
    match step:
        case 0:
            window.message_text = ["最後の敵を討ち果たしたが、しかし・・・",
                                   "",
                                   "襲い掛かって来たのは、紛れもない天使の姿",
                                   "生き物の如く息絶えるなど、有り得るのだろうか",
                                   "",
                                   "亡骸なのか、力を使い果たした抜け殻なのか",
                                   "黄金の像となったそれは、しずかに佇んでいる",
                                   "",
                                   "そもそも、天使とは神の使徒ではなかったか",
                                   "それが何故自分を襲うのか、まるで身に覚えがない",
                                   "",
                                   "生きる為に奪った命が、裁きの天秤に掛けられたのか"]
        case 1:
            window.message_text = ["言葉にし難い感情に戸惑って立ち尽くす",
                                   "",
                                   "・・・そうしてどのくらい経っただろうか",
                                   "ふと気付くと、辺りが穏やかな光に覆われている",
                                   "この旅の中で何度も見てきた、あの光を思い出させる",
                                   "",
                                   "黄金像となった天使を見やる",
                                   "しかし、黄金ではあってもそれ自体は美しいだけだ",
                                   "一体どこから・・・と辺りを見回してみるが",
                                   "",
                                   "光源らしいものは近くに見当たらない",
                                   "何気なく天を仰ぎ、そして気付く"]
        case 2:
            window.message_text = ["光は差しているのではない！自身が光っているのだ！",
                                   "",
                                   "痛みや苦しみはない　熱を感じもしない",
                                   "体に刻まれたはずの、闘いの傷痕すら消え失せている",
                                   "どこか絵空事のような状況に思考が付いていけない",
                                   "",
                                   "辺りの景色は霧のように白く霞み始めた",
                                   "自分は今立っているのか？最早手足の感覚も覚束ない",
                                   "一体何が起きている・・・？思考がまとまらない",
                                   "　そのうちに　眩暈を覚え倒れ込む", 
                                   "",
                                   "　　　そうして薄れゆく意識の中、声を聴いた・・・"]
        case 3:
            return True
    return False


class ShootingStar:
    def __init__(self):
        dx = px.rndf(-1, 1)
        dy = px.rndf(-1, 1)
        while dx == 0 and dy == 0:
            dx = px.rndf(-1, 1)
            dy = px.rndf(-1, 1)
        length = (dx * dx + dy * dy) ** 0.5
        dx /= length
        dy /= length
        speed = px.rndf(2, 4)
        self.vx = dx * speed
        self.vy = dy * speed
        self.x = px.width//2
        self.y = px.height//2
        self.life = 200
        self.colors = [7,7,7,7,7,7,7,7,7,15,15,15,15,15,15,15,6,6,6,6,6,6,14,14,14,14,14,13,13,13,13,10,10,10,9,9,2]
        self.color = self.colors[px.rndi(0,len(self.colors)-1)]
        self.size = px.rndf(0.1,1)

        # 尾の履歴（最大10個）
        self.trail = []

    def update(self):
        # 履歴を追加
        self.trail.append((self.x, self.y))
        if len(self.trail) > 3:  # 尾の長さ
            self.trail.pop(0)

        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return (
            self.life <= 0
            or self.x < -10 or self.x > G_.P_MAIN_WND[2] + G_.P_SUB_WND[2] + 10
            or self.y < -10 or self.y > G_.P_MAIN_WND[3] + 10
        )

    def draw(self):
        # 尾を古い順に描画（色をだんだん暗く）
        for i, (tx, ty) in enumerate(self.trail):
            col = 7 - i // 2  # 段階的に色を暗く
            if col < 1:
                col = 1
            px.circ(tx, ty, 0.001, col)

        px.circ(self.x, self.y, self.size, self.color)


def opening_u(window, step):
    match step:
        case 0:
            window.message_text = ["んんん・・・なんだよ眩しいな・・・",
                                   "おっとそうか　また寝ちまったのか"]
        case 1:
            window.message_text = ["夕べの深酒が効いたか道端でゴロリと寝そべって、",
                                   "高々昇るおてんとさまを眺めてる"]
        case 2:
            window.message_text = ["うー頭いてぇ　水飲みにいくか",
                                   "ゆらりと起き上がり、ふらつく頭で周りを見渡す"]
        case 3:
            window.message_text = ["・・・なんだこりゃ？",
                                   "街の酒場で飲んでたはずが、なんだってこんな"]
        case 4:
            window.message_text = ["周囲は街どころか人影もない原っぱ",
                                   "代わりに居るのは何やら物騒な生き物たち"]
        case 5:
            window.message_text = ["うおおアレやべえんじゃねぇのか？",
                                   "とにかくちょっと移動するか"]
        case 6:
            window.message_text = ["・・・どこへ？　あれ？　何も思い出せねぇや",
                                   "ていうかちょっとまて　俺の名前は何だ？"]
        case 7:
            return True
    return False


def interlude_0_u(window, step):
    match step:
        case 0:
            window.message_text = ["なんだアイツ・・・とんでねぇバケモノだったな",
                                   "突然吠えたと思ったら色まで妙な具合になりやがるし",
                                   "",
                                   "かと思えば死体はまるで灰みたいじゃねぇか",
                                   "吹けば飛ぶってもんでもなさそうだが・・・",
                                   "",
                                   "小突いてみりゃコンコンと固い音がする",
                                   "いやこれ石か！かーっ、肉にありつけると思ったら！",
                                   "",
                                   "まあいいや、飯の事は後で考えるか",
                                   "もう起きてらんねーや"]
        case 1:
            window.message_text = ["・・・",
                                   "・・・ううん",
                                   "",
                                   "ああよく寝た　すっかり調子も戻ったぜ",
                                   "いや何だ？傷も全部治ってんのかよ",
                                   "",
                                   "もしかしたら、寝たら全部無かった事になんのか？！",
                                   "大慌てで荷物を探ってみたんだが・・・",
                                   "",
                                   "問題ねーな！よかったぜ！",
                                   "さっさとこんなトコからずらかるか"]
        case 2:
            return True
    return False


def interlude_1_u(window, step):
    match step:
        case 0:
            window.message_text = ["またこんなのかよ～～勘弁してくれよ　ったく",
                                   "",
                                   "バカでかい割にゃ　大したこた無かったけどな",
                                   "",
                                   "こいつも石ンなってやがんのか",
                                   "まあこんなデケェ蛇なんぞ食うのはヤベーか",
                                   "",
                                   "にしてもさっきまでニョロニョロしてたのが",
                                   "こんな行儀よく固まるってのも気味ワリィな",
                                   "",
                                   "まーいーや　とりあえずひと休みだ",
                                   "後のこたぁ後でいい"]
        case 1:
            window.message_text = ["・・・・・・・・",
                                   "目が覚めたはいいが、こう真っ暗なんじゃあ",
                                   "昼だか夜だかわかりゃしねーな",
                                   "",
                                   "取り敢えず森抜けちまうか",
                                   "さっき見た山の方へ行きゃ少しは明るくなンだろ",
                                   "",
                                   "それにしてもよぉ　なんだってこんな事んなってんだ",
                                   "いけどもいけども畜生共ばっかりでよぉ・・・",
                                   "どこまで行きゃいいんだよ・・・",
                                   "",
                                   "　　　　　　　　　　酒飲みてぇなあ・・・"]
        case 2:
            return True
    return False


def interlude_2_u(window, step):
    match step:
        case 0:
            window.message_text = ["せっ！！どうだオラァ！！！",
                                   "",
                                   "やったか？ぐったりしてやがんぜ　ハハッ",
                                   "ふー、飛び回るやつってな厄介なもんだな",
                                   "",
                                   "今度から羽根生えたヤツは容赦無しだ！",
                                   "",
                                   "ん－、しかしコイツも石か",
                                   "鳥なら美味かっただろうになぁ・・・",
                                   "",
                                   "いやだめだ、酒も無しに焼鳥なんざ！！"]
        case 1:
            window.message_text = ["しかしなんつーか　森の蛇といい",
                                   "図体デケぇ割に大した事ねぇんだよなあ",
                                   "見た目はこう、ヌシ！って感じなんだが・・・",
                                   "",
                                   "まいいか、つええヤツにボコられるよりゃ",
                                   "安全安心で完勝って方がメシもうめぇわ",
                                   "",
                                   "ゴロリと横になって空を見上げる",
                                   "",
                                   "山の上だけあって月がちけぇなあ",
                                   "お星さんもキラキラキラキラ",
                                   "こんな綺麗なモン見たの久しぶりだぜ"]
        case 2:
            return True
    return False


def interlude_3_u(window, step):
    match step:
        case 0:
            window.message_text = ["これでぇっ！！どうでえぇ！！",
                                   "渾身の力を込めた一撃が巨人を打ちのめす！！",
                                   "",
                                   "やっこさん、ガックシ膝ついて仰け反ったら",
                                   "そのままブッ倒れてきやがった！あぶねーだろ！！",
                                   "",
                                   "ん、こいつは石になんねーのか",
                                   "いやでもさすがに同じ形の生きモンは食えねーよ",
                                   "あーなんでこいつに限って・・・",
                                   "こんなクソ寒ぃトコに腰巻イッチョなんだ",
                                   "暖の酒くらい持ってんじゃねーのか！どこだ！！"]
        case 1:
            window.message_text = ["探し回って見つけたのは妙な宝石だ",
                                   "街中なら酒代にもなンだろうが、ここじゃなぁ・・・",
                                   "まあいいさ、駄賃に貰っといてやんよ",
                                   "",
                                   "んでこのデカイ穴、巣穴かと思ってたが・・・",
                                   "奥の方続いてやがんな？灯りも点いてるか？",
                                   "",
                                   "決めた！もう雪はウンザリだ！",
                                   "それによ、こういう深い洞窟はアレだろ？",
                                   "古くからドラゴンが住んでてよ",
                                   "お宝をしこたま溜め込んでるってのが定番だろ？"]
        case 2:
            return True
    return False


def interlude_4_u(window, step):
    match step:
        case 0:
            window.message_text = ["ヒャーッ！さすがに危なかったぜ！！",
                                   "",
                                   "目の前にすっ転がってやがんのはドラゴンだ",
                                   "今までと比べものにならねぇデカさと圧",
                                   "気の弱ぇヤツなら見ただけで失神モンだぜ",
                                   "",
                                   "それをガチで仕留めちまった俺なんだが・・・",
                                   "",
                                   "それなりにつえー自覚はなんとなくあった",
                                   "だがそれもチビ相手だ　こんなデケーのは知らねぇ",
                                   "これをヒネっちまうのはヤベーだろ"]
        case 1:
            window.message_text = ["どいつもこいつも図体のクセして弱ぇと思ってたが",
                                   "もしかして、俺がクソ強くなってんのか？？",
                                   "それともここは雑魚いヤツの集まるシマか？",
                                   "",
                                   "そもそもあの原っぱで目ぇ覚めたってのがヘンだ",
                                   "今起きてる俺は、俺が知ってる俺なのか？",
                                   "",
                                   "・・・あークソ、考えたって分かるワケねぇか！",
                                   "ともかくお宝は無かった！そんだけだ！",
                                   "くたびれ儲けもいいトコだぜ！ったく！！",
                                   "あの小洒落たドア、あの先に期待すっか・・・"]
        case 2:
            return True
    return False


def interlude_5_u(window, step):
    match step:
        case 0:
            window.message_text = ["ぜぇ　ぜぇ　ああぁぁぁ　もう無理だ！",
                                   "もう立ってらんねえぞ！",
                                   "",
                                   "へたりこんでそのまま大の字に倒れる",
                                   "ヘッ、だから言ったろ！羽生えたのは容赦ナシだってよ！",
                                   "",
                                   "金色の天使は、塩の柱のように立ち尽くすや否や",
                                   "腰から下が崩れ落ち、上半身のみの奇怪な像となった",
                                   "",
                                   "逃亡者だの唆しただの、何の話だってんだ",
                                   "意味もフメーでいきなり襲い掛かってくるようなのが",
                                   "天使だとかって、何かの笑い話かよ"]
        case 1:
            window.message_text = ["言葉にし難い感情に戸惑って立ち尽くす",
                                   "",
                                   "・・・そうしてどのくらい経っただろうか",
                                   "ふと気付くと、辺りが休息に暗くなり始めた",
                                   "",
                                   "日の入りにしちゃやけに急いで暗くなりやがんな",
                                   "なんだなんだ、まだなんかのお出ましあんのかよ",
                                   "今掛かってきやがったら・・・どうにもできねぇな",
                                   "指一本動かねぇ　てかマジで何にも見えねぇぞ！",
                                   "",
                                   "なんだよ、こんな終わりってなぁネェだろ・・・",
                                   "最後にウメェ酒浴びる程飲ませてくれよ"]
        case 2:
            window.message_text = ["ダメだ　もう目ェ開けてらんねぇや・・・",
                                   "チックショウ！！こんだけ苦労して最後がコレかよ！",
                                   "",
                                   "これがその邪悪のナントカっていうやつの仕業か！",
                                   "覚えてやがれ！弄ぶようなマネしやがって！！",
                                   "", 
                                   "テメーも羽生えてやがんだろ！見てやがれ！！",
                                   "もいで千切ってギッタギタにしてやっからな！！！",
                                   "",
                                   "ハァ・・・ハァ・・・クソッ・・・！",
                                   "",
                                   ""]
        case 3:
            window.message_text = ["",
                                   "",
                                   "",
                                   "",
                                   "",
                                   "",
                                   "",
                                   "",
                                   "",
                                   "", 
                                   "　　　　　　　　　　　　　　　すまなかった・・・",
                                   "",
                                   ]
        case 4:
            return True
    return False
