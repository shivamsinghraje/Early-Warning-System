# spring-backend/Dockerfile
FROM openjdk:17-jdk-slim

WORKDIR /app

COPY target/early-warning-system-1.0.0.jar app.jar

RUN mkdir -p /app/storage/data /app/storage/models /app/storage/artifacts /app/storage/temp

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]