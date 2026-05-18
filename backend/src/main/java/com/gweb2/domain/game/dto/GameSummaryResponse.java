package com.gweb2.domain.game.dto;

import com.gweb2.domain.game.entity.Game;

import java.time.LocalDate;
import java.util.List;

public record GameSummaryResponse(
        Long id,
        Long steamAppId,
        String name,
        String shortDescription,
        String headerImage,
        LocalDate releaseDate,
        Integer priceInitial,
        Integer priceFinal,
        Integer metacriticScore,
        Integer positiveReviews,
        Integer negativeReviews,
        List<String> genres,
        List<String> tags
) {
    public static GameSummaryResponse from(Game game) {
        return new GameSummaryResponse(
                game.getId(),
                game.getSteamAppId(),
                game.getName(),
                game.getShortDescription(),
                game.getHeaderImage(),
                game.getReleaseDate(),
                game.getPriceInitial(),
                game.getPriceFinal(),
                game.getMetacriticScore(),
                game.getPositiveReviews(),
                game.getNegativeReviews(),
                game.getGenres().stream().map(g -> g.getGenreName()).toList(),
                game.getTags().stream().map(t -> t.getTagName()).toList()
        );
    }
}
