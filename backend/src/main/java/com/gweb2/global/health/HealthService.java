package com.gweb2.global.health;

import lombok.RequiredArgsConstructor;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClient;

import javax.sql.DataSource;
import java.sql.Connection;
import java.util.LinkedHashMap;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class HealthService {

    private final DataSource dataSource;
    private final RestClient restClient;

    @Value("${python.api-url:http://localhost:8000}")
    private String pythonApiUrl;

    public HealthStatusResponse live() {
        return new HealthStatusResponse(
                "UP",
                "backend",
                Map.of("application", "UP")
        );
    }

    public HealthStatusResponse readiness() {
        Map<String, String> details = new LinkedHashMap<>();
        String overallStatus = "UP";

        try (Connection connection = dataSource.getConnection()) {
            if (!connection.isValid(2)) {
                throw new IllegalStateException();
            }
            details.put("database", "UP");
        } catch (Exception e) {
            overallStatus = "DOWN";
            details.put("database", "DOWN");
        }

        try {
            restClient.get()
                    .uri(pythonApiUrl + "/health/ready")
                    .retrieve()
                    .toBodilessEntity();
            details.put("pythonApi", "UP");
        } catch (Exception e) {
            overallStatus = "DOWN";
            details.put("pythonApi", "DOWN");
        }

        return new HealthStatusResponse(overallStatus, "backend", details);
    }
}
