// src/main/java/com/ews/repository/ProjectRepository.java
package com.ews.repository;

import com.ews.model.Project;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface ProjectRepository extends JpaRepository<Project, Integer> {
    Optional<Project> findByProjectId(String projectId);
    boolean existsByProjectId(String projectId);
}