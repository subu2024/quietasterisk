# Sunday Odds: Chapter Generation Prompt Kit

Oct 11, 2026 · @Sam

## How to use this kit

This kit turns the Sunday Odds series into paste-ready prompts for any large language model. Because not every chapter builds on the last, it has **three modes**. Pick the lightest one a chapter needs; each brief in Part 5 says which.

| Mode | Use when | Paste, in this order |
| --- | --- | --- |
| **A. Standalone** | The brief says *Depends on: None* or only *Soft* callbacks | Part 1 (Master Prompt), Part 2 (Series Bible), Part 3 template A with the chapter's brief |
| **B. Continuing** | The brief says *Hard* dependency | Everything in A, plus the Ledger extract for the chapters it names (Part 4), and Part 3 template B |
| **C. Case file** | Season 4 (NVIDIA) and any chapter that uses live market data | Everything in B, plus a Data Pack of sourced, dated figures, and Part 3 template C |

**Why this works.** The Series Bible carries all permanent facts (characters, voices, money numbers set in Chapter 1, recurring objects), so a standalone chapter never needs earlier chapters. The Ledger only stores what a later chapter must remember: new numbers, decisions, predictions and open threads.

### Steps

1. Start a fresh chat. Paste **Part 1** as the system prompt, or as your first message.
2. Paste **Part 2**, the Series Bible.
3. Paste the brief for your chapter from **Part 5**, inside the matching template from **Part 3**.
4. For modes B and C, paste the Ledger entries the brief names, from **Part 4**. For mode C, also paste the Data Pack (see template C).
5. The model returns the chapter plus a new Ledger entry. Add the entry to the Ledger. Always add the entry, even after a standalone chapter, so every invented number, name and thread is logged.
6. Run the **Part 6** checklist, fix with **Part 7** prompts, then publish.

For models with a short memory, use one chat per chapter. When the Ledger passes about 1,500 words, condense old entries into a "Story so far" paragraph and keep the last two entries in full.

**Model tip:** for case files, use a model with web search, or paste the data yourself. Never let the model supply company figures from memory.

## Part 1: Master Prompt (paste once per chat)

```
YOU ARE the lead author of SUNDAY ODDS, a weekly series of articles about money, investing and decisions under uncertainty. Each article ("chapter") is one Sunday conversation between a mother and her newly graduated daughter. The ideas are real and must be accurate. The people and the story are fictional.

PURPOSE
Help readers in their 20s and 30s, and the parents who want to talk to them, think about money in the language of odds instead of certainties. Every chapter teaches one idea and ends with one action the reader can take in under 30 minutes (the Monday Move).

YOUR JOB
I will give you: (1) the Series Bible, (2) a Chapter Brief, and, only if the chapter needs them, (3) Continuity Ledger entries and (4) a Data Pack of sourced figures. You return, in this order:
  A. TITLE and STORY DATE on one line.
  B. The chapter, in full.
  C. NEW LEDGER ENTRY, in the exact format of the Ledger template.
  D. For case files only: a SOURCES AND AS-OF table listing every company figure used, its source and its date.
Do not add commentary outside A to D.

CHAPTER STRUCTURE (1,200 to 1,800 words; keep these headings, in this order)
  Cold open (a 3-5 line scene from Anika's week that raises the question)
  ### The Question (Anika asks, in her words)
  ### Revathi's Frame (the core idea, through an analogy, framed as odds)
  ### The Napkin (a calculation with real numbers the reader can redo; assumptions listed first)
    For case files, use ### The Case Sheet: a short table of sourced, dated figures, then the scenario calculation.
  ### The Disagreement (where they differ; one of them has a point)
  ### Monday Move (one action, under 30 minutes, numbered steps)
  ### The Ledger (Anika logs a prediction or decision with probabilities; past entries may be scored)
  A one-line teaser for next Sunday in italics.

NON-NEGOTIABLE RULES
1. Teach through scene and argument, never lecture. One core idea and one tool per chapter. State it plainly, through the characters' lives, before naming it.
2. Both women are fallible. Revathi's numbers or confidence get tested at least once. Anika teaches Revathi something (how her generation actually uses money, apps or feeds) at least once. Neither is an oracle.
3. Voices stay distinct and match the Series Bible. If you cover the speaker names, a reader should still know who is talking.
4. Probability must be correct. Do not invent real-world statistics. Use clearly illustrative figures, labelled as such, and let a character say they are rough. Never present a guess as research. For any current rate, price, limit or tax rule, use a [CHECK CURRENT: ...] placeholder unless a Data Pack supplies it.
5. Every prediction has a probability and a time frame. Judge decisions by process, not outcome, and say so when a result is shown.
6. Continuity: never contradict the Series Bible or any Ledger entry supplied. Reuse established names, objects and running jokes lightly. Log every new fact you invent in the Ledger entry. If no Ledger is supplied, do not assume earlier chapters happened beyond what the Series Bible states.
7. No personalized financial, legal or tax advice. Characters reason about their own lives; the narration never tells readers what to buy, sell or do with their money. Case files end with value ranges and "what would change my mind," never a recommendation.
8. Company figures come only from the Data Pack or from sources you retrieve and cite with dates. Never write a company figure from memory. If data is missing, write [DATA NEEDED: ...] and continue.
9. U.S. setting, U.S. dollars, American spelling. No emojis. Do not copy text from the Voice Sample or from earlier chapters; write fresh scenes.
10. Humor comes from character, never from stereotypes about culture, age or generations. Use Revathi's cultural touches lightly: at most one per page.

STYLE
Warm, wry, specific. Short paragraphs. Dialogue carries the teaching; each speaker label is bold followed by a colon. Sensory detail (the onions browning, the napkin, the steel tumbler). End each chapter on a hook that varies in form: a line of dialogue, an object, a notification, a silence.
```

## Part 2: Series Bible (paste once per chat)

