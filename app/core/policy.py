"""What the counsellor says, and when it offers the office.

Plain Python so it can be tested without a model. The fee reply in
particular is a fixed string: if the model produced it, paraphrasing drift
would be invisible and untestable.
"""
from __future__ import annotations

import re
from enum import Enum

# The approved file-opening fee reply. Do not reword - there is a test that
# asserts this exact text.
FEE_RESPONSE = (
    "Our team will explain the file-opening process and the applicable "
    "service terms directly. I can help you understand your study options, "
    "assess your profile and prepare the next steps. Would you like me to "
    "arrange a consultation with our team?"
)

DOCUMENT_GUIDANCE = (
    "In general, most applications ask for some combination of: a passport, "
    "academic certificates and transcripts, an English test result where one "
    "is required, a CV where the programme asks for one, and a statement of "
    "purpose or research proposal for many postgraduate courses.\n\n"
    "The exact list changes by country, by university, by programme, by "
    "degree level and by which stage you are at - and admission documents, "
    "scholarship documents and visa documents are three different sets. "
    "Please treat this as a general idea rather than a checklist.\n\n"
    "For the real list for your university and stage, our counsellors put it "
    "together with you directly. Would you like me to arrange a consultation?"
)


class Intent(str, Enum):
    fee_question = "fee_question"
    contact_request = "contact_request"
    document_checklist = "document_checklist"
    admission_chance = "admission_chance"
    find_universities = "find_universities"
    general = "general"


_FEE = [
    r"\bfile[- ]?open(ing)?\b.{0,20}\b(fee|charge|cost|price|money|taka|tk)\b",
    r"\b(fee|charge|cost|price)\b.{0,25}\bfile\b",
    r"\byour\b.{0,15}\b(service|consultancy|agency)\b.{0,15}\b(fee|charge|cost)\b",
    r"\bhow much\b.{0,30}\b(you|nexted|your office)\b.{0,20}\b(charge|cost|fee)\b",
    r"কত\b.{0,20}\b(ফি|চার্জ|টাকা)\b",
]
_DOCS = [
    r"\b(full|complete|entire|whole|all)\b.{0,20}\b(document|checklist|papers?)\b",
    r"\b(document|paper)s?\b.{0,15}\b(checklist|list|required|need)\b",
    r"\bwhat documents\b",
]
_CHANCE = [
    r"\b(chance|chances|odds|probability|likelihood)\b",
    r"\bwill i (get|be) (in|admitted|accepted)\b",
    r"\bcan i get (in|into|admission)\b",
    r"\bam i (eligible|qualified)\b",
]
_CONTACT = [
    r"\b(where|what)\b.{0,20}\b(office|address|located|location)\b",
    r"\b(phone|contact|call|number|map|directions?)\b",
    r"\bvisit\b.{0,15}\b(office|you)\b",
]
_FIND = [
    r"\b(universit|college|program|programme|course)\w*\b",
    r"\b(suggest|recommend|shortlist|options)\b",
    r"\b(deadline|intake|scholarship|admission)\b",
]


def _any(patterns: list[str], text: str) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in patterns)


def classify_intent(message: str) -> Intent:
    """Narrow, must-not-improvise cases first."""
    if not message:
        return Intent.general
    if _any(_FEE, message):
        return Intent.fee_question
    if _any(_DOCS, message):
        return Intent.document_checklist
    if _any(_CHANCE, message):
        return Intent.admission_chance
    if _any(_CONTACT, message):
        return Intent.contact_request
    if _any(_FIND, message):
        return Intent.find_universities
    return Intent.general


_INVITATION = {
    Intent.admission_chance: (
        "I can tell you what a programme asks for, but a realistic read on "
        "your chances needs someone looking at your actual transcript. One of "
        "our counsellors can do that with you - would you like me to arrange "
        "a consultation?"
    ),
    Intent.contact_request: (
        "I would be glad to arrange a consultation for you."
    ),
}


def invitation_for(intent) -> str:
    """One invitation, only on a real trigger.

    Never appended to every message: students learn to skip it within three
    messages, and then the real invitations stop landing too. The fee and
    document replies already contain their own offer, so they get none here.
    """
    return _INVITATION.get(intent, "")
