# Credit Intelligence Platform
## Project Plan

## 1. Project Overview

The Credit Intelligence Platform is an AI-assisted corporate credit
monitoring application designed for corporate credit analysts.

The system helps an analyst:

- review borrower financial information
- monitor credit facilities and financial covenants
- search internal credit documents
- identify deteriorating credit conditions
- run covenant stress tests
- generate grounded credit analysis
- escalate cases that require human review

The system is decision support only.

It may recommend:

- maintain
- review
- escalate

It must never independently approve or reject credit.


## 2. Primary User

### User
Corporate Credit Analyst

### Main decision

The analyst is trying to decide:

"Does this borrower remain within acceptable credit parameters,
or does the case require further investigation or escalation?"

The platform brings together structured financial data and
unstructured credit documentation to support that decision.


## 3. Architecture

Browser
    |
    v
Streamlit UI
    |
    | HTTP
    v
FastAPI
    |
    +--------------------+
    |                    |
    v                    v
Structured Data       AI / RAG
    |                    |
    |                 Claude
    |                    |
    |                 Agent
    |                /     \
    |               /       \
    |              v         v
    |        Knowledge     Covenant
    |          Search      Calculator
    |             |
    |           Voyage
    |             |
    |          ChromaDB
    |
    v
Borrowers / Facilities / Covenants


## 4. Structured Data Model

The system will use three related entity types.

### Borrower

Fields:

- id
- name
- sector
- country
- internal_risk_band
- revenue_m
- ebitda_m
- total_debt_m
- cash_m
- interest_expense_m
- last_financials_date
- watchlist

Example:

Northbridge Components Ltd
Manufacturing
United Kingdom


### Credit Facility

Fields:

- id
- borrower_id
- facility_type
- currency
- committed_amount_m
- drawn_amount_m
- margin_bps
- maturity_date
- secured


### Covenant

Fields:

- id
- facility_id
- metric
- threshold
- comparison
- testing_frequency
- last_test_date

Example:

Net leverage <= 4.0x

Interest cover >= 2.5x


## 5. Entity Relationships

Borrower
    |
    +---- Credit Facility
                |
                +---- Covenant


Example:

Northbridge Components
        |
        +---- £120m Revolving Credit Facility
                    |
                    +---- Net leverage <= 4.0x
                    |
                    +---- Interest cover >= 2.5x


## 6. Structured Dataset

All data will be synthetic.

Initial target:

Borrowers: 6
Facilities: 6+
Covenants: 10+

No real customer information, account numbers or confidential
employer information will be used.


## 7. API Endpoints

### Health

GET /health


### Borrowers

GET    /borrowers
GET    /borrowers/{borrower_id}
POST   /borrowers
PUT    /borrowers/{borrower_id}
DELETE /borrowers/{borrower_id}


Suggested filters:

GET /borrowers?sector=manufacturing

GET /borrowers?watchlist=true


### Facilities

GET    /facilities
GET    /facilities/{facility_id}
POST   /facilities
PUT    /facilities/{facility_id}
DELETE /facilities/{facility_id}


Suggested filters:

GET /facilities?borrower_id=1

GET /facilities?secured=true


### Covenants

GET    /covenants
GET    /covenants/{covenant_id}
POST   /covenants
PUT    /covenants/{covenant_id}
DELETE /covenants/{covenant_id}


## 8. Deterministic Credit Calculations

Financial calculations will be performed in Python rather than
delegated to the language model.

### Net debt

net_debt =
total_debt - cash


### Net leverage

net_leverage =
net_debt / EBITDA


### Interest cover

interest_cover =
EBITDA / interest_expense


### Stress testing

The analyst can apply an EBITDA downside scenario.

Example:

Current EBITDA = £100m

Stress = -20%

Stressed EBITDA = £80m

The platform then recalculates:

- net leverage
- interest cover
- covenant headroom
- covenant status


## 9. Claude Features

### Borrower Summary

POST /borrowers/{borrower_id}/summary

Creates a grounded summary of the borrower using structured data.


### Streaming Summary

GET /borrowers/{borrower_id}/summary/stream

Streams a draft credit memo section as it is generated.


### Structured Credit Assessment

POST /borrowers/{borrower_id}/assessment

Claude must return data validated against a Pydantic model.


## 10. CreditAssessment Schema

Proposed fields:

