# Gunicorn configuration for production
import multiprocessing

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gevent"
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests (helps with memory leaks)
max_requests = 1000
max_requests_jitter = 50

# Logging
accesslog = "/var/log/pocketoj/access.log"
errorlog = "/var/log/pocketoj/error.log"
loglevel = "info"

# Process naming
proc_name = 'pocketoj'

# Server mechanics
daemon = False
pidfile = '/tmp/pocketoj.pid'
user = None
group = None
tmp_upload_dir = None

# CRITICAL: Disable auto-reload to prevent restarts during file creation
reload = False
reload_extra_files = []  # Don't watch any files for changes
