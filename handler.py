"""
Newsletter signup proxy for quiet asterisk.

Deploys as an AWS Lambda function (Python 3.12 runtime) sitting behind a
Function URL or API Gateway route. The homepage's newsletter form
(templates.newsletter_html in the main site generator) POSTs a plain
{"email": "..."} JSON body here. This function is the only thing that
ever holds the Resend secret key, and the only thing that ever calls
Resend — the static site never does either directly.

Deploy steps
------------
1. In Resend, create an Audience (Audiences -> Create Audience) and copy
   its Audience ID.
2. In Resend, create an API key (Settings -> API Keys) scoped to sending/
   contacts. Copy the key (starts with "re_").
3. Create this Lambda (Python 3.12, no extra dependencies/layers needed —
   this file only uses the standard library). Set these environment
   variables on the function:
       RESEND_API_KEY      = re_xxxxxxxxx        (secret — Lambda env only)
       RESEND_AUDIENCE_ID  = the audience ID from step 1
       ALLOWED_ORIGIN       = https://www.quietasterisk.com
   Handler: handler.lambda_handler
4. Enable a Function URL (Configuration -> Function URL -> Auth type NONE,
   since this endpoint is meant to be called from the public homepage) or
   put it behind API Gateway if you want throttling/WAF in front of it —
   recommended, since this endpoint currently has no rate limiting beyond
   whatever AWS gives you by default.
5. Copy the Function URL / API Gateway URL and set it as
   BLOG_NEWSLETTER_API_ENDPOINT before running generate_blog.py:
       export BLOG_NEWSLETTER_API_ENDPOINT="https://xxxx.lambda-url.us-east-1.on.aws/"
       python3 generate_blog.py

Not handled here (worth adding before high traffic):
- Rate limiting / bot protection beyond basic format validation — put API
  Gateway throttling, a WAF rule, or a honeypot field in front of this in
  production.
- Double opt-in / confirmation email. Resend Audiences will accept the
  contact immediately; if you want a confirm-your-email step, send that
  via Resend's transactional Send Email API right after the contact is
  added, and only mark them fully subscribed once they click through.
"""

import json
import os
import re
import urllib.request
import urllib.error

RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_AUDIENCE_ID = os.environ.get("RESEND_AUDIENCE_ID", "")
ALLOWED_ORIGIN = os.environ.get("ALLOWED_ORIGIN", "https://www.quietasterisk.com")

RESEND_API_URL = "https://api.resend.com/audiences/{audience_id}/contacts"

# Deliberately simple — good enough to reject garbage input before it ever
# reaches Resend. Not a full RFC 5322 validator; Resend itself will reject
# genuinely malformed addresses too.
_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _cors_headers():
    return {
        "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


def _response(status_code, body_dict):
    return {
        "statusCode": status_code,
        "headers": {**_cors_headers(), "Content-Type": "application/json"},
        "body": json.dumps(body_dict),
    }


def lambda_handler(event, context):
    """AWS Lambda entry point (Function URL / API Gateway HTTP API event)."""
    method = (
        event.get("requestContext", {}).get("http", {}).get("method")
        or event.get("httpMethod")
        or ""
    )

    # CORS preflight
    if method == "OPTIONS":
        return {"statusCode": 204, "headers": _cors_headers(), "body": ""}

    if method != "POST":
        return _response(405, {"error": "Method not allowed"})

    if not RESEND_API_KEY or not RESEND_AUDIENCE_ID:
        # Fails loud in the Lambda logs rather than silently accepting
        # signups that go nowhere.
        print("ERROR: RESEND_API_KEY / RESEND_AUDIENCE_ID not configured")
        return _response(500, {"error": "Newsletter signup is not configured yet"})

    try:
        payload = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"error": "Invalid request body"})

    email = (payload.get("email") or "").strip()
    if not email or not _EMAIL_RE.match(email):
        return _response(400, {"error": "Please enter a valid email address"})

    resend_request = urllib.request.Request(
        url=RESEND_API_URL.format(audience_id=RESEND_AUDIENCE_ID),
        method="POST",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        data=json.dumps({"email": email, "unsubscribed": False}).encode("utf-8"),
    )

    try:
        with urllib.request.urlopen(resend_request, timeout=8) as resp:
            resp.read()  # drain; we don't need Resend's response body
            return _response(200, {"ok": True})
    except urllib.error.HTTPError as e:
        # Resend returns 4xx for things like a malformed address it still
        # caught, or an audience/key mismatch. Don't leak Resend's error
        # detail (could include account info) back to the browser.
        detail = e.read().decode("utf-8", errors="ignore")
        print(f"Resend API error {e.code}: {detail}")
        if e.code == 422:
            return _response(400, {"error": "Please enter a valid email address"})
        return _response(502, {"error": "Newsletter signup failed — please try again"})
    except urllib.error.URLError as e:
        print(f"Resend API unreachable: {e}")
        return _response(502, {"error": "Newsletter signup failed — please try again"})
