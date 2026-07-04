from src.models.preferences import UserPreferences
from src.llm.recommendation import RecommendationService
from src.services.filter import RestaurantFilter
from data_layer.repository import RestaurantRepository
import json

def run_prediction():
    print("Initializing services...")
    repo = RestaurantRepository()
    filter_service = RestaurantFilter(repository=repo)
    recommendation_service = RecommendationService(filter_service=filter_service)
    
    # Create the user preferences mapping budget 1500 to 'medium'
    prefs = UserPreferences(
        location="bellandur",
        budget="medium",
        min_rating=4.2,
        cuisine=None,
        additional=""
    )
    
    print(f"\nQuerying recommendations for: {prefs}\n")
    try:
        response, warnings = recommendation_service.recommend(prefs)
        
        print("=== SUMMARY ===")
        print(response.summary)
        print("\n=== TOP 5 RECOMMENDATIONS ===")
        for rec in response.recommendations:
            print(f"{rec.rank}. {rec.name} (Rating: {rec.rating}, Cost: {rec.estimated_cost})")
            print(f"   Cuisines: {rec.cuisine}")
            print(f"   Explanation: {rec.explanation}\n")
            
        if warnings:
            print("=== WARNINGS ===")
            for w in warnings:
                print(f"- {w}")
                
    except Exception as e:
        print(f"Error during recommendation: {e}")

if __name__ == "__main__":
    run_prediction()
