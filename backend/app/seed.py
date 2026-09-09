from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import Clinician, Medication, Patient, Visit


# A small RxNorm reference catalog (normalized ingredient concepts). Real
# RxCUIs and attributes. Strength and dose form are not stored — this is the
# set of ingredient concepts that visit-note mentions should be matched against.
MEDICATIONS = [
    ("6809", "metformin", "IN", "Glucophage", "Biguanide antidiabetic"),
    ("29046", "lisinopril", "IN", "Prinivil,Zestril", "ACE inhibitor"),
    ("83367", "atorvastatin", "IN", "Lipitor", "Statin"),
    ("17767", "amlodipine", "IN", "Norvasc", "Calcium channel blocker"),
    ("5487", "hydrochlorothiazide", "IN", "Microzide", "Thiazide diuretic"),
    ("7646", "omeprazole", "IN", "Prilosec", "Proton pump inhibitor"),
    ("10582", "levothyroxine", "IN", "Synthroid,Levoxyl", "Thyroid hormone"),
    ("6918", "metoprolol", "IN", "Lopressor,Toprol XL", "Beta blocker"),
    ("435", "albuterol", "IN", "Ventolin,ProAir", "Short-acting beta agonist"),
    ("25480", "gabapentin", "IN", "Neurontin", "Anticonvulsant"),
    ("36437", "sertraline", "IN", "Zoloft", "SSRI antidepressant"),
    ("5640", "ibuprofen", "IN", "Advil,Motrin", "NSAID"),
    ("161", "acetaminophen", "IN", "Tylenol", "Analgesic / antipyretic"),
    ("1191", "aspirin", "IN", "Bayer,Ecotrin", "NSAID / antiplatelet"),
    ("723", "amoxicillin", "IN", "Amoxil", "Penicillin antibiotic"),
    ("11289", "warfarin", "IN", "Coumadin,Jantoven", "Anticoagulant"),
    ("4603", "furosemide", "IN", "Lasix", "Loop diuretic"),
    ("8640", "prednisone", "IN", "Deltasone", "Corticosteroid"),
    ("52175", "losartan", "IN", "Cozaar", "Angiotensin receptor blocker"),
    ("36567", "simvastatin", "IN", "Zocor", "Statin"),
]


