import dearpygui.dearpygui as dpg
import threading, time, random, requests, urllib.parse, itertools, os
from collections import deque
from concurrent.futures import ThreadPoolExecutor

# ----------------------------
# バックエンド処理（Tkinter 時代の処理を流用）
# ----------------------------

# グローバル変数
token_list = []                  # 現在有効なTokenリスト
invalid_403_tokens = set()       # 403エラーで除外したToken
token_file_path = None           # 選択されたTokenファイルのパス
token_file_monitor_started = False  # Tokenファイル監視スレッドの起動フラグ
fontdir= "./assets/font/font.ttf"

# 全体のレート制限（10分間10000件）
message_timestamps = deque()     
rate_lock = threading.Lock()

# 各Tokenごとの1秒間の送信件数を管理する辞書
token_rate_dict = {}

# 最大10スレッドのプール（送信処理用）
executor = ThreadPoolExecutor(max_workers=25)

# Token ローテーション用イテレータ（select_token_file で更新）
token_cycle = itertools.cycle(token_list)

# 通報成功件数のカウント
successful_count = 0
count_lock = threading.Lock()
custom_font = None

# 通報先 URL（例）
report_url = "https://discord.com/api/v9/reporting/message"

def wait_for_token_rate_limit(token):
    global token_rate_dict
    while True:
        now = time.time()
        dq = token_rate_dict.setdefault(token, deque())
        while dq and dq[0] < now - 1:
            dq.popleft()
        if len(dq) >= 49:
            time.sleep(3)
        else:
            dq.append(now)
            break

def wait_for_rate_limit():
    while True:
        with rate_lock:
            now = time.time()
            while message_timestamps and message_timestamps[0] < now - 600:
                message_timestamps.popleft()
            if len(message_timestamps) < 10000:
                message_timestamps.append(now)
                return
        time.sleep(1.5)

def remove_token_from_file(token):
    global token_file_path
    try:
        with open(token_file_path, "r", encoding="utf-8") as f:
            tokens = f.read().splitlines()
        tokens = [t.strip() for t in tokens if t.strip() and t.strip() != token]
        with open(token_file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(tokens))
        print(f"Token {token[:15]} removed from file due to 401 error")
    except Exception as e:
        print(f"Error updating token file: {e}")

def handle_token_error(token, status_code):
    global token_list, invalid_403_tokens
    if token in token_list:
        token_list.remove(token)
    if status_code == 401:
        remove_token_from_file(token)
        print(f"Token {token[:15]} removed (401)")
    elif status_code == 403:
        invalid_403_tokens.add(token)
        print(f"Token {token[:15]} removed from active tokens (403)")

def check_token_error(response, token):
    if response.status_code == 401:
        handle_token_error(token, 401)
        return True
    elif response.status_code == 403:
        handle_token_error(token, 403)
        return True
    return False

def monitor_token_file():
    global token_list, token_file_path, invalid_403_tokens
    while True:
        if token_file_path:
            try:
                with open(token_file_path, "r", encoding="utf-8") as f:
                    tokens = f.read().splitlines()
                tokens = [t.strip() for t in tokens if t.strip()]
                for token in tokens:
                    if token not in token_list and token not in invalid_403_tokens:
                        token_list.append(token)
                        print(f"New token added: {token[:15]}...")
            except Exception as e:
                print("Error reading token file:", e)
        time.sleep(10)

def select_token_file_from_path(path):
    global token_list, token_file_path, token_file_monitor_started, token_cycle
    token_file_path = path
    try:
        with open(token_file_path, "r", encoding="utf-8") as file:
            tokens = [token.strip() for token in file.read().splitlines() if token.strip()]
        for token in tokens:
            if token not in token_list:
                token_list.append(token)
        print("Token file loaded.")
        token_cycle = itertools.cycle(token_list)
        if not token_file_monitor_started:
            threading.Thread(target=monitor_token_file, daemon=True).start()
            token_file_monitor_started = True
    except Exception as e:
        print("Error reading token file:", e)

