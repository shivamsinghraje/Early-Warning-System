package com.ews.service;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.FileSystemResource;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.io.File;
import java.util.Map;
import java.util.HashMap;

@Service
@RequiredArgsConstructor
public class PythonMLService {
    private final RestTemplate restTemplate;
    private final ObjectMapper objectMapper;

    @Value("${python.ml.service.url:http://localhost:8001}")
    private String pythonServiceUrl;

    public Map<String, Object> cleanData(File csvFile, Map<String, Object> params) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", new FileSystemResource(csvFile));
            body.add("params", objectMapper.writeValueAsString(params));

            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

            ResponseEntity<Map> response = restTemplate.exchange(
                    pythonServiceUrl + "/clean-data",
                    HttpMethod.POST,
                    requestEntity,
                    Map.class
            );

            return response.getBody();
        } catch (Exception e) {
            throw new RuntimeException("Error calling Python ML service: " + e.getMessage());
        }
    }

    public Map<String, Object> trainAnomalyModel(String projectId, String cleanedDataPath) {
        Map<String, Object> request = new HashMap<>();
        request.put("project_id", projectId);
        request.put("data_path", cleanedDataPath);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                pythonServiceUrl + "/train-anomaly",
                request,
                Map.class
        );

        return response.getBody();
    }

    public Map<String, Object> trainForecastModel(String projectId, String cleanedDataPath) {
        Map<String, Object> request = new HashMap<>();
        request.put("project_id", projectId);
        request.put("data_path", cleanedDataPath);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                pythonServiceUrl + "/train-forecast",
                request,
                Map.class
        );

        return response.getBody();
    }

    public Map<String, Object> predict(String projectId, Map<String, Object> data) {
        Map<String, Object> request = new HashMap<>();
        request.put("project_id", projectId);
        request.put("data", data);

        ResponseEntity<Map> response = restTemplate.postForEntity(
                pythonServiceUrl + "/predict",
                request,
                Map.class
        );

        return response.getBody();
    }
}