"""Health & Wellness workflows and experimental SLPS configuration."""

HEALTH_ITEMS = [
    {
        "slug": "pm-jay", "code": "PM-JAY", "name": "Ayushman Bharat PM-JAY",
        "item_type": "Scheme", "slps_enabled": True, "weight": 1.2, "target_days": 7,
        "summary": "Prepare a beneficiary search and coverage guidance request.",
        "eligibility": "The official PM-JAY system checks the beneficiary database and applicable rules. AI Seva cannot confirm coverage or issue an e-card.",
        "documents": ["Accepted identity or family eligibility proof (use a redacted demo copy)"],
        "optional_documents": [],
        "official_url": "https://pmjay.gov.in/",
        "fields": ["state", "district", "family_reference", "identity_consent"],
        "steps": [
            {"title": "Applicant and family", "description": "Enter the applicant’s contact details and the state, district and non-sensitive family reference for the beneficiary search.", "fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "state", "district", "family_reference"]},
            {"title": "Official identity verification", "description": "Acknowledge that beneficiary search and e-KYC are completed on the official PM-JAY portal or at an authorised centre. AI Seva does not collect Aadhaar or OTPs.", "fields": ["identity_consent"]},
            {"title": "Household and review priority", "description": "Provide household details used by the experimental administrative SLPS. Any urgent request must be checked by an authorised officer.", "fields": ["category", "income", "dependents", "has_prior_benefit", "is_rural", "is_urgent", "urgent_reason"]},
            {"title": "Supporting document", "description": "Upload the listed redacted or sample proof for this AI Seva demo record.", "documents": True},
            {"title": "Review PM-JAY request", "description": "Review your beneficiary-search request. The official system must confirm eligibility and issue any card.", "review": True},
        ],
    },
    {
        "slug": "pmmvy", "code": "PMMVY", "name": "PM Matru Vandana Yojana",
        "item_type": "Scheme", "slps_enabled": True, "weight": 1.0, "target_days": 20,
        "summary": "Organise pregnancy, eligibility and instalment information for PMMVY guidance.",
        "eligibility": "Eligibility and benefit conditions depend on current PMMVY rules. Confirm them with the official portal or an authorised Anganwadi/ASHA worker.",
        "documents": ["MCP/RCHI pregnancy registration proof", "One applicable eligibility-category proof (redacted demo copy)"],
        "conditional_documents": {"later_instalment": ["Child birth registration proof (later instalment only)", "Child immunisation record (later instalment only)"]},
        "optional_documents": [],
        "official_url": "https://pmmvy.wcd.gov.in/",
        "fields": ["application_stage", "state", "district", "pregnancy_registration_date", "lmp_date", "anc_first_date", "anc_second_date", "child_order", "child_gender", "child_birth_date", "eligibility_basis", "health_facility", "bank_name", "bank_account_last4", "ifsc_code"],
        "stage_choices": [("pregnancy", "Pregnancy registration"), ("first_instalment", "First instalment"), ("later_instalment", "Later instalment / child details")],
        "default_stage": "pregnancy",
        "optional_fields": ["anc_first_date", "anc_second_date", "child_gender", "child_birth_date"],
        "stage_required_fields": {"later_instalment": ["child_gender", "child_birth_date"]},
        "steps": [
            {"title": "Mother and household profile", "description": "Enter the applicant’s contact details and the household information used for the administrative priority queue.", "fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "category", "income", "dependents", "has_prior_benefit", "is_rural", "is_urgent", "urgent_reason"]},
            {"title": "Pregnancy and eligibility", "description": "Enter pregnancy registration, LMP and ANC dates, child sequence, the applicable eligibility basis and health facility.", "fields": ["application_stage", "state", "district", "pregnancy_registration_date", "lmp_date", "anc_first_date", "anc_second_date", "child_order", "child_gender", "child_birth_date", "eligibility_basis", "health_facility"]},
            {"title": "Bank details for official process", "description": "Provide limited account details for preparation only. Do not enter a full account number, Aadhaar number, PIN or OTP.", "fields": ["bank_name", "bank_account_last4", "ifsc_code"]},
            {"title": "Pregnancy and instalment documents", "description": "Upload the pregnancy and eligibility proof. Child birth and immunisation proof is required only for the later-instalment stage.", "documents": True},
            {"title": "Review PMMVY request", "description": "Review your details before saving. Official authorities verify eligibility and process any benefit.", "review": True},
        ],
    },
    {
        "slug": "jsy", "code": "JSY", "name": "Janani Suraksha Yojana",
        "item_type": "Scheme", "slps_enabled": True, "weight": 1.1, "target_days": 15,
        "summary": "Prepare maternal registration and eligible-facility details for JSY assistance.",
        "eligibility": "Eligibility and assistance depend on state rules, category and delivery facility. An authorised health worker or facility confirms the current requirements.",
        "documents": ["MCP or pregnancy registration proof", "Applicable BPL / SC / ST eligibility proof (redacted demo copy)"],
        "conditional_documents": {"after_delivery": ["Delivery record from the health facility"]},
        "optional_documents": [],
        "official_url": "https://nhm.gov.in/nhm/index1.php?lang=1&level=3&lid=309&sublinkid=841",
        "fields": ["application_stage", "state", "district", "pregnancy_registration_date", "expected_delivery_date", "delivery_date", "jsy_eligibility_category", "health_facility", "facility_type", "bank_name", "bank_account_last4", "ifsc_code"],
        "stage_choices": [("pregnancy", "Pregnancy registration / before delivery"), ("after_delivery", "Delivery completed / benefit follow-up")],
        "default_stage": "pregnancy",
        "optional_fields": ["expected_delivery_date", "delivery_date"],
        "stage_required_fields": {"pregnancy": ["expected_delivery_date"], "after_delivery": ["delivery_date"]},
        "steps": [
            {"title": "Mother and household profile", "description": "Enter the applicant’s contact details and information used for administrative queue support.", "fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "category", "income", "dependents", "has_prior_benefit", "is_rural", "is_urgent", "urgent_reason"]},
            {"title": "Pregnancy registration and facility", "description": "Record pregnancy registration and the expected delivery date before delivery, or the actual delivery date for post-delivery follow-up. JSY processing involves ASHA/ANM staff and the health facility.", "fields": ["application_stage", "pregnancy_registration_date", "expected_delivery_date", "delivery_date", "health_facility", "facility_type", "state", "district"]},
            {"title": "Eligibility and bank information", "description": "Select the applicable BPL/SC/ST category and enter limited bank details for official-process preparation.", "fields": ["jsy_eligibility_category", "bank_name", "bank_account_last4", "ifsc_code"]},
            {"title": "Registration and delivery documents", "description": "Upload pregnancy and applicable eligibility proof. A delivery record is required only for post-delivery follow-up.", "documents": True},
            {"title": "Review JSY request", "description": "Review your request before saving. Health authorities verify eligibility, facility and delivery information.", "review": True},
        ],
    },
    {
        "slug": "abha", "code": "ABHA", "name": "ABHA ID Creation",
        "item_type": "Service", "slps_enabled": False,
        "summary": "Prepare basic details and guidance for creating an ABHA account through ABDM.",
        "eligibility": "Any individual can use the official ABHA service. Identity verification and account creation happen through ABDM.",
        "documents": [], "optional_documents": [],
        "official_url": "https://abha.abdm.gov.in/abha/v3",
        "fields": ["identity_method", "preferred_abha_address", "identity_consent"],
        "optional_fields": ["preferred_abha_address"],
        "steps": [
            {"title": "Account holder details", "description": "Enter the account holder’s name, date of birth and mobile number. AI Seva does not collect Aadhaar numbers or OTPs.", "fields": ["full_name", "date_of_birth", "mobile_number"]},
            {"title": "Identity method and consent", "description": "Choose an available identity method and acknowledge that authentication is completed securely on the official ABDM portal or at a participating facility.", "fields": ["identity_method", "identity_consent"]},
            {"title": "ABHA address preference", "description": "Optionally prepare a preferred ABHA address, then continue to the official service to create the account and card.", "fields": ["preferred_abha_address"]},
            {"title": "Review and continue", "description": "Review your guidance request. AI Seva does not create or issue the ABHA ID.", "review": True},
        ],
    },
    {
        "slug": "ayushman-card", "code": "AYUSHMAN-CARD", "name": "Ayushman Card Generation",
        "item_type": "Service", "slps_enabled": True, "weight": 1.2, "target_days": 7,
        "summary": "Prepare an Ayushman card guidance request for a person found eligible in PM-JAY.",
        "eligibility": "The official PM-JAY beneficiary system must find the person eligible and complete e-KYC before card generation.",
        "documents": ["Accepted identity or family beneficiary proof (redacted demo copy)"],
        "optional_documents": [],
        "official_url": "https://beneficiary.nha.gov.in/",
        "fields": ["state", "district", "family_reference", "identity_consent"],
        "steps": [
            {"title": "Beneficiary details", "description": "Enter the beneficiary name, date of birth, mobile number, state and district. The applicant must already be identified in the PM-JAY beneficiary records.", "fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "state", "district", "family_reference"]},
            {"title": "Family record and e-KYC", "description": "Provide a non-sensitive family reference and acknowledge that mobile OTP and e-KYC are completed only through the official PM-JAY portal or authorised centre.", "fields": ["identity_consent"]},
            {"title": "Administrative review priority", "description": "Provide the household factors used for the experimental officer-side queue. An officer must verify any urgency request.", "fields": ["category", "income", "dependents", "has_prior_benefit", "is_rural", "is_urgent", "urgent_reason"]},
            {"title": "Supporting proof", "description": "Upload a redacted or sample identity/family proof for this demo request.", "documents": True},
            {"title": "Review Ayushman card request", "description": "Review before saving. The official system, not AI Seva, verifies the beneficiary and generates the card.", "review": True},
        ],
    },
    {
        "slug": "e-sanjeevani", "code": "E-SANJEEVANI", "name": "eSanjeevani Online Doctor Consultation",
        "item_type": "Service", "slps_enabled": False,
        "summary": "Prepare for an online doctor consultation and continue to the official eSanjeevani patient portal.",
        "eligibility": "Citizens with access to a phone or computer and internet can use the official patient service, subject to its current availability.",
        "documents": [], "optional_documents": [],
        "official_url": "https://esanjeevaniopd.in/",
        "fields": ["state", "district", "health_concern", "consultation_type", "preferred_language"],
        "optional_fields": ["health_concern"],
        "steps": [
            {"title": "Patient details", "description": "Enter the patient name, age, mobile number and gender needed to prepare for registration.", "fields": ["full_name", "date_of_birth", "gender", "mobile_number"]},
            {"title": "Consultation request", "description": "Briefly note the concern you want to discuss and choose a consultation preference. Do not use this form for emergencies or include highly sensitive details.", "fields": ["state", "district", "health_concern", "consultation_type", "preferred_language"]},
            {"title": "Before your consultation", "description": "Keep previous prescriptions or reports ready if relevant. AI Seva does not collect medical files, triage symptoms, book a doctor or place you in the official queue.", "information": True},
            {"title": "Review and continue", "description": "Review your preparation details, then go to eSanjeevani to verify by mobile OTP, request a token and join the consultation queue.", "review": True},
        ],
    },
]

HEALTH_ITEMS_BY_SLUG = {item["slug"]: item for item in HEALTH_ITEMS}
HEALTH_ITEMS_BY_CODE = {item["code"]: item for item in HEALTH_ITEMS}
HEALTH_SLPS_CODES = {item["code"] for item in HEALTH_ITEMS if item["slps_enabled"]}


def seed_health_catalog():
    """Load the Health catalog into the shared scheme/recommendation tables."""
    from portal.models import Department, Scheme

    department, _ = Department.objects.update_or_create(
        code="HLT",
        defaults={
            "name": "Health & Wellness",
            "description": "Health coverage, maternal benefits and digital health services.",
            "level": "Central",
        },
    )
    for item in HEALTH_ITEMS:
        document_labels = list(item["documents"])
        for conditional_labels in item.get("conditional_documents", {}).values():
            document_labels.extend(label for label in conditional_labels if label not in document_labels)
        Scheme.objects.update_or_create(
            department=department,
            name=item["name"],
            defaults={
                "item_type": item["item_type"],
                "description": item["summary"],
                "official_link": item["official_url"],
                "required_documents": "\n".join(document_labels),
                "access_level": "Partial",
                "level": "Central",
                "is_active": True,
                "min_age": None,
                "max_age": None,
                "max_income": None,
                "allowed_categories": "",
                "allowed_occupations": "",
            },
        )
    return len(HEALTH_ITEMS)
