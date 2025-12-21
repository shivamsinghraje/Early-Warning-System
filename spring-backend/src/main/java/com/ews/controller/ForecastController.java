// src/main/java/com/ews/controller/ForecastController.java
package com.ews.controller;

import com.ews.dto.ForecastResponse;
import com.ews.model.LiveForecast;
import com.ews.service.ForecastService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/forecast")
@RequiredArgsConstructor
public class ForecastController {
    private final ForecastService forecastService;

    @PostMapping("/live/{projectId}")
    public ResponseEntity<ForecastResponse> fetchLiveAndPredict(@PathVariable String projectId) {
        return ResponseEntity.ok(forecastService.fetchLiveAndPredict(projectId));
    }

    @PostMapping("/manual/{projectId}")
    public ResponseEntity<ForecastResponse> manualPredict(
            @PathVariable String projectId,
            @RequestBody Map<String, Object> data) {
        return ResponseEntity.ok(forecastService.manualPredict(projectId, data));
    }

    @GetMapping("/history/{projectId}")
    public ResponseEntity<List<LiveForecast>> getForecastHistory(@PathVariable String projectId) {
        return ResponseEntity.ok(forecastService.getForecastHistory(projectId));
    }
}