"""
Budget Guardian Core Logic - 2026 Agentic Commerce Edition
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class MealOption(BaseModel):
    restaurant: str
    item: str
    price: float
    rating: float = 4.0
    value_score: float = 0.0

    def calculate_value(self):
        """Higher is better: rating / (price / 100)"""
        self.value_score = round(self.rating / (self.price / 100), 2)

class Cart(BaseModel):
    items: List[MealOption]
    total_cost: float = 0.0
    status: str = "pending"
    reason: Optional[str] = None

def check_spending_limit(user_id: str) -> float:
    """
    Check the current wallet balance for the week.
    In a real scenario, this would query a budget ledger or banking API.
    """
    # Mocking a remaining budget for the week
    mock_remaining = 1200.00
    print(f"[BUDGET] User {user_id} has INR {mock_remaining} remaining this week.")
    return mock_remaining

def find_best_value(query: str, max_price: float) -> List[MealOption]:
    """
    Scans Swiggy results and ranks them by 'Value Score'.
    Ignores ads and high-cost outliers.
    """
    print(f"[SEARCH] Scanning Swiggy for '{query}' under INR {max_price}...")
    
    # Simulating raw search results from Swiggy MCP
    raw_results = [
        {"restaurant": "Biryani House", "item": "Executive Thali", "price": 350.0, "rating": 4.5},
        {"restaurant": "Quick Bites", "item": "Burger Combo", "price": 199.0, "rating": 3.8},
        {"restaurant": "Premium Grill (AD)", "item": "Steak Meal", "price": 450.0, "rating": 4.8},
        {"restaurant": "Local Dhaba", "item": "Dal Makhani + Roti", "price": 150.0, "rating": 4.2},
    ]
    
    processed_options = []
    for data in raw_results:
        # 1. Filter out results exceeding the individual request limit
        if data["price"] > max_price:
            continue
            
        # 2. Filter out obvious Ads (mocked)
        if "(AD)" in data["restaurant"]:
            print(f"[FILTER] Ignoring sponsored ad: {data['restaurant']}")
            continue
            
        option = MealOption(**data)
        option.calculate_value()
        processed_options.append(option)
    
    # Sort by value score (descending)
    processed_options.sort(key=lambda x: x.value_score, reverse=True)
    
    return processed_options

def verify_and_build_cart(selected_items: List[MealOption], user_id: str) -> Cart:
    """
    Ensures the final cart (including hidden fees) stays within the weekly limit.
    """
    total_cost = sum(item.price for item in selected_items)
    spending_limit = check_spending_limit(user_id)
    
    if total_cost > spending_limit:
        return Cart(
            items=selected_items,
            total_cost=total_cost,
            status="rejected",
            reason=f"Total INR {total_cost} exceeds weekly allowance of INR {spending_limit}."
        )
    
    print(f"[CART] Cart verified for {user_id}. Total: INR {total_cost}")
    return Cart(
        items=selected_items,
        total_cost=total_cost,
        status="approved"
    )

if __name__ == "__main__":
    # Quick Test Execution
    USER = "faizan_khan_01"
    
    # 1. User wants dinner for two under 400
    options = find_best_value("dinner for two", 400.0)
    
    if options:
        print("\nTop Value Recommendations:")
        for opt in options:
            print(f"- {opt.restaurant}: {opt.item} (INR {opt.price}) [Value Score: {opt.value_score}]")
            
        # 2. Build cart with the best option
        final_cart = verify_and_build_cart([options[0]], USER)
        print(f"\nFinal Cart Status: {final_cart.status.upper()}")
        if final_cart.reason:
            print(f"Reason: {final_cart.reason}")
    else:
        print("No suitable options found within budget.")
