# PLAN.md 

Create a contact-finding pipeline that takes a CSV file containing the rows for `company_name` and `mailing_address` and, if it can verify and return the best reachable billing/payment contact. A verified "not found" or "needs human review" outcome is preferable to creating a precise-looking contact, so the system should be honest about doubt.


## Architecture

I would structure this as a small pipeline with Important stages:

1. **Input normalization**

   - Goal: Clean and standardize incoming CSV data
   - Read CSV rows
   - Remove extra spaces and formatting issues
   - Standardize addresses
   - Generate a unique row ID
   - Flag missing required fields

2. **Company identity resolution**

   - Goal: Know exactly with which company we are dealing with
   - Search available company sources
   - Match company name with address
   - Find their official website
   - resolve uncertainty
3. **Candidate Generation**
   
   - Goal: Gather every relevant contact.
   Possible Sources : 
   - Company website
   - Contact page
   - Billing page
   - Linkedin data
   - Public directories

   why ? Gather as much as you can, and then filter later

4. **Entity and contact matching**
   
   We have to check contacts actually belong to the company we are looking for

   Check : 
   - Domain of the email that matches company domain
   - Contact belongs to the resolved company
   - Address information matching
   - Candidate is not from some other company
   - Duplicate contacts gets merged

   why ? Many names and candidates may look similar but in reality they might belong to different companies
5. **Scoring and ranking**
   
   Goal: Select most likely billing contact
   - Assign scoring factors for each field

6. **Output with provenance**

   Goal: Make sure every result is traceable
   
   why ? Every field should be explainable and traceable to its source

7. **Human review queue**

   - Handle uncertain cases honestly
   - a wrong contact is worse than admitting uncertainity

## Sources & strategy
   
   No single source is enough, so I would combine source types with different strengths:

   - **Business registry / licensing sources** for legal names, owners, officers, and address validation.
   - **Company website / contact pages** for official phone numbers, emails, billing addresses, and staff pages
   - **Structured business directories** for location-level phone numbers, categories, and sometimes manager/owner names
   - **Professional profiles / public web mentions** for role fit when the company match is strong
   - **Email/domain match only as last option** and only when paired with strong identity evidence. I would not output guessed personal emails as verified contacts

   The plan is to first confirm the company's identity, then find credible contacts, and then confirm that a contact is a member of that corporation and suitable for payment outreach.
   
   Additionally, I would handle sources with varying degrees of trust. Compared to directories or inferred contact information, official corporate websites and business registrations would be seen as stronger evidence. Confidence rises when a contact is confirmed by several independent sources. Instead of speculating, I would return a lower-confidence answer or send the record for human review if the evidence is conflicting or still weak.
   
## Quality

### Dedupe

- Deduplicate company entities by normalized name, address, and any discovered domain or identifier.
- Deduplicate contacts by normalized name + email/phone/domain
- Merge evidence from multiple sources instead of creating multiple near-identical contacts.

### Confidence Scoring

Confidence should be explainable, not just numeric. I would start with a weighted score:

- Company/entity match: name, address, domain, and location agreement.
- Role fit: billing, finance, owner/operator, office manager, or executive responsibility.
- Contact reachability: direct email/phone beats generic contact form; generic business phone may be acceptable with lower confidence.
- Source reliability: official or registry source beats scraped directory data.
- Corroboration: independent sources agreeing increases confidence.
- Freshness: recent evidence beats stale records.

Scores should be caluclated against review outcomes once real data exists.

### Provenance

Every output value should trace back to evidence:

- which source produced it,
- which fields came from which source,
- when it was retrieved,
- why it was selected over alternatives,
- what evidence was insufficient when marked cannot verify.

For the user-facing CSV, provenance may be compact. For operators, I would keep a richer JSON audit record per row.

### Cannot-verify States

I would explicitly distinguish:

- no candidate found,
- company could not be confidently matched,
- contact found but role is unclear,
- contact found but source conflict exists,
- contact found but confidence is below the outreach threshold.

All of these should set `needs_human_review = true`.

### False-Positive Risk

False positives are more damaging than misses because they can create privacy, brand, and collection-risk issues. I would bias toward review when:

- the company name is common,
- the address points to a shared office, mailbox, or franchise location,
- only one weak source supports the contact,
- the contact appears tied to a different branch or legal entity,
- the contact is a personal profile without business-context confirmation.

## Privacy / compliance

I would:

- use allowed public, licensed and customer approved sources only
- store only the contact fields needed for payment outreach
- keep source provenance and timestamps for auditability,
- respect source terms, robots/usage constraints, and rate limits
- avoid emrichment that relies on sensitive personal data
- avoid guessing or generating personal emails without verification
- provide supression/deletion , if a contact opts out or is incorrect
- sperate internal audit evidence from the minimal outreach export.

I would not:

- scrape sources that prohibit it
- bypass access controls
- buy or use questionable data broker dumps without review
- output precise-looking contacts when evidence is weak
- use personal social data unless explicitly approved and relevant to business contactability


## Clarifying questions

### 1. What is the acceptable false-positive rate versus coverage target?

**Why it matters:** Payment outreach to the wrong person can damage trust and create compliance risk. The right threshold depends on whether human review is cheap or expensive.

**Default assumption:** Prefer precision over coverage. If uncertain, mark `needs_human_review = true`.

**What changes:** A higher coverage target would lower thresholds and send more borderline cases to outreach or review. A stricter false-positive target would require stronger corroboration and likely reduce automated match rates.

### 2. Which source categories are approved, licensed, or explicitly off-limits?

**Why it matters:** The architecture can support many adapters, but compliance and source terms determine which ones are usable in production.

**Default assumption:** Use only customer-approved, public, and licensed sources; no scraping behind logins, no terms-of-service workarounds, and no unverifiable data broker records.

**What changes:** Approved registries, directories, or enrichment providers would become first-class adapters with higher trust weights. Off-limits sources would be excluded even if they improve match rate.

### 3. Who exactly counts as the "right" decision-maker for this client?

**Why it matters:** Small businesses vary. The owner may be best for some accounts, while AP, office manager, controller, or branch manager may be better for others.

**Default assumption:** Rank billing/AP/finance roles highest, then owner/operator/executive, then office manager, then generic company contact when no named contact can be verified.

**What changes:** If the client wants only named finance contacts, generic phone/email outputs should be review-only. If owner outreach is preferred, owner/officer records from registries get higher role weight.
  