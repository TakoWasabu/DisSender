import tkinter as tk
import threading
from tkinter import filedialog, messagebox
import requests
import random
import time
import urllib.parse

# グローバル変数
token_list = []

def select_token_file():
    global token_list
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, "r", encoding="utf-8") as file:
            tokens = [token.strip() for token in file.read().splitlines() if token.strip()]
            if tokens:
                token_list = tokens  # トークンリスト更新
                entry_token.delete(0, tk.END)
                entry_token.insert(0, tokens[0])  # 最初のトークンを表示

def generate_bypass_string(length=4):
    """bypass文字列をランダムで生成（アルファベット大文字と数字）"""
    return ''.join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ123456789", k=length))

def send_message(url, message, num_requests, bypass=False, mention_users=None, mention_count=0):
    def worker(token):
        headers = {"authorization": token}
        mention_user_ids = mention_users.split("\n") if mention_users else []
        
        for _ in range(num_requests):
            msg = message  # 毎回リセット
            if bypass:
                msg += f" {generate_bypass_string()}"  # リクエストごとに異なるbypassを追加
            
            if mention_users and mention_count > 0:
                cnt = min(mention_count, len(mention_user_ids))
                random_mentions = random.sample(mention_user_ids, cnt)
                msg += " " + " ".join(f"<@!{uid.strip()}>" for uid in random_mentions)
            
            data = {"content": msg}
            try:
                response = requests.post(url, headers=headers, json=data)
                if response.status_code != 200:
                    messagebox.showerror("エラー", f"メッセージ送信に失敗しました: {response.text}")
                else:
                    print(f"Message sent: {msg}")
            except Exception as e:
                messagebox.showerror("エラー", f"メッセージ送信に失敗しました: {e}")
            time.sleep(0.2)

    for token in token_list:
        threading.Thread(target=worker, args=(token,)).start()

def create_threads(url, thread_name, message, num_threads, bypass=False):
    def worker(token, thread_name):
        headers = {"authorization": token}
        
        for _ in range(num_threads):
            tn = f"{thread_name} {generate_bypass_string()}" if bypass else thread_name
            data = {"name": tn, "type": 11, "auto_archive_duration": 60}
            try:
                response = requests.post(url, headers=headers, json=data)
                
                # レート制限チェック
                if response.status_code == 429:
                    retry_after = response.json().get("retry_after", 1)
                    print(f"レート制限: {retry_after}秒待機")
                    time.sleep(retry_after)
                    continue
                if response.status_code == 201:
                    thread_id = response.json().get("id")
                    send_message(f"https://discord.com/api/v9/channels/{thread_id}/messages", message, 1, bypass)
                else:
                    messagebox.showerror("エラー", f"スレッド作成に失敗しました: {response.text}")
            except Exception as e:
                messagebox.showerror("エラー", f"スレッド作成に失敗しました: {e}")
            time.sleep(0.5)

    for token in token_list:
        threading.Thread(target=worker, args=(token, thread_name)).start()

def set_tokens_online():
    url = "https://discord.com/api/v9/users/@me/settings"
    data = {"status": "online"}
    for token in token_list:
        headers = {"authorization": token, "Content-Type": "application/json"}
        try:
            response = requests.patch(url, headers=headers, json=data)
            if response.status_code in (200, 204):
                print(f"Token {token[:5]}... onlineに設定")
            else:
                print(f"Token {token[:5]}... online設定失敗: {response.text}")
        except Exception as e:
            print(f"Token {token[:5]}... online設定エラー: {e}")
        time.sleep(0.5)

def send_typing_indicator(channel_id):
    url = f"https://discord.com/api/v9/channels/{channel_id}/typing"
    for token in token_list:
        headers = {"authorization": token}
        try:
            response = requests.post(url, headers=headers)
            if response.status_code == 204:
                print(f"Token {token[:5]}... typing sent in {channel_id}")
            else:
                print(f"Token {token[:5]}... typing送信失敗: {response.text}")
        except Exception as e:
            print(f"Token {token[:5]}... typing送信エラー: {e}")
        time.sleep(0.2)

def add_reaction(channel_id, message_id, emoji):
    """
    指定したチャンネル・メッセージに対して、全tokenでリアクションを追加する。
    emojiはURLエンコードして送信。
    """
    encoded_emoji = urllib.parse.quote(emoji, safe='')
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me"
    for token in token_list:
        headers = {"authorization": token}
        try:
            response = requests.put(url, headers=headers)
            if response.status_code == 204:
                print(f"Token {token[:5]}... reaction '{emoji}' added")
            else:
                print(f"Token {token[:5]}... reaction追加失敗: {response.text}")
        except Exception as e:
            print(f"Token {token[:5]}... reaction追加エラー: {e}")
        time.sleep(0.2)

def start_action(action_type, bypass_message=False, bypass_thread=False):
    if not token_list:
        messagebox.showerror("エラー", "トークンを選択してください。")
        return
    
    channel_id = entry_channel.get().strip()
    mention_users = entry_mentions.get()
    
    try:
        mention_count = int(entry_mention_count.get())
    except ValueError:
        mention_count = 0
    
    if action_type == "message":
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        threading.Thread(target=send_message, args=(
            url,
            entry_message.get(),
            int(entry_num_messages.get()),
            bypass_message,
            mention_users,
            mention_count
        )).start()

    elif action_type == "thread":
        url = f"https://discord.com/api/v9/channels/{channel_id}/threads"
        threading.Thread(target=create_threads, args=(
            url,
            entry_thread_name.get(),
            entry_thread_message.get(),
            int(entry_num_threads.get()),
            bypass_thread
        )).start()

