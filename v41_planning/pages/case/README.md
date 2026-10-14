# Case Record Workspace

**Temporary v41 design review notes (14 October 2026).** Governing behaviour: [FRD-16](../../../pegasus/docs/frd/frd-16-case-record-workspace.md); presentation: [design authority](../../../pegasus/docs/design/README.md).

- **Routes**: `/Cases/{id:guid}`
- **Interactive mockup**: [`pegasus_case_workspace_v41.html`](../../current/pegasus_case_workspace_v41.html) (`?state=v41-overview&design=proposal` vs `&design=today`)
- [how-it-works.md](how-it-works.md): live implementation on `origin/dev` and usability/design findings.
- [how-it-should-work.md](how-it-should-work.md): proposed v41 design, UI, and UX improvements.
- [states/README.md](states/README.md), [panels/README.md](panels/README.md), [dialogs/README.md](dialogs/README.md).

## Screenshots

| View | Captures (`1580×1000`, `1440×900`, `760×1000`, `1580` whole page) |
| --- | --- |
| Case Workspace — Overview & Report Delivery (proposal) | [1580](../current/v41-shots/22-case-overview-1580.png) · [1440](../current/v41-shots/22-case-overview-1440.png) · [760](../current/v41-shots/22-case-overview-760.png) · [full](../current/v41-shots/22-case-overview-full.png) |
| Case Workspace — Delivery rules & inline Yes/No + hold Done (proposal) | [1580](../current/v41-shots/23-case-delivery-rules-1580.png) · [1440](../current/v41-shots/23-case-delivery-rules-1440.png) · [760](../current/v41-shots/23-case-delivery-rules-760.png) · [full](../current/v41-shots/23-case-delivery-rules-full.png) |
| Case Workspace — Plain delivery without rules (proposal) | [1580](../current/v41-shots/24-case-delivery-plain-1580.png) · [1440](../current/v41-shots/24-case-delivery-plain-1440.png) · [760](../current/v41-shots/24-case-delivery-plain-760.png) · [full](../current/v41-shots/24-case-delivery-plain-full.png) |
| Case Workspace — Delivery stop rule (proposal) | [1580](../current/v41-shots/25-case-delivery-stop-1580.png) · [1440](../current/v41-shots/25-case-delivery-stop-1440.png) · [760](../current/v41-shots/25-case-delivery-stop-760.png) · [full](../current/v41-shots/25-case-delivery-stop-full.png) |
| Case Workspace — Delivery missing To warning (proposal) | [1580](../current/v41-shots/26-case-delivery-missing-1580.png) · [1440](../current/v41-shots/26-case-delivery-missing-1440.png) · [760](../current/v41-shots/26-case-delivery-missing-760.png) · [full](../current/v41-shots/26-case-delivery-missing-full.png) |
| Case Workspace — Post-report open tasks in Next step (proposal) | [1580](../current/v41-shots/27-case-next-action-tasks-1580.png) · [1440](../current/v41-shots/27-case-next-action-tasks-1440.png) · [760](../current/v41-shots/27-case-next-action-tasks-760.png) · [full](../current/v41-shots/27-case-next-action-tasks-full.png) |
| Case Workspace — Tasks dialog & Send to AI dialog (proposal) | [1580](../current/v41-shots/28-case-tasks-dialog-1580.png) · [1440](../current/v41-shots/28-case-tasks-dialog-1440.png) · [760](../current/v41-shots/28-case-tasks-dialog-760.png) · [full](../current/v41-shots/28-case-tasks-dialog-full.png) |
| Case Workspace — Engineer read view (proposal) | [1580](../current/v41-shots/29-case-engineer-read-1580.png) · [1440](../current/v41-shots/29-case-engineer-read-1440.png) · [760](../current/v41-shots/29-case-engineer-read-760.png) · [full](../current/v41-shots/29-case-engineer-read-full.png) |
| Case Workspace — Engineer edit view (proposal) | [1580](../current/v41-shots/30-case-engineer-edit-1580.png) · [1440](../current/v41-shots/30-case-engineer-edit-1440.png) · [760](../current/v41-shots/30-case-engineer-edit-760.png) · [full](../current/v41-shots/30-case-engineer-edit-full.png) |
