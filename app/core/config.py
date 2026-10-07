import os
from dotenv import load_dotenv


load_dotenv()


DB_URL = os.environ["DATABASE_URL"]

JWT_SECRET = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = os.environ["JWT_ALGORITHM"]
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ['ACCESS_TOKEN_EXPIRE_MINUTES'])


OPEN_METEO_GEOCODING_URL = os.environ[
    "OPEN_METEO_GEOCODING_URL"
]

OPEN_METEO_FORECAST_URL = os.environ[
    "OPEN_METEO_FORECAST_URL"
]

HTTP_TIMEOUT_SECONDS = float(os.environ.get("HTTP_TIMEOUT_SECONDS", "10.0"))



# _keys_to_check = {
#     "DATABASE_URL": DB_URL,
#     "JWT_SECRET_KEY": JWT_SECRET,
#     "JWT_ALGORITHM": JWT_ALGORITHM,
#     "ACCESS_TOKEN_EXPIRE_MINUTES": str(ACCESS_TOKEN_EXPIRE_MINUTES),
#     "OPEN_METEO_GEOCODING_URL": OPEN_METEO_GEOCODING_URL,
#     "OPEN_METEO_FORECAST_URL": OPEN_METEO_FORECAST_URL,
# }
#
# for _name, _value in _keys_to_check.items():
#     try:
#         if not _value:
#             raise ValueError(f"{_name} is present but empty")
#         print(f"{_name}: active, starts with '{_value[:8]}'")
#     except Exception as e:
#         print(f"{_name}: NOT active ({e})")
