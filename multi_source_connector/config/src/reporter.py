import os
import sys
import pandas as pd
import matplotlib.pyplot as plt

# Add src to path for imports
sys.path.append(os.path.dirname(__file__))

from analyzer import analyze_transactions
from insights import generate_insights

def create_report(df: pd.DataFrame, template_path: str = "report.html", output_path: str = "final_report.html"):
    """
    Input:  canonical DataFrame of transactions
    Output: rendered HTML report with charts + insights
    """

    # Step 1 — Run analyzer
    results = analyze_transactions(df)

    # Step 2 — Generate insights
    insights = generate_insights(results)

    # Step 3 — Generate charts
    os.makedirs("charts", exist_ok=True)

    # Category Pie Chart
    plt.figure(figsize=(8, 6))
    plt.pie(
        results["category_summary"].values(),
        labels=results["category_summary"].keys(),
        autopct="%1.1f%%"
    )
    plt.title("Spending by Category")
    plt.tight_layout()
    plt.savefig("charts/category_pie.png")
    plt.close()

    # Monthly Trend Chart
    plt.figure(figsize=(10, 6))
    months = list(results["monthly_trend"].keys())
    values = list(results["monthly_trend"].values())
    plt.plot(months, values, marker="o")
    plt.xticks(rotation=45)
    plt.title("Monthly Spending Trend")
    plt.tight_layout()
    plt.savefig("charts/monthly_trend.png")
    plt.close()

    # Step 4 — Load HTML template
    with open(template_path, "r") as f:
        template = f.read()

    # Step 5 — Replace placeholders with actual values
    rendered_html = template.replace("{{ inflow }}", str(results["total_inflow"]))
    rendered_html = rendered_html.replace("{{ outflow }}", str(results["total_outflow"]))

    # Replace insights list
    insights_html = "".join([f"<li>{i}</li>" for i in insights])
    rendered_html = rendered_html.replace("{% for insight in insights %}", "")
    rendered_html = rendered_html.replace("{% endfor %}", "")
    rendered_html = rendered_html.replace("{{ insight }}", insights_html)

    # Step 6 — Save final report
    with open(output_path, "w") as f:
        f.write(rendered_html)

    print(f"Report generated: {output_path}")


if __name__ == "__main__":
    # Example: load merged transactions
    df = pd.read_csv("data/processed/merged_transactions.csv")

    # Step 1 — Create report
    create_report(df)

    # Step 2 — Print confirmation
    print("\n=== Report Generation Complete ===")
