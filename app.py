#!/usr/bin/env python
# coding: utf-8

# In[10]:


channel_access_token = 'eMuStXIhJpZ0x0ZXQuEE+oiqVUU3Ad1YMUqoRALpbvmwLzEiekE5ZpLVRF66kind8sV/x0m/AP8Qv5Fr7ZFuhhj23Y2Igo9ldvXT6Haa1az0zXeJwK83jtEZD6Gyywzywq6+hiXilIbdVi8Xi9ALoQdB04t89/1O/w1cDnyilFU='
channel_secret = 'a8491d99f9a02e36953b2e1c938b7459'


# In[11]:


from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,ImageSendMessage
)

app = Flask(__name__)

line_bot_api = LineBotApi(channel_access_token)

handler = WebhookHandler(channel_secret)


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


# In[12]:


'''

消息判斷器

讀取指定的json檔案後，把json解析成不同格式的SendMessage

讀取檔案，
把內容轉換成json
將json轉換成消息
放回array中，並把array傳出。

'''

# 引用會用到的套件http://localhost:8888/notebooks/Heroku/app-Copy1.ipynb#
from linebot.models import (
    ImagemapSendMessage,TextSendMessage,ImageSendMessage,LocationSendMessage,FlexSendMessage
)

from linebot.models.template import (
    ButtonsTemplate,CarouselTemplate,ConfirmTemplate,ImageCarouselTemplate
    
)

from linebot.models.template import *
import json
def detect_json_array_to_new_message_array(fileName):
    
    #開啟檔案，轉成json
    with open(fileName, encoding='utf8') as f:
        jsonArray = json.load(f)
    
    # 解析json
    returnArray = []
    for jsonObject in jsonArray:

        # 讀取其用來判斷的元件
        message_type = jsonObject.get('type')
        
        # 轉換
        if message_type == 'text':
            returnArray.append(TextSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'imagemap':
            returnArray.append(ImagemapSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'template':
            returnArray.append(TemplateSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'image':
            returnArray.append(ImageSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'sticker':
            returnArray.append(StickerSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'audio':
            returnArray.append(AudioSendMessage.new_from_json_dict(jsonObject))  
        elif message_type == 'location':
            returnArray.append(LocationSendMessage.new_from_json_dict(jsonObject))
        elif message_type == 'flex':
            returnArray.append(FlexSendMessage.new_from_json_dict(jsonObject))    

    # 回傳
    return returnArray


# In[13]:


'''

handler處理關注消息

用戶關注時，讀取 素材 -> 關注 -> reply.json

將其轉換成可寄發的消息，傳回給Line

'''

# 引用套件
from linebot.models import (
    FollowEvent
)

# 關注事件處理
@handler.add(FollowEvent)
def process_follow_event(event):
    
    # 讀取並轉換
    result_message_array =[]
    replyJsonPath = "material/follow/reply.json"
    result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

    # 消息發送
    line_bot_api.reply_message(
        event.reply_token,
        result_message_array
    )
    # 取出消息內User的資料
    user_profile = line_bot_api.get_profile(event.source.user_id)
        
     # 將用戶資訊存在檔案內
    with open("./users.txt", "a") as myfile:
        myfile.write(json.dumps(vars(user_profile),sort_keys=True))
        myfile.write('\r\n')
    # 綁定圖文選單至用戶
    begin = open('material/rich_menu_begin/rich_menu_id','r').read()
    line_bot_api.link_rich_menu_to_user(event.source.user_id,begin)


# In[14]:


# '''

# handler處理文字消息

# 收到用戶回應的文字消息，
# 按文字消息內容，往素材資料夾中，找尋以該內容命名的資料夾，讀取裡面的reply.json

# 轉譯json後，將消息回傳給用戶

# '''

# # 引用套件
# from linebot.models import (
#     MessageEvent, TextMessage
# )

# # 文字消息處理
# @handler.add(MessageEvent,message=TextMessage)
# def process_text_message(event):

#     # 讀取本地檔案，並轉譯成消息
#     result_message_array =[]
#     replyJsonPath = "material/"+event.message.text+"/reply.json"
#     result_message_array = detect_json_array_to_new_message_array(replyJsonPath)

#     # 發送
#     line_bot_api.reply_message(
#         event.reply_token,
#         result_message_array
#     )


# In[15]:


'''

handler處理Postback Event

載入功能選單與啟動特殊功能

解析postback的data，並按照data欄位判斷處理

現有三個欄位
menu, folder, tag

若folder欄位有值，則
    讀取其reply.json，轉譯成消息，並發送

若menu欄位有值，則
    讀取其rich_menu_id，並取得用戶id，將用戶與選單綁定
    讀取其reply.json，轉譯成消息，並發送

'''
from linebot.models import (
    PostbackEvent
)

from urllib.parse import parse_qs 
import time
@handler.add(PostbackEvent)
def process_postback_event(event):
    

    #解析Data
    query_string_dict = parse_qs(event.postback.data)
    
    print(query_string_dict)
    result_message_array =[]
    #在data欄位裡面有找到folder
    # folder=abcd&tag=xxx
    if 'folder' in query_string_dict:
    
        
        # 去素材資料夾下，找abcd資料夾內的reply.json
        replyJsonPath = 'material/'+query_string_dict.get('folder')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )
        line_bot_api.unlink_rich_menu_from_user(event.source.user_id)
        begin = open('material/rich_menu_begin/rich_menu_id','r').read()
        line_bot_api.link_rich_menu_to_user(event.source.user_id,begin)
    elif 'menu' in query_string_dict:
        line_bot_api.unlink_rich_menu_from_user(event.source.user_id)
        time.sleep(0.5)
        linkRichMenuId = open("material/"+query_string_dict.get('menu')[0]+'/rich_menu_id', 'r').read()
        time.sleep(0.3)
        line_bot_api.link_rich_menu_to_user(event.source.user_id,linkRichMenuId)
        
        replyJsonPath = 'material/'+query_string_dict.get('menu')[0]+"/reply.json"
        result_message_array = detect_json_array_to_new_message_array(replyJsonPath)
  
        line_bot_api.reply_message(
            event.reply_token,
            result_message_array
        )


# In[16]:


# '''
#     用戶回傳文字消息的處理辦法
# '''
# import json
# @handler.add(MessageEvent, message=TextMessage)
# def handle_message(event):
#     #JSON文字 ->字串
#     messageString = '''{
#   "type": "image",
#   "originalContentUrl": "https://i.kinja-img.com/gawker-media/image/upload/s--ybB1Ua8t--/c_scale,f_auto,fl_progressive,q_80,w_800/jbmyedbnmxkbj9itp9f4.jpg",
#   "previewImageUrl": "https://upload.wikimedia.org/wikipedia/en/thumb/5/5c/Kirby.png/220px-Kirby.png",
#   "animated": false
# }'''
#     #字串 ->JSON物件
#     messageJson = json.loads(messageString)
    
#     #將JSON物件轉換成TextSendMessage
#     messageInstance = ImageSendMessage.new_from_json_dict(messageJson)
#     #拿著token跟line做回覆
#     line_bot_api.reply_message(
#         event.reply_token,
#         messageInstance
#     )


# In[17]:


# if __name__ == "__main__":
#     app.run()


# In[18]:


'''

Application 運行（heroku版）

'''

import os
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=os.environ['PORT'])

