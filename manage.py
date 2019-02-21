#!/usr/bin/env python
import os
import sys
# from yolo.predict import init_model
# from django.conf import settings
# config_path=settings.BASE_DIR+'/config.json'
if __name__ == '__main__':

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    # print('test if keep running')
    # init_model(config_path)
    # print("start loading weight")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
