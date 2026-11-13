"""Labour, Skill & MSME catalogue with citizen-to-officer workflows."""

VISHWAKARMA_TRADES = [
    "Carpenter (Suthar/Badhai)", "Boat Maker", "Armourer", "Blacksmith (Lohar)",
    "Hammer and Tool Kit Maker", "Locksmith", "Goldsmith (Sonar)", "Potter (Kumhaar)",
    "Sculptor / Stone Carver / Stone Breaker", "Cobbler / Shoesmith / Footwear Artisan",
    "Mason (Rajmistri)", "Basket / Mat / Broom Maker / Coir Weaver",
    "Traditional Doll and Toy Maker", "Barber (Naai)", "Garland Maker (Malakaar)",
    "Washerman (Dhobi)", "Tailor (Darzi)", "Fishing Net Maker",
]

LABOUR_ITEMS = [
    {
        "slug": "pm-vishwakarma", "code": "PM-VISHWAKARMA", "name": "PM Vishwakarma Yojana", "item_type": "Scheme",
        "summary": "Artisan registration guidance for recognition, skills, toolkit support, credit and market linkage.",
        "purpose": "Supports traditional artisans and craftspeople working with hands and tools in 18 covered trades.",
        "eligibility": "The official scheme generally requires an artisan aged 18 or above, self-employed in an eligible trade on the registration date. Family, government-employment and prior-credit restrictions also apply. New-registration availability can depend on the current portal intake; confirm it with an authorised CSC / official portal before preparing to apply.",
        "documents": ["Trade and work details", "Family and occupation information", "Records requested by the official CSC / portal"],
        "workflow": ["Review the 18 eligible trades and confirm that new registration intake is currently open", "If intake is open, visit an authorised Common Service Centre (CSC); official enrolment uses Aadhaar-based biometric authentication on the official system", "The CSC submits the application on the PM Vishwakarma portal", "Gram Panchayat or Urban Local Body verifies trade, family and applicant details", "District Implementation Committee vets and recommends the application", "Screening Committee makes the registration approval decision", "Approved beneficiaries receive a certificate and ID card; skill assessment/training and applicable toolkit, credit and marketing supports follow under their separate conditions"],
        "result": ["Official registration decision", "Certificate and ID card if approved", "Next-step guidance for training and other eligible benefits"],
        "official_link": "https://pmvishwakarma.gov.in/", "form_fields": ["vishwakarma_trade", "traditional_trade_confirm", "years_in_trade"],
    },
    {
        "slug": "pm-svanidhi", "code": "PM-SVANIDHI", "name": "PM SVANidhi", "item_type": "Scheme",
        "summary": "Street-vendor application guidance for progressive collateral-free working-capital loans.",
        "purpose": "Supports eligible street vendors with progressive collateral-free working-capital loans (up to ₹15,000, ₹25,000 and ₹50,000 by tranche), digital adoption and related inclusion measures. The restructured lending period runs through 31 March 2030.",
        "eligibility": "Vendor identification and applicable documents are checked through the current scheme process. A Certificate of Vending / identity card, or a Letter of Recommendation route where applicable, may be used. The lending institution independently assesses and decides each loan.",
        "documents": ["Vendor activity and location details", "Certificate of Vending / vendor ID / Letter of Recommendation status as applicable", "Further KYC and bank details supplied only through the official portal, CSC/ULB or authorised lender"],
        "workflow": ["Check the current PM SVANidhi eligibility and application route", "Provide vendor details and applicable CoV / ID / LoR information through the official digital lending process or an authorised facilitator", "If required, the ULB identifies / verifies the vendor or processes the applicable LoR route", "The application is routed to the selected lending institution", "The lender performs its own checks and makes the loan decision", "Track application, disbursement and repayment through the official system; subsequent tranches depend on scheme rules and prior repayment"],
        "result": ["Official application reference and lender status", "Loan decision and disbursement only from the lending institution"],
        "official_link": "https://pmsvanidhi.mohua.gov.in/", "form_fields": ["vending_activity", "vending_location", "vendor_document_type", "vendor_document_reference"],
    },
    {
        "slug": "pmkvy", "code": "PMKVY", "name": "Pradhan Mantri Kaushal Vikas Yojana (PMKVY)", "item_type": "Scheme",
        "summary": "Explore PMKVY training pathways, counselling and certification through Skill India Digital.",
        "purpose": "PMKVY 4.0 includes Short-Term Training, Recognition of Prior Learning and Special Projects, subject to active programmes and approved batches.",
        "eligibility": "Course, pathway, candidate and batch requirements depend on the active programme. Confirm details on Skill India Digital Hub (SIDH) and with the selected training centre.",
        "documents": ["Candidate profile information requested by SIDH", "Course, job-role and preferred centre details", "Any records requested by the live programme"],
        "workflow": ["Browse active PMKVY pathways and counselling information", "Register or sign in to Skill India Digital Hub as a learner and complete its required profile/e-KYC on that official portal", "Choose the available PMKVY programme, course/job role and training centre", "Review batch availability and submit interest through SIDH", "The training centre reviews candidate interest; the candidate responds to an offer if approved", "The training centre completes enrolment; training, assessment and certification follow the selected pathway"],
        "result": ["AI Seva guidance tracking ID", "Official candidate and batch status remains on SIDH"],
        "official_link": "https://www.skillindiadigital.gov.in/home", "form_fields": ["pmkvy_pathway", "job_role", "sector", "training_district", "training_centre", "batch_ids"],
    },
    {
        "slug": "pmkvy-training-registration", "code": "PMKVY-TRAINING", "name": "PMKVY Skill Training Registration", "item_type": "Service",
        "summary": "Prepare course and batch preferences before submitting interest through Skill India Digital.",
        "purpose": "This is the candidate’s course/batch enrolment service under PMKVY, not a separate benefit scheme.",
        "eligibility": "Only active courses and batches shown in SIDH can be selected. Candidate e-KYC/profile requirements and final enrolment are handled in SIDH by the candidate and training centre.",
        "documents": ["SIDH learner profile and required official e-KYC", "Job role, sector, centre and batch preferences", "Further course-specific records requested by SIDH / training centre"],
        "workflow": ["Register or sign in on SIDH and complete its required profile/e-KYC there", "Find the relevant PMKVY programme and job role; check sector and batch details", "Select up to five available batch preferences and submit interest on SIDH", "The training centre reviews the request", "If approved, accept the invitation in SIDH; the centre completes batch enrolment", "Track the request in SIDH and follow the centre’s instructions for training"],
        "result": ["AI Seva guidance tracking ID", "Official interest, approval and enrolment status remains on SIDH"],
        "official_link": "https://www.skillindiadigital.gov.in/home", "form_fields": ["pmkvy_pathway", "job_role", "sector", "training_district", "training_centre", "batch_ids"],
    },
    {
        "slug": "samadhan-grievance", "code": "SAMADHAN", "name": "Labour Grievance Filing & Tracking (SAMADHAN)", "item_type": "Service",
        "summary": "Prepare for filing or tracking an employment-related dispute, claim or grievance.",
        "purpose": "The Ministry of Labour & Employment SAMADHAN portal supports industrial disputes, claims under applicable labour laws and general employment grievances.",
        "eligibility": "Who may file and which authority handles the matter depend on the selected dispute/claim type and applicable law. The official portal routes the matter to the relevant authority.",
        "documents": ["Worker and employer / establishment details", "Complaint category, facts and relief sought", "Relevant employment, wage or dispute records, if available"],
        "workflow": ["Register on the official SAMADHAN portal using the required name, mobile number and user type; verify the account there", "Start a new industrial dispute, claim or general complaint and select the applicable category", "Enter worker, employer, State/district, dispute facts and requested relief", "Attach relevant documents and submit, or save a draft if needed", "Use the official reference number to track the matter and respond to authority requests", "The competent labour authority handles conciliation, claim processing or other proceedings under applicable law"],
        "result": ["Official SAMADHAN reference and status", "Outcome determined by the competent labour authority"],
        "official_link": "https://samadhan.labour.gov.in/", "form_fields": ["labour_complaint_type", "employer_name", "employer_address", "employment_start_date", "employment_end_date", "claim_amount", "relief_sought", "supporting_document_1", "supporting_document_2"],
    },
    {
        "slug": "msme-delayed-payment", "code": "MSME-DELAYED-PAYMENT", "name": "MSME Delayed Payment Complaint Filing & Tracking", "item_type": "Service",
        "summary": "Prepare an eligible micro or small enterprise’s delayed-payment filing information.",
        "purpose": "The MSME Samadhaan / applicable MSME ODR process supports eligible micro and small enterprise suppliers seeking action on delayed payments.",
        "eligibility": "The supplier generally needs valid Udyam registration as a micro or small enterprise. Under MSMED Act payment rules, an agreed payment period cannot exceed 45 days; where there is no written agreement, the appointed-day rules apply. Check the contract, acceptance date and current official requirements; the competent MSEFC / process determines the case.",
        "documents": ["Udyam registration details", "Buyer details and purchase/work order or agreement", "Invoice, delivery / service evidence, payment terms and outstanding amount", "Other evidence requested by the official filing portal"],
        "workflow": ["Check that the supplier and transaction meet the current micro/small enterprise requirements", "Create or access an account on the official MSME filing portal and provide enterprise details; use the official Udyam-linked information", "Enter buyer, contract/order, invoice, delivery/service and outstanding-payment particulars", "Upload supporting evidence and submit the delayed-payment application", "The official system routes it to the relevant MSEFC / applicable ODR process", "The Council/process manages dispute resolution, including conciliation and, where applicable, arbitration; track status on the official portal"],
        "result": ["Official filing reference and council / ODR status", "Dispute outcome determined by the competent MSEFC / process"],
        "official_link": "https://samadhaan.msme.gov.in/", "form_fields": ["enterprise_name", "udyam_number", "buyer_name", "buyer_address", "purchase_order_reference", "invoice_number", "invoice_date", "payment_due_date", "outstanding_amount", "economic_impact", "supporting_document_1", "supporting_document_2"],
    },
]

LABOUR_ITEMS_BY_SLUG = {item["slug"]: item for item in LABOUR_ITEMS}
LABOUR_ITEMS_BY_CODE = {item["code"]: item for item in LABOUR_ITEMS}


def seed_labour_catalog():
    from portal.models import Department, Scheme

    department, _ = Department.objects.update_or_create(
        code="LSM",
        defaults={"name": "Labour, Skill & MSME", "description": "Labour, skill development and MSME schemes and services.", "level": "Central"},
    )
    Scheme.objects.filter(
        department=department,
        name__in=["PM Kaushal Vikas Yojana", "e-Shram Registration", "Udyam Registration"],
    ).update(is_active=False)
    for item in LABOUR_ITEMS:
        Scheme.objects.update_or_create(
            department=department, name=item["name"],
            defaults={
                "item_type": item["item_type"], "description": item["purpose"],
                "official_link": item["official_link"], "required_documents": "\n".join(item["documents"]),
                "access_level": "Partial", "level": "Central", "is_active": True,
                "min_age": None, "max_age": None, "max_income": None,
                "allowed_categories": "", "allowed_occupations": "",
            },
        )
    return len(LABOUR_ITEMS)
