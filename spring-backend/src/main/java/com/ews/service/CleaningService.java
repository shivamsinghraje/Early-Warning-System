package com.ews.service;

import com.ews.dto.CleanRequest;
import com.ews.util.CSVUtils;
import com.ews.util.ExcelUtils;
import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.Map;


@Service
@RequiredArgsConstructor
public class CleaningService {
    private final PythonMLService pythonMLService;

    @Value("${storage.path:./storage}")
    private String storagePath;

    public Map<String, Object> cleanDataOnly(MultipartFile file, CleanRequest request) {
        try {
            // Create temp directory
            String tempDir = storagePath + "/temp/" + System.currentTimeMillis();
            Files.createDirectories(Paths.get(tempDir));

            // Convert to CSV if needed
            File csvFile;
            String fileName = file.getOriginalFilename();
            if (fileName.endsWith(".xlsx") || fileName.endsWith(".xls")) {
                csvFile = ExcelUtils.convertToCSV(file, tempDir + "/converted.csv");
            } else {
                csvFile = new File(tempDir + "/original.csv");
                file.transferTo(csvFile);
            }

            // Validate columns
            if (!CSVUtils.validateColumns(csvFile, request)) {
                throw new RuntimeException("Required columns not found in file");
            }

            // Call Python service
            Map<String, Object> params = new HashMap<>();
            params.put("datetime_col", request.getDatetimeCol());
            params.put("target_col", request.getTargetCol());
            params.put("gnd_cols", request.getGndCols());

            Map<String, Object> result = pythonMLService.cleanData(csvFile, params);

            // Add download link
            String cleanedPath = (String) result.get("cleaned_path");
            result.put("download_url", "/api/download/" + Paths.get(cleanedPath).getFileName());

            return result;

        } catch (Exception e) {
            throw new RuntimeException("Error cleaning data: " + e.getMessage());
        }
    }
}