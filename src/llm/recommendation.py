import logging
from typing import List, Tuple, Dict, Any
from src.models.preferences import UserPreferences
from src.models.restaurant import Restaurant
from src.models.recommendation import Recommendation, RecommendationResponse
from src.services.filter import RestaurantFilter
from src.llm.prompt_builder import PromptBuilder
from src.llm.llm_client import LLMClient
from src.llm.response_parser import ResponseParser
from src.config import settings

logger = logging.getLogger(__name__)

class RecommendationEnricher:
    @staticmethod
    def enrich(parsed_response: Dict[str, Any], candidates: List[Restaurant]) -> RecommendationResponse:
        candidate_map = {str(r.id): r for r in candidates}
        
        recs = []
        seen_ids = set()
        for item in parsed_response.get("recommendations", []):
            r_id = str(item["id"])
            if r_id in candidate_map and r_id not in seen_ids:
                seen_ids.add(r_id)
                recs.append(Recommendation(
                    restaurant_id=r_id,
                    name=candidate_map[r_id].name,
                    cuisine=", ".join(candidate_map[r_id].cuisines),
                    rating=candidate_map[r_id].rating,
                    estimated_cost=candidate_map[r_id].cost_for_two,
                    rank=item["rank"],
                    explanation=item["explanation"]
                ))
            elif r_id not in candidate_map:
                logger.warning(f"LLM recommended unknown restaurant ID: {r_id}")
                
        # Sort by rank
        recs.sort(key=lambda x: x.rank)
        
        return RecommendationResponse(
            summary=parsed_response.get("summary", ""),
            recommendations=recs
        )

class RecommendationService:
    def __init__(self, filter_service: RestaurantFilter, llm_client: LLMClient = None):
        self.filter_service = filter_service
        self.llm_client = llm_client or LLMClient()
        
    def recommend(self, prefs: UserPreferences) -> Tuple[RecommendationResponse, List[str]]:
        candidates, warnings = self.filter_service.filter(prefs)
        
        if not candidates:
            return RecommendationResponse(summary="No restaurants found matching your criteria.", recommendations=[]), warnings
            
        messages = PromptBuilder.build_prompt(prefs, candidates)
        
        try:
            raw_response = self.llm_client.complete(messages)
            try:
                parsed_response = ResponseParser.parse(raw_response)
            except ValueError:
                logger.warning("Failed to parse LLM response. Retrying with temperature=0.1")
                raw_response = self.llm_client.complete(messages, temperature=0.1)
                parsed_response = ResponseParser.parse(raw_response)
                
            response = RecommendationEnricher.enrich(parsed_response, candidates)
            # if LLM returns 0 recommendations for some reason, fallback
            if not response.recommendations:
                raise ValueError("LLM returned 0 valid recommendations")
                
            return response, warnings
            
        except Exception as e:
            logger.error(f"LLM pipeline failed: {e}. Falling back to heuristic ranking.")
            fallback_response = self._heuristic_fallback(candidates)
            warnings.append("AI recommendations temporarily unavailable. Showing top-rated options.")
            return fallback_response, warnings
            
    def _heuristic_fallback(self, candidates: List[Restaurant]) -> RecommendationResponse:
        """
        Fallback heuristic ranking used when the LLM service is unavailable, fails to parse, 
        or times out. It guarantees the user still receives valid recommendations.
        
        Methodology:
        1. Sorts all filtered candidates by rating and total votes in descending order.
        2. Slices the top-K items as defined in settings.
        3. Constructs a synthetic explanation explaining why it was chosen based on rating and cuisine.
        """
        # Sort by rating and votes
        sorted_candidates = sorted(candidates, key=lambda x: (x.rating, x.votes), reverse=True)
        top_k = sorted_candidates[:settings.TOP_K_RECOMMENDATIONS]
        
        recs = []
        for i, r in enumerate(top_k):
            recs.append(Recommendation(
                restaurant_id=str(r.id),
                name=r.name,
                cuisine=", ".join(r.cuisines),
                rating=r.rating,
                estimated_cost=r.cost_for_two,
                rank=i+1,
                explanation=f"Highly rated ({r.rating}/5) restaurant known for {', '.join(r.cuisines)}."
            ))
            
        return RecommendationResponse(
            summary="Here are the top-rated restaurants matching your preferences.",
            recommendations=recs
        )
