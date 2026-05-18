package com.gweb2.domain.game.controller;

import com.gweb2.domain.game.dto.GameDataRequest;
import com.gweb2.domain.game.dto.GameSummaryResponse;
import com.gweb2.domain.game.service.GameDataService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.data.web.PageableDefault;
import java.util.List;

@RestController
@RequestMapping("/api/games")
@RequiredArgsConstructor
public class GameController {

    private final GameDataService gameDataService;

    // 게임 데이터 수집 요청 (appId → Python → DB)
    @PostMapping("/fetch")
    public ResponseEntity<GameSummaryResponse> fetchGame(@Valid @RequestBody GameDataRequest request) {
        var game = gameDataService.requestDataFetch(request.appId());
        return ResponseEntity.ok(GameSummaryResponse.from(game));
    }

    // 게임명 검색
    @GetMapping("/search")
    public ResponseEntity<List<GameSummaryResponse>> search(@RequestParam String keyword) {
        var games = gameDataService.searchByName(keyword);
        return ResponseEntity.ok(games.stream().map(GameSummaryResponse::from).toList());
    }

    // 단건 조회
    @GetMapping("/{steamAppId}")
    public ResponseEntity<GameSummaryResponse> getGame(@PathVariable Long steamAppId) {
        var game = gameDataService.getGame(steamAppId);
        return ResponseEntity.ok(GameSummaryResponse.from(game));
    }

    // 전체 게임 페이징 조회
    @GetMapping
    public ResponseEntity<Page<GameSummaryResponse>> getGames(
            @PageableDefault(size = 8, sort = "id", direction = Sort.Direction.DESC) Pageable pageable) {
        var gamesPage = gameDataService.getGames(pageable);
        return ResponseEntity.ok(gamesPage.map(GameSummaryResponse::from));
    }
}

