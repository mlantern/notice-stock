import os
import tushare as ts
from notion_client import Client

# 从环境变量中获取密钥
notion_api_key = os.getenv("NOTION_API_KEY")
tushare_api_key = os.getenv("TUSHARE_API_KEY")
database_id = os.getenv("DATABASE_ID")

# 设置 Tushare API 客户端
ts.set_token(tushare_api_key)
pro = ts.pro_api()

# 设置 Notion API 客户端
notion = Client(auth=notion_api_key)

# 获取股票实时价格
def get_stock_price(symbol):
    df = pro.daily(ts_code=symbol)
    if not df.empty:
        return df.iloc[0]['close']
    else:
        return None

# 更新 Notion 数据库中的股票价格
def update_stock_prices():
    response = notion.databases.query(database_id=database_id)
    for page in response["results"]:
        properties = page["properties"]
        print("Properties:", properties)  # 调试打印属性名称
        stock_code = properties["股票代码"]["title"][0]["text"]["content"]
        current_price = get_stock_price(stock_code)
        
        if current_price is not None:
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
