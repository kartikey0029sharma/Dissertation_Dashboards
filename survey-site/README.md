# Decision-Making with Business Intelligence Dashboards

Online instrument for an MSc Business Analytics dissertation (ISO8007), Newcastle University
Business School. A within-subjects vignette experiment on dashboard reliance, with an optional
written interview that runs straight after it.

| File | What it is |
|---|---|
| `index.html` | The instrument. Survey and written interview, in one self-contained page. |
| `admin.html` | Researcher page. Extract, upload and monitor. |
| `schema.js` | Every column name, question and rating statement. The single source of truth. |
| `config.js` | The only file you edit after deployment. Holds the Worker URL. |
| `worker/` | The Cloudflare Worker and the D1 schema. Not part of the website. |

## The design

Two factors, both fully within participant: **data signal** (a data quality notice shown or
suppressed) crossed with **accountability** (the decision reviewed against the system, or recorded
as the manager's own). Four cells, each seen twice, so eight vignettes per participant. Scenario is
rotated against condition by a Latin square across four versions, drawn at random on load, so
scenario is orthogonal to condition and can be entered in the model. Risk is not manipulated;
perceived stakes is measured after each vignette instead.

The written interview is twelve open questions, eight rating statements and a short background
block. Its consent page asks only the three things the survey's own consent did not already cover:
quotation, storage and retention, and not typing confidential material into free text.

**The study holds no personal data.** No name, no email address, no IP address. A participant who
wants the written interview later is shown their own reference and an address to write to, rather
than handing over contact details. Q10 is built automatically from the participant's own vignette record, naming the scenario,
what the dashboard indicated, what they knew locally and what they chose. In the emailed workbook
that line has to be filled in by hand for each person, and it is the item that makes the sampling
behavioural rather than convenience based.

## Running it on your own computer

Nothing to install, no account, no internet connection needed. You need Node.js;
`node --version` will tell you if you have it, and https://nodejs.org has it if you do not.

On Windows, double-click **`start-local.cmd`**. On anything else, run `node local-server.js`.

It prints where to go:

```
  Survey            http://localhost:8787/
  Researcher tools  http://localhost:8787/admin.html

  Endpoint to paste on the researcher page:  http://localhost:8787
  Admin key:                                 local-dev-key
```

One server hosts the pages and the API together, so `config.js` needs no editing: a page opened from
localhost talks to whatever is serving it. That also means nothing needs changing back when you go
live on Cloudflare.

Responses land in two files under `local-data/`, one JSON object per line. Open them in a text
editor to see exactly what was recorded. The folder is in `.gitignore`, so real responses can never
be committed to the public repository by accident, and the server refuses to serve those files over
HTTP even though they sit inside the folder it is hosting.

Set your own key with `ADMIN_KEY=something-long node local-server.js` if you prefer. The server
listens on localhost only, so nothing outside this computer can reach it.

**This is for rehearsing the study, not for collecting from real participants.** Nobody else can
open a localhost address on your machine. When you are ready for real collection, deploy the Worker
as below and paste its URL into `config.js`.

## Deploying

### 1. The store: Cloudflare Worker and D1

You need a free Cloudflare account and Node on your machine. Everything below runs from
`worker/`.

```
cd worker
npx wrangler login
npx wrangler d1 create dashboard-study --location=weur
```

The `--location=weur` hint keeps the database in western Europe. If you want a hard guarantee
rather than a hint, create it with `--jurisdiction=eu` instead. **A jurisdiction can only be set at
creation and can never be added afterwards**, so decide before you run the command.

Copy the `database_id` it prints into `wrangler.toml`, then:

```
npx wrangler d1 execute dashboard-study --remote --file=./schema.sql
npx wrangler secret put ADMIN_KEY
npx wrangler deploy
```

`wrangler secret put` prompts for a value. Use a long random string and keep a copy; it is what
protects the data from anyone who finds the Worker URL. It is stored encrypted by Cloudflare, and it
never appears in this repository.

`wrangler deploy` prints the Worker URL, ending in `.workers.dev`.

### 2. The pages: GitHub Pages

The repository is already published. Paste the Worker URL into `config.js`, with no trailing slash,
then commit and push. Pages republishes in about a minute.

```js
window.SURVEY_CONFIG = {
  endpoint: "https://dashboard-study.your-subdomain.workers.dev",
  email: "k.sharma7@newcastle.ac.uk"
};
```

### 3. Check it end to end

Complete the survey once, say yes to the interview, and choose to do it now. The final page should
say both parts have been received. Open `admin.html`, enter the Worker URL and the admin key, and
press **Check the connection**: one participant, eight rows, one interview. Then delete that test
participant before real collection begins:

```
npx wrangler d1 execute dashboard-study --remote --command "DELETE FROM survey WHERE response_id='RXXXXXX'; DELETE FROM interview WHERE response_id='RXXXXXX';"
```

## What a participant sees

1. Information sheet, consent with a select-all, two screening questions.
2. Eight situations, each a dashboard, a brief and a short question set.
3. Two manipulation checks and a suspicion probe.
4. Demographics, ending with the offer of the written interview.
5. If they accept, they choose **now** or **later**.
   - **Now**: the interview runs immediately, about fifteen more minutes.
   - **Later**: they are shown their reference and an address, and write in when it suits them.
     Nothing about them is stored.
6. Debrief, and a copy of their own data to download.

The survey is sent to the store **before** the interview begins, so a participant who starts the
interview and abandons it still leaves a complete survey record.

## Getting the data out

`admin.html` has four extract buttons. Each fetches the file and downloads it; the admin key travels
in an `X-Admin-Key` header and never appears in the address bar.

- **Survey** — one row per vignette.
- **Written interviews** — one row per participant.
- **Survey plus interviews** — the survey with each participant's interview answers repeated across
  their rows. This is the shape the analysis expects, and the same shape as the combined upload
  template.
**Check the connection** shows participant, row and interview counts, observations per design cell, and how many interviews arrived by each route. Watch the cell counts while collection
runs: a persistent gap means people are abandoning part way rather than that allocation has drifted.

## The analysis dashboard

**Generate the analysis dashboard** on `admin.html` pulls the survey and interview files and computes
the study's results in the browser. Nothing is sent anywhere: `analysis.js` carries its own statistics
and draws its own charts, so the page works offline once loaded and no participant data leaves the
machine. **Save it as an HTML file** writes the whole dashboard, styles included, to a single file you
can open later or attach to a supervision meeting.

Exclusions are applied before anything is computed, and the rule is stated on the first card so the
number is auditable: a participant is dropped if they failed an attention check or if their median
time per vignette falls under the threshold in the box (10 seconds by default — raise it and re-run to
see how sensitive the results are).

Nine cards, in the order the write-up needs them:

1. **The sample after exclusions** — analytic N, observations, overall over-reliance and accuracy,
   median time per vignette, and exactly who was excluded and why.
2. **Over-reliance by condition** — the marginal rates for each factor.
3. **The four design cells** — the 2×2 as grouped bars plus a table of cell means.
4. **Within-person effects, with 95% intervals** — the confirmatory tests. Each participant is their
   own control: their rate under one level minus their rate under the other, then a paired *t* on
   those differences. Reported as percentage points with a CI, *t*, df, *p* and Cohen's *dz*. H1
   (fault hidden vs visible), H2 (auditable vs own judgement), H1a (accuracy), H1b (asked for more
   before acting), and H3, the interaction, flagged as exploratory because the design is not powered
   for it.
5. **Confidence, and the options considered** — mean confidence by condition, and whether people
   narrowed their options when the dashboard was confident.
6. **By experience, descriptive only** — a breakdown by years of experience, not a moderation test.
7. **Design integrity** — the widest gap between the fullest and emptiest cell, and a scenario ×
   condition grid shaded by departure from the expected count. Allocation is balanced by
   construction, so a healthy grid reads flat grey; colour means people are dropping out part way, or
   a blank column means the rotation is not reaching a combination.
8. **Who took part** — sector, seniority, experience, formal dissent routes.
9. **The written interview strand** — the rating items with means and spread, and coding progress
   across the free-text questions.

The paired *t* is the honest small-sample test and is what the confirmatory claims rest on. A GEE
logistic model with participant clustering is the natural robustness check for the write-up; run that
in R or Python on the extracted CSV rather than in the browser.

## Uploading data collected offline

For responses that never reached the store, such as a file a participant emailed after a failed
send. Download one of the two templates, fill it, and upload. The uploader reads the header row and
works out which template you used.

- **Survey only**, 38 columns. Eight rows per participant sharing a `response_id`, `position` 1 to 8.
- **Survey plus written interview**, 85 columns. The same, followed by the interview columns. Repeat
  each participant's interview answers on every one of their rows, or fill them on the first row
  only. The first non-empty value per participant is taken.

Select one file or many. A single file may hold hundreds of participants: it is split into batches
of 400 rows automatically, with a progress bar, and a summary at the end. A 200-participant file is
1,600 rows and four batches.

Rows are keyed on `response_id` and `position`, so uploading the same file twice replaces those rows
rather than duplicating them. Fixing a typo and re-uploading the whole file is safe.

## Shape of the data

One survey row per vignette and one interview row per participant. Join on `response_id`.

Vignette level: `position`, `scenario`, `scenario_sector`, `data_signal`, `accountability`,
`choice_key`, `over_reliance`, `accuracy`, `confidence`, `perceived_stakes`, `verification_intent`,
`options_asked`, `options_generated`, `seconds_on_page`, `attn_shown`, `attn_correct`.

Participant level, repeated on every survey row: `response_id`, `version`, `use_frequency`, `role`,
`sector`, `experience`, `seniority`, `org_size`, `analytics_familiarity`, `dissent_route`,
`follow_up`, `attn_pass`, `attn_total`, `mc_immediate_correct`, `mc_count_response`,
`mc_count_correct`, `suspicion_pattern`, `suspicion_text`, `started`, `submitted`, `total_seconds`.

Interview: the three consent confirmations and their date, background, `Q1_text` to `Q12_text` plus the generated
`Q10_prompt`, `R1` to `R8`, and `blame_asymmetry_R5_minus_R4`, which is R5 minus R4 computed on the
server rather than trusted from the file. The coding columns (`behavioural_profile`,
`fault_detected`, `objection_raised`, `objection_recorded`, `objection_answered`, `outcome`,
`codes`) are left empty on collection and filled during analysis.

Suggested exclusions, to be stated in the methodology before the data is looked at: any participant
failing either attention check, and any participant whose median time on a vignette is implausibly
short.

## Things to settle before collection

**Where the data is held.** The GDPR Data Management Assessment in the ISO8007 guidelines asks you
to confirm that you will keep all data and documentation on the University server. Cloudflare is
not the University server. The defensible arrangement is to treat the Worker as a transient
collector, export to CSV regularly, hold the working dataset on University storage as the system of
record, and clear the D1 tables when collection closes. Say exactly that on the GDPR form and in the
methodology chapter.

**The design has changed since approval.** Section 1.6 of the guidelines says that a change of
research design after ethical approval may need further approval and a fresh look at GDPR. The
design has moved from 2×2×2 with four vignettes to 2×2 with eight, the interview has become an
asynchronous written form rather than a recorded call, and an email address is now collected. All
three need to be raised with the supervisor.

**Deception.** The ethics form asks whether the research deliberately misleads participants. It
does: the dashboards are built so that the screen can mislead. Make sure the submitted form says so
and justifies it, and that the debrief is what the approval expects.

**Anonymity.** The study collects no personal data at all: no name, no email address, and no IP
address, although Cloudflare makes one available on every request. Responses are anonymous rather
than pseudonymous, and the only link between a participant and their data is the reference they hold
themselves. That also means a withdrawal request has to quote the reference, because there is no
other way to find their rows.

## Notes on the Worker

`POST /submit` and `/interview` are open, because a public survey has no login. They
validate the shape of what arrives and cap the row count. `POST /import`, `GET /export` and
`GET /status` all require the admin key. Without it, `GET /` returns only that the endpoint is live.

`ALLOWED_ORIGIN` in `wrangler.toml` locks browser calls to the Pages site, so a copy of the
instrument hosted elsewhere cannot post into the dataset.

To change a column: edit `schema.js`, regenerate `worker/schema.sql`, apply the migration, and
redeploy. Nothing else hard-codes a column name.