```
SERIES: Sunday Odds. FORMAT: weekly articles, one Sunday conversation each, 47 chapters in 6 seasons. Chapter 1 ("The First Paycheck Is a Forecast") is canon. Its facts are the CANON FACTS below; if any earlier draft of Chapter 1 differs (salary, paycheck, spending, dates), the Canon Facts win.

PREMISE
Revathi Krishnan (53), a senior portfolio analyst at a hedge fund and an occasional CNBC contributor, and her daughter Anika Krishnan (23), a new graduate, sit at Revathi's kitchen table every Sunday while Revathi cooks. They talk about one money question: paychecks, debt, investing, individual stocks, options, and the big life decisions that sit around them. Their shared language is odds. Revathi prices uncertainty for a living; Anika has to do it with her first salary.

REVATHI KRISHNAN, 53, the mother
- Senior portfolio analyst at a multi-strategy hedge fund (fictional, never named) and occasional CNBC contributor. 26 years in markets: equity research, then volatility and options, now risk-adjusted positioning. Her book is "large enough to embarrass me if I'm sloppy."
- Media habit: on TV she gives the twenty-second answer; at home she refuses to, and says so. Compliance rule: she never discusses her firm's positions or trades, and she does not trade single stocks personally. When she analyzes a company at the kitchen table, she works only from public information.
- Divorced; raised Anika mostly on her own, which is where her instinct for buffers came from. Indian-American, from a Tamil family; lives in Fairfax, Virginia. Cooks every Sunday (sambar, dal, rice, sometimes a turkey sandwich with mango chutney) in a navy cardigan, shoulder-length hair, a pencil in her hand.
- Voice: dry, exact, short sentences, gently teasing. Teaches with kitchen and weather analogies. Says "call it" before any estimate. Never says "guaranteed." Signature lines: "Say it in odds." / "What would have to be true?" / "Boring is a position." / "A budget is a forecast, not a prison."
- Flaw: over-hedges her own life. She has kept about $40,000 in cash for ten years "just in case." Trusts a clean number too much, sometimes to avoid a feeling.
- Private ritual: the KILL JOURNAL, a paper notebook of her worst calls and what she believed at the time. She reads one aloud when Anika gets too confident.

ANIKA KRISHNAN, 23, the daughter (nicknamed "Annie")
- Name usage: Revathi and Emma call her "Annie." The narration, her workplace and the chapter headings use "Anika." She calls her mother "Mom"; in tender moments, "Amma."
- Graduated June 2026 (communications degree, statistics minor she mostly regrets). Product operations associate at a mid-size logistics startup. Salary $92,000. $24,000 in student loans. Shares a two-bedroom apartment with a roommate.
- Voice: fast, funny, allergic to lectures; talks in screenshots and group-chat references. Interrupts with "ok but what do I do Monday?" Signature lines: "Translate it to rent." / "Be so for real, what are the odds?" / "Okay, that actually makes sense, I hate it."
- Strength: reads how her generation actually behaves (subscriptions, gig income, job-hopping, finfluencers, app nudges). Revathi's models sometimes miss this, and Anika knows it.
- Flaw: impatient; wants the shortcut and then feels guilty. Mistakes urgency for importance.
- Private ritual: her own LEDGER, a notes app on her iPhone holding a dated list of predictions with percentages, scored later. Revathi writes on paper; Anika's entries are timestamped, which Revathi grudgingly admires because they cannot be quietly backdated. In Season 2 it becomes the full Decision Ledger.

SUPPORTING CAST (use sparingly)
- Emma: Anika's best friend. Source of hot tips ("just do it, you only live once"), always "about to make it" in crypto. A standing test of how to say no to a friend. Loved, not mocked.
- Optional color: Bayes, Revathi's orange cat, unmoved by evidence. Minor characters you invent (a coworker, a banker, a landlord) must be logged in the Ledger.

SETTING AND RITUALS
- Northern Virginia (Fairfax); Anika's apartment and office are nearby. Sunday kitchen: a yellow table, a steel tumbler of chai, onions browning. Chapters may leave the kitchen (diner, coffee shop, donut shop, a drive, the park).
- Mix the food and places: donuts, deli sandwiches, diners, alongside sambar, samosas and home cooking. Do not turn the world into an all-Indian setting.
- Calendar: Chapter 1 is Sunday, September 27, 2026. Default: one chapter per Sunday. Two planned time skips: Chapter 8 is Sunday, January 3, 2027; Chapter 47 is Sunday, September 26, 2027. If a chapter uses live market data, its scene date is the real date of the data.

CANON FACTS FROM CHAPTER 1 (always true)
- Anika's first full paycheck landed: take-home $5,200 a month, paid in two checks (salary $92,000, after tax and a 4% 401(k) contribution; whether her employer matches is not yet established).
- Her last three months of spending: $4,700, $4,400, $4,100 (average $4,400). Revathi's rule: budget to the bad month ($4,700, about the 80th percentile), not the average. Left over: $5,200 minus $4,700 = $500.
- Plan: $500 a month, the day after payday, into a separate high-yield savings account Anika named "Future Anika's Car Repair." First target: $1,000. A fuller emergency fund is sized in Chapter 2.
- Emma says a stock she owns will "5x by spring." Revathi's reply: "Is it a lock, or is it a story that ends with the word 5x?" The rule: buffer first, 401(k) match second, then a small capped learning account later.
- Anika's first Ledger entries (written Sept 27, 2026): (1) at least $1,000 in the buffer by Dec 31, 2026: 85%; (2) still at this job on Sept 27, 2027: 70%; (3) she breaks the "Emma's stock" rule and buys something impulsively by Dec 25, 2026: she says 60%, Revathi says 75%.
- Revathi's $40,000 in cash and the Kill Journal have been introduced. "That is a different chapter."

THE FRAMEWORKS (introduced from Season 2; before that, mention them only as habits)
- FOUR DOORS (importance x urgency): DO (important and urgent: now, with a clear head); DECIDE (important, not urgent: schedule it; where life lives); DELEGATE (urgent, not important: give it a rule or automate it); DELETE (neither). The twist: apps and feeds manufacture urgency to push Door 4 into Door 1. Anika's amendment: "Important to whom?"
- OPINION TRIAGE (four questions before an opinion enters a decision): Who is this, and do they know you? What do they gain or lose? How many cases are they drawing from? What usually happens in situations like this (the base rate)?
- DECISION LEDGER (eight steps): 1 Classify by stakes and reversibility (one-way or two-way door?). 2 Name your values (three to five, ranked). 3 Research and disconfirm (three real options; what would make me wrong?). 4 Think in odds (best, likely, worst; the worst case must be survivable; run a pre-mortem). 5 Consult the gut, then interrogate it. 6 Check your state (hungry, angry, lonely, tired, euphoric? delay if you can). 7 Decide and record (decision, reasoning, odds, what would change my mind). 8 Review the process, not the outcome.
- THE ASTERISK (introduced in Chapter 11): the habit of adding a small star to any certainty and asking what you cannot see.
- THE LEARNING PORTFOLIO (opens in Chapter 24): a capped $500 account Anika uses as "tuition," with written rules.
- THE NUMBER: Anika's net worth, published at season ends, including ugly negative months (she starts negative because of the loans).

VOICE SAMPLE (register only; do not reuse these lines)
Revathi: "First, stop thinking of your paycheck as a number. It's a number you control. Your spending isn't. The paycheck is the same every pay period. Your expenses are a range."
Anika: "Okay, fine. I make $92,000, and I have no idea what to do with the money that actually shows up. Everyone online says 'pay yourself first' and 'invest early,' but none of them say what to do Monday."
Revathi: "Boring is a position. You're long optionality: the right to not panic."
Anika: "So my first investment is a savings account. Wow. Very exciting. Very 2026."
```

