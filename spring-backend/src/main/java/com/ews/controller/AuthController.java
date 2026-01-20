
package com.ews.controller;

import com.ews.dto.LoginRequest;
import com.ews.service.AuthService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import jakarta.validation.Valid;
import java.util.Map;
import java.util.HashMap;

@RestController
@RequestMapping("/api/auth")
@RequiredArgsConstructor
public class AuthController {
    private final AuthService authService;

    @GetMapping("/setup")
    public ResponseEntity<Map<String, Object>> checkSetup() {
        boolean adminExists = authService.adminExists();
        Map<String, Object> response = new HashMap<>();
        response.put("adminExists", adminExists);

        if (!adminExists) {
            return ResponseEntity.status(404).body(response);
        }
        return ResponseEntity.ok(response);
    }

    @PostMapping("/setup")
    public ResponseEntity<Map<String, Object>> setupAdmin(@RequestBody Map<String, String> request) {
        String password = request.get("password");
        if (password == null || password.length() < 8) {
            throw new RuntimeException("Password must be at least 8 characters ");
        }
        return ResponseEntity.ok(authService.setupAdmin(password));
    }

    @PostMapping("/login")
    public ResponseEntity<Map<String, Object>> login(@Valid @RequestBody LoginRequest request) {
        return ResponseEntity.ok(authService.login(request));
    }

    @PostMapping("/logout")
    public ResponseEntity<Map<String, Object>> logout(@RequestHeader("Authorization") String token) {
        authService.logout(token.replace("Bearer ", ""));
        return ResponseEntity.ok(Map.of("message", "Logged out successfully"));
    }

    @PostMapping("/reset-password")
    public ResponseEntity<Map<String, Object>> resetPassword(@RequestBody Map<String, String> request) {
        authService.resetPassword(
                request.get("username"),
                request.get("oldPassword"),
                request.get("newPassword")
        );
        return ResponseEntity.ok(Map.of("message", "Password reset successfully"));
    }
}