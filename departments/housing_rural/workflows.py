"""Service-specific guided application steps for Housing and Rural Development."""

COMMON_CONTACT = ["full_name", "mobile_number", "address"]
COMMON_LOCATION = ["state", "district", "block", "village"]
SCORING_FIELDS = ["annual_income", "dependents", "vulnerability", "is_urgent", "urgent_reason"]
DOCUMENT_FIELDS = ["income_document", "vulnerability_document", "household_document"]

HOUSING_PROCEDURES = {
    "pmay-gramin": [
        {"title": "Applicant details", "description": "Provide contact details for a PMAY-G/AwaasPlus guidance request.", "applicant_fields": COMMON_CONTACT},
        {"title": "Household and village", "description": "Identify the rural household and the Gram Panchayat area. Do not enter Aadhaar or OTP details here.", "detail_fields": COMMON_LOCATION + ["request_details"]},
        {"title": "Housing need and supporting records", "description": "Describe the housing condition and attach only relevant supporting records. Official AwaasPlus survey and e-KYC must be completed in the authorised process.", "detail_fields": ["housing_condition"] + SCORING_FIELDS + DOCUMENT_FIELDS},
        {"title": "Review PMAY-G request", "description": "Review the household details before saving this AI Seva guidance request.", "review": True},
    ],
    "nsap-pensions": [
        {"title": "Applicant and pension type", "description": "Enter applicant details and select the pension category for guidance.", "applicant_fields": COMMON_CONTACT + ["date_of_birth", "gender"], "detail_fields": ["nsap_pension_type"]},
        {"title": "Address and household circumstances", "description": "Add the location and approximate household circumstances. The local authority applies the relevant State/UT criteria.", "detail_fields": COMMON_LOCATION + ["request_details"] + SCORING_FIELDS},
        {"title": "Supporting records", "description": "Attach optional supporting records for this guidance request. Submit bank/payment details only through the official process.", "detail_fields": DOCUMENT_FIELDS},
        {"title": "Review pension guidance request", "description": "Check the pension category and contact details before saving.", "review": True},
    ],
    "day-nrlm": [
        {"title": "Contact details", "description": "Provide contact details so the local SHG or mission facilitator can be identified for guidance.", "applicant_fields": COMMON_CONTACT},
        {"title": "Village and household", "description": "Describe the location, household circumstances and any existing SHG connection.", "detail_fields": COMMON_LOCATION + ["request_details"] + SCORING_FIELDS},
        {"title": "Livelihood support", "description": "Share brief livelihood context and optional supporting records for referral. Joining and support are handled through community institutions.", "detail_fields": ["livelihood_hardship", "livelihood_details"] + DOCUMENT_FIELDS},
        {"title": "Review DAY-NRLM request", "description": "Review your contact and livelihood information before saving.", "review": True},
    ],
    "mgnrega-job-card": [
        {"title": "Adult household contact", "description": "Enter the adult household member’s contact details for a new rural household registration guidance request.", "applicant_fields": COMMON_CONTACT},
        {"title": "Household and Gram Panchayat", "description": "Provide the household location and names and ages of household members. Submit official registration to the Gram Panchayat.", "detail_fields": COMMON_LOCATION + ["household_members", "request_details"]},
        {"title": "Household circumstances", "description": "These optional details help officers triage the guidance request. They do not determine statutory eligibility.", "detail_fields": SCORING_FIELDS + DOCUMENT_FIELDS},
        {"title": "Review job card guidance request", "description": "Review the household list and Gram Panchayat location before saving.", "review": True},
    ],
    "pmay-urban-2": [
        {"title": "Applicant details", "description": "Provide contact details for PMAY-U 2.0 application guidance.", "applicant_fields": COMMON_CONTACT},
        {"title": "Urban location and vertical", "description": "Choose the PMAY-U 2.0 vertical and identify the concerned Urban Local Body area.", "detail_fields": ["pmay_vertical"] + COMMON_LOCATION + ["request_details"]},
        {"title": "Housing need and household", "description": "Describe the current housing condition and household circumstances for guidance. The ULB/State/UT/PLI verifies official eligibility.", "detail_fields": ["housing_condition"] + SCORING_FIELDS + DOCUMENT_FIELDS},
        {"title": "Review PMAY-U 2.0 request", "description": "Review your selected vertical and details before saving.", "review": True},
    ],
    "nsap-status-check": [
        {"title": "Applicant contact", "description": "Provide contact details for help checking an existing NSAP pension application.", "applicant_fields": COMMON_CONTACT},
        {"title": "Application reference and location", "description": "Enter the NSAP application number and local area. Complete any CAPTCHA only on the official NSAP tracker.", "detail_fields": ["nsap_application_number"] + COMMON_LOCATION + ["request_details"]},
        {"title": "Review status enquiry", "description": "Confirm the application reference before saving this guidance enquiry.", "review": True},
    ],
    "vbg-ramg-employment-demand": [
        {"title": "Worker contact", "description": "Provide contact details for follow-up on an employment demand already submitted through an official channel.", "applicant_fields": COMMON_CONTACT},
        {"title": "Card and demand reference", "description": "Provide your job card reference, the date of the official demand and the local area. AI Seva does not file the statutory demand.", "detail_fields": ["job_card_reference", "employment_demand_date"] + COMMON_LOCATION + ["request_details"]},
        {"title": "Review employment follow-up", "description": "Check the official demand date and reference before saving. The statutory timeline is handled separately from SLPS ranking.", "review": True},
    ],
}
