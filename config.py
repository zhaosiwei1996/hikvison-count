import logging

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s [%(funcName)s]-%(process)d %(message)s')
logger = logging.getLogger(__name__)

# 替换成你的摄像头 RTSP 地址
RTSP_URL = 'rtsp://admin:CMEV201811G@192.168.0.105:554/Streaming/Channels/101?transportmode=unicast&streamtype=sub&proto=udp'

# YOLOv5 模型路径
MODEL_PATH = 'yolov5s.pt'

# 窗口大小
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# 定义边界
BOUNDARIES = {'right': 1300}

# 冷却时间（秒）
COOLDOWN_TIME = 2.0

# InfluxDB 配置
# local
INFLUXDB_TOKEN = "BLUnYl1EbFDUg-o8frrkkK2FzenGgIfwaT8IF_yHjN0w_HiS58dQI-Eke9ZAZ9z-Wz4McXIturdlf7QYe_Z_wA=="  # 替换为实际的 InfluxDB token
# server
#INFLUXDB_TOKEN = "WhSFqV-_r1Q_xCRjV0XE4DTcrvY5bidu7mNINXyG3ac-yNpkKOCSAk-zoRLQuC6kGy2s1HrOkyW3DmSUauXlxA=="  # 替换为实际的 InfluxDB token
INFLUXDB_ORG = "cmev"
INFLUXDB_BUCKET = "test"
INFLUXDB_URL = "http://localhost:8086"

# 时区
TIMEZONE = "Asia/Bangkok"
