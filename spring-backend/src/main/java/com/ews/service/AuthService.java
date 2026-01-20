//package com.ews.service;
//
//import com.ews.dto.LoginRequest;
//import com.ews.model.User;
//import com.ews.repository.UserRepository;
//import lombok.RequiredArgsConstructor;
//import org.springframework.security.crypto.password.PasswordEncoder;
//import org.springframework.stereotype.Service;
//import java.util.HashMap;
//import java.util.Map;
//import java.util.UUID;
//
//@Service
//@RequiredArgsConstructor
//public class AuthService {
//    private final UserRepository userRepository;
//    private final PasswordEncoder passwordEncoder;
//    private final Map<String, String> activeSessions = new HashMap<>();
//
//    public Map<String, Object> setupAdmin(String password) {
//        if (userRepository.existsByUsername("admin")) {
//            throw new RuntimeException("Admin already exists");
//        }
//
//        User admin = new User();
//        admin.setUsername("admin");
//        admin.setPasswordHash(passwordEncoder.encode(password));
//        userRepository.save(admin);
//
//        Map<String, Object> response = new HashMap<>();
//        response.put("message", "Admin created successfully");
//        return response;
//    }
//
//    public Map<String, Object> login(LoginRequest request) {
//        User user = userRepository.findByUsername(request.getUsername())
//                .orElseThrow(() -> new RuntimeException("Invalid credentials"));
//
//        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
//            throw new RuntimeException("Invalid credentials");
//        }
//
//        String token = UUID.randomUUID().toString();
//        activeSessions.put(token, user.getUsername());
//
//        Map<String, Object> response = new HashMap<>();
//        response.put("token", token);
//        response.put("username", user.getUsername());
//        return response;
//    }
//
//    public void logout(String token) {
//        activeSessions.remove(token);
//    }
//
//    public boolean validateToken(String token) {
//        return activeSessions.containsKey(token);
//    }
//
//    public void resetPassword(String username, String oldPassword, String newPassword) {
//        User user = userRepository.findByUsername(username)
//                .orElseThrow(() -> new RuntimeException("User not found"));
//
//        if (!passwordEncoder.matches(oldPassword, user.getPasswordHash())) {
//            throw new RuntimeException("Invalid old password");
//        }
//        user.setPasswordHash(passwordEncoder.encode(newPassword));
//        userRepository.save(user);
//    }
//}


package com.ews.service;

import com.ews.dto.LoginRequest;
import com.ews.model.User;
import com.ews.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final Map<String, String> activeSessions = new HashMap<>();

    public boolean adminExists() {
        return userRepository.existsByUsername("admin");
    }

    public Map<String, Object> setupAdmin(String password) {
        if (userRepository.existsByUsername("admin")) {
            throw new RuntimeException("Admin already exists");
        }

        User admin = new User();
        admin.setUsername("admin");
        admin.setPasswordHash(passwordEncoder.encode(password));
        userRepository.save(admin);

        Map<String, Object> response = new HashMap<>();
        response.put("message", "Admin created successfully");
        return response;
    }

    public Map<String, Object> login(LoginRequest request) {
        User user = userRepository.findByUsername(request.getUsername())
                .orElseThrow(() -> new RuntimeException("Invalid credentials"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPasswordHash())) {
            throw new RuntimeException("Invalid credentials");
        }

        String token = UUID.randomUUID().toString();
        activeSessions.put(token, user.getUsername());

        Map<String, Object> response = new HashMap<>();
        response.put("token", token);
        response.put("username", user.getUsername());
        return response;
    }

    public void logout(String token) {
        activeSessions.remove(token);
    }

    public boolean validateToken(String token) {
        return activeSessions.containsKey(token);
    }

    public void resetPassword(String username, String oldPassword, String newPassword) {
        User user = userRepository.findByUsername(username)
                .orElseThrow(() -> new RuntimeException("User not found"));

        if (!passwordEncoder.matches(oldPassword, user.getPasswordHash())) {
            throw new RuntimeException("Invalid old password");
        }

        user.setPasswordHash(passwordEncoder.encode(newPassword));
        userRepository.save(user);
    }
}