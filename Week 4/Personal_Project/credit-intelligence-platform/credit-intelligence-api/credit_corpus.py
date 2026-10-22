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

CREDIT_DOCUMENTS.extend([
    {
        "id": "credit-doc-011",
        "title": "Northbridge Components - September Monitoring Update",
        "type": "monitoring_note",
        "body": (
            "Northbridge Components Ltd reported updated financial information dated 30 September 2026. "
            "Revenue is £535m, EBITDA is £79m, total debt is £252m, cash is £34m and interest expense is £25m. "
            "The borrower remains outside the watchlist. Facility FAC-2048 has £90m drawn against its £120m commitment. "
            "Net leverage is approximately 2.76x and interest cover is approximately 3.16x. "
            "This monitoring update supersedes the August 2026 annual review for current financial metrics."
        ),
    },
    {
        "id": "credit-doc-012",
        "title": "Northbridge Components - Facility Amendment",
        "type": "facility_amendment",
        "body": (
            "Facility FAC-2048 remains a £120m revolving credit facility for Northbridge Components Ltd. "
            "Its maturity remains 30 June 2029. The margin increases from 225 basis points to 250 basis points from 1 October 2026. "
            "No change was made to the committed amount or final maturity."
        ),
    },
    {
        "id": "credit-doc-013",
        "title": "Meridian Logistics Group - Covenant Certificate",
        "type": "covenant_certificate",
        "body": (
            "Meridian Logistics Group's term facility is reference FAC-3115. "
            "Covenant COV-4201 requires net leverage not to exceed 4.5x. "
            "Covenant COV-4202 requires interest cover of at least 2.25x. "
            "Current net leverage is approximately 3.51x and interest cover is approximately 3.10x. "
            "Meridian therefore remains within both covenant thresholds."
        ),
    },
    {
        "id": "credit-doc-014",
        "title": "Meridian Logistics Group - Refinancing Update",
        "type": "refinancing_note",
        "body": (
            "Meridian Logistics Group has begun lender discussions ahead of the 31 December 2028 maturity of its term facility. "
            "Management is considering refinancing options, extension proposals and potential debt reduction. "
            "No refinancing transaction has yet been agreed and the existing maturity remains unchanged. "
            "The note contains no external agency credit rating."
        ),
    },
    {
        "id": "credit-doc-015",
        "title": "Asteron Retail Group - Covenant Downside Review",
        "type": "covenant_review",
        "body": (
            "Asteron Retail Group's revolving facility is reference FAC-5300. "
            "Covenant COV-5301 requires net leverage not to exceed 4.25x. "
            "Current net leverage is approximately 3.96x. Under a 20 percent EBITDA downside, net leverage would rise to approximately 4.95x, "
            "which would exceed the covenant threshold and require escalation."
        ),
    },
    {
        "id": "credit-doc-016",
        "title": "Asteron Retail Group - September Monitoring Update",
        "type": "monitoring_note",
        "body": (
            "Asteron Retail Group reported updated financial information dated 30 September 2026. "
            "Revenue is £1,195m, EBITDA is £101m, total debt is £468m, cash is £39m and interest expense is £41m. "
            "The borrower remains on the watchlist with a high internal risk band. "
            "This update supersedes the March 2026 credit committee note for current financial metrics."
        ),
    },
    {
        "id": "credit-doc-017",
        "title": "Helios Renewables plc - Covenant Certificate",
        "type": "covenant_certificate",
        "body": (
            "Helios Renewables plc is tested under facility FAC-4410. "
            "Covenant COV-4411 requires net leverage not to exceed 3.0x. "
            "Covenant COV-4412 requires interest cover of at least 3.0x. "
            "Current net leverage is approximately 1.51x and interest cover is approximately 7.09x. "
            "Helios remains comfortably within both covenant thresholds."
        ),
    },
    {
        "id": "credit-doc-018",
        "title": "Helios Renewables plc - Solar Portfolio Financing",
        "type": "facility_note",
        "body": (
            "Helios Renewables plc also maintains project financing reference FAC-4420 for a UK solar portfolio. "
            "FAC-4420 is separate from the corporate term facility FAC-4410. "
            "The project financing has a committed amount of £95m and matures on 31 December 2032."
        ),
    },
    {
        "id": "credit-doc-019",
        "title": "Redwood Healthcare Holdings - Annual Credit Review",
        "type": "credit_review",
        "body": (
            "Redwood Healthcare Holdings reported updated financial information dated 31 August 2026. "
            "Revenue is £450m, EBITDA is £76m, total debt is £211m, cash is £35m and interest expense is £18m. "
            "The borrower has a moderate internal risk band and is not on the watchlist. "
            "Its revolving facility is reference FAC-6200, committed at £100m with £65m drawn."
        ),
    },
    {
        "id": "credit-doc-020",
        "title": "Redwood Healthcare Holdings - Covenant Certificate",
        "type": "covenant_certificate",
        "body": (
            "Facility FAC-6200 is subject to covenant COV-6201 requiring net leverage not to exceed 3.5x. "
            "Covenant COV-6202 requires interest cover of at least 3.0x. "
            "Redwood Healthcare Holdings currently has net leverage of approximately 2.32x and interest cover of approximately 4.22x. "
            "The borrower remains within both covenant thresholds."
        ),
    },
    {
        "id": "credit-doc-021",
        "title": "Orion Business Services - Covenant Review",
        "type": "covenant_review",
        "body": (
            "Orion Business Services' acquisition facility is reference FAC-7300. "
            "Covenant COV-7301 requires net leverage not to exceed 4.75x. "
            "Current net leverage is approximately 3.45x. "
            "The facility remains within covenant but headroom is monitored because of Orion's elevated internal risk band."
        ),
    },
    {
        "id": "credit-doc-022",
        "title": "Orion Business Services - September Watchlist Update",
        "type": "watchlist_review",
        "body": (
            "Orion Business Services remains on the watchlist as at 30 September 2026. "
            "The internal risk band remains elevated. Management attention is focused on leverage reduction, trading performance and refinancing options. "
            "No decision has been taken to remove Orion from the watchlist."
        ),
    },
    {
        "id": "credit-doc-023",
        "title": "Credit Risk Policy - Watchlist Escalation",
        "type": "policy",
        "body": (
            "A borrower may be considered for watchlist escalation when there is material covenant pressure, deteriorating liquidity, refinancing uncertainty "
            "or a significant deterioration in operating performance. Watchlist classification requires human credit judgement. "
            "The Credit Intelligence system may recommend review or escalation but must not independently change a borrower's watchlist status."
        ),
    },
    {
        "id": "credit-doc-024",
        "title": "Credit Risk Policy - Evidence Hierarchy",
        "type": "policy",
        "body": (
            "When borrower-specific documents contain different financial figures, the most recent dated borrower-specific source should be used for current metrics. "
            "Older documents remain valid historical evidence and must not be silently rewritten. "
            "Contractual facility and covenant terms should be taken from the relevant facility, amendment or covenant document. "
            "If two current sources conflict and neither can be established as authoritative, the discrepancy must be escalated for human review."
        ),
    },
])