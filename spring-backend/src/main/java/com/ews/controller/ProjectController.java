// src/main/java/com/ews/controller/ProjectController.java
package com.ews.controller;

import com.ews.dto.LoginRequest;
import com.ews.dto.ProjectRequest;
import com.ews.model.Project;
import com.ews.service.ProjectService;
import com.ews.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import jakarta.validation.Valid;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/projects")
@RequiredArgsConstructor
public class ProjectController {
    private final ProjectService projectService;
    private final AuthService authService;

    @PostMapping("/add")
    public ResponseEntity<Map<String, Object>> addProject(
            @RequestPart("file") MultipartFile file,
            @RequestPart("data") @Valid ProjectRequest request) {
        return ResponseEntity.ok(projectService.addProject(request, file));
    }

    @GetMapping
    public ResponseEntity<List<Project>> getAllProjects() {
        return ResponseEntity.ok(projectService.getAllProjects());
    }

    @GetMapping("/{projectId}")
    public ResponseEntity<Project> getProject(@PathVariable String projectId) {
        return ResponseEntity.ok(projectService.getProject(projectId));
    }

    @GetMapping("/{projectId}/historical-data")
    public ResponseEntity<Map<String, Object>> getHistoricalData(@PathVariable String projectId) {
        return ResponseEntity.ok(projectService.getHistoricalData(projectId));
    }

    @GetMapping("/{projectId}/live-data")
    public ResponseEntity<Map<String, Object>> getLiveData(
            @PathVariable String projectId,
            @RequestParam(defaultValue = "1d") String duration) {
        return ResponseEntity.ok(projectService.getLiveData(projectId, duration));
    }

    @DeleteMapping("/{projectId}")
    public ResponseEntity<Map<String, Object>> deleteProject(
            @PathVariable String projectId,
            @RequestBody Map<String, String> request) {
        // Verify password
        String password = request.get("password");
        LoginRequest loginRequest = new LoginRequest();
        loginRequest.setUsername("admin");
        loginRequest.setPassword(password);

        try {
            authService.login(loginRequest);
            projectService.deleteProject(projectId, password);
            return ResponseEntity.ok(Map.of("message", "Project deleted successfully"));
        } catch (Exception e) {
            throw new RuntimeException("Invalid password");
        }
    }
}