// src/main/java/com/ews/dto/CleanRequest.java
package com.ews.dto;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import java.util.List;

@Data
public class CleanRequest {
    @NotBlank
    private String projectName;

    @NotBlank
    private String projectId;

    @NotBlank
    private String datetimeCol;

    @NotBlank
    private String targetCol;

    @NotNull
    private List<String> gndCols;
}