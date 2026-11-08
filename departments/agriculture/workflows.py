"""Distinct step-by-step procedures for Agriculture scheme and service requests."""

AGRICULTURE_PROCEDURES = {
    "pm-kisan": [
        {"title": "Farmer details", "description": "Enter the applicant’s contact information for this PM-KISAN guidance request.", "applicant_fields": ["full_name", "mobile_number", "address"]},
        {"title": "Land record location", "description": "Identify the state, district, village and cultivated plot covered by the request.", "detail_fields": ["state", "district", "village", "survey_number", "land_area_acres"]},
        {"title": "Landholding and declaration", "description": "Choose the landholding type and acknowledge that official land records and exclusion rules determine eligibility.", "detail_fields": ["farmer_category", "eligibility_declaration"]},
        {"title": "Review PM-KISAN request", "description": "Check the farmer and land details before creating the AI Seva tracking record.", "review": True},
    ],
    "pmfby": [
        {"title": "Farmer details", "description": "Enter the applicant’s contact information for crop insurance guidance.", "applicant_fields": ["full_name", "mobile_number", "address"]},
        {"title": "Farm and insured crop", "description": "Identify the farm plot and the crop for which you want to check insurance enrollment.", "detail_fields": ["state", "district", "village", "survey_number", "land_area_acres", "crop_name"]},
        {"title": "Season and cultivation", "description": "Add sowing date and cultivation type, then confirm that you will check current crop, area and enrollment notifications.", "detail_fields": ["season", "sowing_date", "cultivator_type", "notified_crop_check"]},
        {"title": "Review crop insurance request", "description": "Review the crop, land and season information before saving.", "review": True},
    ],
    "kisan-credit-card": [
        {"title": "Farmer and contact details", "description": "Provide the applicant’s name, mobile number and address.", "applicant_fields": ["full_name", "mobile_number", "address"]},
        {"title": "Farm and activity profile", "description": "Describe the farm location, applicant type and agricultural or allied activity.", "detail_fields": ["state", "district", "village", "survey_number", "land_area_acres", "applicant_type", "farming_type", "crops_cultivated"]},
        {"title": "Credit requirement and bank", "description": "State the intended credit use and any existing agriculture loan, then select a preferred bank.", "detail_fields": ["credit_purpose", "has_existing_agri_loan", "existing_loan_details", "preferred_bank"]},
        {"title": "Review KCC request", "description": "Review the credit guidance details. The bank decides eligibility and any credit limit.", "review": True},
    ],
    "soil-health-card": [
        {"title": "Farmer details", "description": "Enter applicant contact information for soil testing guidance.", "applicant_fields": ["full_name", "mobile_number", "address"]},
        {"title": "Farm location", "description": "Identify the farm and plot where the soil sample is located.", "detail_fields": ["state", "district", "village", "survey_number", "land_area_acres", "soil_type"]},
        {"title": "Crop and sample plan", "description": "Name the current or planned crop and describe the sample location for coordination with the local authority.", "detail_fields": ["current_crop", "sample_location"]},
        {"title": "Review soil testing request", "description": "Review the farm and sample details before saving the assistance request.", "review": True},
    ],
    "enam-registration": [
        {"title": "Farmer profile", "description": "Enter the farmer’s contact and basic profile details for e-NAM onboarding guidance.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address"]},
        {"title": "Market and produce", "description": "Identify the farm location, preferred mandi/APMC and produce you plan to trade.", "detail_fields": ["state", "district", "village", "preferred_apmc", "produce"]},
        {"title": "Registration contact and bank", "description": "Add the email address and bank name requested for onboarding preparation. Do not enter a bank account number.", "detail_fields": ["email", "bank_name"]},
        {"title": "Review e-NAM request", "description": "Review the market and produce information before saving. Official onboarding and KYC happen through e-NAM and the selected APMC.", "review": True},
    ],
}
