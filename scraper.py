import requests
import feedparser
import json
from datetime import datetime
import pytz

# 请把下面引号里的内容，替换为您部署 Google Apps Script 得到的 Web 网址
WEBHOOK_URL = 'https://docs.google.com/spreadsheets/d/1Jm1YgI7siyJpdvv5QCsaFH4xibPR6yLBxrX79AWYQOQ/edit?gid=1871002511#gid=1871002511'

tz = pytz.timezone('Asia/Shanghai')
current_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def fetch_cpsc():
    print("开始抓取美国 CPSC...")
    results = []
    try:
        feed = feedparser.parse('https://www.cpsc.gov/Newsroom/CPSC-RSS-Feed/Recalls-RSS')
        for entry in feed.entries:
            results.append([
                current_time, 
                "美国 CPSC", 
                entry.title, 
                entry.published, 
                entry.link
            ])
    except Exception as e:
        print(f"美国 CPSC 抓取异常: {e}")
    return results

def fetch_eu():
    print("开始抓取欧盟 Safety Gate...")
    results = []
    api_url = "https://ec.europa.eu/safety-gate-alerts/public/api/notifications/search"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Content-Type': 'application/json'
    }
    # 获取最新的 20 条记录
    payload = {
        "searchCriteria": {},
        "page": 0,
        "size": 20,
        "sortField": "notificationDate",
        "sortOrder": "DESC"
    }
    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        if response.status_code == 200:
            data = response.json()
            # 兼容解析欧盟的数据结构
            items = data.get('results', data.get('_embedded', {}).get('notifications', []))
            for item in items:
                reference = item.get('reference', '')
                title = item.get('product', {}).get('name', '未命名产品') if isinstance(item.get('product'), dict) else item.get('name', '未命名产品')
                date = item.get('notificationDate', '')
                link = f"https://ec.europa.eu/safety-gate-alerts/screen/webReport/detail/{reference}" if reference else ""
                
                if link:
                    results.append([
                        current_time,
                        "欧盟 Safety Gate",
                        title,
                        date,
                        link
                    ])
        else:
            print(f"欧盟抓取失败，状态码: {response.status_code}")
    except Exception as e:
        print(f"欧盟抓取异常: {e}")
    return results

def send_to_google_sheet(data):
    if not data:
        print("没有数据需要发送。")
        return
        
    print(f"正在发送 {len(data)} 条数据到 Google Sheets...")
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(WEBHOOK_URL, data=json.dumps(data), headers=headers)
        print("Google 表格返回结果:", response.text)
    except Exception as e:
        print(f"发送到 Google 表格失败: {e}")

def main():
    all_data = []
    
    # 1. 抓取美国数据
    cpsc_data = fetch_cpsc()
    all_data.extend(cpsc_data)
    
    # 2. 抓取欧盟数据
    eu_data = fetch_eu()
    all_data.extend(eu_data)
    
    # 3. 统一发送数据到表格
    send_to_google_sheet(all_data)

if __name__ == "__main__":
    main()
