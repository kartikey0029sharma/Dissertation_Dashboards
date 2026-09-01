/* ============================================================================
   Study configuration. This is the ONLY file you edit after deployment.

   endpoint  The base URL of the store, with no trailing slash. The instrument
             appends /submit, /interview and /contact to it; the researcher page
             appends /status, /export and /import.

             Leave it empty and the study still runs, but nothing is stored:
             each participant is asked to download their file and email it.

   email     Where a participant should send their file if sending fails, and
             where they are told to write if they want their data removed.

   RUNNING LOCALLY. When the page is opened from localhost, the endpoint below
   is ignored and the page talks to whatever server is hosting it. That is what
   `node local-server.js` sets up: one port serving both the pages and the API.
   So this file needs no editing to test locally, and no editing back before
   going live.

   This file is public, because GitHub Pages serves it to every visitor. The
   admin key is NEVER in here. It lives only as a server secret and is typed
   into the researcher page when needed.
   ========================================================================= */
(function () {
  var LOCAL = /^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname);

  window.SURVEY_CONFIG = {
    /* Paste the deployed Worker URL here when you go live. */
    endpoint: LOCAL ? location.origin : "",
    email: "k.sharma7@newcastle.ac.uk",
    running_locally: LOCAL
  };
})();
