"""Item-specific citizen steps for Education scheme and service requests."""

EDUCATION_PROCEDURES = {
    "post-matric-scholarship": [
        {"title": "Student profile", "description": "Confirm the student’s identity and contact details.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address"]},
        {"title": "Scholarship category and income", "description": "Enter the category and annual family income used in scholarship screening. An officer verifies evidence before it affects SLPS.", "detail_fields": ["category", "annual_income"]},
        {"title": "Course and academic record", "description": "Add the institution, course, current year and previous academic result.", "detail_fields": ["course_name", "current_year", "institution_name", "previous_percentage"], "applicant_fields": ["purpose", "priority_group", "supporting_document"]},
        {"title": "Review and submit", "description": "Review the scholarship request details before saving your AI Seva record.", "review": True},
    ],
    "pm-vidyalaxmi": [
        {"title": "Student profile", "description": "Confirm the student’s identity and contact details.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "purpose"]},
        {"title": "Admission and course", "description": "Enter the institution and course information from the admission record.", "detail_fields": ["institution_name", "course_name", "admission_year", "course_duration"]},
        {"title": "Loan and family finances", "description": "Record the requested loan and fee information. The participating lender makes all credit decisions.", "detail_fields": ["annual_course_fee", "loan_amount_required", "annual_family_income", "bank_name"], "applicant_fields": ["priority_group", "supporting_document"]},
        {"title": "Admission documents", "description": "Attach available admission and fee documents for this AI Seva demo record.", "detail_fields": ["admission_letter", "fee_structure"]},
        {"title": "Review and submit", "description": "Review the information and selected files before saving.", "review": True},
    ],
    "nsp-student-registration": [
        {"title": "Student profile", "description": "Confirm the student’s identity and contact details.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "purpose"]},
        {"title": "Domicile and scholarship category", "description": "Enter domicile, category and annual family income details for the student profile.", "detail_fields": ["domicile_state", "category", "annual_family_income"], "applicant_fields": ["priority_group", "supporting_document"]},
        {"title": "Institution and course", "description": "Use the institution and course details for the academic year you are registering for.", "detail_fields": ["institution_name", "course_name", "academic_year"]},
        {"title": "Bank information", "description": "Enter limited bank details only. Never provide a PIN, password, OTP or complete account number.", "detail_fields": ["bank_name", "bank_account_last4", "ifsc_code"]},
        {"title": "Review and submit", "description": "Check the student profile before saving the assistance request.", "review": True},
    ],
    "abc-id-creation": [
        {"title": "Student profile", "description": "Confirm the student’s identity and contact details.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "purpose"]},
        {"title": "Institution and admission", "description": "Enter the admission identifiers shown on the institution’s records.", "detail_fields": ["institution_name", "admission_number", "admission_year", "registration_number"]},
        {"title": "Course and identity reference", "description": "Enter the course and a non-sensitive identity verification reference. Do not enter an Aadhaar number.", "detail_fields": ["course_name", "identity_reference"], "applicant_fields": ["priority_group", "supporting_document"]},
        {"title": "Review and submit", "description": "Review the academic identifiers before saving.", "review": True},
    ],
    "scholarship-status-document-verification": [
        {"title": "Student profile", "description": "Confirm the student’s identity and contact details.", "applicant_fields": ["full_name", "date_of_birth", "gender", "mobile_number", "address", "purpose"]},
        {"title": "Scholarship reference", "description": "Provide the scholarship name, academic year and application reference you want help with.", "detail_fields": ["scholarship_application_id", "scholarship_name", "academic_year"], "applicant_fields": ["priority_group", "supporting_document"]},
        {"title": "Document query", "description": "Select the document type and optionally attach a supporting file for this demo request.", "detail_fields": ["document_type", "document", "applicant_remarks"]},
        {"title": "Review and submit", "description": "Review the reference and document query before saving.", "review": True},
    ],
}
