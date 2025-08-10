# gsoc-2025-fhir
Google Summer of Code 2025 FHIR Project Repo

## Prerequisites:  

1. Maven  
sudo apt install maven -y


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

for testing:  
```bash
curl -X GET "http://localhost:8080/fhir/StructureDefinition?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/CodeSystem?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/ValueSet?_summary=count" -H "Accept: application/fhir+json"
curl -X GET "http://localhost:8080/fhir/Patient?_summary=count" -H "Accept: application/fhir+json"
```

## Authorization:
<img width="826" height="546" alt="Screenshot 2025-08-02 at 6 08 52 PM" src="https://github.com/user-attachments/assets/0e02c1b1-0277-4b96-9b59-db25453d6e56" />
