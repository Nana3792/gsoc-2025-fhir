from starlette.config import Config 


config = Config(".env")

FHIR_SERVER_URL = config("FHIR_SERVER_URL", default="")
AUTH_SERVER_URL = config("AUTH_SERVER_URL", default="")
