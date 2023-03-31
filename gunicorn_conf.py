from multiprocessing import cpu_count

bind = 'unix:/var/www/zpanel/gunicorn.sock'
workers = cpu_count() + 1
worker_class = 'uvicorn.workers.UvicornWorker'

loglevel = 'debug'
accesslog = '/var/www/zpanel/access_log'
errorlog =  '/var/www/zpanel/error_log'