def generate_bypass_string(length=4):
    include_ranges = [(0x0000, 0xFFFF)]
    alphabet = [chr(code_point) for current_range in include_ranges
                for code_point in range(current_range[0], current_range[1] + 1)]
    generated = "".join(random.sample(alphabet, length))
    result = generated.encode("utf-8", "replace")
    result = result.decode('utf-8')
    return result

def send_message(url, message, num_requests, bypass=False, vortex=False, wick=False, mention_users="", mention_count=0):
    def worker(token):
        headers = {"authorization": token}
        # もしメンション指定があれば改行で分割
        lines = mention_users.split("\n") if mention_users else []
        counter = 0  # Wick mode用のメッセージカウンタ
        for _ in range(num_requests):
            counter += 1
            if wick:
                # 基本メッセージはランダムな長さのbypass文字列
                msg = generate_bypass_string(random.randint(1, 30))
                # 3メッセージに1回、40%の確率でメンションを追加する
                if counter % 3 == 0 and lines and random.random() < 0.4:
                    cnt = min(mention_count, len(lines)) if mention_count > 0 else 1
                    msg += " " + " ".join(f"<@!{uid.strip()}>" for uid in random.sample(lines, cnt))
            elif vortex:
                msg = "".join(char + generate_bypass_string() for char in message)
            elif bypass:
                msg = message + " " + generate_bypass_string()
            else:
                msg = message
            # 非Wickモードの場合は通常のメンション処理
            if not wick and lines and mention_count > 0:
                cnt = min(mention_count, len(lines))
                msg += " " + " ".join(f"<@!{uid.strip()}>" for uid in random.sample(lines, cnt))
            data = {"content": msg}
            try:
                wait_for_token_rate_limit(token)
                wait_for_rate_limit()
                response = requests.post(url, headers=headers, json=data)
                if check_token_error(response, token):
                    continue
                if response.status_code != 200:
                    print("エラー", f"メッセージ送信失敗: {response.text}")
                else:
                    print(f"Message sent: {msg}")
            except Exception as e:
                print("エラー", f"メッセージ送信例外: {e}")
            if wick:
                time.sleep(random.uniform(3, 7))
    for token in token_list.copy():
        executor.submit(worker, token)

def create_threads(url, thread_name, message, num_threads, bypass=False):
    def worker(token, thread_name):
        headers = {"authorization": token}
        for _ in range(num_threads):
            tn = f"{thread_name} {generate_bypass_string()}" if bypass else thread_name
            data = {"name": tn, "type": 11, "auto_archive_duration": 60}
            try:
                wait_for_token_rate_limit(token)
                response = requests.post(url, headers=headers, json=data)
                if check_token_error(response, token):
                    continue
                if response.status_code == 429:
                    retry_after = response.json().get("retry_after", 1)
                    print(f"レート制限: {retry_after}秒待機")
                    time.sleep(retry_after)
                    continue
                if response.status_code == 201:
                    thread_id = response.json().get("id")
                    send_message(f"https://discord.com/api/v9/channels/{thread_id}/messages", message, 1, bypass)
                else:
                    print("エラー", f"スレッド作成失敗: {response.text}")
            except Exception as e:
                print("エラー", f"スレッド作成例外: {e}")
    for token in token_list.copy():
        executor.submit(worker, token, thread_name)

def set_tokens_online():
    url = "https://discord.com/api/v9/users/@me/settings"
    data = {"status": "online"}
    def worker(token):
        headers = {"authorization": token, "Content-Type": "application/json"}
        try:
            wait_for_token_rate_limit(token)
            response = requests.patch(url, headers=headers, json=data)
            if check_token_error(response, token):
                return
            if response.status_code in (200, 204):
                print(f"Token {token[:15]}... onlineに設定")
            else:
                print(f"Token {token[:15]}... online設定失敗: {response.text}")
        except Exception as e:
            print(f"Token {token[:15]}... online設定例外: {e}")
    for token in token_list.copy():
        executor.submit(worker, token)

