import os
import time
import schedule
from mootdx.quotes import Quotes
from notion_client import Client

# 从环境变量中获取密钥
notion_api_key = os.getenv("NOTION_API_KEY")
database_id = os.getenv("DATABASE_ID")

# 设置 Notion API 客户端
notion = Client(auth=notion_api_key)

# 设置 MooTDX Quotes 客户端
client = Quotes.factory(market='std')  # 使用标准市场（市场: 'std' or 'ext'）

# 获取股票实时价格及其他信息
def get_stock_info(symbol):
    data = client.quotes(symbol)
    print(f"Data for {symbol}: {data}")  # 打印数据以调试
    if not data.empty:
        return {
            'price': data['price'][0],
            'symbol': data['symbol'][0]
        }
    else:
        return None

# 更新 Notion 数据库中的股票信息
def update_stock_info():
    response = notion.databases.query(database_id=database_id)
    for page in response["results"]:
        properties = page["properties"]
        print("Properties:", properties)  # 调试打印属性名称

        # 检查并提取股票代码
        if "股票代码" in properties and properties["股票代码"]["title"]:
            stock_code = properties["股票代码"]["title"][0]["text"]["content"]
        else:
            print(f"Skipping page {page['id']} due to missing or empty '股票代码'")
            continue
        
        # 获取股票信息
        stock_info = get_stock_info(stock_code)
        
        if stock_info is not None:
            # 更新股票信息
            notion.pages.update(
                page_id=page["id"],
                properties={
                    "当前价格": {
                        "number": stock_info['price']
                    },
                }
            )
        else:
            print(f"Could not retrieve info for stock code {stock_code}")

# 每分钟运行一次更新函数
schedule.every(1).minutes.do(update_stock_info)

# 运行调度器
while True:
    schedule.run_pending()
    time.sleep(1)
