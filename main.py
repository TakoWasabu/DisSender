import tkinter as tk
from tkinter import filedialog
import requests
import random
import time


def send_requests(url, token, message, num_requests):
BypassStrings = '1234567890qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM-_,.あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン아이우에오카키쿠케코사시스세소타치츠쓰쯔테토나니누네노하히후헤호마미무메모야유요라리루레로와오응은음亜哀愛悪握圧扱安暗案以位依偉囲委威尉意慰易為異移維緯胃衣違遺医井域育一壱逸稲芋印員因姻引飲院陰隠韻右宇羽雨渦浦運雲営影映栄永泳英衛詠鋭液疫益駅悦謁越閲円園宴延援沿演炎煙猿縁遠鉛塩汚凹央奥往応押横欧殴王翁黄沖億屋憶乙卸恩温穏音下化仮何価佳加可夏嫁家寡科暇果架歌河火禍稼箇花荷華菓課貨過蚊我画芽賀雅餓介会解回塊壊快怪悔懐戒拐改械海灰界皆絵開階貝劾外害慨概涯街該垣嚇各拡格核殻獲確穫覚角較郭閣隔革学岳楽額掛潟割喝括活渇滑褐轄且株刈乾冠寒刊勘勧巻喚堪完官寛干幹患感慣憾換敢棺款歓汗漢環甘監看管簡緩缶肝艦観貫還鑑間閑関陥館丸含岸眼岩頑顔願企危喜器基奇寄岐希幾忌揮机旗既期棋棄機帰気汽祈季紀規記貴起軌輝飢騎鬼偽儀宜戯技擬欺犠疑義議菊吉喫詰却客脚虐逆丘久休及吸宮弓急救朽求泣球究窮級糾給旧牛去居巨拒拠挙虚許距漁魚享京供競共凶協叫境峡強恐恭挟教橋況狂狭矯胸脅興郷鏡響驚仰凝暁業局曲極玉勤均斤琴禁筋緊菌襟謹近金吟銀九句区苦駆具愚虞空偶遇隅屈掘靴繰桑勲君薫訓群軍郡係傾刑兄啓型契形径恵慶憩掲携敬景渓系経継茎蛍計警軽鶏芸迎鯨劇撃激傑欠決潔穴結血月件倹健兼券剣圏堅嫌建憲懸検権犬献研絹県肩見謙賢軒遣険顕験元原厳幻弦減源玄現言限個古呼固孤己庫弧戸故枯湖誇雇顧鼓五互午呉娯後御悟碁語誤護交侯候光公功効厚口向后坑好孔孝工巧幸広康恒慌抗拘控攻更校構江洪港溝甲皇硬稿紅絞綱耕考肯航荒行衡講貢購郊酵鉱鋼降項香高剛号合拷豪克刻告国穀酷黒獄腰骨込今困墾婚恨懇昆根混紺魂佐唆左差査砂詐鎖座債催再最妻宰彩才採栽歳済災砕祭斎細菜裁載際剤在材罪財坂咲崎作削搾昨策索錯桜冊刷察撮擦札殺雑皿三傘参山惨散桟産算蚕賛酸暫残仕伺使刺司史嗣四士始姉姿子市師志思指支施旨枝止死氏祉私糸紙紫肢脂至視詞詩試誌諮資賜雌飼歯事似侍児字寺慈持時次滋治璽磁示耳自辞式識軸七執失室湿漆疾質実芝舎写射捨赦斜煮社者謝車遮蛇邪借勺尺爵酌釈若寂弱主取守手朱殊狩珠種趣酒首儒受寿授樹需囚収周宗就州修愁拾秀秋終習臭舟衆襲週酬集醜住充十従柔汁渋獣縦重銃叔宿淑祝縮粛塾熟出術述俊春瞬准循旬殉準潤盾純巡遵順処初所暑庶緒署書諸助叙女序徐除傷償勝匠升召商唱奨宵将小少尚床彰承抄招掌昇昭晶松沼消渉焼焦照症省硝礁祥称章笑粧紹肖衝訟証詔詳象賞鐘障上丈乗冗剰城場壌嬢常情条浄状畳蒸譲醸錠嘱飾植殖織職色触食辱伸信侵唇娠寝審心慎振新森浸深申真神紳臣薪親診身辛進針震人仁刃尋甚尽迅陣酢図吹垂帥推水炊睡粋衰遂酔錘随髄崇数枢据杉澄寸世瀬畝是制勢姓征性成政整星晴正清牲生盛精聖声製西誠誓請逝青静斉税隻席惜斥昔析石積籍績責赤跡切拙接摂折設窃節説雪絶舌仙先千占宣専川戦扇栓泉浅洗染潜旋線繊船薦践選遷銭銑鮮前善漸然全禅繕塑措疎礎祖租粗素組訴阻僧創双倉喪壮奏層想捜掃挿操早曹巣槽燥争相窓総草荘葬藻装走送遭霜騒像増憎臓蔵贈造促側則即息束測足速俗属賊族続卒存孫尊損村他多太堕妥惰打駄体対耐帯待怠態替泰滞胎袋貸退逮隊代台大第題滝卓宅択拓沢濯託濁諾但達奪脱棚谷丹単嘆担探淡炭短端胆誕鍛団壇弾断暖段男談値知地恥池痴稚置致遅築畜竹蓄逐秩窒茶嫡着中仲宙忠抽昼柱注虫衷鋳駐著貯丁兆帳庁弔張彫徴懲挑朝潮町眺聴脹腸調超跳長頂鳥勅直朕沈珍賃鎮陳津墜追痛通塚漬坪釣亭低停偵貞呈堤定帝底庭廷弟抵提程締艇訂逓邸泥摘敵滴的笛適哲徹撤迭鉄典天展店添転点伝殿田電吐塗徒斗渡登途都努度土奴怒倒党冬凍刀唐塔島悼投搭東桃棟盗湯灯当痘等答筒糖統到討謄豆踏逃透陶頭騰闘働動同堂導洞童胴道銅峠匿得徳特督篤毒独読凸突届屯豚曇鈍内縄南軟難二尼弐肉日乳入如尿任妊忍認寧猫熱年念燃粘悩濃納能脳農把覇波派破婆馬俳廃拝排敗杯背肺輩配倍培媒梅買売賠陪伯博拍泊白舶薄迫漠爆縛麦箱肌畑八鉢発髪伐罰抜閥伴判半反帆搬板版犯班畔繁般藩販範煩頒飯晩番盤蛮卑否妃彼悲扉批披比泌疲皮碑秘罷肥被費避非飛備尾微美鼻匹必筆姫百俵標氷漂票表評描病秒苗品浜貧賓頻敏瓶不付夫婦富布府怖扶敷普浮父符腐膚譜負賦赴附侮武舞部封風伏副復幅服福腹複覆払沸仏物分噴墳憤奮粉紛雰文聞丙併兵塀幣平弊柄並閉陛米壁癖別偏変片編辺返遍便勉弁保舗捕歩補穂募墓慕暮母簿倣俸包報奉宝峰崩抱放方法泡砲縫胞芳褒訪豊邦飽乏亡傍剖坊妨帽忘忙房暴望某棒冒紡肪膨謀貿防北僕墨撲朴牧没堀奔本翻凡盆摩磨魔麻埋妹枚毎幕膜又抹末繭万慢満漫味未魅岬密脈妙民眠務夢無矛霧婿娘名命明盟迷銘鳴滅免綿面模茂妄毛猛盲網耗木黙目戻問紋門匁夜野矢厄役約薬訳躍柳愉油癒諭輸唯優勇友幽悠憂有猶由裕誘遊郵雄融夕予余与誉預幼容庸揚揺擁曜様洋溶用窯羊葉要謡踊陽養抑欲浴翌翼羅裸来頼雷絡落酪乱卵欄濫覧利吏履理痢裏里離陸律率立略流留硫粒隆竜慮旅虜了僚両寮料涼猟療糧良量陵領力緑倫厘林臨輪隣塁涙累類令例冷励礼鈴隷零霊麗齢暦歴列劣烈裂廉恋練連錬炉路露労廊朗楼浪漏老郎六録論和話賄惑枠湾腕'    last_request_time = time.time()
    for _ in range(num_requests):
        if use_bypass.get():
            # バイパス機能が有効の場合、ランダムな文字列を生成
            testa = random.randrange(6, 15)
            Bypass = ''.join(random.choice(BypassStrings) for _ in range(testa))
            data = {"content": message + Bypass}
        else:
            data = {"content": message}
        while time.time() - last_request_time < 0.2:  # 1秒間で15リクエストの場合、1リクエストあたり0.2秒
            time.sleep(0.5)

        headers = {"authorization": token}
        response = requests.post(url, headers=headers, data=data)
        print(f"Request: {response.status_code}")

        last_request_time = time.time()





