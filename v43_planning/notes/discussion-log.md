# v43 discussion log

How the round came to be. This log is not design authority.

## 2 November 2026: the brief

The operator:

> Case page adjustments.
>
> Case Contact section - to remove. Include the extraction logic in the removal, not just
> the frontend. We dont need the case contact at all.
>
> "Claim Source" needs two notes sections - one for every case, and one for this case.
> They should be under the "Claim Source" container
>
> "Notes from client" - to remove
>
> Principal notes can go in its own container seperate from claim source
>
> The "Claim Source" section is actually erroneously labelled as Principal.

### What was explored

- The live Case details section (`_CaseOverview.cshtml` on `826c2aed7`) has four sub-panels:
  Case, a card headed *Principal* that holds the Claim source and its contact, *Case
  contact*, and a *Notes* band with the Principal's and Claim source's notes. The accident
  band holds Accident circumstances and Notes from client.
- **Case contact** is the Case data facts `contact_name`, `contact_email_address` and
  `contact_phone_number`. Two paths fill them at creation:
  1. R462's sender fill (`SenderContactFill`, PR #1781). It reads the instruction e-mail's
     sender and the first UK phone number below the sign-off.
  2. The Principal API's `fileHandler` block, through `InstructionDraft.FileHandler*`.

  Staff and the MCP Case-edit tool can also write them. No report prints them.
- **Notes from client** is the Case data fact `client_notes`. Only staff and the MCP
  Case-edit tool write it. No extraction fills it, and no report prints it.
- R462 (28 October 2026) kept Case contact extraction as a feature. This brief reverses it.

### Questions and answers

| Question | Answer |
| --- | --- |
| Where does the round live? The 15 October direction said `artifacts/`, but the skill and v42 use the archive. | **Design archive** |
| Where does the Principal notes container sit? | **Full-width band** (where the Notes band is today) |
| What is the container called? | **Principal** |
| What happens to stored Case contact and Notes from client values? | **Drop it** (destructive migration) |
| The Principal API `fileHandler` block feeds only the Case contact. Does it go too? | **Remove it** |

The operator also asked what notes or extraction logic exist for client notes. The answer
was none: staff and the MCP Case-edit tool are the only writers.

### Raised

Open items **F** (Accident circumstances width), **G** (this Case's Principal notes cell
when the record has none) and **H** (the DFD *Contact details if not client* review line).
See [v43-notes.md §6](v43-notes.md#6-sign-off).
