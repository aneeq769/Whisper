import os

env = os.getenv("DJANGO_ENV", "local")

if env == "prod":
    from .prod_settings import *
else:
    from .local_settings import *