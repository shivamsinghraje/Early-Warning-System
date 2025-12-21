// src/main/java/com/ews/service/ForecastService.java (Complete)
package com.ews.service;

import com.ews.dto.ForecastResponse;
import com.ews.model.LiveForecast;
import com.ews.model.Project;
import com.ews.repository.LiveForecastRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class ForecastService {
    private final ProjectService projectService;
    private final LiveForecastRepository liveForecastRepository;
    private final PythonMLService pythonMLService;
    private final RestTemplate restTemplate;

    public ForecastResponse fetchLiveAndPredict(String projectId) {
        Project project = projectService.getProject(projectId);

        if (!project.getIsLiveEnabled() || project.getApiUrl() == null) {
            throw new RuntimeException("Live mode not enabled for this project");
        }

        try {
            // Fetch from external API
            HttpHeaders headers = new HttpHeaders();
            headers.set("Authorization", "Bearer " + project.getApiToken());
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<Map> apiResponse = restTemplate.exchange(
                    project.getApiUrl(),
                    HttpMethod.GET,
                    entity,
                    Map.class
            );

            Map<String, Object> liveData = apiResponse.getBody();

            // Predict using Python service
            Map<String, Object> prediction = pythonMLService.predict(projectId, liveData);

            // Save to database
            LiveForecast forecast = new LiveForecast();
            forecast.setProjectIdRef(projectId);
            forecast.setTimestamp(LocalDateTime.now());
            forecast.setActualValue((Double) liveData.get("value"));
            forecast.setForecastedValue((Double) prediction.get("forecast"));
            forecast.setStatus(LiveForecast.Status.valueOf((String) prediction.get("status")));

            liveForecastRepository.save(forecast);

            // Create response
            ForecastResponse response = new ForecastResponse();
            response.setTimestamp(forecast.getTimestamp());
            response.setActualValue(forecast.getActualValue());
            response.setForecastedValue(forecast.getForecastedValue());
            response.setStatus(forecast.getStatus().toString());
            response.setMessage("Live data fetched and predicted successfully");

            return response;

        } catch (Exception e) {
            throw new RuntimeException("Error fetching live data: " + e.getMessage());
        }
    }

    public ForecastResponse manualPredict(String projectId, Map<String, Object> data) {
        // Predict using Python service
        Map<String, Object> prediction = pythonMLService.predict(projectId, data);

        // Save to database
        LiveForecast forecast = new LiveForecast();
        forecast.setProjectIdRef(projectId);
        forecast.setTimestamp(LocalDateTime.now());
        forecast.setActualValue((Double) data.get("value"));
        forecast.setForecastedValue((Double) prediction.get("forecast"));
        forecast.setStatus(LiveForecast.Status.valueOf((String) prediction.get("status")));

        liveForecastRepository.save(forecast);

        // Create response
        ForecastResponse response = new ForecastResponse();
        response.setTimestamp(forecast.getTimestamp());
        response.setActualValue(forecast.getActualValue());
        response.setForecastedValue(forecast.getForecastedValue());
        response.setStatus(forecast.getStatus().toString());
        response.setMessage("Manual prediction completed");

        return response;
    }

    public List<LiveForecast> getForecastHistory(String projectId) {
        return liveForecastRepository.findByProjectIdRefOrderByTimestampDesc(
                projectId,
                org.springframework.data.domain.PageRequest.of(0, 26000)
        ).getContent();
    }
}