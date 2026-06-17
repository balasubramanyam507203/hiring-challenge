import csv
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "companies.csv"
MOCK_FILE = BASE_DIR / "mocks" / "enrichment_responses.json"
OUTPUT_FILE = BASE_DIR / "output.csv"

THRESHOLD = 70


def role_rank(role):
    if not role:
        return 0

    role = role.lower()

    if "accounts payable" in role or "ap" == role:
        return 40
    if "owner" in role or "founder" in role or "president" in role:
        return 35
    if "cfo" in role or "finance" in role:
        return 30
    if "office manager" in role or "manager" in role:
        return 20
    if "registered agent" in role:
        return 15

    return 10


def normalize_name(name):
    if not name:
        return ""

    name = name.lower()
    name = name.replace("dr.", "").replace("dr ", "")
    name = name.replace("s.", "sean")
    name = name.replace("bob", "robert")
    name = name.replace("(manager)", "")
    return " ".join(name.split())


def score_company(company_data):
    registry = company_data.get("registry", {})
    listing = company_data.get("listing", {})
    enrichment = company_data.get("enrichment", {})

    score = 0
    reasons = []

    sources = []
    for provider_name, provider_data in company_data.items():
        if provider_data and provider_data.get("source_url"):
            sources.append(provider_data["source_url"])

    if registry:
        score += 25
        reasons.append("registry source present")

    if listing:
        score += 15
        reasons.append("listing source present")

    if enrichment:
        provider_confidence = enrichment.get("provider_confidence", 0)
        score += int(provider_confidence * 0.35)
        reasons.append(f"enrichment confidence {provider_confidence}")

    registry_name = normalize_name(registry.get("name"))
    listing_name = normalize_name(listing.get("name"))

    if registry_name and listing_name and registry_name == listing_name:
        score += 20
        reasons.append("registry and listing agree on contact name")

    enrichment_phone = enrichment.get("phone")
    listing_phone = listing.get("phone")

    if enrichment_phone and listing_phone and enrichment_phone == listing_phone:
        score += 15
        reasons.append("listing and enrichment agree on phone")

    role = registry.get("role") or ""
    score += role_rank(role)
    if role:
        reasons.append(f"role signal: {role}")

    return min(score, 100), reasons, sources


def choose_contact(company_data):
    registry = company_data.get("registry", {})
    listing = company_data.get("listing", {})
    enrichment = company_data.get("enrichment", {})

    name = registry.get("name") or listing.get("name") or ""
    role = registry.get("role") or ""

    email = enrichment.get("email") or ""
    phone = enrichment.get("phone") or listing.get("phone") or ""

    contact = email or phone

    return name, role, contact


def main():
    with open(MOCK_FILE, "r") as f:
        mock_data = json.load(f)

    rows = []

    with open(DATA_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            company_name = row["company_name"]
            mailing_address = row["mailing_address"]
            company_data = mock_data.get(company_name, {})

            confidence_score, reasons, sources = score_company(company_data)

            contact_name, contact_role, contact_email_or_phone = choose_contact(company_data)

            needs_human_review = confidence_score < THRESHOLD

            if needs_human_review:
                contact_email_or_phone = ""

            if not company_data:
                contact_name = ""
                contact_role = ""
                contact_email_or_phone = ""
                reasons = ["no mock provider data found"]
                sources = []

            rows.append(
                {
                    "company_name": company_name,
                    "mailing_address": mailing_address,
                    "contact_name": contact_name,
                    "contact_role": contact_role,
                    "contact_email_or_phone": contact_email_or_phone,
                    "confidence_score": confidence_score,
                    "needs_human_review": str(needs_human_review).lower(),
                    "provenance": " | ".join(sources),
                    "confidence_reason": "; ".join(reasons),
                }
            )

    with open(OUTPUT_FILE, "w", newline="") as f:
        fieldnames = [
            "company_name",
            "mailing_address",
            "contact_name",
            "contact_role",
            "contact_email_or_phone",
            "confidence_score",
            "needs_human_review",
            "provenance",
            "confidence_reason",
        ]

        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote results to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()