import os
import gspread
import requests
from datetime import datetime, timedelta
from oauth2client.service_account import ServiceAccountCredentials

def get_tasks():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ["SPREADSHEET_ID"]).sheet1
    rows = sheet.get_all_records()
    today = datetime.utcnow() + timedelta(hours=8)
    msg = f"🎯 {today.strftime('%Y-%m-%d')} 的任务如下：\n"
    for row in rows:
        if row["是否启用"] != "是":
            continue
        if row["类型"] == "每日":
            msg += f"✅ {row['任务内容']} —— {row.get('标签（可选）', '')}\n"
        elif row["类型"] == "限时":
            if row["截止日期"] and today.strftime('%Y-%m-%d') <= row["截止日期"]:
                msg += f"⏳ {row['任务内容']}（截止 {row['截止日期']}）\n"
        elif row["类型"] == "长期":
            msg += f"📌 {row['任务内容']}（长期任务）\n"
    return msg.strip()

def post_to_discord(content):
    url = os.environ["DISCORD_WEBHOOK"]
    requests.post(url, json={"content": content})

if __name__ == "__main__":
    post_to_discord(get_tasks())