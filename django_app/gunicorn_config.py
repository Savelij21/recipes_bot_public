
import sys
import os

# ----- LOGS -------

logs_dir = './logs'

if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

gunicorn_logs_dir = os.path.join(logs_dir, 'gunicorn')

if not os.path.exists(gunicorn_logs_dir):
    os.makedirs(gunicorn_logs_dir)

access_log_file = os.path.join(gunicorn_logs_dir, 'access.log')
error_log_file = os.path.join(gunicorn_logs_dir, 'error.log')

logconfig_dict = {  # gunicorn сам считывает эту переменную
    'formatters': {
        'simple': {
            'format': '%(name)s [%(levelname)s] %(message)s'  # message формируется на основе access_log_format
        },
        'error': {
            'format': '[{asctime}.{msecs:03.0f}] [{levelname}] ({module}) {message}',
            'style': '{',
            'datefmt': '%d-%m-%Y, %H:%M:%S',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'stream': sys.stdout,  # Можно изменить на sys.stderr, если хотите использовать только стандартную ошибку
        },
        'access_file_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'filename': access_log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
        },
        'error_file_handler': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'error',
            'filename': error_log_file,
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
        },
    },
    'loggers': {
        '': {  # хз зачем, для подстраховки
            'handlers': ['console'],
            'level': 'INFO',
        },
        'gunicorn': {  # хз зачем, для подстраховки
            'handlers': ['console'],
            'level': 'INFO',
        },
        'gunicorn.access': {
            'handlers': ['access_file_handler', 'console'],
            'level': 'INFO',
        },
        'gunicorn.error': {
            'handlers': ['error_file_handler', 'console'],
            'level': 'INFO',
        },
    },
    'root': {  # хз зачем, для подстраховки
        "level": "INFO",
        "handlers": ['console'],
    },
}

access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s (%(b)s b)'  # gunicorn сам считывает эту переменную

# ------------- SERVICE---------------
# gunicorn сам считывает эти переменные
bind = '127.0.0.1:8000'
workers = 2
proc_name = 'zhzhgis_recipes_django'

# Логи доступа и ошибок
# accesslog = '-'  # Логи доступа выводятся в консоль
# errorlog = '-'   # Логи ошибок выводятся в консоль

# Формат логов доступа
# loglevel = 'info'
