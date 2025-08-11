from fastapi import FastAPI, Request, Header, HTTPException  
from fastapi.responses import JSONResponse  
import httpx  
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse  
from app.config import (
    ARBORIST_URL,
    ARBORIST_TIMEOUT,
    HAPI_FHIR_URL,
    SECURITY_TAG_PREFIX,
    PROXY_TIMEOUT
)


app = FastAPI()  


####################################################################################################################################

#From Proxy->Arborist
# Async function to get accessible resource tags from Arborist given a JWT token
async def get_accessible_resources(token: str) -> list[str]:
    headers = {"Authorization": f"Bearer {token}"}  # Set Authorization header with Bearer token
    async with httpx.AsyncClient(timeout=ARBORIST_TIMEOUT) as client:  # Create async HTTP client with timeout
        resp = await client.get(ARBORIST_URL, headers=headers)  # Call Arborist endpoint with token header
        resp.raise_for_status()  # Raise exception if HTTP status is 404,401,500 etc
        data = resp.json()  # Parse JSON response from Arborist
        return data.get("resources", [])  # Return list of resource tags, or empty list if missing

#assumes {"resources": ["team1", "project2"]}



####################################################################################################################################

# Function to rewrite FHIR URL by adding _security tags for access control
def rewrite_fhir_url(original_url: str, resources: list[str]) -> str:
    parsed = urlparse(original_url)  # Parse URL into components 
    query_params = parse_qs(parsed.query)  # Parse query string into dict with keys and list of values
    security_tags = [SECURITY_TAG_PREFIX + res for res in resources]  # Prefix each resource with security tag prefix
    query_params["_security"] = security_tags  # Add or overwrite _security parameter with these tags
    new_query = urlencode(query_params, doseq=True)  # Re-encode query parameters; doseq=True encodes lists properly
    return urlunparse(parsed._replace(query=new_query))  # Rebuild full URL with updated query string


# Original: https://fhir-server/Patient?name=Alice
# Rewritten: https://fhir-server/Patient?name=Alice&_security=team1&_security=project2
####################################################################################################################################

# Main proxy endpoint that accepts all paths and HTTP methods
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
#/{path:path} catches all subpaths

async def proxy_fhir(path: str, request: Request, authorization: str = Header(None)):
    # Check if Authorization header exists and starts with "Bearer "
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")  # Return 401 Unauthorized if missing or invalid
    
    token = authorization[len("Bearer "):]  # Extract JWT token by removing "Bearer " prefix

####################################################################################################################################

  
 # Call Arborist to get allowed resource tags for this token
    
    try:
        allowed_resources = await get_accessible_resources(token)
    except httpx.HTTPStatusError as e:  # If Arborist returns error status (e.g. 401 or 403)
        raise HTTPException(status_code=403, detail="Unauthorized or failed to get resources from Arborist")
    #Status Code Definition 403: A server that receives valid credentials that are not adequate to
   # gain access ought to respond with the 403 (Forbidden) status code
   # (Section 6.5.3 of [RFC7231]).

    
    # Rebuild the original FHIR server URL, including any query parameters from user request
    original_url = f"{HAPI_FHIR_URL}/{path}"
    if request.query_params:
        original_url += "?" + str(request.query_params)

    # Rewrite the URL by adding _security query params for filtering based on allowed resources
    rewritten_url = rewrite_fhir_url(original_url, allowed_resources)

    # Prepare headers for forwarding to HAPI FHIR, excluding headers like 'host' or 'content-length'
    forward_headers = {k: v for k, v in request.headers.items() if k.lower() not in ["host", "content-length"]}
    forward_headers["Authorization"] = f"Bearer {token}"  # Ensure Authorization header with token is forwarded
    forward_headers["Accept"] = "application/fhir+json"  # Set Accept header for FHIR JSON response
    forward_headers["Content-Type"] = "application/fhir+json"  # Set Content-Type for FHIR JSON requests

    body = None  # Initialize request body variable
    if request.method in ("POST", "PUT"):  # For POST or PUT, get the body content from incoming request
        body = await request.body()

    async with httpx.AsyncClient() as client:  # Create async HTTP client for forwarding
        try:
            resp = await client.request(  # Send the original HTTP method to rewritten FHIR URL
                method=request.method,
                url=rewritten_url,
                headers=forward_headers,
                content=body  # Include body for POST/PUT; None otherwise
            )
            resp.raise_for_status()  # Raise exception for HTTP error statuses
        except httpx.HTTPStatusError as e:  # If HAPI FHIR returns an error status
            raise HTTPException(status_code=e.response.status_code, detail=f"FHIR server error: {e.response.text}")
        except httpx.RequestError as e:  # For network/connection errors
            raise HTTPException(status_code=502, detail=f"Error communicating with FHIR server: {str(e)}")


####################################################################################################################################


    # Return the JSON response from HAPI FHIR directly to the user, preserving status code
    return JSONResponse(content=resp.json(), status_code=resp.status_code)