def seed_database(db: Session) -> dict[str, int]:
    db.query(Visit).delete()
    db.query(Patient).delete()
    db.query(Clinician).delete()

    # Medications are deliberately NOT wiped. The catalog can be built up from
    # RxNav (POST /api/medications/import), and reloading demo patients should
    # not throw that away. Only the demo concepts the seeded notes rely on are
    # inserted, and only when missing.
    existing = {rxcui for (rxcui,) in db.query(Medication.rxcui).all()}
    db.add_all(
        Medication(
            rxcui=rxcui,
            name=name,
            tty=tty,
            synonym=None,
            brand_names=brand_names,
            drug_class=drug_class,
        )
        for rxcui, name, tty, brand_names, drug_class in MEDICATIONS
        if rxcui not in existing
    )

    clinicians = [
        Clinician(
            id=str(uuid4()),
            name="Dr. Sarah Chen",
            email="sarah.chen@clinic.com",
            specialty="Internal Medicine",
        ),
        Clinician(
            id=str(uuid4()),
            name="Dr. Michael Roberts",
            email="michael.roberts@clinic.com",
            specialty="Family Medicine",
        ),
        Clinician(
            id=str(uuid4()),
            name="Dr. Emily Watson",
            email="emily.watson@clinic.com",
            specialty="Geriatrics",
        ),
    ]
    db.add_all(clinicians)
    db.flush()

    patients = [
        Patient(
            id=str(uuid4()),
            name="John Smith",
            dob="1965-03-15",
            mrn="MRN001",
            assigned_clinician_id=clinicians[0].id,
        ),
        Patient(
            id=str(uuid4()),
            name="Mary Johnson",
            dob="1978-07-22",
            mrn="MRN002",
            assigned_clinician_id=clinicians[0].id,
        ),
        Patient(
            id=str(uuid4()),
            name="Robert Williams",
            dob="1952-11-08",
            mrn="MRN003",
            assigned_clinician_id=clinicians[0].id,
        ),
        Patient(
            id=str(uuid4()),
            name="Patricia Brown",
            dob="1989-01-30",
            mrn="MRN004",
            assigned_clinician_id=clinicians[1].id,
        ),
        Patient(
            id=str(uuid4()),
            name="James Davis",
            dob="1971-09-14",
            mrn="MRN005",
            assigned_clinician_id=clinicians[1].id,
        ),
        Patient(
            id=str(uuid4()),
            name="Linda Miller",
            dob="1945-05-20",
            mrn="MRN006",
            assigned_clinician_id=clinicians[2].id,
        ),
        Patient(
            id=str(uuid4()),
            name="William Wilson",
            dob="1938-12-03",
            mrn="MRN007",
            assigned_clinician_id=clinicians[2].id,
        ),
        Patient(
            id=str(uuid4()),
            name="Elizabeth Moore",
            dob="1942-08-17",
            mrn="MRN008",
            assigned_clinician_id=clinicians[2].id,
        ),
    ]
    db.add_all(patients)
    db.flush()

    # Notes mix exact names, brand names, shorthand (HCTZ, ASA, APAP, MTX),
    # misspellings, and — for the form/dosage stretch — some strengths and forms.
    visits = [
        Visit(
            id=str(uuid4()),
            patient_id=patients[0].id,
            clinician_id=clinicians[0].id,
            visit_date="2026-01-15",
            chief_complaint="Annual physical exam",
            notes=(
                "Patient reports feeling well. Blood pressure 128/82. "
                "Continue metformin 500 mg tablets for type 2 diabetes and "
                "lisinopril 10 mg daily for hypertension. Discussed diet and "
                "exercise."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[0].id,
            clinician_id=clinicians[0].id,
            visit_date="2026-02-01",
            chief_complaint="Follow-up for hypertension",
            notes=(
                "Blood pressure improved to 122/78. Started atorvastatn for "
                "elevated cholesterol. Patient also takes ASA 81 mg daily for "
                "cardioprotection."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[1].id,
            clinician_id=clinicians[0].id,
            visit_date="2026-01-20",
            chief_complaint="Persistent cough",
            notes=(
                "Cough for 2 weeks, no fever. Lungs clear. Prescribed "
                "amoxicillin. Advised Tylenol as needed for discomfort and "
                "a Ventolin inhaler for wheezing. Plenty of fluids."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[2].id,
            clinician_id=clinicians[0].id,
            visit_date="2026-01-28",
            chief_complaint="Diabetes management",
            notes=(
                "HbA1c 7.2%. Continue Glucophage 1000 mg; patient compliant "
                "with diet. Also on lisinapril and HCTZ 25 mg for blood pressure."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[3].id,
            clinician_id=clinicians[1].id,
            visit_date="2026-01-18",
            chief_complaint="New patient visit",
            notes=(
                "Established care. Complete history obtained. Reports "
                "occasional heartburn, takes omeprazol 20 mg OTC. No acute "
                "concerns."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[3].id,
            clinician_id=clinicians[1].id,
            visit_date="2026-02-03",
            chief_complaint="Anxiety symptoms",
            notes=(
                "Reports increased stress at work. Started Zoloft. Discussed "
                "coping strategies and will follow up in 4 weeks."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[4].id,
            clinician_id=clinicians[1].id,
            visit_date="2026-01-25",
            chief_complaint="Back pain",
            notes=(
                "Lower back pain for 1 week after lifting. No radicular "
                "symptoms. Advised Advil as needed and rest."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[5].id,
            clinician_id=clinicians[2].id,
            visit_date="2026-01-10",
            chief_complaint="Memory concerns",
            notes=(
                "Daughter concerned about forgetfulness. MMSE 26/30. Current "
                "medications include Synthroid, amlodipine, and gabapentn for "
                "neuropathy."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[5].id,
            clinician_id=clinicians[2].id,
            visit_date="2026-01-31",
            chief_complaint="Medication review",
            notes=(
                "Reviewed regimen. Continues Coumadin 5 mg with stable INR; "
                "also on Lasix 40 mg and metoprolol. No interactions identified."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[6].id,
            clinician_id=clinicians[2].id,
            visit_date="2026-01-22",
            chief_complaint="Fall risk assessment",
            notes=(
                "Mild unsteadiness noted. On furosemide and HCTZ — reviewed "
                "orthostatic risk. Uses APAP for arthritis pain. Recommended "
                "physical therapy."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[7].id,
            clinician_id=clinicians[2].id,
            visit_date="2026-01-29",
            chief_complaint="Chronic pain management",
            notes=(
                "Arthritis pain well controlled on MTX weekly with folic acid "
                "supplement. Continue current regimen. Patient satisfied."
            ),
        ),
        Visit(
            id=str(uuid4()),
            patient_id=patients[7].id,
            clinician_id=clinicians[2].id,
            visit_date="2026-02-04",
            chief_complaint="Follow-up visit",
            notes=(
                "Routine follow-up. Vitals stable. Refilled levothyroxine and "
                "simvastatin. No new concerns."
            ),
        ),
    ]
    db.add_all(visits)
    db.commit()

    return {
        "clinicians": len(clinicians),
        "patients": len(patients),
        "visits": len(visits),
        # Catalog size, not the number of rows inserted — the demo concepts are
        # only added when missing, and an imported catalog is left intact.
        "medications": db.query(Medication).count(),
    }
