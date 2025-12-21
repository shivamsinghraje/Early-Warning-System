// src/main/java/com/ews/dto/ForecastResponse.java
package com.ews.dto;

import lombok.Data;
import java.time.LocalDateTime;

@Data
public class ForecastResponse {
    private LocalDateTime timestamp;
    private Double actualValue;
    private Double forecastedValue;
    private String status;
    private String message;
}