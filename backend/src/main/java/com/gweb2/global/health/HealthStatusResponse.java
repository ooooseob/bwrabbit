package com.gweb2.global.health;

import java.util.Map;

public record HealthStatusResponse(
        String status,
        String service,
        Map<String, String> details
) {
}