def start_reaction():
    channel_id = entry_channel.get().strip()
    message_id = entry_message_id.get().strip()
    emoji = entry_emoji.get().strip()
    if not channel_id or not message_id or not emoji:
        messagebox.showerror("エラー", "チャンネルID、メッセージID、絵文字を入力してください。")
        return
    threading.Thread(target=add_reaction, args=(channel_id, message_id, emoji)).start()

# GUI設定
window = tk.Tk()
window.title("DisRaider - By takowasabu")
window.geometry("1100x400")

frame_top = tk.Frame(window)
frame_top.pack(fill="x", padx=10, pady=5)

label_token = tk.Label(frame_top, text="Token:")
label_token.pack(side="left")
entry_token = tk.Entry(frame_top, width=40)
entry_token.pack(side="left")
button_select_token = tk.Button(frame_top, text="Select Token File", command=select_token_file)
button_select_token.pack(side="left", padx=5)

label_channel = tk.Label(frame_top, text="Channel ID:")
label_channel.pack(side="left", padx=10)
entry_channel = tk.Entry(frame_top, width=20)
entry_channel.pack(side="left")

button_online = tk.Button(frame_top, text="Set All Online", command=lambda: threading.Thread(target=set_tokens_online).start())
button_online.pack(side="left", padx=5)

button_typing = tk.Button(frame_top, text="Send Typing", command=lambda: threading.Thread(target=send_typing_indicator, args=(entry_channel.get().strip(),)).start())
button_typing.pack(side="left", padx=5)

frame_main = tk.Frame(window)
frame_main.pack(padx=10, pady=10, fill="both", expand=True)

# メッセージ送信フレーム
frame_message = tk.LabelFrame(frame_main, text="メッセージ送信", padx=5, pady=5)
frame_message.pack(side="left", padx=5, pady=5, fill="both", expand=True)

label_message = tk.Label(frame_message, text="Message:")
label_message.pack()
entry_message = tk.Entry(frame_message, width=40)
entry_message.pack()

label_num_messages = tk.Label(frame_message, text="Number of Messages:")
label_num_messages.pack()
entry_num_messages = tk.Entry(frame_message, width=20)
entry_num_messages.pack()

label_mentions = tk.Label(frame_message, text="Mention User IDs (newline-separated):")
label_mentions.pack()
entry_mentions = tk.Entry(frame_message, width=40)
entry_mentions.pack()

label_mention_count = tk.Label(frame_message, text="Number of Mentions:")
label_mention_count.pack()
entry_mention_count = tk.Entry(frame_message, width=20)
entry_mention_count.pack()

bypass_message = tk.BooleanVar()
bypass_button_message = tk.Checkbutton(frame_message, text="bypassを追加", variable=bypass_message)
bypass_button_message.pack()

button_send_message = tk.Button(frame_message, text="実行", command=lambda: start_action("message", bypass_message.get(), False))
button_send_message.pack()

# リアクション追加フレーム
frame_reaction = tk.LabelFrame(frame_main, text="リアクション追加", padx=5, pady=5)
frame_reaction.pack(side="left", padx=5, pady=5, fill="both", expand=True)

label_message_id = tk.Label(frame_reaction, text="Message ID:")
label_message_id.pack()
entry_message_id = tk.Entry(frame_reaction, width=30)
entry_message_id.pack()

label_emoji = tk.Label(frame_reaction, text="Emoji:")
label_emoji.pack()
entry_emoji = tk.Entry(frame_reaction, width=10)
entry_emoji.pack()

button_reaction = tk.Button(frame_reaction, text="リアクション追加", command=start_reaction)
button_reaction.pack(pady=5)

# スレッド作成フレーム
frame_thread = tk.LabelFrame(frame_main, text="スレッド作成", padx=5, pady=5)
frame_thread.pack(side="left", padx=5, pady=5, fill="both", expand=True)

label_thread_name = tk.Label(frame_thread, text="Thread Name:")
label_thread_name.pack()
entry_thread_name = tk.Entry(frame_thread, width=40)
entry_thread_name.pack()

label_thread_message = tk.Label(frame_thread, text="Thread Message:")
label_thread_message.pack()
entry_thread_message = tk.Entry(frame_thread, width=40)
entry_thread_message.pack()

label_num_threads = tk.Label(frame_thread, text="Number of Threads:")
label_num_threads.pack()
entry_num_threads = tk.Entry(frame_thread, width=20)
entry_num_threads.pack()

bypass_thread = tk.BooleanVar()
bypass_button_thread = tk.Checkbutton(frame_thread, text="bypassを追加", variable=bypass_thread)
bypass_button_thread.pack()

button_create_thread = tk.Button(frame_thread, text="実行", command=lambda: start_action("thread", False, bypass_thread.get()))
button_create_thread.pack()

window.mainloop()

