"""Housing and rural development guidance catalogue."""

HOUSING_ITEMS = [
    {
        "slug": "pmay-gramin", "name": "PMAY-Gramin",
        "full_name": "Pradhan Mantri Awaas Yojana – Gramin", "item_type": "Scheme",
        "summary": "Guidance on rural housing assistance and application preparation.",
        "description": "PMAY-G supports eligible rural households with housing assistance under government selection and verification processes.",
        "eligibility": "Selection depends on the current official rural housing list, program rules and local verification. This site cannot confirm eligibility.",
        "documents": ["Applicant and household details", "Current address and village", "Any records requested by the Gram Panchayat"],
        "workflow": ["Review the preparation checklist", "Submit an AI Seva guidance request", "Contact the Gram Panchayat or block office for official verification"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://pmayg.nic.in/",
    },
    {
        "slug": "nsap-pensions", "name": "NSAP Pensions",
        "full_name": "National Social Assistance Programme", "item_type": "Scheme",
        "summary": "Prepare to ask about old age, widow or disability pension assistance.",
        "description": "NSAP includes social assistance pension schemes administered through government processes and applicable state rules.",
        "eligibility": "Age, household circumstances, disability criteria and state implementation rules vary by pension. Confirm requirements with the local authority.",
        "documents": ["Applicant and contact details", "Current address and residence proof, if requested", "Supporting records for the pension category"],
        "workflow": ["Choose the pension category to ask about", "Submit an AI Seva guidance request", "Complete application and verification through the local authority"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://nsap.nic.in/",
    },
    {
        "slug": "day-nrlm", "name": "DAY-NRLM",
        "full_name": "Deendayal Antyodaya Yojana – National Rural Livelihoods Mission", "item_type": "Scheme",
        "summary": "Find guidance on rural livelihoods and women’s Self-Help Groups.",
        "description": "DAY-NRLM works through community institutions and Self-Help Groups to support rural livelihoods.",
        "eligibility": "Group formation, participation and available support are handled through local mission structures. Contact your block mission unit for current details.",
        "documents": ["Applicant contact details", "Village and block", "Existing Self-Help Group details, if applicable"],
        "workflow": ["Share your village and group details", "Submit an AI Seva guidance request", "Connect with the local Block Mission Management Unit"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://nrlm.gov.in/",
    },
    {
        "slug": "mgnrega-job-card", "name": "MGNREGA Job Card Request",
        "full_name": "Mahatma Gandhi National Rural Employment Guarantee Act", "item_type": "Service",
        "summary": "Prepare a household request for a rural job card and wage work.",
        "description": "Rural households may apply for a job card through the Gram Panchayat under MGNREGA. Work demand and job card processing are handled by the official local administration.",
        "eligibility": "The scheme applies to rural households whose adult members volunteer for unskilled manual work, subject to official registration and verification.",
        "documents": ["Household member names and ages", "Village and Gram Panchayat", "Photographs and residence details as requested by the Gram Panchayat"],
        "workflow": ["Enter household and village details", "Submit an AI Seva guidance request", "File or complete the official request with the Gram Panchayat"],
        "result": ["AI Seva tracking ID", "Request status"], "official_link": "https://nrega.nic.in/",
    },
]

HOUSING_ITEMS_BY_SLUG = {item["slug"]: item for item in HOUSING_ITEMS}
