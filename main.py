from yolov5 import YOLOv5
from influxdb_client import InfluxDBClient, Point
from datetime import datetime
from pytz import timezone
import cv2
import warnings
import time
import config
import logging

# 忽略未来警告
warnings.filterwarnings('ignore', category=FutureWarning)


# 初始化模型和 InfluxDB 客户端
def initialize():
    # 加载 YOLOv5 模型
    model = YOLOv5(config.MODEL_PATH)

    # 初始化 InfluxDB 客户端
    client = InfluxDBClient(url=config.INFLUXDB_URL, token=config.INFLUXDB_TOKEN, org=config.INFLUXDB_ORG)
    return model, client


# 从 InfluxDB 恢复计数器
def load_counters(client):
    query_api = client.query_api()

    # 获取当前时间，并将其转换为 GMT+7 时区
    tz = timezone(config.TIMEZONE)  # GMT+7
    start_of_day = datetime.now(tz).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()

    query = f'''
    from(bucket: "{config.INFLUXDB_BUCKET}")
      |> range(start: {start_of_day})
      |> filter(fn: (r) => r._measurement == "entry_exit_metric")
      |> last()
    '''
    tables = query_api.query(query, org=config.INFLUXDB_ORG)
    entry_count = 0
    exit_count = 0
    for table in tables:
        for record in table.records:
            if record.get_field() == "entry":
                entry_count = int(record.get_value())
            elif record.get_field() == "exit":
                exit_count = int(record.get_value())
    return entry_count, exit_count


# 处理视频帧
def process_video(model, client):
    cap = cv2.VideoCapture(config.RTSP_URL)
    write_api = client.write_api()

    # 恢复计数器
    entry_count, exit_count = load_counters(client)
    logging.info(f"恢复的计数：进门 = {entry_count}，出门 = {exit_count}")

    # 记录上一次检测到的中心位置和时间
    previous_x = None
    last_entry_time = 0
    last_exit_time = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            logging.error("无法获取视频帧")
            break

        current_time = time.time()

        # 使用YOLOv5进行人类检测
        results = model.predict(frame)
        entry_count, exit_count, previous_x = update_counts(results, previous_x, entry_count, exit_count, current_time,
                                                            last_entry_time, last_exit_time, write_api)

        # 绘制右边界的红线
        draw_boundary(frame)

        # 调整帧的大小
        frame_resized = cv2.resize(frame, (config.WINDOW_WIDTH, config.WINDOW_HEIGHT))

        # 显示调整后的帧
        cv2.imshow('YOLOv5 Detection', frame_resized)

        # 按下 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()


# 更新进出计数
def update_counts(results, previous_x, entry_count, exit_count, current_time, last_entry_time, last_exit_time,
                  write_api):
    for det in results.xyxy[0]:
        if int(det[5]) == 0:  # 人类类别ID为0
            x1, y1, x2, y2 = int(det[0]), int(det[1]), int(det[2]), int(det[3])
            center_x = (x1 + x2) // 2

            if previous_x is None:
                previous_x = center_x

            # 进门逻辑
            if previous_x > config.BOUNDARIES['right'] and center_x < config.BOUNDARIES['right']:
                if current_time - last_entry_time > config.COOLDOWN_TIME:
                    entry_count += 1
                    last_entry_time = current_time
                    logging.info(f"实时进门计数: {entry_count}")
                    write_data(write_api, "entry", entry_count)

            # 出门逻辑
            elif previous_x < config.BOUNDARIES['right'] and center_x > config.BOUNDARIES['right']:
                if current_time - last_exit_time > config.COOLDOWN_TIME:
                    exit_count += 1
                    last_exit_time = current_time
                    logging.info(f"实时出门计数: {exit_count}")
                    write_data(write_api, "exit", exit_count)

            previous_x = center_x
    return entry_count, exit_count, previous_x


# 写入数据到 InfluxDB
def write_data(write_api, field_name, value):
    point = Point("entry_exit_metric").field(field_name, value)
    write_api.write(bucket=config.INFLUXDB_BUCKET, org=config.INFLUXDB_ORG, record=point)


# 绘制边界线
def draw_boundary(frame):
    cv2.line(frame, (config.BOUNDARIES['right'], 0), (config.BOUNDARIES['right'], 2600), (0, 0, 255), 2)


# 主函数
if __name__ == "__main__":
    model, client = initialize()
    process_video(model, client)
