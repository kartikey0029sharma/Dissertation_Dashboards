-- D1 schema for the dashboard decision study.
-- Apply with:  npx wrangler d1 execute dashboard-study --remote --file=./schema.sql
-- Every column is TEXT. D1 is SQLite, so numbers stored as text still compare
-- and CAST cleanly, and it keeps the schema in step with the CSV columns.
--
-- There is no contacts table. The study collects no name, no email address and
-- no IP address, so it holds no personal data at all.

-- one row per vignette; a finished participant contributes eight
CREATE TABLE IF NOT EXISTS survey (
  data_status TEXT,
  response_id TEXT,
  version TEXT,
  position TEXT,
  scenario TEXT,
  scenario_sector TEXT,
  data_signal TEXT,
  accountability TEXT,
  choice_key TEXT,
  over_reliance TEXT,
  accuracy TEXT,
  confidence TEXT,
  perceived_stakes TEXT,
  verification_intent TEXT,
  options_asked TEXT,
  options_generated TEXT,
  seconds_on_page TEXT,
  attn_shown TEXT,
  attn_correct TEXT,
  use_frequency TEXT,
  role TEXT,
  sector TEXT,
  experience TEXT,
  seniority TEXT,
  org_size TEXT,
  analytics_familiarity TEXT,
  dissent_route TEXT,
  follow_up TEXT,
  attn_pass TEXT,
  attn_total TEXT,
  mc_immediate_correct TEXT,
  mc_count_response TEXT,
  mc_count_correct TEXT,
  suspicion_pattern TEXT,
  suspicion_text TEXT,
  started TEXT,
  submitted TEXT,
  total_seconds TEXT,
  PRIMARY KEY (response_id, position)
);

-- one row per written interview
CREATE TABLE IF NOT EXISTS interview (
  response_id TEXT,
  interview_mode TEXT,
  submitted_at TEXT,
  consent_quotes TEXT,
  consent_storage TEXT,
  consent_confidential TEXT,
  consent_date TEXT,
  country TEXT,
  iv_sector TEXT,
  job_title TEXT,
  level TEXT,
  years_experience TEXT,
  dashboard_frequency TEXT,
  people_responsible TEXT,
  stale_warning_shown TEXT,
  bi_training TEXT,
  age_band TEXT,
  qualification TEXT,
  Q1_text TEXT,
  Q2_text TEXT,
  Q3_text TEXT,
  Q4_text TEXT,
  Q5_text TEXT,
  Q6_text TEXT,
  Q7_text TEXT,
  Q8_text TEXT,
  Q9_text TEXT,
  Q10_prompt TEXT,
  Q10_text TEXT,
  Q11_text TEXT,
  Q12_text TEXT,
  R1 TEXT,
  R2 TEXT,
  R3 TEXT,
  R4 TEXT,
  R5 TEXT,
  R6 TEXT,
  R7 TEXT,
  R8 TEXT,
  blame_asymmetry_R5_minus_R4 TEXT,
  behavioural_profile TEXT,
  fault_detected TEXT,
  objection_raised TEXT,
  objection_recorded TEXT,
  objection_answered TEXT,
  outcome TEXT,
  codes TEXT,
  iv_total_seconds TEXT,
  PRIMARY KEY (response_id)
);

CREATE INDEX IF NOT EXISTS idx_survey_participant ON survey (response_id);
CREATE INDEX IF NOT EXISTS idx_survey_cell        ON survey (data_signal, accountability);
CREATE INDEX IF NOT EXISTS idx_interview_mode     ON interview (interview_mode);
