# /var/www/ttennis/gunicorn_config.py

bind = "127.0.0.1:8001"
workers = 3
worker_class = "sync"
timeout = 120
keepalive = 5

# 🔥 КЛЮЧЕВЫЕ настройки для быстрого рестарта:
preload_app = False  # ← Убираем preload (замедляет рестарт)
max_requests = 1000  # Перезапускать воркер после N запросов (борьба с утечками)
max_requests_jitter = 50  # Добавляем случайность, чтобы воркеры не рестартовали одновременно

# Логирование
accesslog = "-"  # stdout
errorlog = "-"   # stdout
loglevel = "info"

# Грацияльный shutdown
graceful_timeout = 30
