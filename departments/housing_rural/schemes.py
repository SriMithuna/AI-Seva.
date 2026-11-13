"""Housing and rural development guidance catalogue."""

HOUSING_ITEMS = [
    {
        "slug": "pmay-gramin", "code": "PMAY-G", "name": "PMAY-Gramin",
        "full_name": "Pradhan Mantri Awaas Yojana – Gramin", "item_type": "Scheme",
        "slps_enabled": True, "importance_multiplier": 1.15,
        "summary": "Guidance on rural housing surveys, beneficiary lists and PMAY-G follow-up.",
        "description": "PMAY-G beneficiary identification follows official survey, verification, prioritisation and target-based selection. An AI Seva request does not place a household on the official list.",
        "eligibility": "The Gram Sabha and designated authorities verify household details and selection under the official guidelines. A self-survey is not a promise of sanction.",
        "documents": ["Household and village details for the official AwaasPlus survey", "Supporting records requested by the official survey or Gram Panchayat"],
        "workflow": ["Check the official PMAY-G/AwaasPlus channel for an open survey", "Complete the official self-survey or seek an authorised assisted survey; official e-KYC is completed only in AwaasPlus", "A designated Gram Panchayat surveyor corroborates a self-survey and higher authorities review it", "Gram Sabha and officials verify eligible lists; approved lists are processed in AwaasSoft against available targets", "Use the official PMAY-G ID and channel to track a sanction after selection"],
        "result": ["AI Seva tracking ID", "Official survey/list/sanction status only when checked through PMAY-G or the local authority"], "official_link": "https://pmayg.nic.in/",
    },
    {
        "slug": "nsap-pensions", "code": "NSAP", "name": "NSAP Pensions",
        "full_name": "National Social Assistance Programme", "item_type": "Scheme",
        "slps_enabled": True, "importance_multiplier": 1.20,
        "summary": "Prepare an application enquiry for an NSAP social assistance pension.",
        "description": "NSAP pensions are implemented by States and Union Territories. Local bodies help identify, receive and verify cases; state rules and designated authorities govern sanction and payment.",
        "eligibility": "Pension criteria differ by pension type and State/UT implementation. Confirm the current criteria and application route with the local designated authority.",
        "documents": ["Applicant details and current address", "Records requested by the local authority for the relevant pension category", "Bank/post-office payment details only through the official process"],
        "workflow": ["Ask the Gram Panchayat/Ward office or designated local authority which pension and state form apply", "Submit the application and supporting evidence through that official route", "Local officials verify the application and discuss eligibility through the applicable local process", "The State/UT competent authority sanctions eligible cases and arranges payment, commonly through DBT", "Use the NSAP application tracker with the NSAP application number for status"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://nsap.nic.in/",
    },
    {
        "slug": "day-nrlm", "code": "DAY-NRLM", "name": "DAY-NRLM",
        "full_name": "Deendayal Antyodaya Yojana – National Rural Livelihoods Mission", "item_type": "Scheme",
        "slps_enabled": True, "importance_multiplier": 1.00,
        "summary": "Connect with local Self-Help Groups and DAY-NRLM livelihood support.",
        "description": "DAY-NRLM organises support through women’s Self-Help Groups and their federations, with community-led livelihood, financial inclusion and capacity-building services.",
        "eligibility": "Joining, group formation and available support are handled through community institutions and State Rural Livelihood Missions; there is no single universal individual benefit application on this AI Seva form.",
        "documents": ["Village and contact details for referral", "Existing SHG name or member details, if applicable"],
        "workflow": ["Ask the village-level SHG/Community Resource Person or local mission facilitator about joining or forming an SHG", "The SHG organises regular meetings, savings and group processes under local mission guidance", "The SHG may connect members to village/block federations, capacity-building and livelihood support", "For an existing SHG or member record, contact the Block Mission Management Unit or State Rural Livelihood Mission"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://nrlm.gov.in/",
    },
    {
        "slug": "mgnrega-job-card", "code": "VB-G-RAM-G", "name": "VB-G RAM G Job Card Request",
        "full_name": "Viksit Bharat–Guarantee for Rozgar and Ajeevika Mission (Gramin)", "item_type": "Service",
        "slps_enabled": True, "importance_multiplier": 1.10,
        "summary": "Prepare a new rural household registration request for a Gramin Rozgar Guarantee Card.",
        "description": "From 1 July 2026, VB-G RAM G provides a 125-day annual wage-employment guarantee to eligible rural households whose adult members volunteer for unskilled manual work. AI Seva only prepares a guidance request; registration is completed through the official local process.",
        "eligibility": "Any rural household whose adult members volunteer for unskilled manual work may apply, subject to official registration and verification. Existing MGNREGA cards with completed e-KYC remain valid during the transition until new cards are issued.",
        "documents": ["Names and ages of household members", "Household address and Gram Panchayat", "Any additional records requested by the Gram Panchayat"],
        "workflow": ["An adult household member submits the household names, ages and address to the concerned Gram Panchayat", "The Gram Panchayat processes registration and issues the official Gramin Rozgar Guarantee Card under the applicable process", "After registration, adult members request employment separately through the Gram Panchayat, Programme Officer or an authorised person", "Keep the official card and employment-demand receipt/reference for tracking; employment-demand deadlines are handled in a separate follow-up process"],
        "result": ["AI Seva tracking ID", "Official card/registration status only when checked with the Gram Panchayat or designated official"], "official_link": "https://www.pib.gov.in/FaqDetails.aspx?ModuleId=4&NoteId=158511&lang=1&reg=3",
    },
    {
        "slug": "pmay-urban-2", "code": "PMAY-U2", "name": "PMAY-Urban 2.0",
        "full_name": "Pradhan Mantri Awas Yojana – Urban 2.0", "item_type": "Scheme",
        "slps_enabled": True, "importance_multiplier": 1.10,
        "summary": "Prepare a PMAY-U 2.0 application through the appropriate housing vertical.",
        "description": "PMAY-U 2.0 has four verticals: Beneficiary Led Construction, Affordable Housing in Partnership, Affordable Rental Housing and Interest Subsidy Scheme. The official portal, CSCs and Urban Local Bodies provide application routes.",
        "eligibility": "The applicable EWS/LIG/MIG, no-pucca-house and other vertical-specific conditions must be checked against current official rules. The ULB/State/UT/PLI verifies the application; AI Seva cannot confirm eligibility.",
        "documents": ["Applicant and household details for the official form", "Records required for the selected vertical; land proof may be required for BLC", "Identity and financial documents only through the official portal/CSC/ULB process"],
        "workflow": ["Choose the appropriate vertical with the official PMAY-U 2.0 guidance", "Apply through the Unified Web Portal, a Common Service Centre, or the concerned Urban Local Body/Municipality", "The responsible ULB/State/UT/PLI verifies eligibility and supporting records", "Follow the official portal for application, survey/geo-tagging where applicable, sanction or other next steps"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://pmaymis.gov.in/PMAYMIS2_2024/",
    },
    {
        "slug": "nsap-status-check", "code": "NSAP-STATUS", "name": "NSAP Pension Status Check",
        "full_name": "National Social Assistance Programme pension status enquiry", "item_type": "Service",
        "slps_enabled": False, "importance_multiplier": None,
        "summary": "Track an existing NSAP pension application by its application number.",
        "description": "The NSAP-MIS tracker reports status for an existing application. This enquiry is not a benefit application and does not use the normal SLPS score.",
        "eligibility": "Use the pension reference details requested by the official portal or local authority. AI Seva cannot retrieve live pension status.",
        "documents": ["NSAP application number", "Captcha entered only on the official tracker"],
        "workflow": ["Open the official NSAP application tracker", "Enter the NSAP application number and complete the on-page CAPTCHA", "For a missing/incorrect record, contact the local authority that accepted the pension application"],
        "result": ["AI Seva tracking ID for the guidance enquiry", "Official status only when checked on the NSAP-MIS tracker"], "official_link": "https://nsap.dord.gov.in/applicationTrack1.do?methodName=showStatus",
    },
    {
        "slug": "vbg-ramg-employment-demand", "code": "VB-G-EMPLOYMENT", "name": "VB-G RAM G Employment Demand Follow-up",
        "full_name": "Employment demand and statutory deadline follow-up", "item_type": "Service",
        "slps_enabled": False, "importance_multiplier": None,
        "summary": "Follow up an official demand for rural wage employment and its statutory timeline.",
        "description": "An adult rural worker may demand employment through the Gram Panchayat, Programme Officer or authorised person. Employment is due within 15 days; a missed deadline may give rise to unemployment allowance under the applicable process.",
        "eligibility": "This service is for households that have already submitted an official employment demand. AI Seva does not submit the statutory demand or determine allowance entitlement.",
        "documents": ["Job/Gramin Rozgar Guarantee Card or household reference", "Date and receipt/reference for the official employment demand"],
        "workflow": ["Submit the employment demand to the Gram Panchayat, Programme Officer or authorised person (oral, written Form 6, or an official digital route)", "Keep the date and acknowledgement/reference of the official demand", "If work is not provided within 15 days, contact the Programme Officer/Gram Panchayat about the statutory follow-up and any unemployment allowance process", "AI Seva records a guidance enquiry only; deadlines and entitlements are handled separately from SLPS"],
        "result": ["AI Seva tracking ID", "A verified statutory deadline is flagged for separate officer review"], "official_link": "https://www.pib.gov.in/FaqDetails.aspx?ModuleId=4&NoteId=158511&lang=1&reg=3",
    },
]

HOUSING_ITEMS_BY_SLUG = {item["slug"]: item for item in HOUSING_ITEMS}
HOUSING_ITEMS_BY_CODE = {item["code"]: item for item in HOUSING_ITEMS}
HOUSING_SLPS_CODES = {item["code"] for item in HOUSING_ITEMS if item["slps_enabled"]}
# Preserve recognition of application rows created before the act name was updated.
HOUSING_ITEMS_BY_CODE["JOB-CARD"] = HOUSING_ITEMS_BY_SLUG["mgnrega-job-card"]
HOUSING_SLPS_CODES.add("JOB-CARD")


def seed_housing_catalog():
    """Load this department's current guidance items into shared catalog tables."""
    from portal.models import Department, Scheme

    department, _ = Department.objects.update_or_create(
        code="HRD",
        defaults={
            "name": "Housing & Rural Development",
            "description": "Housing assistance and rural services guidance.",
            "level": "Central",
        },
    )
    # Keep prior rows for historical application references, but stop presenting
    # their superseded catalog labels as active choices.
    Scheme.objects.filter(
        department=department,
        name__in=["PMAY-Urban", "MGNREGA Job Card Request"],
    ).update(is_active=False)
    for item in HOUSING_ITEMS:
        Scheme.objects.update_or_create(
            department=department,
            name=item["name"],
            defaults={
                "item_type": item["item_type"],
                "description": item["description"],
                "official_link": item["official_link"],
                "required_documents": "\n".join(item["documents"]),
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
    return len(HOUSING_ITEMS)
