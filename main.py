import os
import gspread
import requests
from datetime import datetime, timedelta
from google.oauth2 import service_account

def get_tasks():
    # 使用新版google-auth认证
    creds = service_account.Credentials.from_service_account_file(
        "service_account.json",
        scopes=["https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"]
    )
    client = gspread.authorize(creds)
    
    # 获取表格数据
    sheet = client.open_by_key(os.environ["SPREADSHEET_ID"]).sheet1
    rows = sheet.get_all_records()
    
    # 生成任务消息 (UTC+8时间)
    today = datetime.utcnow() + timedelta(hours=8)
    msg = f"🗓️【今日任务 · {today.strftime('%Y-%m-%d')}】\n\n"
    
    # 添加每日任务
    msg += "🎯 每日任务：\n"
    msg += "\n".join([f"① {row['任务内容']}" for row in rows 
                     if row["类型"] == "每日" and row["是否启用"] == "是"]) + "\n\n"
    
    # 添加限时任务
    msg += "⏰ 限时任务：\n"
    msg += "\n".join([f"② {row['任务内容']} (截止 {row['截止日期']})" for row in rows 
                     if row["类型"] == "限时" and row["是否启用"] == "是" 
                     and row["截止日期"] and today.strftime('%Y-%m-%d') <= row["截止日期"]]) + "\n\n"
    
    # 添加长期任务
    msg += "♾️ 长期任务：\n"
    msg += "\n".join([f"③ {row['任务内容']}" for row in rows 
                     if row["类型"] == "长期" and row["是否启用"] == "是"])
    
    return msg

def post_to_discord(content):
    requests.post(
        os.environ["DISCORD_WEBHOOK"],
        json={"content": content}
    )

if __name__ == "__main__":
    post_to_discord(get_tasks())
