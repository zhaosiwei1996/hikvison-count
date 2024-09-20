import json
from influxdb_client import InfluxDBClient
from datetime import datetime
import config

# 初始化 InfluxDB 客户端
client = InfluxDBClient(url=config.INFLUXDB_URL, token=config.INFLUXDB_TOKEN, org=config.INFLUXDB_ORG)
query_api = client.query_api()

# 获取当天最后一条记录
start_of_day = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).isoformat() + 'Z'

query_today_last = f'''
from(bucket: "{config.INFLUXDB_BUCKET}")
  |> range(start: {start_of_day})
  |> filter(fn: (r) => r._measurement == "entry_exit_metric")
  |> last()
'''
tables_today_last = query_api.query(query_today_last, org=config.INFLUXDB_ORG)

# 解析当天最后一条记录
last_entry_count = 0
last_exit_count = 0
for table in tables_today_last:
    for record in table.records:
        if record.get_field() == "entry":
            last_entry_count = int(record.get_value())
        elif record.get_field() == "exit":
            last_exit_count = int(record.get_value())

# 构建当天最后一条记录的 JSON 数据
today_last_json = {
    "date": datetime.now().strftime('%Y-%m-%d'),
    "entry": last_entry_count,
    "exit": last_exit_count
}

print("当天最后一条记录（JSON格式）:")
print(json.dumps(today_last_json, indent=4))


# 获取历史最后一条记录
query_history_last = f'''
from(bucket: "{config.INFLUXDB_BUCKET}")
  |> range(start: 0)
  |> filter(fn: (r) => r._measurement == "entry_exit_metric")
  |> last()
'''
tables_history_last = query_api.query(query_history_last, org=config.INFLUXDB_ORG)

# 解析历史最后一条记录
history_entry_count = 0
history_exit_count = 0
history_date = ""
for table in tables_history_last:
    for record in table.records:
        if record.get_field() == "entry":
            history_entry_count = int(record.get_value())
        elif record.get_field() == "exit":
            history_exit_count = int(record.get_value())
        history_date = record.get_time().strftime('%Y-%m-%d')  # 只保留日期部分

# 构建历史最后一条记录的 JSON 数据
history_last_json = {
    "date": history_date,
    "entry": history_entry_count,
    "exit": history_exit_count
}

print("历史最后一条记录（JSON格式）:")
print(json.dumps(history_last_json, indent=4))
