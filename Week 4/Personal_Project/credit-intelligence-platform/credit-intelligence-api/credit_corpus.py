"""Synthetic credit documents used for retrieval and RAG evaluation."""

CREDIT_DOCUMENTS = [
    {
        "id": "credit-doc-001",
        "title": "Northbridge Components - Annual Credit Review",
        "type": "credit_review",
        "body": (
            "Northbridge Components Ltd is a UK manufacturing borrower with revenue of £520m and EBITDA of £82m. "
            "Total debt is £245m and cash is £38m, giving net debt of £207m. Interest expense is £24m. "
            "The latest financial information is dated 31 August 2026. The borrower is not currently on the watchlist. "
            "Its revolving credit facility is reference FAC-2048, with a committed amount of £120m and £85m currently drawn. "
            "The facility matures on 30 June 2029 and carries a margin of 225 basis points."
        ),
    },
    {
        "id": "credit-doc-002",
        "title": "Northbridge Components - Covenant Certificate",
        "type": "covenant_certificate",
        "body": (
            "Northbridge Components Ltd is tested against two financial covenants under facility FAC-2048. "
            "Covenant COV-3102 requires net leverage not to exceed 4.0x. Covenant COV-3103 requires interest cover of at least 2.5x. "
            "Based on current financials, net leverage is approximately 2.52x and interest cover is approximately 3.42x. "
            "The borrower therefore remains within both covenant limits."
        ),
    },
    {
        "id": "credit-doc-003",
        "title": "Meridian Logistics Group - Watchlist Review",
        "type": "watchlist_review",
        "body": (
            "Meridian Logistics Group is a UK transport and logistics borrower with an elevated internal risk band. "
            "Revenue is £760m, EBITDA is £96m, total debt is £365m and cash is £28m. Interest expense is £31m. "
            "The latest financial information is dated 31 July 2026 and the borrower is on the watchlist. "
            "Its £250m term facility is fully drawn and matures on 31 December 2028. "
            "Management attention remains focused on leverage, refinancing capacity and covenant headroom."
        ),
    },
    {
        "id": "credit-doc-004",
        "title": "Asteron Retail Group - Credit Committee Note",
        "type": "credit_committee",
        "body": (
            "Asteron Retail Group is a UK retail borrower with a high internal risk band and is currently on the watchlist. "
            "Revenue is £1,180m, EBITDA is £108m, total debt is £470m and cash is £42m. Interest expense is £39m. "
            "The latest financial information is dated 31 March 2026. "
            "Asteron's revolving facility has a committed amount of £180m, of which £145m is drawn, and matures on 31 March 2028. "
            "A 20 percent EBITDA downside would materially weaken leverage and interest cover and would create covenant pressure."
        ),
    },
    {
        "id": "credit-doc-005",
        "title": "Helios Renewables plc - Annual Credit Review",
        "type": "credit_review",
        "body": (
            "Helios Renewables plc is a UK renewable energy borrower with a low internal risk band. "
            "Revenue is £640m, EBITDA is £156m, total debt is £310m and cash is £74m. Interest expense is £22m. "
            "The latest financial information is dated 31 August 2026 and the borrower is not on the watchlist. "
            "Its £220m term facility is reference FAC-4410, with £210m currently drawn and maturity on 30 September 2031. "
            "The facility is unsecured and carries a margin of 180 basis points."
        ),
    },
    {
        "id": "credit-doc-006",
        "title": "Redwood Healthcare Holdings - Relationship Review",
        "type": "relationship_review",
        "body": (
            "Redwood Healthcare Holdings is a UK healthcare borrower with a moderate internal risk band. "
            "Revenue is £430m, EBITDA is £71m, total debt is £205m and cash is £31m. Interest expense is £18m. "
            "The latest financial information is dated 30 June 2026 and the borrower is not currently on the watchlist. "
            "Its revolving facility is committed at £100m with £62m drawn and matures on 31 January 2029."
        ),
    },
    {
        "id": "credit-doc-007",
        "title": "Orion Business Services - Monitoring Note",
        "type": "monitoring_note",
        "body": (
            "Orion Business Services is a UK business services borrower with an elevated internal risk band and is on the watchlist. "
            "Revenue is £295m, EBITDA is £47m, total debt is £181m and cash is £19m. Interest expense is £17m. "
            "The latest financial information is dated 31 May 2026. "
            "Its acquisition facility is committed at £150m with £138m drawn, carries a margin of 340 basis points and matures on 30 June 2028. "
            "The facility is secured."
        ),
    },
    {
        "id": "credit-doc-008",
        "title": "Credit Risk Policy - Financial Information Freshness",
        "type": "policy",
        "body": (
            "For this synthetic Credit Intelligence policy, financial information up to 90 days old is treated as current. "
            "Financial information between 91 and 180 days old is treated as ageing. "
            "Financial information more than 180 days old is treated as stale. "
            "A current borrower-specific credit assessment must not be generated from stale financial information without human review."
        ),
    },
    {
        "id": "credit-doc-009",
        "title": "Credit Risk Policy - Lending Decisions",
        "type": "policy",
        "body": (
            "The Credit Intelligence system is a decision-support tool and does not have authority to approve or reject lending. "
            "Permitted recommended actions are maintain, review and escalate. "
            "Final credit approval, decline and limit decisions remain the responsibility of authorised human credit officers and committees."
        ),
    },
    {
        "id": "credit-doc-010",
        "title": "Covenant Monitoring Standard",
        "type": "policy",
        "body": (
            "Covenant monitoring should compare calculated borrower metrics with the contractual covenant thresholds. "
            "Net leverage is calculated as net debt divided by EBITDA. Interest cover is calculated as EBITDA divided by interest expense. "
            "If required financial inputs are missing, the system must not invent values or perform the calculation. "
            "Stress testing may apply an EBITDA downside scenario to assess how covenant headroom changes under weaker operating performance."
        ),
    },
]