def stop_sending():
    global running
    running = False



# ウィンドウの作成
window = tk.Tk()
window.title("DisSender - ver1.1")

def select_token_file():
    file_path = filedialog.askopenfilename(filetypes=[("テキストファイル", "*.txt")])
    entry_token_file.delete(0, tk.END)
    entry_token_file.insert(0, file_path)



# ファイル選択ボタン
label_num_requests = tk.Label(window, text="Token")
label_num_requests.pack()
entry_token_file = tk.Entry(window)
entry_token_file.pack()
button_select_token_file = tk.Button(window, text="トークンファイルを選択", command=select_token_file)
button_select_token_file.pack()



# 変数部分を入力するラベルとエントリー
label_variable = tk.Label(window, text="channelID:")
label_variable.pack()
entry_variable = tk.Entry(window)  # Define entry_variable here
entry_variable.pack()


# メッセージ入力欄
label_message = tk.Label(window, text="msg:")
label_message.pack()
entry_message = tk.Entry(window)
entry_message.pack()

# 送信回数入力欄
label_num_requests = tk.Label(window, text="num:")
label_num_requests.pack()
entry_num_requests = tk.Entry(window)
entry_num_requests.pack()



# バイパス機能の有効/無効を切り替える変数
use_bypass = tk.BooleanVar()

# バイパス機能のチェックボックス
check_bypass = tk.Checkbutton(window, text="BypassMode", variable=use_bypass)
check_bypass.pack()

# ベースURLを定義
base_url = "https://discord.com/api/v9/channels/"
base_url2 = "/messages"

# 送信ボタン
button = tk.Button(window, text="送信", command=lambda: send_requests(
    base_url + entry_variable.get() + base_url2,
    entry_token_file.get(),
    entry_message.get(),
    int(entry_num_requests.get())
))
button.pack()

# 停止ボタン
stop_button = tk.Button(window, text="Stop", command=stop_sending)
stop_button.pack()

# 結果表示欄
result_label = tk.Label(window)
result_label.pack()

window.mainloop()