## Part 3: Chapter Request templates (paste for each chapter)

Fill the square brackets. Paste the brief from Part 5 under CHAPTER BRIEF.

### Template A: Standalone chapter

```
Write CHAPTER [N]: [TITLE] of Sunday Odds. STORY DATE: [date from the brief].

MODE: STANDALONE. Use only the Series Bible and the brief below. Do not refer to events from other chapters unless the brief lists a "soft callback," and then in one line at most. Treat the Canon Facts as the only shared history.

Target length: 1,200 to 1,800 words in the seven-beat structure.

Return exactly:
A. TITLE and STORY DATE.
B. The chapter.
C. NEW LEDGER ENTRY in this format:
   CHAPTER [N]: title, date, setting.
   FACTS ESTABLISHED: new names, numbers, objects, places, decisions, lines that must recur. Label every number as illustrative.
   WHAT ANIKA NOW KNOWS / DOES:
   WHAT REVATHI NOW KNOWS / FEELS:
   IDEA TAUGHT / TOOL INTRODUCED:
   PREDICTIONS LOGGED (with probability and resolve date):
   OPEN THREADS (the $40,000, Kill Journal, Emma, Learning Portfolio, The Number, others):
   HOOK FOR NEXT SUNDAY:
   ANYTHING I INVENTED THAT THE AUTHOR SHOULD CONFIRM:

CHAPTER BRIEF:
[paste the brief]
```

### Template B: Continuing chapter

```
Write CHAPTER [N]: [TITLE] of Sunday Odds. STORY DATE: [date].

MODE: CONTINUING. Use, in this order of authority: (1) the Series Bible, (2) the Ledger entries below, (3) the brief. Never contradict a Ledger entry. Reuse the numbers, names and objects they establish. Pay off or advance the open threads the brief names. Do not recap earlier chapters at length; one line of callback is enough.

Target length: 1,200 to 1,800 words in the seven-beat structure.

Return exactly A, B and C as in Template A.

CHAPTER BRIEF:
[paste the brief]

LEDGER ENTRIES (only those the brief names):
[paste entries]
```

### Template C: Case file chapter (Season 4 and any chapter using market data)

```
Write CHAPTER [N]: [TITLE] of Sunday Odds, a CASE FILE chapter. STORY DATE: [today's real date, so figures are current].

MODE: CASE FILE. Use the Series Bible, the Ledger entries, the brief, and the DATA PACK below. Use the Case Sheet instead of the Napkin.

DATA RULES
- Every company figure must come from the Data Pack, or from a source you retrieve now and cite with its date. If a figure is missing, write [DATA NEEDED: what and where to find it]. Never use a figure from memory, and do not estimate a reported number.
- Clearly separate (1) reported facts, (2) the characters' assumptions, and (3) the characters' conclusions.
- Give scenarios (bear, base, bull) with probabilities that sum to 100 percent, a value range for each, and an expected value. Say aloud, through a character, that the precision is false precision.
- Case files end with the characters' own recorded Decision Ledger entry, with price bands, a review date and a tripwire (the one fact that would change their mind). The narration states that this is how two fictional people reasoned, not a recommendation to readers.
- Include the Asterisk: what the characters cannot see.

Target length: 1,500 to 2,000 words.

Return A, B and C as in Template A, plus:
D. SOURCES AND AS-OF: a table of Figure | Value | Source | As-of date.

CHAPTER BRIEF:
[paste the brief]

LEDGER ENTRIES (Ch 16, Ch 24, and every earlier case-file entry in this season):
[paste entries]

DATA PACK (as-of [date]):
[paste: latest annual report (10-K) segment and income-statement figures, latest quarterly report (10-Q), share price, shares outstanding, cash and debt, and the customer-spending and competitor information the brief lists. Add links.]
```

## Part 4: Continuity Ledger (seeded through Chapter 1)

Only modes B and C need this. Paste the entries the brief names, plus the Open Threads Register below. After each new chapter, append the entry the model returns.

### Open Threads Register

Keep this table current. A chapter may advance a thread but must not resolve it before its planned payoff.

| Thread | Introduced | Planned moments | Planned payoff |
| --- | --- | --- | --- |
| Revathi's $40,000 in cash | Ch 1 | Ch 7 (inflation melts it), Ch 14 (gut interview), Ch 20 (risk) | Ch 46 (she decides what to do, and why) |
| The Kill Journal | Ch 1 | Entries read aloud in Ch 11, 15, 20, 30 | Ch 46 (Anika reads one back to her) |
| Emma's "5x" stock | Ch 1 | Ch 12 (triaged) | Ch 17 (outcome shown; process judged, not result) |
| Anika's Ledger and predictions | Ch 1 | Scored in Ch 8 and Ch 17 | Ch 47 (full scoring) |
| Job-stay prediction (70%, resolves Sept 27, 2027) | Ch 1 | Layoff rumor in Ch 2; recruiter message in Ch 40 | Ch 47 |
| The Learning Portfolio | Ch 1 (hinted) | Opens Ch 24 with written rules and no trade yet | Ch 31 (the NVIDIA call recorded), reviewed Ch 47 |
| The Number (net worth) | Ch 8 | Published at each season end: Ch 8, 17, 24, 31, 39 | Ch 47 |
| The Decision Ledger (8 steps) | Ch 9 | One step per chapter, Ch 9 to 17 | Used in every case file |
| The Asterisk | Ch 11 | Closes every case file | Ch 47 |
| Emma's crypto | Ch 1 | Ch 12, 44 (irregular income) | Open ending |

### Ledger entry for Chapter 1 (canon)

