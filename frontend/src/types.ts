export interface Clinician {
  id: string;
  name: string;
  email: string;
  specialty: string;
}

export interface Patient {
  id: string;
  name: string;
  dob: string;
  mrn: string;
  assigned_clinician_id: string;
}

export interface Visit {
  id: string;
  patient_id: string;
  clinician_id: string;
  visit_date: string;
  chief_complaint: string;
  notes: string;
  created_at: string;
  updated_at: string;
  clinician_name?: string;
  clinician_specialty?: string;
  patient_name?: string;
  patient_dob?: string;
  patient_mrn?: string;
}

export interface Medication {
  rxcui: string;
  name: string;
  tty: string;
  synonym: string | null;
  brand_names: string[];
  drug_class: string | null;
  source: string;
}

export interface ImportJob {
  state: "idle" | "running" | "done" | "error";
  phase: string;
  processed: number;
  total: number;
  concepts: number;
  created: number;
  updated: number;
  error: string | null;
  started_at: string | null;
  finished_at: string | null;
}

export interface ScrapeResult {
  name: string;
  status: "created" | "updated" | "not_found";
  rxcui: string | null;
}

export interface ScrapeSummary {
  created: number;
  updated: number;
  not_found: number;
  results: ScrapeResult[];
}

export type MatchType =
  | "exact"
  | "brand"
  | "synonym"
  | "misspelling"
  | "shorthand"
  | "unknown";

export interface MedicationMention {
  text: string;
  start: number;
  end: number;
  matched: boolean;
  match_type: MatchType;
  correction: string | null;
  confidence: number | null;
  medication: Medication | null;
  strength?: string | null;
  dose_form?: string | null;
  product_rxcui?: string | null;
  product_name?: string | null;
}

export interface NoteAnalysis {
  visit_id: string;
  note: string;
  mentions: MedicationMention[];
  implemented: boolean;
}

export interface Wound {
  id: string;
  patient_id: string;
  clinician_id: string;
  location: string;
  wound_type: string;
  description: string;
  image_data: string | null;
  status: string;
  version: number;
  created_at: string;
  updated_at: string;
}

export interface WoundAssessment {
  id: string;
  wound_id: string;
  clinician_id: string;
  length_cm: number;
  width_cm: number;
  depth_cm: number;
  tissue_type: string;
  exudate_amount: string;
  healing_stage: string;
  push_score: number;
  ai_generated: boolean;
  notes: string;
  created_at: string;
}

export interface AIJob {
  id: string;
  wound_id: string;
  job_type: string;
  status: string;
  result: Record<string, unknown> | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}
