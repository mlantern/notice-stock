import os
import requests
from notion_client import Client

# 从环境变量中获取密钥
notion_api_key = os.getenv("NOTION_API_KEY")
alpha_vantage_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
database_id = os.getenv("DATABASE_ID")

# 设置 Notion API 客户端
notion = Client(auth=notion_api_key)

# 配置 Alpha Vantage API
API_URL = "https://www.alphavantage.co/query"

# 获取股票当前价格
def get_stock_price(symbol):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": "5min",
        "apikey": alpha_vantage_api_key
    }
    response = requests.get(API_URL, params=params)
    data = response.json()
    time_series = data["Time Series (5min)"]
    latest_time = next(iter(time_series))
    latest_price = time_series[latest_time]["4. close"]
    return float(latest_price)

# 更新 Notion 数据库中的股票价格
def update_stock_prices():
    response = notion.databases.query(database_id=database_id)
    for page in response["results"]:
        properties = page["properties"]
        stock_code = properties["股票代码"]["title"][0]["text"]["content"]
        current_price = get_stock_price(stock_code)
        
        notion.pages.update(
            page_id=page["id"],
            properties={
                "当前价格": {
                    "number": current_price
                }
            }
        )

# 运行更新函数
update_stock_prices()
