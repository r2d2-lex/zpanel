from multiprocessing import cpu_count

bind = 'unix:/var/www/zpanel/gunicorn.sock'
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

loglevel = 'debug'
accesslog = '/var/log/zpanel/access_log'
errorlog =  '/var/log/zpanel/error_log'
