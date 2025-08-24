from starlette.config import Config

config = Config(".env")

ARBORIST_URL = config("ARBORIST_URL", default="http://localhost:8081/auth/resources")
ARBORIST_TIMEOUT = config("ARBORIST_TIMEOUT", cast=int, default=5)
HAPI_FHIR_URL = config("HAPI_FHIR_URL", default="http://localhost:8080/fhir")
SECURITY_TAG_PREFIX = config("SECURITY_TAG_PREFIX", default="gen3|")
PROXY_TIMEOUT = config("PROXY_TIMEOUT", cast=float, default=30.0)
GEN3_USER_URL= config("GEN3_USER_URL", default="https://qa.planx-pla.net/user/user")
