from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

# 已經為您填入專屬的 Token 與 Secret
line_bot_api = LineBotApi('NgwAbcWRcN+adpx3OS/cdTtnewuY931DGl6xROWmoD2XFZNkcSViVeU6/394Qj3LyjBQ2bvdoLi3fwwlu2vGi0furRg/UCEh/8k9d3Zp5LGgOEyovPXQ3eKET078QfsvSNaZrH6UPcVhZJHkCy7yXwdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('d5e15aa1ee60d1d3318595a94db4a82c')

# 接收 LINE 傳遞過來的 Webhook 事件
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理文字訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    
    # 設定觸發自動回覆的關鍵字清單
    order_keywords = ["預定", "預約", "訂購", "訂餐", "我要訂", "預留", "自取"]
    
    # 檢查客人的訊息中是否包含上述任一關鍵字
    if any(keyword in user_message for keyword in order_keywords):
        reply_text = (
            "您好！感謝您的詢問😊\n\n"
            "若是「當日訂單」或較急迫的需求，為了避免訊息漏接或回覆較慢，"
            "建議您直接致電門市，將由專人立刻為您處理喔！\n\n"
        )
        
        # 回傳訊息給客人
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )

if __name__ == "__main__":
    # 啟動伺服器
    app.run(host='0.0.0.0', port=8080)
