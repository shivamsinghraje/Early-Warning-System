package com.ews.controller;


import com.ews.dto.CleanRequest;
import com.ews.service.CleaningService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import jakarta.validation.Valid;
import java.util.Map;

@RestController
@RequestMapping("/api/process")
@RequiredArgsConstructor
public class CleaningController {
    private final CleaningService cleaningService;

    @PostMapping("/clean-only")
    public ResponseEntity<Map<String, Object>> cleanDataOnly(
            @RequestPart("file") MultipartFile file,
            @RequestPart("data") @Valid CleanRequest request) {
        return ResponseEntity.ok(cleaningService.cleanDataOnly(file, request));
    }
}