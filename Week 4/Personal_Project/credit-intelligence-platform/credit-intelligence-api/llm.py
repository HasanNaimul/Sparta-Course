import anthropic
from anthropic import APIStatusError, APITimeoutError, RateLimitError

from config import settings
from models import CreditAssessment


client = anthropic.Anthropic(api_key=settings.anthropic_api_key, timeout=30.0, max_retries=3)


SYSTEM_PROMPT = (
    "You are a corporate credit analyst writing for an institutional audience. "
    "Use British English. Use only the borrower information supplied to you. "
    "Never invent financial figures, covenant positions or credit facts. "
    "Clearly distinguish observed facts from interpretation. "
    "You may recommend maintain, review or escalate, but you must never approve or reject lending."
)


def build_borrower_prompt(borrower: dict, metrics: dict) -> str:
    return (
        f"Borrower: {borrower['name']}\n"
        f"Sector: {borrower['sector']}\n"
        f"Country: {borrower['country']}\n"
        f"Internal risk band: {borrower['internal_risk_band']}\n"
        f"Revenue: £{borrower['revenue_m']}m\n"
        f"EBITDA: £{borrower['ebitda_m']}m\n"
        f"Total debt: £{borrower['total_debt_m']}m\n"
        f"Cash: £{borrower['cash_m']}m\n"
        f"Interest expense: £{borrower['interest_expense_m']}m\n"
        f"Net debt: £{metrics['net_debt_m']}m\n"
        f"Net leverage: {metrics['current_net_leverage']}x\n"
        f"Interest cover: {metrics['current_interest_cover']}x\n"
        f"Last financials: {borrower['last_financials_date']}\n"
        f"Watchlist: {borrower['watchlist']}"
    )


def summarise_borrower(borrower: dict, metrics: dict) -> dict:
    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=400,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": f"Summarise this borrower in two short paragraphs.\n\n{build_borrower_prompt(borrower, metrics)}"}],
    )

    return {
        "summary": response.content[0].text,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
    }


def stream_borrower_summary(borrower: dict, metrics: dict):
    prompt = f"Summarise this borrower in two short paragraphs.\n\n{build_borrower_prompt(borrower, metrics)}"

    with client.messages.stream(model=settings.anthropic_model, max_tokens=400, system=SYSTEM_PROMPT, messages=[{"role": "user", "content": prompt}]) as stream:
        for text in stream.text_stream:
            yield text


def analyse_borrower(borrower: dict, metrics: dict) -> dict:
    prompt = f"Assess this borrower using only the supplied information.\n\n{build_borrower_prompt(borrower, metrics)}"

    response = client.messages.parse(
        model=settings.anthropic_model,
        max_tokens=600,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
        output_format=CreditAssessment,
    )

    return {
        "analysis": response.content[0].parsed_output,
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "stop_reason": response.stop_reason,
    }