# Shell and sign-in

Today is the page captured from the application; it is not redrawn. The Proposal is the same page with the changes below.

| State | Page | Changes |
| --- | --- | --- |
| `auth-signin` | Sign in | none |
| `auth-signin-failed` | Sign in · refused | none |
| `auth-signed-out` | Signed out | none |
| `auth-password-forced` | Password change · required | S6 |
| `auth-password-voluntary` | Password change | S1, S3, S4, S6 |
| `auth-access-denied` | Access denied | none |
| `consent` | Connector consent | S5 |
| `error` | Error | none |
| `status-404` | Not found | S7 |
| `release-notes` | Release notes | S1, S2, S3, S4 |
| `whats-new` | What's new | S1, S2, S3, S4 |

## Changes

- **S1**: Release notes, Report a problem and Change password move into the Account dialog body; the foot keeps Close and Sign out.
- **S2**: Mark all read moves to the Notifications dialog head.
- **S3**: The command palette's Cases icon matches the rail's Cases icon.
- **S4**: The utility bar's freshness line goes; the rail health line keeps the one clock.
- **S5**: The raw scope identifiers go from the connector request; the descriptions stay. One scope's description (the intake scope's, not requested here) contains the word intake, which the interface does not use; its wording is left to Stage 2 PR 1 and is put to the operator when that PR is drafted.
- **S6**: Change password: the submit button sits directly in the form, full width as on sign-in, and each password field gets the Show/Hide control.
- **S7**: The Not found page's one action is the primary button.
