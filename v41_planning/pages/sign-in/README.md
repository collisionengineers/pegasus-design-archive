# Shared Shell, Auth, Consent, Error & Utility Pages

**Temporary v41 design review notes (14 October 2026).** Governing behaviour: [FRD-04](../../../pegasus/docs/frd/frd-04-parties-accounts-and-access.md) and [FRD-12](../../../pegasus/docs/frd/frd-12-operator-experience.md); presentation: [design authority](../../../pegasus/docs/design/README.md).

- **Routes**: `/Account/SignIn`, `/Account/SignOut`, `/Account/PasswordChange`, `/Account/AccessDenied`, `/Connect/Authorize`, `/Error`, `/StatusCode`, `/ReleaseNotes`, `/Notifications`, `/ProblemReports`, plus shared shell `_Layout.cshtml` & `_ShellDialogs.cshtml`
- **Interactive mockup**: [`pegasus_shell_v41.html`](../../current/pegasus_shell_v41.html) (`?state=auth-signin&design=proposal` vs `&design=today`)
- [how-it-works.md](how-it-works.md): live implementation on `origin/dev` and usability/design findings.
- [how-it-should-work.md](how-it-should-work.md): proposed v41 design, UI, and UX improvements.
- [states/README.md](states/README.md), [panels/README.md](panels/README.md), [dialogs/README.md](dialogs/README.md).

## Screenshots

| View | Captures (`1580×1000`, `1440×900`, `760×1000`, `1580` whole page) |
| --- | --- |
| Sign-in & Password Change (proposal) | [1580](../current/v41-shots/01-auth-signin-1580.png) · [1440](../current/v41-shots/01-auth-signin-1440.png) · [760](../current/v41-shots/01-auth-signin-760.png) · [full](../current/v41-shots/01-auth-signin-full.png) |
| OAuth Consent (proposal) | [1580](../current/v41-shots/02-auth-consent-1580.png) · [1440](../current/v41-shots/02-auth-consent-1440.png) · [760](../current/v41-shots/02-auth-consent-760.png) · [full](../current/v41-shots/02-auth-consent-full.png) |
| OAuth Consent (today) | [1580](../current/v41-shots/03-auth-consent-today-1580.png) · [1440](../current/v41-shots/03-auth-consent-today-1440.png) · [760](../current/v41-shots/03-auth-consent-today-760.png) · [full](../current/v41-shots/03-auth-consent-today-full.png) |
| Error, Status Code & Release Notes (proposal) | [1580](../current/v41-shots/04-auth-errors-1580.png) · [1440](../current/v41-shots/04-auth-errors-1440.png) · [760](../current/v41-shots/04-auth-errors-760.png) · [full](../current/v41-shots/04-auth-errors-full.png) |
| Shell Dialogs & Utility Bar (proposal) | [1580](../current/v41-shots/05-shell-dialogs-1580.png) · [1440](../current/v41-shots/05-shell-dialogs-1440.png) · [760](../current/v41-shots/05-shell-dialogs-760.png) · [full](../current/v41-shots/05-shell-dialogs-full.png) |
