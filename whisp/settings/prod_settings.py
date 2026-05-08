from .base_settings import *
import os
# import dj_database_url

DEBUG = False

# used later
# DATABASES = {
#     'default': dj_database_url.parse(
#         os.environ.get("DATABASE_URL"),
#         conn_max_age=600,
#         conn_health_checks=True,
#     )
# }

# DATABASES['default']['OPTIONS'] = {
#     'sslmode': 'require',
# }