package com.gweb2.domain.game.service;

import com.gweb2.domain.game.entity.Game;
import com.gweb2.domain.game.repository.GameRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class GameDataService {

    private final GameRepository gameRepository;
    private final RestClient restClient;

    @Value("${python.api-url:http://localhost:8000}")
    private String pythonApiUrl;

    public Game requestDataFetch(Long appId) {
        if (gameRepository.existsBySteamAppId(appId)) {
            log.info("Game {} already exists in DB", appId);
            return gameRepository.findBySteamAppId(appId).orElseThrow();
        }

        log.info("Requesting Python to fetch game appId={}", appId);
        try {
            Map<?, ?> response = restClient.post()
                    .uri(pythonApiUrl + "/fetch")
                    .body(Map.of("app_id", appId))
                    .retrieve()
                    .body(Map.class);
            log.info("Python fetch response: {}", response);
        } catch (RestClientException e) {
            log.error("Python server call failed for appId={}: {}", appId, e.getMessage());
            throw new IllegalStateException("Python 서버 호출 실패: " + e.getMessage(), e);
        }

        return gameRepository.findBySteamAppId(appId)
                .orElseThrow(() -> new IllegalStateException("Game not found after fetch: " + appId));
    }

    @Transactional(readOnly = true)
    public List<Game> searchByName(String keyword) {
        return gameRepository.findByNameSimilarity(keyword, 10);
    }

    @Transactional(readOnly = true)
    public Game getGame(Long steamAppId) {
        return gameRepository.findBySteamAppId(steamAppId)
                .orElseThrow(() -> new IllegalArgumentException("Game not found: " + steamAppId));
    }

    @Transactional(readOnly = true)
    public Page<Game> getGames(Pageable pageable) {
        return gameRepository.findAll(pageable);
    }
}

