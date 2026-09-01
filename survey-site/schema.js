/* ============================================================================
   Column definitions for the whole study. This file is the single source of
   truth: the instrument builds its CSV from it, the researcher page builds the
   upload templates and validates uploads against it, and the Worker uses the
   same names as its D1 column names.

   If you add a column, add it here and nowhere else, then run the migration
   noted in worker/schema.sql.
   ========================================================================= */
(function (root) {

  /* --- one row per vignette. A participant who finishes contributes 8. ---- */
  var SURVEY_COLS = [
    'data_status', 'response_id', 'version', 'position', 'scenario', 'scenario_sector',
    'data_signal', 'accountability', 'choice_key', 'over_reliance', 'accuracy', 'confidence',
    'perceived_stakes', 'verification_intent', 'options_asked', 'options_generated',
    'seconds_on_page', 'attn_shown', 'attn_correct', 'use_frequency', 'role', 'sector',
    'experience', 'seniority', 'org_size', 'analytics_familiarity', 'dissent_route',
    'follow_up', 'attn_pass', 'attn_total', 'mc_immediate_correct', 'mc_count_response',
    'mc_count_correct', 'suspicion_pattern', 'suspicion_text', 'started', 'submitted',
    'total_seconds'
  ];

  /* --- one row per written interview, joined to the survey on response_id --- */
  var INTERVIEW_COLS = [
    'response_id', 'interview_mode', 'submitted_at',
    /* consent: only what the survey's own consent did not already cover */
    'consent_quotes', 'consent_storage', 'consent_confidential', 'consent_date',
    /* background */
    'country', 'iv_sector', 'job_title', 'level', 'years_experience',
    'dashboard_frequency', 'people_responsible', 'stale_warning_shown', 'bi_training',
    'age_band', 'qualification',
    /* the twelve open questions */
    'Q1_text', 'Q2_text', 'Q3_text', 'Q4_text', 'Q5_text', 'Q6_text',
    'Q7_text', 'Q8_text', 'Q9_text', 'Q10_prompt', 'Q10_text', 'Q11_text', 'Q12_text',
    /* the eight rating statements and the derived asymmetry score */
    'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'blame_asymmetry_R5_minus_R4',
    /* filled by the researcher during coding, blank on collection */
    'behavioural_profile', 'fault_detected', 'objection_raised', 'objection_recorded',
    'objection_answered', 'outcome', 'codes',
    'iv_total_seconds'
  ];

  /* No CONTACT_COLS. The study collects no email address and no name, so there
     is no personal data to isolate. A participant who wants the interview later
     is given the researcher's address and their own reference, and writes in.
     That keeps the information sheet's promise of anonymity literally true. */

  /* --- the two upload templates the researcher page offers ---------------- */
  var TEMPLATES = {
    survey: {
      name: 'survey',
      label: 'Survey only',
      file: 'template_survey.csv',
      cols: SURVEY_COLS,
      note: 'One row per vignette. Eight rows per participant, all sharing a response_id.'
    },
    combined: {
      name: 'combined',
      label: 'Survey plus written interview',
      file: 'template_survey_interview.csv',
      /* interview values repeat on each of that participant's survey rows, the
         same way the demographics already do. The importer takes the first
         non-empty value per response_id. */
      cols: SURVEY_COLS.concat(INTERVIEW_COLS.filter(function (c) { return c !== 'response_id'; })),
      note: 'Survey columns followed by the interview columns. Repeat the interview values on each of that participant\'s rows, or fill them on the first row only.'
    }
  };

  /* --- the eight rating statements, used by the instrument and the docs ---- */
  var RATINGS = [
    ['R1', 'When a dashboard figure conflicts with what I know from the ground, I usually go with the dashboard.'],
    ['R2', 'I can tell from the screen alone whether the data behind it is current.'],
    ['R3', 'In my organisation, a decision backed by a report is easier to defend than one backed by personal judgement.'],
    ['R4', 'If I follow the dashboard and the decision turns out badly, I am personally held responsible.'],
    ['R5', 'If I overrule the dashboard and the decision turns out badly, I am personally held responsible.'],
    ['R6', 'When someone disagrees with what a report shows, that disagreement gets recorded somewhere.'],
    ['R7', 'Someone has to formally answer a raised concern before the decision goes ahead.'],
    ['R8', 'Working from dashboards narrows the range of options my team considers.']
  ];

  /* --- what the written interview adds to the consent already given -------
     The survey's own consent already covers taking part, stopping at any time,
     and anonymised aggregate reporting. Repeating those here would be noise, so
     only the three things the interview genuinely adds are asked. -------- */
  var IV_CONSENT = [
    'I agree that short quotations from my answers may be used, in anonymised form, in the dissertation and in any publication arising from it.',
    'I agree that my answers may be stored securely until the retention date and deleted after that, and I understand that I may withdraw them before then by emailing the researcher with my reference.',
    'I confirm that I will not type any confidential, client or commercially sensitive information into my answers.'
  ];

  /* --- the twelve open questions, with the guidance shown under each ------- */
  var IV_QUESTIONS = [
    ['Q1_text', 'To begin, please tell me about the dashboards or reports you use in a typical week. Which ones do you open most often, and what is the first thing you look at when one opens?',
      'Name the screens and say what your eye goes to first. Two or three sentences is enough.'],
    ['Q2_text', 'Please walk me through one recent decision that started from a dashboard. What did the screen show, what did you notice first, and what did you check before you decided?',
      'Please pick a real decision you remember well and describe it in order: what you were deciding, what the screen showed, what you checked, what you decided. Four to six sentences.'],
    ['Q3_text', 'How do you know whether the numbers in front of you are current and complete? What would make you doubt them?',
      'Please also say whether your tools display any warning when a feed has failed or the data is stale, and what you do when you see one. If they display nothing, please say so plainly.'],
    ['Q4_text', 'Has a dashboard ever told you something you did not believe? Please describe that occasion and say what you did about it.',
      'One specific occasion is worth more than a general answer. Please say what the screen showed, why you doubted it, and what action you took, if any.'],
    ['Q5_text', 'Staying with that same occasion: what happened after you raised it? Who responded, was your objection written down anywhere, and what was the outcome in the end?',
      'This question is about what the organisation did with your objection, not about the decision itself. If nothing happened, please say so. "It went nowhere" is a useful answer, not a failed one.'],
    ['Q6_text', 'When a decision is questioned later in your organisation, what kind of evidence carries weight? Is a decision backed by a report easier to defend than one backed by your own reading of the situation?',
      'Please answer both parts, and give an example if one comes to mind.'],
    ['Q7_text', 'Think about the two ways a decision can go wrong. If you follow the dashboard and the outcome is bad, what happens to you? If you overrule the dashboard and the outcome is bad, what happens to you? Are the two the same?',
      'Please answer for how things actually work where you are, not how they are supposed to work.'],
    ['Q8_text', 'Think of a time a colleague closer to the ground, a site manager or a front line analyst, disagreed with what a report showed. Where did that disagreement go? Was it recorded anywhere?',
      'Please say who raised it, who heard it, whether anyone wrote it down, and what happened in the end.'],
    ['Q9_text', 'When you work from a dashboard, does it change the range of options you consider? Which options never make it on to the table?',
      'Please give an example of an option that would not get discussed because the screen does not show it or has not costed it.'],
    ['Q10_text', null,   /* the stem is built from this participant's own record */
      'Please answer as honestly as you can. There is no right answer here, and the scenarios were written to be difficult on purpose.'],
    ['Q11_text', 'What would have to be true, in the tool, in the process, or in the culture, for people to push back on a dashboard more often?',
      'Please be specific. Naming one change that would actually work is more useful than a long list.'],
    ['Q12_text', 'Is there anything important about this that I have not asked?',
      'Anything at all. If nothing comes to mind, please write "nothing further".']
  ];

  root.STUDY_SCHEMA = {
    SURVEY_COLS: SURVEY_COLS,
    INTERVIEW_COLS: INTERVIEW_COLS,
    TEMPLATES: TEMPLATES,
    RATINGS: RATINGS,
    IV_CONSENT: IV_CONSENT,
    IV_QUESTIONS: IV_QUESTIONS
  };

  /* so the Worker and the test harness can require this file directly */
  if (typeof module !== 'undefined' && module.exports) module.exports = root.STUDY_SCHEMA;

})(typeof window !== 'undefined' ? window : globalThis);
