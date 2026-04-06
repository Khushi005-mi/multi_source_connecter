import os
import sys

# Add src to path for imports
sys.path.append(os.path.dirname(__file__))

def generate_insights(results: dict) -> list:
    """
    Input:  dictionary of computed metrics from analyzer
    Output: list of human-readable insights (strings)
    """
    insights = []

    # Step 1 — Spending vs Income check
    if results["total_outflow"] >= results["total_inflow"]:
        insights.append("⚠️ You spent more than you earned this month.")
    else:
        insights.append("✅ Great job! You earned more than you spent this month.")

    # Step 2 — Top spending category
    if results.get("category_summary"):
        top_category = max(results["category_summary"], key=results["category_summary"].get)
        top_amount = results["category_summary"][top_category]
        insights.append(f"Top spending category: {top_category} (₹{top_amount}).")
    else:
        insights.append("No spending categories found.")

    # Step 3 — Savings rate (optional, only if provided in results)
    if "savings_rate" in results and results["total_inflow"] > 0:
        savings_rate = results["savings_rate"] * 100
        insights.append(f"Savings rate: {savings_rate:.2f}%.")

    # Step 4 — Monthly trend highlight
    if results.get("monthly_trend"):
        highest_month = max(results["monthly_trend"], key=results["monthly_trend"].get)
        insights.append(f"Highest spending month: {highest_month}.")
    else:
        insights.append("No monthly trend data available.")

    return insights


if __name__ == "__main__":
    # Example: dummy results dictionary
    results = {
        "total_inflow": 50000,
        "total_outflow": 60000,
        "category_summary": {"Food": 12000, "Rent": 20000, "Travel": 8000},
        "monthly_trend": {"2026-01": 15000, "2026-02": 18000, "2026-03": 27000},
        "savings_rate": 0.25
    }

    insights = generate_insights(results)

    print("\n=== Insights ===")
    for i, insight in enumerate(insights, 1):
        print(f"{i}. {insight}")
