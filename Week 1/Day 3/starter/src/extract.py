"""Extract a monetary amount from a line of text, using a model.

LEARNER STARTER. SYNTHETIC PLACEHOLDER DATA ONLY.

This module currently does the naive thing. It runs. It is also untestable and
unsafe, in ways the three gates from Day 1 will only partly catch.
"""

from decimal import Decimal
import re
from pydantic import BaseModel, ValidationError, field_validator
from model_client import ModelClient 

class ModelRefused(Exception):
    """The model did not provide an answer."""


class ModelContractViolation(Exception):
    """The model returned an invalid answer."""

class ModelReply(BaseModel):
    amount: Decimal
    @field_validator("amount", mode="before")
    @classmethod
    def reject_float(cls, value: object) -> Decimal:
        if isinstance(value, float):
            raise ValueError("amount must be a string, not float")
        return value 
        

def extract_amount(line: str, client: ModelClient) -> Decimal:
    reply = client.complete(f"What is the amount in this line? {line}")
    _JSON_OBJECT = re.compile(r"\{.*\}", re.DOTALL)

    match = _JSON_OBJECT.search(reply)
    if match is None:
        raise ModelRefused(reply.strip()[:200])
    try:
        return ModelReply.model_validate_json(match.group(0)).amount
    except ValidationError as error:
        raise ModelContractViolation(str(error).splitlines()[0]) from error