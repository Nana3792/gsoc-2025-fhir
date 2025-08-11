from starlette.config import Config
from starlette.datastructures import Secret

config = Config(".env")

PROXY_TIMEOUT = config("PROXY_TIMEOUT", cast=float, default=30.0)
ARBORIST_URL = config("ARBORIST_URL", default="")
ARBORIST_TIMEOUT = config("ARBORIST_TIMEOUT", cast=int, default=5)
HAPI_FHIR_URL = config("HAPI_FHIR_URL", default="http://localhost:8080")
SECURITY_TAG_PREFIX = config("SECURITY_TAG_PREFIX", default="gen3|")