def send_typing_indicator_single(channel_id, token):
    url = f"https://discord.com/api/v9/channels/{channel_id}/typing"
    headers = {"authorization": token}
    try:
        wait_for_token_rate_limit(token)
        response = requests.post(url, headers=headers)
        if check_token_error(response, token):
            return
        if response.status_code == 204:
            print(f"Token {token[:15]}... typing送信成功 in {channel_id}")
        else:
            print(f"Token {token[:15]}... typing送信失敗: {response.text}")
    except Exception as e:
        print(f"Token {token[:15]}... typing送信例外: {e}")

def continuous_typing(channel_id):
    tokens_to_use = token_list if len(token_list) <= 10 else token_list[:10]
    while dpg.does_item_exist("MainWindow"):
        for token in tokens_to_use.copy():
            executor.submit(send_typing_indicator_single, channel_id, token)
        time.sleep(2)

def add_reaction(channel_id, message_id, emoji):
    encoded_emoji = urllib.parse.quote(emoji, safe='')
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me?location=Message Hover Bar&type=0"
    def worker(token):
        headers = {"authorization": token}
        try:
            wait_for_token_rate_limit(token)
            response = requests.put(url, headers=headers)
            if check_token_error(response, token):
                return
            if response.status_code == 204:
                print(f"Token {token[:15]}... reaction '{emoji}' added")
            else:
                print(f"Token {token[:15]}... reaction追加失敗: {response.text}")
        except Exception as e:
            print(f"Token {token[:15]}... reaction追加例外: {e}")
    for token in token_list.copy():
        executor.submit(worker, token)

