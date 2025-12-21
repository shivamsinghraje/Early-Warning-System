// src/main/java/com/ews/repository/LiveForecastRepository.java
package com.ews.repository;

import com.ews.model.LiveForecast;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;
import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface LiveForecastRepository extends JpaRepository<LiveForecast, Long> {
    Page<LiveForecast> findByProjectIdRefOrderByTimestampDesc(String projectIdRef, Pageable pageable);

    @Query("SELECT lf FROM LiveForecast lf WHERE lf.projectIdRef = ?1 AND lf.timestamp >= ?2 ORDER BY lf.timestamp DESC")
    List<LiveForecast> findByProjectIdRefAndTimestampAfter(String projectIdRef, LocalDateTime after);

    void deleteByProjectIdRef(String projectIdRef);
}