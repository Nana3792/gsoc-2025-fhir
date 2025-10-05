# gsoc-2025-fhir
Google Summer of Code 2025 – FHIR Proxy Project

This project implements a FHIR proxy on Gen3, supporting NCPI FHIR resources with secure access control. 
It provides a fully containerized FastAPI proxy, HAPI FHIR server, and Arborist authorization service for local or cloud deployment.

---

## Contributor Information
- **Name:** Andriana Sielli  
- **Organization:** Center for Translational Data Science, University of Chicago  
- **Mentors:** Alex Vantol, Kyle Burton  
- **GSoC Year:** 2025
  
---

## Table of Contents

2. [Environment Variables](#environment-variables)  
3. [HAPI FHIR Server Setup](#hapi-fhir-server-setup)  
4. [PostgreSQL Setup](#postgresql-setup)  
5. [Data Ingestion](#data-ingestion)  
   - [Synthea Data](#synthea-data)  
   - [NCPI FHIR](#ncpi-fhir)  
6. [Proxy & Authorization](#proxy--authorization)  
7. [Dockerization](#dockerization)  
8. [Unit Testing](#unit-testing)  
9. [Useful Links / References](#useful-links--references)  

---
## Environmental Variables  
 
### .env example  
AUTH_SERVER_URL=https://auth.example.com  
SECURITY_TAG_PREFIX=ncpi-security  
PROXY_TIMEOUT=3000  
ARBORIST_URL=https://arborist.example.com  
HAPI_FHIR_URL=https://fhir.example.com  
ARBORIST_TIMEOUT=5000  

## HAPI FHIR JPA SERVER:  
git clone https://github.com/hapifhir/hapi-fhir-jpaserver-starter.git  
cd hapi-fhir-jpaserver-starter  

mvn clean install  
mvn spring-boot:run


## PostgreSQL database:  
FOR MacOs:  

brew install postgresql  
brew services start postgresql  

psql postgres -c "CREATE DATABASE hapi_database;"  
psql postgres -c "CREATE USER hapi_user WITH PASSWORD 'Password';"  
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE hapi_database TO hapi_user;"  

nano pom.xml  

inside dependencies add:      
```xml
<dependency>  
  <groupId>org.postgresql</groupId>  
  <artifactId>postgresql</artifactId>  
  <scope>runtime</scope>  
</dependency>
``` 



application.yaml   
```yaml
  spring:  
    datasource:  
        url: jdbc:postgresql://localhost:5432/hapi_database  
        username: hapi_user  
        password: Password  
        driverClassName: org.postgresql.Driver  
        max-active: 15  
    jpa:  
        properties:  
          hibernate.dialect: ca.uhn.fhir.jpa.model.dialect.HapiFhirPostgresDialect  
  ```


## Synthea Data 

git clone https://github.com/synthetichealth/synthea.git  
cd synthea  

for ten records, the default is FHIR json. 
  
./gradlew build  
./run_synthea -p 10  



The data are here :  
synthea/output/fhir/

Order of ingestion:  
1. Organization  
2. Location  
3. Practitioner  
4. PractitionerRole  
5. Patient  
6. Encounter  
7. Condition  
8. Observation  
9. Medication  
10. MedicationRequest  
11. CareTeam  
12. CarePlan  

## NCPI FHIR  
### prerequisites:  
sushi  
npm install -g sushi  
sushi .  


git clone https://github.com/NIH-NCPI/ncpi-fhir-ig-2.git
cd ncpi-fhir-ig-2



Dependencies:  




./_updatePublisher.sh  
./_genonce.sh  



INGEST:  
```bash 
for file in *.json; do
  # Extract resource type and id from filename
  # Filename pattern: ResourceType-ResourceId.json
  resource_type="${file%%-*}"
  resource_id="${file#*-}"
  resource_id="${resource_id%.json}"

  echo "Uploading $file to $resource_type/$resource_id ..."

  curl -X PUT "http://localhost:8080/fhir/${resource_type}/${resource_id}" \
       -H "Content-Type: application/fhir+json" \
       -d @"$file"

  echo ""


```
<img width="492" height="217" alt="Screenshot 2025-08-08 at 2 34 44 PM" src="https://github.com/user-attachments/assets/009a9b64-8201-4977-a3e1-d4b1b65bdba3" />

for testing:  
```bash
curl -X GET "http://localhost:8080/fhir/StructureDefinition?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/CodeSystem?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/ValueSet?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/Patient?_summary=count" -H "Accept: application/fhir+json"
```

## Authorization:
Architecture Flow  

Client → Proxy: Sends request with Bearer token.  
Proxy → Arborist: Validates token + gets resources.  
Proxy → FHIR: Forwards request with _security tags.  
FHIR → Proxy: Returns filtered data.  
Proxy → Client: Passes through response.  
<img width="826" height="546" alt="Screenshot 2025-08-02 at 6 08 52 PM" src="https://github.com/user-attachments/assets/0e02c1b1-0277-4b96-9b59-db25453d6e56" />

Arborist   
export OIDC_ISSUER=https://qa.planx-pla.net/user  
export JWKS_ENDPOINT=https://qa.planx-pla.net/user/.well-known/jwks  

./bin/arborist --port 8081  

##  Dockerization of the FHIR proxy  


Run the FHIR proxy locally using Docker Compose.

- **Stack Components:**
  - `fhir-proxy` – FastAPI service with Gunicorn, exposed on port 8888
  - `hapi-fhir` – HAPI FHIR server, exposed on port 8080
  - `arborist` – Authorization service, exposed on port 8081
- **Dependencies:** Python packages managed via Poetry
- **Configuration:** Environment variables control URLs, timeouts, and security tags
- **Functionality:** Proxy forwards requests to HAPI FHIR while enforcing security via Arborist

```bash
docker-compose up --build
```

## Unit Testing:  

The project includes unit tests to verify the FHIR proxy’s functionality and security.  

- **Tools:** `pytest`, `pytest-asyncio`, `pytest-httpx`  
- **What is tested:**  
  - Retrieval of individual FHIR resources  
  - Search queries with `_security` filters  
  - Enforcement of bearer token permissions

All external services (Gen3 authorization and HAPI FHIR server) are mocked so tests can run locally without a live server. 

To run the tests:

```bash
pytest -v tests/
```
 
Environment file: .env.test

GEN_USER_URL=https://qa.planx-pla.net/user/user  
FHIR_SERVER_URL=http://localhost:8080/fhir



# LINKS:
1. Create a FastAPI instance: https://fastapi.tiangolo.com/tutorial/first-steps/  
2. Async Support: https://www.python-httpx.org/async/  
3. URL Parse: https://docs.python.org/3/library/urllib.parse.html#urllib.parse.urlparse
4. FHIR Security: https://www.hl7.org/fhir/security.html
5. Bearer Token Usage: https://www.rfc-editor.org/rfc/rfc6750





