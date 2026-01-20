package com.ews.service;

import com.ews.dto.ProjectRequest;
import com.ews.model.Project;
import com.ews.model.LiveForecast;
import com.ews.repository.ProjectRepository;
import com.ews.repository.LiveForecastRepository;
import com.ews.util.FileUtils;
import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class ProjectService {
    private final ProjectRepository projectRepository;
    private final LiveForecastRepository liveForecastRepository;
    private final PythonMLService pythonMLService;
    private final CleaningService cleaningService;
    private final ObjectMapper objectMapper;

    @Value("${storage.path:./storage}")
    private String storagePath;

    @Transactional
    public Map<String, Object> addProject(ProjectRequest request, MultipartFile file) {
        try {
            // Check if project exists
            if (projectRepository.existsByProjectId(request.getProjectId())) {
                throw new RuntimeException("Project ID already exists");
            }

            // Create project directories
            String projectDir = storagePath + "/projects/" + request.getProjectId();
            Files.createDirectories(Paths.get(projectDir + "/data"));
            Files.createDirectories(Paths.get(projectDir + "/models"));
            Files.createDirectories(Paths.get(projectDir + "/artifacts"));

            // Save original file
            String originalPath = projectDir + "/data/original.csv";
            File csvFile = FileUtils.saveFile(file, originalPath);

            // Clean data
            Map<String, Object> cleanParams = new HashMap<>();
            cleanParams.put("datetime_col", request.getDatetimeCol());
            cleanParams.put("target_col", request.getTargetCol());
            cleanParams.put("gnd_cols", request.getGndCols());

            Map<String, Object> cleanResult = pythonMLService.cleanData(csvFile, cleanParams);
            String cleanedPath = projectDir + "/data/cleaned.csv";

            // Train models
            Map<String, Object> anomalyResult = pythonMLService.trainAnomalyModel(
                    request.getProjectId(), cleanedPath
            );
            Map<String, Object> forecastResult = pythonMLService.trainForecastModel(
                    request.getProjectId(), cleanedPath
            );

            // Create project entity
            Project project = new Project();
            project.setProjectId(request.getProjectId());
            project.setProjectName(request.getProjectName());
            project.setDatetimeCol(request.getDatetimeCol());
            project.setTargetCol(request.getTargetCol());
            project.setGndCols(objectMapper.valueToTree(request.getGndCols()));
            project.setIsLiveEnabled(request.getIsLiveEnabled());
            project.setApiUrl(request.getApiUrl());
            project.setApiToken(request.getApiToken());
            project.setOriginalDataPath(originalPath);
            project.setCleanedDataPath(cleanedPath);
            project.setAnomalyModelPath((String) anomalyResult.get("model_path"));
            project.setForecastModelPath((String) forecastResult.get("model_path"));
            project.setScalerPath((String) anomalyResult.get("scaler_path"));
            project.setThresholdPath((String) anomalyResult.get("threshold_path"));

            projectRepository.save(project);

            Map<String, Object> response = new HashMap<>();
            response.put("message", "Project added successfully");
            response.put("project_id", project.getProjectId());
            return response;

        } catch (Exception e) {
            throw new RuntimeException("Error adding project: " + e.getMessage());
        }
    }

    public List<Project> getAllProjects() {
        return projectRepository.findAll();
    }

    public Project getProject(String projectId) {
        return projectRepository.findByProjectId(projectId)
                .orElseThrow(() -> new RuntimeException("Project not found"));
    }

    public Map<String, Object> getHistoricalData(String projectId) {
        Project project = getProject(projectId);
        List<LiveForecast> forecasts = liveForecastRepository
                .findByProjectIdRefOrderByTimestampDesc(projectId, PageRequest.of(0, 26000))
                .getContent();

        Map<String, Object> response = new HashMap<>();
        response.put("project", project);
        response.put("data", forecasts);
        return response;
    }

    public Map<String, Object> getLiveData(String projectId, String duration) {
        LocalDateTime cutoff = switch (duration) {
            case "1d" -> LocalDateTime.now().minusDays(1);
            case "2d" -> LocalDateTime.now().minusDays(2);
            case "7d" -> LocalDateTime.now().minusDays(7);
            case "30d" -> LocalDateTime.now().minusDays(30);
            default -> LocalDateTime.now().minusDays(1);
        };

        List<LiveForecast> forecasts = liveForecastRepository
                .findByProjectIdRefAndTimestampAfter(projectId, cutoff);

        Map<String, Object> response = new HashMap<>();
        response.put("data", forecasts);
        response.put("count", forecasts.size());
        return response;
    }

    @Transactional
    public void deleteProject(String projectId, String password) {
        // Verify password in controller
        Project project = getProject(projectId);

        // Delete from database
        liveForecastRepository.deleteByProjectIdRef(projectId);
        projectRepository.delete(project);

        // Delete files
        try {
            FileUtils.deleteDirectory(Paths.get(storagePath + "/projects/" + projectId));
        } catch (Exception e) {
            // Log error but do not fail
        }

    }
}