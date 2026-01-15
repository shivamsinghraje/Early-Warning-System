package com.ews.model;

import jakarta.persistence.*;
import lombok.Data;
import java.time.LocalDateTime;

@Entity
@Table(name = "live_forecasts", indexes = {
        @Index(name = "idx_project_timestamp", columnList = "project_id_ref, timestamp")
})
@Data
public class LiveForecast {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "project_id_ref", nullable = false)
    private String projectIdRef;

    @Column(nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "actual_value")
    private Double actualValue;

    @Column(name = "forecasted_value", nullable = false)
    private Double forecastedValue;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private Status status;

    public enum Status {
        Normal, Anomaly
    }
}