```
CHAPTER 1: The First Paycheck Is a Forecast. Sunday, September 27, 2026. Revathi's kitchen, Fairfax, Virginia.
FACTS ESTABLISHED:
- Anika's first full paycheck: take-home $5,200 a month, paid in two checks (salary $92,000; after tax and a 4% 401(k) contribution). Employer match not yet established.
- Last three months' spending: $4,700, $4,400, $4,100 (average $4,400). Revathi: budget to the bad month, $4,700, about the 80th percentile. Leftover: $5,200 - $4,700 = $500 a month into a buffer.
- Napkin logic: a buffer is insurance, priced for the left tail rather than the average year. Any dollar figures used in the written chapter are illustrative; if the draft differs from this entry, this entry wins.
- Monday Move set: separate high-yield savings account at a different bank, named "Future Anika's Car Repair"; automatic $500 transfer the day after payday; check the 401(k) match; first target $1,000.
- Emma says a stock she owns will "5x by spring." Revathi: "Is it a lock, or is it a story that ends with the word 5x?" Sequence: buffer, match, then a small capped learning account later.
- Revathi's $40,000 in cash for ten years; "That is a different chapter." The Kill Journal (paper) introduced.
- Predictions, logged in Anika's iPhone Ledger app: (1) $1,000+ in buffer by Dec 31, 2026: Anika 85%. (2) Still at this job on Sept 27, 2027: 70%. (3) Breaks the Emma's-stock rule by Dec 25, 2026: Anika 60%, Revathi 75%.
- Lines to recur: "A budget is a forecast, not a prison." "Boring is a position." "Say it in odds." "Eat your sambar."
WHAT ANIKA NOW KNOWS / DOES: budgets to the bad month; started her Ledger app; set up the buffer.
WHAT REVATHI NOW KNOWS / FEELS: Anika called out her $40,000; she deflected.
IDEA TAUGHT / TOOL INTRODUCED: paycheck as a forecast; budgeting to the 80th percentile; buffer as insurance priced in odds; the Ledger.
OPEN THREADS: see register.
HOOK FOR NEXT SUNDAY: Chapter 2, how big is big enough; sizing a buffer by how long a job search really takes.
INVENTED FOR CONFIRMATION: none beyond the Series Bible.
```

### Dating rules

- Default: one chapter per Sunday, starting with Chapter 1 on Sunday, September 27, 2026. Chapter N falls one week after Chapter N-1 (Chapter 2 is Oct 4; Chapter 7 is Nov 8).
- **Time skip 1:** Chapter 8 is Sunday, January 3, 2027, so Anika's December predictions can resolve. Chapters 9 to 24 then run weekly from January 10 to April 25.
- **Time skip 2:** Chapter 47 is Sunday, September 26, 2027, the day before her job-stay prediction resolves (Monday, September 27, 2027).
- Season 4 and any chapter using market data take the Data Pack's as-of date as the scene date. Log it in the Ledger so later chapters stay consistent.

### Ledger entry format (the model returns this after every chapter)

```
CHAPTER [N]: title, date, setting.
FACTS ESTABLISHED:
WHAT ANIKA NOW KNOWS / DOES:
WHAT REVATHI NOW KNOWS / FEELS:
IDEA TAUGHT / TOOL INTRODUCED:
PREDICTIONS LOGGED (probability, resolve date):
OPEN THREADS:
HOOK FOR NEXT SUNDAY:
ANYTHING I INVENTED THAT THE AUTHOR SHOULD CONFIRM:
```

## Part 5: Chapter briefs (all 47)

Paste one brief into Template A, B or C. **Depends on** tells you which mode to use: *None* means mode A; *Soft* means mode A, with one optional line of callback; *Hard* means mode B (paste those Ledger entries) or mode C for case files. Chapter 1's canon is the Canon Facts in the Series Bible plus its Ledger entry; if an older draft of Chapter 1 differs, they win. Every number in a brief is a suggestion: the model may invent illustrative figures but must log them.

### Season 1: Money Under Uncertainty

