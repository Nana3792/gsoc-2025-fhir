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
./run_synthea 10  


 

The data are here :  
synthea/output/fhir/



           
