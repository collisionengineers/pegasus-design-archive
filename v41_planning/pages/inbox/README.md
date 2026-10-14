# Inbox & Message Record

**Temporary v41 design review notes (14 October 2026).** Governing behaviour: [FRD-20](../../../pegasus/docs/frd/frd-20-mailbox-workspace.md); presentation: [design authority](../../../pegasus/docs/design/README.md).

- **Routes**: `/Inbox` and `/Inbox/{id:guid}`
- **Interactive mockup**: [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) (`?state=inbox&design=proposal` vs `&design=today`)
- [how-it-works.md](how-it-works.md): live implementation on `origin/dev` and usability/design findings.
- [how-it-should-work.md](how-it-should-work.md): proposed v41 design, UI, and UX improvements.
- [states/README.md](states/README.md), [panels/README.md](panels/README.md), [dialogs/README.md](dialogs/README.md).

## Screenshots

| View | Captures (`1580×1000`, `1440×900`, `760×1000`, `1580` whole page) |
| --- | --- |
| Inbox 3-pane workspace (proposal) | [1580](../current/v41-shots/10-inbox-1580.png) · [1440](../current/v41-shots/10-inbox-1440.png) · [760](../current/v41-shots/10-inbox-760.png) · [full](../current/v41-shots/10-inbox-full.png) |
| Inbox 3-pane workspace (today) | [1580](../current/v41-shots/11-inbox-today-1580.png) · [1440](../current/v41-shots/11-inbox-today-1440.png) · [760](../current/v41-shots/11-inbox-today-760.png) · [full](../current/v41-shots/11-inbox-today-full.png) |
| Message Record `/Inbox/{id}` (proposal) | [1580](../current/v41-shots/12-mail-message-1580.png) · [1440](../current/v41-shots/12-mail-message-1440.png) · [760](../current/v41-shots/12-mail-message-760.png) · [full](../current/v41-shots/12-mail-message-full.png) |
