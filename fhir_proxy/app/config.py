from starlette.config import Config

config = Config(".env")

# Arborist Configuration
ARBORIST_URL = config("ARBORIST_URL", default="")
ARBORIST_TIMEOUT = config("ARBORIST_TIMEOUT", cast=int, default=5)

# FHIR Configuration
HAPI_FHIR_URL = config("HAPI_FHIR_URL", default="http://localhost:8080")
SECURITY_TAG_PREFIX = config("SECURITY_TAG_PREFIX", default="gen3|")

# Proxy Configuration
PROXY_TIMEOUT = config("PROXY_TIMEOUT", cast=float, default=30.0)
