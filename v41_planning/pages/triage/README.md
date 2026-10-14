# Triage Case Workspace

**Temporary v41 design review notes (14 October 2026).** Governing behaviour: [FRD-15](../../../pegasus/docs/frd/frd-15-work-centre-queues-and-search.md#triage-workspace); presentation: [design authority](../../../pegasus/docs/design/README.md).

- **Routes**: `/Cases/{id:guid}` (when `Type == Triage`)
- **Interactive mockup**: [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) (`?state=triage-case&design=proposal` vs `&design=today`)
- [how-it-works.md](how-it-works.md): live implementation on `origin/dev` and usability/design findings.
- [how-it-should-work.md](how-it-should-work.md): proposed v41 design, UI, and UX improvements.
- [states/README.md](states/README.md), [panels/README.md](panels/README.md), [dialogs/README.md](dialogs/README.md).

## Screenshots

| View | Captures (`1580×1000`, `1440×900`, `760×1000`, `1580` whole page) |
| --- | --- |
| Triage Case `/Cases/{id}` (proposal) | [1580](../current/v41-shots/16-triage-case-1580.png) · [1440](../current/v41-shots/16-triage-case-1440.png) · [760](../current/v41-shots/16-triage-case-760.png) · [full](../current/v41-shots/16-triage-case-full.png) |
