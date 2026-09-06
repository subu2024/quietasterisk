# Newsletter signup proxy (Resend)

This is **not** part of the static site build — `generate_blog.py` never
imports or runs this. It's a separate, small backend that you deploy once
(AWS Lambda), so the homepage newsletter form has somewhere safe to submit
to. Full deploy steps are in the docstring at the top of `handler.py`.

## Why this exists

Resend's Audiences API needs a secret key on every request
(`Authorization: Bearer re_xxx`). A static site has no server to keep that
key secret — anything embedded in the page HTML/JS is visible to anyone
who opens dev tools. So the browser talks to this tiny proxy instead
(no secret involved, safe to expose its URL publicly), and the proxy —
which holds the real Resend key as a Lambda environment variable — talks
to Resend.

```
homepage form  --{ "email": "..." }-->  this Lambda  --Resend Audiences API-->  Resend
              (no secret needed)         (holds RESEND_API_KEY)
```

## Environment variables (set on the Lambda, nowhere else)

| Variable | Value |
|---|---|
| `RESEND_API_KEY` | Your Resend API key (`re_...`) — treat like a password |
| `RESEND_AUDIENCE_ID` | The Audience ID contacts get added to |
| `ALLOWED_ORIGIN` | `https://www.quietasterisk.com` (restricts which site can call this) |

## After deploying

Copy the Lambda's Function URL (or API Gateway URL) and set it as an
environment variable wherever you run the site generator:

```bash
export BLOG_NEWSLETTER_API_ENDPOINT="https://xxxxxxxx.lambda-url.us-east-1.on.aws/"
python3 generate_blog.py
```

If this isn't set, the homepage still builds — the newsletter section
just renders in a disabled state and the build log warns you.

## Testing without deploying

`handler.py` has no third-party dependencies, so you can exercise its
logic locally before deploying:

```python
import json, handler
event = {"requestContext": {"http": {"method": "POST"}},
         "body": json.dumps({"email": "test@example.com"})}
print(handler.lambda_handler(event, None))
```
