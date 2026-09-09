# Test transcripts

Sample visit notes for testing your medication-detection implementation (see
[../EXERCISE.md](../EXERCISE.md)). They're deliberately messy: exact names, brand
names, shorthand, misspellings, plus supplements and a drug that isn't in the
small seeded catalog.

These are separate from the seeded demo notes so you can test against text your
code hasn't been tuned on.

## How to use them

**In the app:** log in, open any patient's visit, click **Edit**, paste the
contents of a `transcript-*.txt` file into the notes field, **Save**, then view
the visit. Your analyzer runs and the medications should highlight.

**Against the API directly:** paste the text into a visit via `PUT
/api/visits/{id}`, then `POST /api/visits/{id}/analyze`. Or feed the text straight
into your detection function in a unit test.

Each highlight should surface the normalized RxNorm concept, and for misspellings
it should show the proper spelling. How you present that is your design call.

Some lines also include a form or a dose. That is the form-and-dosage stretch in
[EXERCISE.md](../EXERCISE.md), not part of the core name-matching task.

## Answer keys

"In catalog?" refers to the **20 seeded demo concepts**, the catalog you get
before importing anything. After `POST /api/medications/import` the catalog holds
~15k concepts and essentially every real drug below resolves locally — including
the ones marked "no". What gets harder then is picking the *right* candidate out
of 15k, not finding one at all.

### transcript-01.txt

<details><summary>Show answer key</summary>

| Written in note | Kind | Normalized (RxCUI) | Correction | In catalog? |
| --- | --- | --- | --- | --- |
| `lisinopril` | exact | lisinopril (29046) | — | yes |
| `metformin` | exact | metformin (6809) | — | yes |
| `Lipitor` | brand | atorvastatin (83367) | — | yes |
| `Norvasc` | brand | amlodipine (17767) | — | yes |
| `HCTZ` | shorthand | hydrochlorothiazide (5487) | — | yes |
| `ASA` | shorthand | aspirin (1191) | — | yes |
| `hydrochlorothiazde` | misspelling | hydrochlorothiazide (5487) | hydrochlorothiazide | yes |

Note: `HCTZ` and `hydrochlorothiazde` refer to the same drug — deciding how to
present duplicate references to one concept is a design choice. `lisinopril 20
mg`, `metformin 1000 mg`, and `ASA 81 mg` also name a dose.

</details>

### transcript-02.txt

<details><summary>Show answer key</summary>

| Written in note | Kind | Normalized (RxCUI) | Correction | In catalog? |
| --- | --- | --- | --- | --- |
| `Coumadin` | brand | warfarin (11289) | — | yes |
| `metopralol` | misspelling | metoprolol (6918) | metoprolol | yes |
| `omeprazole` | exact | omeprazole (7646) | — | yes |
| `gabapentine` | misspelling | gabapentin (25480) | gabapentin | yes |
| `sertralin` | misspelling | sertraline (36437) | sertraline | yes |
| `Ventolin` | brand | albuterol (435) | — | yes |
| `Tylenol` | brand | acetaminophen (161) | — | yes |
| `warfarin` | exact | warfarin (11289) | — | yes |
| `levothyroxin` | misspelling | levothyroxine (10582) | levothyroxine | yes |
| `MTX` | shorthand | methotrexate (6851) | — | **no** — not seeded |
| `vitamin D` | supplement | vitamin D (11253) | — | **no** — not seeded |
| `folic acid` | supplement | folic acid (4511) | — | **no** — not seeded |

Notes:
- `Coumadin` and `warfarin` are the same concept mentioned twice.
- `MTX` (methotrexate) is a real drug that is **not** among the 20 seeded
  concepts. Against the seeded catalog a matcher should mark it unmatched or
  resolve it via live RxNav; after a full import it resolves locally.
- `vitamin D` and `folic acid` are supplements. They *are* real RxNorm
  ingredients, so a full catalog will match them — the judgment call is whether
  a supplement belongs in a medication list at all, not whether you can find it.
  Be deliberate either way.
- The genuinely unmatchable text in these notes is everything that isn't a drug:
  scores (`MMSE 26/30`), labs, conditions, and dosing words. Those must not turn
  into confident matches — which is easier to get wrong once the catalog has
  15,000 names to fuzzy-match against.
- `Ventolin inhaler` also names a form. Most other mentions in this note do not.

</details>
