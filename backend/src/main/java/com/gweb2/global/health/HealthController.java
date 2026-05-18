package com.gweb2.global.health;

import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequiredArgsConstructor
public class HealthController {

    private final HealthService healthService;

    @GetMapping("/health/live")
    public ResponseEntity<HealthStatusResponse> live() {
        return ResponseEntity.ok(healthService.live());
    }

    @GetMapping("/health/ready")
    public ResponseEntity<HealthStatusResponse> ready() {
        HealthStatusResponse response = healthService.readiness();
        HttpStatus status = "UP".equals(response.status()) ? HttpStatus.OK : HttpStatus.SERVICE_UNAVAILABLE;
        return ResponseEntity.status(status).body(response);
    }
}
