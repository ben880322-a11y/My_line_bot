from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import datetime

app = Flask(__name__)

# 您的專屬 Token 與 Secret
line_bot_api = LineBotApi('NgwAbcWRcN+adpx3OS/cdTtnewuY931DGl6xROWmoD2XFZNkcSViVeU6/394Qj3LyjBQ2bvdoLi3fwwlu2vGi0furRg/UCEh/8k9d3Zp5LGgOEyovPXQ3eKET078QfsvSNaZrH6UPcVhZJHkCy7yXwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d5e15aa1ee60d1d3318595a94db4a82c')

# 建立一個全域變數（字典），用來紀錄「誰」在「哪一天」已經被回覆過了
user_reply_history = {}

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    user_id = event.source.user_id  # 取得傳送訊息的客人的專屬 ID
    
    # ==========================================
    # 功能 1：特定帳號名稱不回覆（黑名單）
    # ==========================================
    # 將不想被回覆的 LINE 顯示名稱填入這個清單中
    excluded_names = ["包囍管理員-B", "包囍管理員-M", "包囍管理員-R", "包囍管理員-S", "包囍管理員-WQD", "包囍管理員-X", "蔡秉謙(Ben)"]
    
    try:
        # 呼叫 LINE API 取得這個使用者的個人檔案（包含顯示名稱）
        profile = line_bot_api.get_profile(user_id)
        user_name = profile.display_name
        
        # 如果使用者的名字在排除名單內，直接 return 結束程式，不予理會
        if user_name in excluded_names:
            return
    except:
        # 如果因為某些原因（例如未加好友）抓不到名字，就跳過檢查繼續往下走
        pass

    # ==========================================
    # 功能 2：檢查今天是否已經回覆過（一天一次）
    # ==========================================
    # 設定為台灣時區 (UTC+8)
    taiwan_tz = datetime.timezone(datetime.timedelta(hours=8))
    # 取得「台灣時間」的今天日期（格式如：2026-03-19）
    today_str = datetime.datetime.now(taiwan_tz).strftime('%Y-%m-%d')
    
    # 檢查這個 user_id 今天的紀錄。如果紀錄的日期就是今天，代表回過了，直接結束
    if user_reply_history.get(user_id) == today_str:
        return

    # ==========================================
    # 核心邏輯：關鍵字觸發
    # ==========================================
    order_keywords = ["預定", "預約", "訂購", "訂餐", "我要訂", "預留", "自取"]
    
    if any(keyword in user_message for keyword in order_keywords):
        reply_text = (
            "您好！感謝您的詢問😊\n\n"
            "若是「當日訂單」或較急迫的需求，為了避免訊息漏接或回覆較慢，"
            "建議您直接致電門市，將由專人立刻為您處理喔！\n\n"
        )
        
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
        
        # 成功發送回覆後，把這個使用者的 ID 跟「今天的日期」寫入歷史紀錄中
        user_reply_history[user_id] = today_str

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
