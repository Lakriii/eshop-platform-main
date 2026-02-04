from jinja2 import Template
from playwright.sync_api import sync_playwright
import datetime

def generate_pdf():
    # Load HTML template
    with open("templates/report.html", "r", encoding="utf-8") as f:
        html_template = f.read()

    template = Template(html_template)

    html_content = template.render(
        date=datetime.date.today(),
        total_orders=1520,
        revenue=45670,
        customers=892,
        chart_path="static/report/sales_chart.png"
    )

    # Save rendered HTML
    with open("report_rendered.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # Playwright PDF
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto("file://" + __import__("os").path.abspath("report_rendered.html"))
        page.pdf(
            path="eshop_report.pdf",
            format="A4",
            print_background=True
        )
        browser.close()

if __name__ == "__main__":
    generate_pdf()
