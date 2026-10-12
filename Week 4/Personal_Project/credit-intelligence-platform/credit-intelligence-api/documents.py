"""Synthetic credit documents used for RAG and evaluation."""

CREDIT_DOCUMENTS = [
    {
        "id": "credit-doc-101",
        "borrower_id": 1,
        "type": "credit_review",
        "date": "2026-09-15",
        "title": "Northbridge Components - Annual Credit Review",
        "body": (
            "Northbridge Components continues to trade broadly in line with expectations. "
            "Revenue remains supported by long-term manufacturing contracts and customer retention is stable. "
            "Management's main priority is protecting operating margin while raw-material costs remain volatile. "
            "Liquidity is considered adequate, with cash available alongside undrawn revolving credit capacity. "
            "The borrower is not currently on the watchlist. No covenant breach has been reported."
        ),
    },
    {
        "id": "credit-doc-102",
        "borrower_id": 2,
        "type": "watchlist_review",
        "date": "2026-09-01",
        "title": "Meridian Logistics Group - Watchlist Review",
        "body": (
            "Meridian Logistics remains on the internal watchlist following weaker freight volumes and higher operating costs. "
            "Management has started a cost-reduction programme and expects benefits to emerge over the next two quarters. "
            "Debt remains elevated relative to earnings and covenant headroom has reduced. "
            "Liquidity remains sufficient for current operations, but further deterioration in EBITDA would increase refinancing risk."
        ),
    },
    {
        "id": "credit-doc-103",
        "borrower_id": 3,
        "type": "covenant_review",
        "date": "2026-04-15",
        "title": "Asteron Retail Group - Covenant Review",
        "body": (
            "Asteron Retail has experienced pressure from weaker discretionary spending and increased store operating costs. "
            "The borrower remains on the watchlist. Current leverage is close to the maximum covenant threshold. "
            "A downside scenario involving a further fall in EBITDA would result in a covenant breach. "
            "Management is reviewing store closures and working-capital measures to preserve liquidity."
        ),
    },
    {
        "id": "credit-doc-104",
        "borrower_id": 4,
        "type": "credit_review",
        "date": "2026-09-20",
        "title": "Helios Renewables - Credit Review",
        "body": (
            "Helios Renewables continues to demonstrate strong operating performance supported by contracted renewable-energy revenues. "
            "Cash generation remains healthy and leverage is moderate relative to EBITDA. "
            "The borrower is not on the watchlist and current covenant headroom is comfortable. "
            "The main risks are construction delays on new projects and exposure to changes in power-market pricing."
        ),
    },
    {
        "id": "credit-doc-105",
        "borrower_id": 5,
        "type": "portfolio_update",
        "date": "2026-08-10",
        "title": "Redwood Healthcare Holdings - Portfolio Update",
        "body": (
            "Redwood Healthcare continues to generate stable demand across its core healthcare services. "
            "Revenue growth has been modest but predictable, while EBITDA margins remain broadly stable. "
            "Debt service capacity is considered adequate and the borrower retains reasonable covenant headroom. "
            "Management is monitoring wage inflation and staff shortages, which remain the main operating risks."
        ),
    },
    {
        "id": "credit-doc-106",
        "borrower_id": 6,
        "type": "watchlist_review",
        "date": "2026-07-15",
        "title": "Orion Business Services - Watchlist Review",
        "body": (
            "Orion Business Services remains on the watchlist following an acquisition that increased debt materially. "
            "Integration is progressing, but expected cost savings have not yet been fully achieved. "
            "Leverage remains elevated and interest cover is weaker than the portfolio average. "
            "A sustained reduction in EBITDA would create pressure on covenant headroom and could require lender engagement."
        ),
    },
    {
        "id": "credit-doc-107",
        "borrower_id": None,
        "type": "methodology",
        "date": "2026-09-30",
        "title": "Credit Monitoring Methodology",
        "body": (
            "The platform uses net leverage and interest cover as core credit-monitoring metrics. "
            "Net leverage is calculated as total debt less cash, divided by EBITDA. "
            "Interest cover is calculated as EBITDA divided by interest expense. "
            "Covenant stress testing applies an EBITDA downside scenario while holding debt, cash and interest expense constant. "
            "Model-generated recommendations are limited to maintain, review or escalate and do not constitute lending approval."
        ),
    },
    {
        "id": "credit-doc-108",
        "borrower_id": None,
        "type": "market",
        "date": "2026-10-01",
        "title": "UK Corporate Credit Market Update",
        "body": (
            "UK corporate borrowers continue to face pressure from elevated financing costs and uneven demand. "
            "Highly leveraged borrowers are more exposed to refinancing risk where debt maturities fall within the next two years. "
            "Lenders are placing increased emphasis on liquidity, covenant headroom and the resilience of EBITDA under downside scenarios. "
            "Businesses with predictable cash flows and lower leverage remain better positioned to absorb economic volatility."
        ),
    },
]