risk_level:
- low
- moderate
- elevated
- high

strengths:
- list of key credit strengths

risks:
- list of key credit risks

covenant_status:
- comfortable
- tight
- breached
- unknown

outlook:
- positive
- stable
- negative

recommended_action:
- maintain
- review
- escalate

rationale:
- short evidence-based explanation


The model cannot independently approve or reject a credit facility.


## 11. Document Corpus

The first version will contain at least ten realistic synthetic
documents.

doc-001
Corporate Lending Policy - Leveraged Credit

doc-002
Northbridge Components - Annual Credit Review

doc-003
UK Manufacturing Sector Outlook

doc-004
Meridian Logistics - Covenant Monitoring Review

doc-005
Asteron Retail Group - Downside Scenario Review

doc-006
Financial Covenant Monitoring Policy

doc-007
Energy Transition Sector Risk Note

doc-008
Corporate Credit Early Warning Indicators Guide

doc-009
Revolving Credit Facility Structuring Guidance

doc-010
Credit Committee Escalation Policy


Documents will use realistic professional formats such as:

- credit memos
- policy documents
- sector research
- covenant reviews
- risk notes

Each document will contain metadata including:

- document id
- title
- document type
- borrower id where applicable
- as-of date


## 12. Embeddings and Vector Search

Embedding provider:

Voyage AI

Vector database:

ChromaDB

The Chroma collection will be persistent.

Documents will be embedded using:

input_type="document"

Questions will be embedded using:

input_type="query"


## 13. Knowledge Endpoints

POST /knowledge/index

Embeds and upserts the document corpus.


POST /knowledge/search

Performs retrieval only.

Returns:

- document id
- title
- text
- similarity score


POST /knowledge/ask

Runs grounded RAG question answering.

Flow:

question
    |
    v
Voyage query embedding
    |
    v
Chroma search
    |
    v
relevance filter
    |
    +---- nothing relevant ---> refuse
    |
    v
build context
    |
    v
Claude
    |
    v
grounded answer + citations


## 14. Relevance Floor

The initial experimental relevance floor will be:

0.30

This value is NOT final.

An evaluation set will be used to test several thresholds.

Example thresholds:

0.20
0.25
0.30
0.35
0.40

The final threshold will be selected based on the trade-off between:

- false positive retrieval
- false refusals
- correct retrieval


## 15. Refusal Rules

### Rule 1 - Retrieval confidence

If no retrieved document clears the relevance floor:

Do not call Claude.

Return:

"Insufficient relevant evidence in the knowledge base."


### Rule 2 - Stale financial information

A current borrower-specific credit assessment must not be produced
when required financial information is more than 180 days old.

Return a message explaining that the financial information is stale.


### Rule 3 - Missing financial information

If required values such as EBITDA, debt or interest expense are
missing, calculations dependent on those fields must not be performed.


### Rule 4 - Human credit authority

The system may recommend:

maintain
review
escalate

It must never independently approve or reject lending.


## 16. Time-Sensitive Behaviour

Dates will be part of the data model.

Important dates:

- financials as-of date
- document as-of date
- covenant test date
- facility maturity date


Initial synthetic freshness classification:

0-90 days:
current

91-180 days:
ageing

over 180 days:
stale


These thresholds represent an internal synthetic policy for this
project and are not presented as regulatory requirements.


## 17. Agent

The agent will have at least two tools.


### Tool 1

search_knowledge_base

Purpose:

Search credit policies, credit memos, sector research and other
unstructured documentation.


### Tool 2

calculate_covenant_headroom

Purpose:

Perform deterministic credit calculations using borrower and
covenant data.


Potential input:

borrower_id
ebitda_shock_pct


Potential output:

current EBITDA
stressed EBITDA
net debt
current leverage
stressed leverage
interest cover
covenant threshold
headroom
status


Possible status:

comfortable
tight
breached


## 18. Agent Safety

The agent will have:

MAX_ITERATIONS

The exact limit will be configurable.

Unknown tools must return controlled errors.

Missing tool arguments must return controlled errors.

Tool failures must be returned to Claude as tool errors rather
than crashing the application.

The final response will include:

- answer
- completed
- tool_calls_made
- input_tokens
- output_tokens
- stop_reason


## 19. Streamlit UI

The UI will run as a separate project and virtual environment.

Required screens/features:


### Ask the Credit Agent

User enters a free-text question.

Display:

- answer
- completion status
- tool calls
- token usage


### Search Knowledge Base

Retrieval without generation.

Display:

- title
- document id
- similarity score
- document text


### Streaming Borrower Summary

User selects a borrower.

The summary is displayed as text arrives.


### Covenant Stress-Test Workbench

This is the custom portfolio feature.

The analyst selects:

- borrower
- EBITDA downside scenario

Example slider:

0%
-5%
-10%
-15%
-20%
-25%
-30%


Display:

Current leverage
Stressed leverage
Covenant threshold
Headroom
Interest cover
Status


## 20. Future Watchlist Dashboard

Potential additional portfolio feature:

Borrower | Leverage | Headroom | Data Age | Status

This provides a portfolio-level view of deteriorating borrowers.


## 21. Testing Strategy

LLM and embedding calls must be mocked.

Core tests:

### API

- health endpoint
- borrower CRUD
- facility CRUD
- invalid Pydantic input
- unknown records


### LLM

- summary success
- timeout maps to 504
- rate limit maps to 429
- provider error maps to 502
- structured assessment validates


### RAG

- index builds
- relevant question retrieves expected source
- irrelevant question refuses
- refusal occurs before Claude is called


### Agent

- search tool executes
- covenant tool executes
- unknown tool handled
- missing tool arguments handled
- tool failure handled
- MAX_ITERATIONS stops an infinite tool loop


### Calculations

- net debt calculation
- leverage calculation
- interest cover calculation
- stress scenario calculation
- covenant breach calculation


## 22. Retrieval Evaluation

Create a small evaluation dataset.

Target:

25 questions


Each record should contain:

question
expected_document
expected_refusal


Metrics:

Top-1 retrieval accuracy
Top-3 retrieval accuracy
Correct refusal rate
False refusal rate


This evaluation will be used to justify the relevance floor.


## 23. Environment Variables

No secrets will be stored in source code.

Expected variables:

ANTHROPIC_API_KEY

VOYAGE_API_KEY

ANTHROPIC_MODEL

VOYAGE_EMBED_MODEL

RELEVANCE_FLOOR

MAX_AGENT_ITERATIONS

FINANCIAL_STALE_DAYS

CHROMA_PATH


## 24. Project Structure

credit-intelligence-platform/

    credit-intelligence-api/

        main.py
        config.py
        data.py
        models.py
        documents.py
        calculations.py
        llm.py
        knowledge_store.py
        agent.py

        routers/
            borrowers.py
            facilities.py
            covenants.py
            insights.py
            knowledge.py
            agent.py

        tests/
            test_borrowers.py
            test_calculations.py
            test_llm.py
            test_knowledge.py
            test_agent.py

        requirements.txt
        README.md


    credit-intelligence-ui/

        app.py
        api_client.py

        requirements.txt
        README.md


    docs/

        architecture.md
        evaluation.md


    PROJECT-PLAN.md
    DESIGN-NOTE.md
    README.md


## 25. Stretch Goals

Stretch goals will only be started after all core requirements pass.

Preferred order:

1. Retrieval evaluation dataset
2. Chroma metadata filtering
3. Document chunking where justified
4. Watchlist dashboard
5. Reranking
6. Docker
7. Authentication and rate limiting


## 26. Portfolio Demonstration

The final demo should show three different behaviours.


### Demo 1 - Agent uses knowledge search

Example:

"What does our lending policy say about highly leveraged borrowers
in cyclical sectors?"


### Demo 2 - Agent uses calculation tool

Example:

"Would Northbridge remain within its leverage covenant if EBITDA
fell by 20%?"


### Demo 3 - Correct refusal

Example:

"Give me a current credit assessment for a borrower whose latest
financial information is stale."


The system should refuse rather than pretending that stale evidence
is current.


## 27. Definition of Done

The project is complete when:

- the API runs from the README instructions
- the UI runs from the README instructions
- all CRUD endpoints work
- all provider errors are handled
- Claude summary works
- streaming works
- structured credit assessment works
- Chroma persists documents
- retrieval works
- grounded RAG works
- refusal works
- both agent tools work
- iteration limit works
- Streamlit contains all required features
- covenant stress testing works
- automated tests pass
- secrets are not committed
- requirements files are complete
- design note is complete
- demo scenarios work end to end