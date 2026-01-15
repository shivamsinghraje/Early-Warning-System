package com.ews.model;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Type;
import com.fasterxml.jackson.databind.JsonNode;
import java.time.LocalDateTime;

@Entity
@Table(name = "projects")
@Data
public class Project {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "project_id", unique = true, nullable = false)
    private String projectId;

    @Column(name = "project_name", nullable = false)
    private String projectName;

    @Column(name = "datetime_col", nullable = false)
    private String datetimeCol;

    @Column(name = "target_col", nullable = false)
    private String targetCol;

    @Column(name = "gnd_cols", columnDefinition = "JSON", nullable = false)
    @Convert(converter = JsonNodeConverter.class)
    private JsonNode gndCols;

    @Column(name = "is_live_enabled")
    private Boolean isLiveEnabled = false;

    @Column(name = "api_url")
    private String apiUrl;

    @Column(name = "api_token")
    private String apiToken;

    @Column(name = "original_data_path")
    private String originalDataPath;

    @Column(name = "cleaned_data_path")
    private String cleanedDataPath;

    @Column(name = "anomaly_model_path")
    private String anomalyModelPath;

    @Column(name = "forecast_model_path")
    private String forecastModelPath;

    @Column(name = "scaler_path")
    private String scalerPath;

    @Column(name = "threshold_path")
    private String thresholdPath;

    @Column(name = "created_at")
    private LocalDateTime createdAt = LocalDateTime.now();
}