def send_report(msgid, channel, target_success, bypass=False):
    global successful_count
    token = next(token_cycle)
    payload = {
        "version": "1.0",
        "variant": "6",
        "language": "en",
        "breadcrumbs": [3, 61, 71, 106],
        "elements": {},
        "channel_id": channel,
        "message_id": msgid,
        "name": "message"
    }
    headers = {
        "Authorization": token,
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    try:
        # Report用にも各Tokenごとのレート制限および全体のレート制限を適用
        wait_for_token_rate_limit(token)
        wait_for_rate_limit()
        response = requests.post(report_url, json=payload, headers=headers)
        if check_token_error(response, token):
            return
        if response.status_code == 200:
            with count_lock:
                successful_count += 1
                print(f"Success: {successful_count}/{target_success}")
        else:
            print(f"Failure: Status Code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

def report_action():
    msgid = dpg.get_value("report_message_id")
    channel = dpg.get_value("report_channel_id")
    try:
        target_success = int(dpg.get_value("target_success_input"))
    except:
        target_success = 0
    global successful_count
    successful_count = 0
    with ThreadPoolExecutor(max_workers=10) as ex:
        futures = set()
        from concurrent.futures import wait, FIRST_COMPLETED
        while successful_count < target_success:
            while len(futures) < 3 and successful_count < target_success:
                futures.add(ex.submit(send_report, msgid, channel, target_success, False))
            done, futures = wait(futures, return_when=FIRST_COMPLETED)

def start_action(action_type, bypass_message=False, vortex=False, wick=False, bypass_thread=False):
    if not token_list:
        print("エラー: トークンが読み込まれていません。")
        return
    channel_id = dpg.get_value("channel_id_input")
    mention_users = dpg.get_value("mention_ids_input")
    try:
        mention_count = int(dpg.get_value("mention_count_input"))
    except ValueError:
        mention_count = 0
    if action_type == "message":
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        send_message(url, dpg.get_value("message_input"), int(dpg.get_value("num_messages_input")),
                     bypass_message, vortex, wick, mention_users, mention_count)
    elif action_type == "thread":
        url = f"https://discord.com/api/v9/channels/{channel_id}/threads"
        create_threads(url, dpg.get_value("thread_name_input"), dpg.get_value("thread_message_input"),
                       int(dpg.get_value("num_threads_input")), bypass_thread)

def start_reaction():
    channel_id = dpg.get_value("channel_id_input")
    message_id = dpg.get_value("reaction_message_id")
    emoji = dpg.get_value("emoji_input")
    if not channel_id or not message_id or not emoji:
        print("エラー: 必要な情報が入力されていません。")
        return
    add_reaction(channel_id, message_id, emoji)

# ----------------------------
# Settings の実装
# ----------------------------
def apply_settings_callback(sender, app_data, user_data):
    # カラーピッカーは0.0～1.0の値を返すため、0～255に変換
    bg_color = dpg.get_value("bg_color_picker")  # 例: [r, g, b, a]
    text_color = dpg.get_value("text_color_picker")
    transparency = dpg.get_value("transparency_slider")
    bg = (int(bg_color[0]*255), int(bg_color[1]*255), int(bg_color[2]*255), int(transparency*255))
    txt = (int(text_color[0]*255), int(text_color[1]*255), int(text_color[2]*255), 255)
    with dpg.theme() as custom_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, bg)
            dpg.add_theme_color(dpg.mvThemeCol_Text, txt)
    dpg.bind_theme(custom_theme)
    print("Settings applied.")

# ----------------------------
# DearPyGui GUI 部分
# ----------------------------

dpg.create_context()

with dpg.font_registry():
    with dpg.font(fontdir, 20):

        # add the default font range
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
        dpg.add_font_range_hint(dpg.mvFontRangeHint_Japanese)

        # add specific range of glyphs
        dpg.add_font_range(0x3100, 0x3ff0)

        # add specific glyphs
        dpg.add_font_chars([0x3105, 0x3107, 0x3108])

        # remap や to %
        dpg.add_char_remap(0x3084, 0x0025)

#with dpg.font_registry():
#    custom_font = dpg.add_font(fontdir, 20)
#    dpg.bind_font(custom_font)

# ファイルダイアログ（Tokenファイル選択用）
with dpg.file_dialog(directory_selector=False, show=False, callback=lambda s, a, u: select_token_file_from_path(a["file_path_name"]), tag="file_dialog_id"):
    dpg.add_file_extension(".txt", color=[255,255,0])

# メニューのページ切り替えコールバック
def show_page(page_tag):
    for tag in ["MeinMenu", "ChatSender", "Reaction", "Thread", "Report", "Settings"]:
        dpg.configure_item(tag, show=False)
    dpg.configure_item(page_tag, show=True)

# Wick mode の場合に Message 入力欄の有効無効を更新するコールバック
def update_message_field_state_dpg(sender, app_data, user_data):
    if dpg.get_value("wick_checkbox"):
        dpg.configure_item("message_input", enabled=False)
    else:
        dpg.configure_item("message_input", enabled=True)

# メインウィンドウ
with dpg.window(label="DisRaider - By takowasabu & yutodadil", tag="MainWindow", width=1100, height=700):
    with dpg.group(horizontal=True):
        # 左側のメニュー
        with dpg.child_window(width=200, tag="menu_window"):
            dpg.add_text("Menu")
            dpg.add_separator()
            dpg.add_button(label="MeinMenu", callback=lambda: show_page("MeinMenu"))
            dpg.add_button(label="Chat Sender", callback=lambda: show_page("ChatSender"))
            dpg.add_button(label="Reaction", callback=lambda: show_page("Reaction"))
            dpg.add_button(label="Thread", callback=lambda: show_page("Thread"))
            dpg.add_button(label="Report", callback=lambda: show_page("Report"))
            dpg.add_button(label="Settings", callback=lambda: show_page("Settings"))
        # 右側のコンテンツ領域
        with dpg.child_window(tag="main_content", border=False):
            # MeinMenu ページ
            with dpg.group(tag="MeinMenu", show=True):
                dpg.add_text("MeinMenu")
                dpg.add_button(label="Select Token File", callback=lambda: dpg.show_item("file_dialog_id"))
                dpg.add_input_text(label="Channel ID", tag="channel_id_input")
                dpg.add_button(label="Set All Online", callback=lambda: executor.submit(set_tokens_online))
            # Chat Sender ページ
            with dpg.group(tag="ChatSender", show=False):
                dpg.add_text("Chat Sender")
                dpg.add_input_text(label="Message", tag="message_input", width=400)
                dpg.add_input_text(label="Number of Messages", tag="num_messages_input", default_value="1")
                dpg.add_input_text(label="Mention User IDs (newline separated)", tag="mention_ids_input", multiline=True, width=400)
                dpg.add_input_text(label="Number of Mentions", tag="mention_count_input", default_value="0")
                dpg.add_checkbox(label="bypass", tag="bypass_checkbox")
                dpg.add_checkbox(label="Vortex mode", tag="vortex_checkbox")
                dpg.add_checkbox(label="Wick mode", tag="wick_checkbox", callback=update_message_field_state_dpg)
                dpg.add_button(label="Run", callback=lambda: executor.submit(
                    start_action, "message",
                    dpg.get_value("bypass_checkbox"),
                    dpg.get_value("vortex_checkbox"),
                    dpg.get_value("wick_checkbox"),
                    False
                ))
                dpg.add_button(label="Send Typing Continuously", callback=lambda: threading.Thread(
                    target=continuous_typing,
                    args=(dpg.get_value("channel_id_input"),),
                    daemon=True
                ).start())
            # Reaction ページ
            with dpg.group(tag="Reaction", show=False):
                dpg.add_text("Reaction")
                dpg.add_input_text(label="Message ID", tag="reaction_message_id", width=400)
                dpg.add_input_text(label="Emoji", tag="emoji_input", width=100)
                dpg.add_button(label="Add Reaction", callback=lambda: start_reaction())
            # Thread ページ
            with dpg.group(tag="Thread", show=False):
                dpg.add_text("Thread")
                dpg.add_input_text(label="Thread Name", tag="thread_name_input", width=400)
                dpg.add_input_text(label="Thread Message", tag="thread_message_input", width=400)
                dpg.add_input_text(label="Number of Threads", tag="num_threads_input", default_value="1")
                dpg.add_checkbox(label="bypass", tag="thread_bypass_checkbox")
                dpg.add_button(label="Run", callback=lambda: executor.submit(
                    start_action, "thread",
                    False, False, False, dpg.get_value("thread_bypass_checkbox")
                ))
            # Report ページ
            with dpg.group(tag="Report", show=False):
                dpg.add_text("Report")
                dpg.add_input_text(label="Message ID", tag="report_message_id", width=400)
                dpg.add_input_text(label="Channel ID", tag="report_channel_id", width=400,)
                dpg.add_input_text(label="Target Success Count", tag="target_success_input", default_value="10")
                dpg.add_button(label="Run", callback=lambda: report_action())
            # Settings ページ（設定の適用）
            with dpg.group(tag="Settings", show=False):
                dpg.add_text("Settings")
                with dpg.group(horizontal=True):
                    dpg.add_color_picker(label="Background", tag="bg_color_picker", width=150, height=150, no_side_preview=True, no_small_preview=False, default_value=[0.1, 0.1, 0.1, 1.0])
                    dpg.add_color_picker(label="Text", tag="text_color_picker", width=150, height=150, no_side_preview=True, no_small_preview=False, default_value=[1.0, 1.0, 1.0, 1.0])
                dpg.add_slider_float(label="Transparency", tag="transparency_slider", default_value=1.0, min_value=0.0, max_value=1.0)
                dpg.add_button(label="Apply Settings", callback=apply_settings_callback)

dpg.create_viewport(title="DisRaider - By takowasabu & yutodadil", width=1100, height=400)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
