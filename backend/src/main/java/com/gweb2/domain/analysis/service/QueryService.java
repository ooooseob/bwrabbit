package com.gweb2.domain.analysis.service;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.gweb2.domain.analysis.entity.UserQuery;
import com.gweb2.domain.analysis.repository.DocumentChunkRepository;
import com.gweb2.domain.analysis.repository.UserQueryRepository;
import com.gweb2.domain.game.entity.Game;
import com.gweb2.domain.game.repository.GameRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.client.RestClient;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class QueryService {

    private final UserQueryRepository userQueryRepository;
    private final GameRepository gameRepository;
    private final DocumentChunkRepository documentChunkRepository;
    private final RestClient restClient;
    private final ObjectMapper objectMapper;

    @Value("${ollama.base-url}")
    private String ollamaBaseUrl;

    @Value("${ollama.llm-model}")
    private String llmModel;

    @Value("${python.api-url:http://localhost:8000}")
    private String pythonApiUrl;

    @Transactional
    public UserQuery process(String queryText, String sessionId) {
        long start = System.currentTimeMillis();

        UserQuery userQuery = UserQuery.builder()
                .queryText(queryText)
                .sessionId(sessionId)
                .build();
        userQueryRepository.save(userQuery);

        try {
            Map<String, Object> analysisResult = requestPythonAnalysis(queryText);

            String intent = (String) analysisResult.getOrDefault("intent", "");
            List<Long> matchedIds = parseMatchedIds(analysisResult);
            String embStr = toEmbeddingString(analysisResult);

            userQuery.setAnalysisResult(null, intent, objectMapper.writeValueAsString(matchedIds));

            String context = buildContext(matchedIds, embStr);
            String llmAnswer = callOllama(queryText, context);


            userQuery.complete(llmAnswer, System.currentTimeMillis() - start);

        } catch (Exception e) {
            log.error("Query processing failed", e);
            userQuery.complete("처리 중 오류가 발생했습니다: " + e.getMessage(), System.currentTimeMillis() - start);
        }

        return userQueryRepository.save(userQuery);
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> requestPythonAnalysis(String queryText) {
        return restClient.post()
                .uri(pythonApiUrl + "/analyze")
                .body(Map.of("query", queryText))
                .retrieve()
                .body(Map.class);
    }

    private String toEmbeddingString(Map<String, Object> result) {
        Object raw = result.get("embedding");
        if (raw instanceof List<?> list) {
            StringBuilder sb = new StringBuilder("[");
            for (int i = 0; i < list.size(); i++) {
                if (i > 0) sb.append(',');
                sb.append(((Number) list.get(i)).floatValue());
            }
            return sb.append(']').toString();
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private List<Long> parseMatchedIds(Map<String, Object> result) {
        Object raw = result.get("matched_game_ids");
        if (raw instanceof List<?> list) {
            return list.stream().map(o -> ((Number) o).longValue()).toList();
        }
        return List.of();
    }

    private String buildContext(List<Long> matchedIds, String embStr) {
        StringBuilder ctx = new StringBuilder();

        List<Game> games = gameRepository.findAllById(matchedIds);
        games.forEach(g -> ctx.append(String.format(
                "[게임: %s] 장르: %s | 태그: %s | 설명: %s\n",
                g.getName(),
                g.getGenres().stream().map(genre -> genre.getGenreName()).collect(Collectors.joining(", ")),
                g.getTags().stream().limit(5).map(t -> t.getTagName()).collect(Collectors.joining(", ")),
                g.getShortDescription() != null ? g.getShortDescription().substring(0, Math.min(200, g.getShortDescription().length())) : ""
        )));

        if (embStr != null) {
            documentChunkRepository.findSimilarChunks(embStr, 3)
                    .forEach(chunk -> ctx.append("[참고] ").append(chunk.getContent(), 0, Math.min(300, chunk.getContent().length())).append("\n"));
        }

        return ctx.toString();
    }

    @SuppressWarnings("unchecked")
    private String callOllama(String query, String context) {
        String prompt = String.format("""
                당신은 게이머와 개발자를 위한 게임 전문 AI 어시스턴트입니다.
                아래 게임 정보를 참고하여 사용자의 질문에 답변하세요.

                [참고 게임 정보]
                %s

                [사용자 질문]
                %s

                친절하고 전문적으로 답변하세요.
                """, context, query);

        Map<String, Object> body = Map.of(
                "model", llmModel,
                "prompt", prompt,
                "stream", false
        );

        Map response = restClient.post()
                .uri(ollamaBaseUrl + "/api/generate")
                .body(body)
                .retrieve()
                .body(Map.class);

        return response != null ? (String) response.get("response") : "응답을 받지 못했습니다.";
    }
}
