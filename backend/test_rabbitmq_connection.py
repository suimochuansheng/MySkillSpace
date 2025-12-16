from celery import Celery

# 使用您 .env 中的配置
broker_url = 'amqp://guest:guest@localhost:5672//'

app = Celery('test', broker=broker_url)

try:
    with app.connection_for_read() as conn:
        conn.ensure_connection(max_retries=3)
        print("✅ 成功连接到 RabbitMQ!")
except Exception as e:
    print(f"❌ 连接失败: {e}")