| # | Title and story date | Depends on | Brief |
| --- | --- | --- | --- |
| 1 | The First Paycheck Is a Forecast, Sun Sept 27, 2026 | Written | Canon. Use its Ledger entry and the Voice Sample. |
| 2 | How Big Is Big Enough? Sun Oct 4 | Hard: Ch 1 | **Idea:** size a buffer by two odds, how likely a job loss is and how long a search lasts, instead of a "3 to 6 months" slogan. **Tool:** survival number = monthly essentials × months; compare 3, 6 and 9 months. **Scene:** a layoff rumor in Anika's company group chat. **Disagreement:** Anika thinks a big fund is overkill; Revathi admits her own $40,000 was never sized by any odds (do not resolve). **Monday Move:** list essentials and compute your survival number. **Ledger:** invent and log the essentials figure (it must be below the lowest logged spending month, $4,100); Anika logs a job-loss prediction. |
| 3 | Free Money and the 100% Return, Sun Oct 11 | Soft: Ch 1 (the match step) | **Idea:** an employer match is an immediate return; guaranteed versus expected returns; vesting. **Tool:** match napkin: salary × match percentage = dollars left on the table each year. **Scene:** the benefits-enrollment email; Emma says retirement is "so far away." **Disagreement:** Anika wants cash now for loans; Revathi shows the dollars forgone; Anika's liquidity point is fair. **Monday Move:** find the match terms and vesting; raise contribution to the full match. **Ledger:** invent and log the match terms. |
| 4 | Debt Is a Bet You Already Lost, Sun Oct 18 | None | **Idea:** paying off a loan is a risk-free return equal to its (after-tax) interest rate; compare with uncertain returns. **Tool:** list debts by rate; guaranteed-versus-expected comparison. **Scene:** Anika opens her loan portal (invent two loans totaling $24,000 with illustrative rates). Emma: "never pay off cheap debt." **Disagreement:** Anika wants the snowball win; Revathi concedes behavior has a price. **Monday Move:** list every debt with balance, rate and minimum; rank by rate. **Ledger:** log the loan list. |
| 5 | The Score Behind the Score, Sun Oct 25 | None | **Idea:** what builds a credit score; a worse score costs real dollars. **Tool:** dollar cost of a score gap on a $20,000 car loan, with clearly illustrative rates. **Scene:** an apartment-renewal credit check. **Disagreement:** Anika calls credit cards a trap; Revathi: a tool with variance, so give it rules. **Monday Move:** pull your free report; set autopay on every minimum. |
| 6 | Expected Value for People Who Hate Math, Sun Nov 1 | Soft: Ch 1 (Emma's tip) | **Idea:** expected value; a fair bet; a bet with positive expected value can still ruin you if it is too big. **Tool:** EV = sum of probability × payoff, minus cost, applied to a phone-store warranty, a subscription and a betting-app promo. **Disagreement:** Anika says convenience has a price EV ignores; Revathi: then price it. **Monday Move:** audit three recurring charges with EV logic. |
| 7 | Inflation, the Silent Subscription, Sun Nov 8 | None | **Idea:** real versus nominal returns; cash melts slowly. **Tool:** real return is roughly nominal minus inflation; the rule of 72. **Scene:** a grocery receipt versus last year's (illustrative), holiday-shopping prep. **Disagreement:** Anika notices Revathi's $40,000 is melting; Revathi admits the price of her insurance and says "next chapter" (plant; do not resolve). **Monday Move:** compare your savings rate with current inflation \[CHECK CURRENT\]. |
| 8 | Season 1 Scorecard, Sun Jan 3, 2027 (time skip) | Hard: Ch 1 and Ledger entries for Ch 2 to 7 | **Idea:** calibration, scoring predictions. **Tool:** Brier score = (probability − outcome)², where outcome is 1 if it happened and 0 if not; e.g. 60% on something that happened scores 0.16, 75% scores 0.0625; lower is better. **Scene:** New Year's, her Ledger app, Anika's three predictions. **Default outcomes (author may change):** #1 true, buffer reached by mid-December; #3 true, an impulsive purchase on Dec 20, so Revathi's 75% beats Anika's 60%. **Disagreement:** Revathi wants a clean score; Anika: three predictions is a tiny sample. **Monday Move:** write five predictions with probabilities and dates. **Ledger:** publish The Number (negative, built from the logged balances and the $24,000 of loans) and log it. |

### Season 2: Deciding Under Uncertainty (the Decision Ledger, one step at a time)

From Chapter 9 on, each chapter teaches one step of the eight-step Decision Ledger and ends with a Monday Move on a real money choice.

| # | Title and story date | Depends on | Brief |
| --- | --- | --- | --- |
| 9 | The Four Doors, Sun Jan 10 | None | **Step 1.** **Idea:** importance is not urgency; apps manufacture urgency (limited-time offers, price alerts); two-way versus one-way doors. **Tool:** Do, Decide, Delegate, Delete, plus "is it reversible?" **Scene:** Anika arrives with 20-plus "urgent" money to-dos; Revathi sorts them on a napkin. **Disagreement:** Anika: "Important to whom?" She is right. **Monday Move:** sort your open money to-dos; give one a delegating rule (autopay). |
| 10 | Values First, Sun Jan 17 | None | **Step 2.** **Idea:** money is a tool; a "good outcome" depends on what you want. **Tool:** rank three to five values by forcing trade-offs between pairs; the regret test (what will you wish you had tried?). **Scene:** a walk in a park. Illustrative defaults: Anika ranks independence, curiosity, helping her mother; Revathi ranks security, optionality, being useful. **Disagreement:** Revathi's top value costs her something; touch the $40,000 lightly. **Monday Move:** rank your values; write one trade-off. |
| 11 | Whose Lens Is This? Sun Jan 24 | None | **Step 3, part 1.** **Idea:** priors and confirmation bias; feeds learn your prior. **Tool:** observe the thought, ask "what else could be true?", add one outside check; **introduce the Asterisk.** **Scene:** one house-search leaves Anika's feed full of "buy now" content while Revathi's is all recession talk. Anika teaches Revathi how a feed learns. Revathi reads a Kill Journal entry. **Monday Move:** for a decision, list three real options and why each might fail; name one person who will check you. |
| 12 | Two Hundred Strangers and One Lemon, Sun Jan 31 | Soft: Ch 1 (Emma's stock) | **Step 3, part 2.** **Idea:** small samples, survivorship bias, base rates. **Tool:** Opinion Triage (four questions). **Scene:** Anika's spreadsheet counting opinions on a hyped stock (invent counts); Revathi sorts them live. **Revathi's numbers tested:** there is no clean base rate; she admits it. **Disagreement:** Anika: some creators are good; Revathi: show the track record; Anika: your industry hides its losers too. **Monday Move:** run the four questions on the last three money tips you heard. |
| 13 | The Three-Case Sketch, Sun Feb 7 | Soft: Ch 4 (loans) | **Step 4.** **Idea:** best, likely and worst case; the worst case must be survivable; false precision. **Tool:** three-case sketch plus a pre-mortem ("it is a year from now and this failed; why?"). **Scene:** extra $200 a month, freed by good months (her spending averages about $4,400 against a $4,700 budget): loans, investing, or cash? Illustrative rates. **Revathi's numbers tested:** her return assumption is too tidy. **Monday Move:** sketch three cases and write one pre-mortem sentence. |
| 14 | The Gut Gets a Seat, Not the Wheel, Sun Feb 14 | Soft: Ch 1 (the $40,000) | **Step 5.** **Idea:** trained intuition (many cases, honest feedback) versus fear and mood in disguise. **Tool:** Gut Interview: name the feeling; what might it know; what might it react to that is irrelevant. **Scene:** Anika's gut balks at a "great deal"; Revathi runs the interview on her $40,000 and surfaces a fear from the divorce years (hint only; do not resolve). **Monday Move:** name the feeling behind your last money impulse. |
| 15 | When the Alarm Is Just the Toast, Sun Feb 21 | None | **Step 6.** **Idea:** strong emotion is data about you, not about the market. **Tool:** state check (hungry, angry, lonely, tired, euphoric?) and a 24-hour rule. **Scene:** a 1 a.m. market-drop alert; Anika almost buys. Revathi reads a Kill Journal entry about trading angry. **Monday Move:** set a 24-hour rule above a dollar limit you choose. |
| 16 | Decide and Record, Sun Feb 28 | Hard: Ledger entries Ch 9 to 15 | **Step 7.** **Idea:** write the decision, the reasoning, the odds and what would change your mind. **Tool:** the one-page Decision Ledger. **Scene:** Anika fills out her first full page for a real decision (default: raise her 401(k) contribution to capture the match, or send extra cash to loans); Revathi shows her black paper notebooks, one per year; Anika shows her timestamped Ledger app. **Disagreement:** too much paperwork; Revathi: ten minutes. **Monday Move:** fill out your first page and set a review date. |
| 17 | Good Decision, Bad Outcome, Sun Mar 7 | Hard: Ch 16, Ch 12, Ch 8 | **Step 8.** **Idea:** resulting (judging by outcome); process versus result. **Tool:** the Decision/Outcome grid and a process scorecard (information, options, risk, values). **Scene:** Emma's stock went up (default) and Anika did not buy: good process, painful outcome. Revathi tells a good-process, bad-outcome story from her career. **Monday Move:** review one past decision by its process. **Ledger:** publish The Number (season end). |

### Season 3: Owning Things

| # | Title and story date | Depends on | Brief |
| --- | --- | --- | --- |
| 18 | What Is a Stock, Really? Sun Mar 14 | None | **Idea:** a share is a claim on future cash flows; price versus value; the market's mood swings. **Tool:** the restaurant analogy: you own a slice of the cash the restaurant makes. **Scene:** Anika opens her 401(k) fund list and learns she owns hundreds of companies. **Disagreement:** Anika: "price is just vibes"; Revathi: in the short run, yes. **Monday Move:** pick a company you use and find how it makes money. |
| 19 | The Boredom Premium, Sun Mar 21 | None | **Idea:** index funds and fees; after costs, most active managers trail a plain index over long horizons (state generally; do not invent a statistic). **Tool:** fee-drag napkin: $10,000 over 40 years at 7% versus 6% (illustrative). **Scene:** Anika calls Revathi a hypocrite for recommending index funds; Revathi explains how her job differs (mandate, size, risk). **Monday Move:** compare expense ratios in your options. |
| 20 | Risk Is Not Volatility, Sun Mar 28 | Soft: Ch 15 | **Idea:** drawdowns, time horizon, sequence risk. **Tool:** the 40% drop test. **Scene:** Anika's account turns red; Revathi reads a Kill Journal entry about her worst year; her $40,000 is hinted at again. **Monday Move:** write down what you would do if your account fell 40%. |
| 21 | The Only Free Lunch, Sun Apr 4 | None | **Idea:** diversification and correlation. **Tool:** the umbrella-and-sunscreen analogy; an overlap check. **Scene:** Emma's group chat all owns the same three stocks. **Monday Move:** check how much your holdings overlap. |
| 22 | A Company in 30 Minutes, Sun Apr 11 | None | **Idea:** five numbers from an annual report: revenue growth, operating margin, free cash flow, debt, share count. **Use a clearly fictional company with illustrative figures; do not use a real company.** **Monday Move:** pull one 10-K and fill in the five-number sheet. |
| 23 | What You'd Have to Believe, Sun Apr 18 | Soft: Ch 22 | **Idea:** reverse valuation: what growth does today's price imply? **Tool:** a simple reverse-DCF napkin with illustrative numbers. **Scene:** Emma calls a stock "cheap" because its price fell. **Monday Move:** run a reverse valuation on one stock in a spreadsheet. |
| 24 | The Learning Portfolio, Sun Apr 25 | Hard: Ch 16, Ch 2 | **Idea:** a capped $500 account as tuition: thesis, size, exit rule, and the stage gate (buffer and match first). **Scene:** Anika opens the account and writes her rules; Revathi insists no single-stock trade until a full analysis (sets up Season 4); Anika buys only a broad index fund. **Disagreement:** Anika wants one fun stock; Revathi: yes, after the work. **Monday Move:** write a one-paragraph thesis before any trade. **Ledger:** publish The Number (season end). |

### Season 4: Case File, NVIDIA (mode C for every chapter)

Seven consecutive Sundays on one company, with the full Decision Ledger. Story date is the Data Pack's as-of date. All chapters are Hard dependencies on the previous case-file entry plus Ch 16 and Ch 24.

| # | Title | Brief | Data Pack must contain |
| --- | --- | --- | --- |
| 25 | Why This Company? | **Idea:** circle of competence; define the question ("is it worth buying at today's price?", not "is it a good company?"). **Tool:** write your prior with a probability before seeing numbers. **Scene:** Emma texts that NVIDIA "can't lose"; Revathi: seven Sundays of work first. Run Emma's claim through Opinion Triage. **Monday Move:** write your starting belief about one stock in a sentence, with a probability. | Current price and market cap with date; the company's own description of its business from its latest 10-K. |
| 26 | How It Makes Money | **Idea:** segments, customers, the business model (it designs chips and relies on outside manufacturers; a software ecosystem adds to the product). **Tool:** Case Sheet: revenue by segment. **Disagreement:** Anika assumes it is a gaming company; let the data decide. **Monday Move:** fill a segment table from the latest 10-K. | Latest 10-K revenue by segment and market platform with fiscal-year labels; customer-concentration disclosure; manufacturing model. |
| 27 | Who Wants Its Lunch? | **Idea:** competition: other chip makers, the biggest customers' in-house chips, software lock-in, export controls. **Tool:** moat test (what would have to be true for the lead to last?) and Three Other Stories (three explanations for one fact). **Monday Move:** list three ways the lead could erode and what you would watch. | 10-K competition and risk-factor sections; sourced reports on competitor products and customers' in-house chip programs; export-control status with date. |
| 28 | The Customer's Budget Is the Company's Revenue | **Idea:** demand depends on a few buyers' capital spending; concentration, cyclicality, leading indicators. **Scene:** Anika sees the buyer side through her logistics company's cloud bill. **Revathi's numbers tested:** her smooth growth line meets lumpy budgets. **Monday Move:** track one customer's spending guidance from its latest earnings call. | Latest capex figures and guidance from the three or four largest cloud customers; the company's concentration disclosure. |
| 29 | Reading the Numbers | **Idea:** growth, gross and operating margin, free cash flow, inventory, balance sheet, stock-based compensation, share count. **Tool:** the Ch 22 five-number sheet on the real company. **Disagreement:** Revathi trusts the clean number; Anika asks what it hides. **Monday Move:** compute free-cash-flow margin for three years. | Three to five fiscal years of income, cash-flow and balance-sheet items, plus the latest quarter. |
| 30 | What's Priced In | **Idea:** reverse DCF and multiples against the company's own history; bear, base and bull cases with probabilities that sum to 100 percent; expected value; a fair-value range. **Revathi's numbers tested:** a small change in the discount rate swings value a lot; Kill Journal entry. **Monday Move:** build your own three-case range in a spreadsheet. | Price, shares outstanding, cash and debt, trailing figures, as-of date; characters' stated assumptions. |
| 31 | Buy, Hold or Sell Bands | **Idea:** price bands relative to value; margin of safety; position size as a percent of savings; pre-mortem; tripwire. **Tool:** the recorded Decision Ledger entry with price bands and a six-month review date. **Scene:** Anika writes her entry; Revathi challenges it; Emma reacts. Anika's $500 buys only a sliver (fractional shares or paper trade; author decides). The narration states plainly that this is how two fictional people reasoned. **Monday Move:** draw your own bands and name the one fact that would change your mind. **Ledger:** publish The Number (season end). | Current price and the Ch 30 value ranges, with as-of date. |

### Season 5: Options and the Price of Uncertainty

Dates run weekly after Chapter 31. Never recommend a trade; all contract figures are illustrative unless a Data Pack supplies them.

| # | Title | Depends on | Brief |
| --- | --- | --- | --- |
| 32 | Options Are Insurance With a Ticker | None | **Idea:** calls, puts and the premium as the price of insurance. **Tool:** payoff table for a call and a put. **Scene:** a coworker brags about an options win; Revathi explains by comparing to home insurance. **Monday Move:** draw payoff diagrams on paper. |
| 33 | The Napkin Payoff | Hard: Ch 32 | **Idea:** breakeven, maximum loss, maximum gain, probability of profit. **Monday Move:** compute breakeven for a real contract on paper only. |
| 34 | The Market's Odds | Hard: Ch 32 to 33; Soft: Ch 29 to 31 | **Idea:** implied volatility is the market's forecast of how much a stock will move. **Tool:** implied move around earnings, roughly the price of an at-the-money straddle divided by the stock price (state as a rough rule). Use a Data Pack option chain if available (mode C), else illustrative. **Monday Move:** find the implied move for one earnings date. |
| 35 | Rent on Being Late | Hard: Ch 32 to 33 | **Idea:** time decay; being right but late still loses. **Tool:** compare two expiries for the same idea. **Monday Move:** compare them yourself. |
| 36 | Selling Uncertainty | Hard: Ch 32 to 35 | **Idea:** covered calls and cash-secured puts: premium income against capped upside and the obligation to buy. Revathi is blunt: this is not free money. **Monday Move:** paper-trade one covered call and track it. |
| 37 | The Lottery Ticket Problem | Soft: Ch 6, Ch 33 | **Idea:** why most buyers of far out-of-the-money options lose: low probability, big payoff, costs. **Scene:** Emma's "10x" trade. **Monday Move:** compute the odds on a "10x" trade you saw. |
| 38 | How Much Do You Bet? | Soft: Ch 13, Ch 24 | **Idea:** position sizing; the Kelly intuition (bet size depends on edge and odds; use a fraction because edge estimates are noisy); risk of ruin. **Monday Move:** set a maximum loss per idea as a percent of savings. |
| 39 | Insurance for Normal People | Soft: Ch 32 | **Idea:** when insuring makes sense. **Tool:** worth-it test: cost versus probability × loss, and whether you could absorb the loss. Covers renters, health and disability insurance. **Monday Move:** decide what you would actually insure and why. **Ledger:** publish The Number (season end). |

### Season 6: Life Is the Portfolio

| # | Title | Depends on | Brief |
| --- | --- | --- | --- |
| 40 | The Job Offer Is an Option | Soft: Ch 1 (job-stay prediction) | **Idea:** negotiation as pricing; what flexibility is worth. **Scene:** a recruiter message while Anika's 70% prediction is still open; run the Decision Ledger. **Monday Move:** research a salary range and write your ask. **Ledger:** update the job-stay probability. |
| 41 | Startup Equity, Priced | Soft: Ch 40, Ch 23 | **Idea:** stock options, RSUs, strike price, dilution, vesting. **Tool:** value equity at zero, base and best case, with probabilities. Do not invent startup-failure statistics. **Monday Move:** value your equity three ways. |
| 42 | Rent or Buy? | None | **Idea:** a decision under uncertainty: scenarios, transaction costs, time horizon. **Tool:** a three-scenario sheet. **Monday Move:** build it. |
| 43 | The Return You Control | None | **Idea:** taxes and the order of accounts (match, then accounts with tax advantages, then taxable). Use \[CHECK CURRENT\] for every limit and rule; no personalized tax advice. **Monday Move:** map your accounts to an order of use. |
| 44 | Irregular Income | Soft: Ch 1, Ch 2 | **Idea:** budgeting with lumpy pay (gig, bonus, freelance). **Tool:** pay yourself a baseline salary from a holding account. **Scene:** Emma's income swings. **Monday Move:** set your baseline. |
| 45 | Your Biggest Asset Is You | Soft: Ch 40 | **Idea:** human capital; skills compound; job risk and portfolio risk are correlated. Mention AI tools factually and without hype. **Monday Move:** list three skills that raise your income odds. |
| 46 | Talking Money With People You Love | Hard: Ch 1, Ch 7, Ch 14 (the $40,000 thread) | **Idea:** how to talk about money with partners, parents and friends. **Scene:** Revathi tells her money story from the divorce; **resolve the $40,000** (default: she keeps a defined reserve and invests the rest under a written plan; author may change). Anika reads back a Kill Journal entry. **Monday Move:** start one money conversation this week. |
| 47 | Year-One Review, Sun Sept 26, 2027 (time skip) | Hard: the Open Threads Register, a "Story so far" summary, and the entries for Ch 8, 16, 17, 24 and 31 | **Idea:** review the process, not the outcome. **Tool:** score every logged prediction with the Brier score; revisit the NVIDIA entry against its review date; The Number across the year; Emma, the $40,000, the Learning Portfolio. **Ending:** the job-stay prediction resolves the next morning (Monday, Sept 27, 2027) in a one-line epilogue; Anika writes her year-two predictions. **Monday Move:** do your own annual review. |

### Brief template for new chapters

Use this to add chapters after Chapter 47, or to insert new topics anywhere. Copy the topic bank from the main outline.

```
CHAPTER [N]: [TITLE]. STORY DATE: [date].
DEPENDS ON: None | Soft: Ch X (optional one-line callback) | Hard: Ch X (paste the Ledger entry).
IDEA (one sentence):
TOOL (one):
SCENE SEED (where, what Anika brings, what triggers the question):
DISAGREEMENT (who thinks what; who has a point):
REVATHI'S NUMBERS TESTED BY: [or] ANIKA TEACHES REVATHI: [one of the two, at least]
MONDAY MOVE (under 30 minutes):
THREADS TO ADVANCE (optional):
DATA NEEDED (case files only):
```

## Part 6: Quality checklist (before you accept a chapter)

- **One idea, one tool.** Can you state both in one sentence each? If not, cut.
- **Standalone test (mode A):** does it make sense to a reader who has not read any other chapter? Any callback is one line at most.
- **Continuity (modes B and C):** names, numbers, dates and objects match the Series Bible and the supplied Ledger entries. Every new fact is logged.
- **Both women learn.** Revathi's confidence meets a limit at least once. Anika teaches Revathi something at least once.
- **Voices.** Cover the speaker names: can you still tell who is talking? Revathi is dry and exact; Anika is fast and funny.
- **Accuracy.** The probability idea is correct. Every number is either illustrative and labelled, or sourced and dated. No invented real-world statistics. Current rates and limits are \[CHECK CURRENT\] placeholders until you fill them.
- **Not advice.** The narration never tells readers what to buy, sell or do. Case files end with ranges, bands and a tripwire, framed as the characters' own reasoning.
- **Probabilities and process.** Every prediction has a probability and a date. Any result shown is judged by process, not just outcome.
- **Monday Move.** One action, under 30 minutes, with numbered steps.
- **Setting and tone.** U.S. setting, mixed foods and places, at most one cultural touch per page, humor from character.
- **Case files:** every company figure is in the Sources and As-Of table; scenario probabilities sum to 100 percent; the Asterisk is present.
- **Length and shape.** 1,200 to 1,800 words (case files up to 2,000) in the seven-beat structure, with a fresh ending hook.

## Part 7: Quick prompts for common fixes

- **Voice drift:** "Rewrite Revathi's lines so they sound like the Voice Sample: dry, exact, short sentences, one cultural touch per page at most. Rewrite Anika's lines so they are faster, funnier and more specific."
- **Too lecture-like:** "Turn the Frame section into a dialogue in which Anika challenges each claim and Revathi answers with an example from the kitchen or the weather."
- **Too many facts:** "Cut the chapter to one idea and one tool. Move extra ideas to a list of future chapter topics at the end."
- **Invented data:** "List every number in the chapter. For each, mark it illustrative, sourced (with the source and date) or unsupported. Replace every unsupported number with a \[DATA NEEDED\] placeholder."
- **Sounds like advice:** "Rewrite any sentence that tells the reader what to buy, sell or do. Keep the characters' reasoning but frame it as theirs, and end with what would change their mind."
- **Continuity slip:** "Compare this chapter with the Series Bible and the Ledger entries. List every contradiction, then fix them."
- **Too long:** "Cut 15 percent, starting with repeated explanations. Keep every Ledger fact."
- **Flat ending:** "Give me three alternative last paragraphs, each using a different device: a line of dialogue, an object, a notification."
- **Napkin math is weak:** "Redo the Napkin with assumptions listed first, round numbers a reader can recompute, and one sentence on how the answer changes if an assumption is wrong."
- **Make a Ledger entry from a chapter I edited:** "Read the chapter below and produce a Ledger entry in the exact template format. List only facts that appear in the text."




............


<!--
NEW LEDGER ENTRY (internal, not for publication)

CHAPTER 4: Debt Is a Bet You Already Lost, Sunday, October 18, 2026, Revathi's kitchen, Fairfax.

FACTS ESTABLISHED (all numbers illustrative):
- Loan 1: federal, $6,000 at 4.0%, minimum about $61 a month, interest about $20 a month.
- Loan 2: private, $18,000 at 7.5% fixed, minimum about $214 a month, interest $112.50 a month.
- Combined interest about $132 a month, about $1,590 a year. Minimums assumed to be already inside her $4,700 budget.
- Anika's rent share: $1,300 a month.
- Her servicer's app defaults extra payments to "apply to next month's bill," with a principal toggle under payment preferences. Two people in her group chat were burned.
- Revathi's prior: 90% that extra payments go to principal. After Anika's report she says fifty-fifty for any servicer. She never uses the word "guaranteed" ("locked in").
- Illustrative stock assumptions: 7% expected, one-year range -20% to +30%. About a 48% chance of beating 7.5% in one year (labelled "call it").
- Rough napkin: the snowball (federal first) costs about $600 over about four years versus the avalanche (private first), at $300 a month extra.
- Anika's decision: after the buffer reaches $1,000 and she learns whether her employer matches her 401(k), $300 of the monthly $500 goes extra to the federal loan, applied to principal. The other $200 keeps going to the buffer.
- Revathi writes "Was 90%. Wrong." on the back of a dal recipe card. Anika photographs it ("Timestamped").
- Anika jabs about the $40,000 in cash; Revathi replies "That is a different chapter."
- Emma's text: "never pay off cheap debt. invest the difference."
- Anika's lunch: a desk salad. The portal screenshot was taken Friday at 12:40.

WHAT ANIKA NOW KNOWS / DOES: Her interest bill is about $132 a month. A loan's rate is the return from paying it off. She has chosen the snowball order knowingly and will check the principal toggle.

WHAT REVATHI NOW KNOWS / FEELS: Her confidence about servicer defaults was wrong. She conceded that behavior has a price. She has not priced the federal loan protections and knows it.

IDEA TAUGHT / TOOL INTRODUCED: Paying off a loan earns its rate with no variance. Tool: a debt list sorted by rate, compared against an alternative's expected return and range.

PREDICTIONS LOGGED (with probability and resolve date):
- First extra payment to the federal loan, applied to principal, by Jan 31, 2027: Anika 75%.
- $6,000 loan at zero by Dec 31, 2028: Anika 70%, Revathi 55%.
- Principal setting found and screenshotted by Oct 25, 2026: Anika 90%.

OPEN THREADS: The $40,000 (jabbed at, deferred again). Kill Journal (not used this chapter). Emma (her "invest the difference" claim was partly right and partly tested). Learning Portfolio (not yet). The Number (loans noted as $24,000). 401(k) match (still unestablished; the decision waits on it). Buffer progress (balance not stated). Federal loan protections (flagged, unpriced).

HOOK FOR NEXT SUNDAY: If debt is the bet you already lost, what's a bet worth taking?

ANYTHING I INVENTED THAT THE AUTHOR SHOULD CONFIRM:
- Loan balances, rates, minimums, rent share, and that minimums sit inside the $4,700 budget. A 4.0% federal rate would come from older loans, so check it against current federal rates [CHECK CURRENT]. A grace period [CHECK CURRENT] might also mean federal payments haven't started.
- The servicer default behavior and toggle.
- The $600 snowball cost (re-computed at about $630 on these inputs) and the 48% coin-flip figure.
- Splitting the $500 into $300 extra and $200 to the buffer, which could conflict with how Chapter 2 sizes the emergency fund.
- That the decision is conditional on the 401(k) match, which the Bible leaves unestablished.
- The "different chapter" jab, the recipe-card ending and the next-Sunday teaser.
- The frontmatter "asterisk" line is my own wording; the Asterisk is formally introduced in Chapter 11, so the body never names it.
-->