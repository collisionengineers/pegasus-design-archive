# v43 Stage 2 conformance

The implemented Case details on `task/case-details-claim-source` (commit `4e56385c0`, 2 November
2026), captured with the same `ZzMockupCaptureCase` lane and fixture as the mockup's Today, and
compared with the signed-off Proposal.

| Path | What it is |
| --- | --- |
| `captured-live/` | The implemented Case pages and the branch's `wwwroot` |
| `pegasus_v43_conformance.html` | The captures in the mockup frame (Today is the implementation) |
| `build/` | The mockup tooling, pointed at these captures; `build/conformance-v43.py` shoots and pairs |
| `shots/cNNN-<state>-<width>.png` | The implemented Case details section; `NNN` is the mockup's Proposal shot |
| `shots/sNNN-<state>-<width>.png` | Side by side: the signed-off Proposal left, the implementation right |
| `shots/conformance.json` | Each pair, with both section heights and the page errors (none) |

## Result (2 November 2026)

- 15 pairs, covering 5 states (read, edit, read bare, edit bare, Claim source chosen) at 1580×1000,
  1440×900 and 760×1000. Every section height matches. 12 pairs are pixel-identical. In the other 3,
  only the section head's Edit button glyph differs, by anti-aliasing.
- The mockup's own self-check, run against the implementation
  (`python -X utf8 build/check-v43.py --no-shots`), gives `okCount 61`. It fails only the three checks
  that assert the old live layout or the rejected F variant:
  - `today: live sub-panels Case, Principal, Case contact, Notes`
  - `today: Notes from client beside Accident circumstances`
  - `F variant: Accident circumstances keeps its half-width cell`
- Proven on the routed page:
  - The Claim source select fills the contact cells and the record-notes cell, which now sits in the
    Claim source card.
  - The two this-Case notes textareas post with the Save form.
  - With no Principal record notes, this Case's cell keeps its half-width place (G).

These are captures from the test host (`IntakeWebApplicationFactory` over the recording Case store),
not production. CI on the PR head is the test evidence.
