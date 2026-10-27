# Case — panels

| Panel | Source | v42 Proposal |
| --- | --- | --- |
| Ribbon (`.case-ribbon`) | `Pages/Cases/Shared/_CaseRibbon.cshtml` | Purple `Query` stage chip stays while any query is open (**AA**); `Actions` menu keeps `Log query` (without the colleague-lease gate, **J**) and removes `Resolve query` (**K**). |
| Next action aside (`[data-next-action]`) | `Pages/Cases/Shared/_CaseAside.cshtml`, `Presentation/CaseNextAction.cs` | Query stage step reads **Answer query** with **Reply** (when the oldest open query is an e-mail, linking with `markQueryDone=true`) or **Mark done** (when logged) (**K**). `Cancellation received` row stays (**E**). |
| Files › Correspondence (`#case-files-correspondence`) | `Pages/Cases/Shared/_CaseCorrespondence.cshtml` | Column header `Classification` becomes **Type**; cells show `Correspondence` (or one of the three types) plus the e-mail's query chip (`Query` / `Done`); `Tag as query` becomes **Open query** once the report is sent (**N**, **X**, **AA**). |
| Queries (`#section-queries`) | `Pages/Cases/Shared/_CaseQueries.cshtml` | Columns `State`, `Raised`, `Raised by`, `Channel`, `Message`, **Assigned to**, **Done**; open rows carry `Mark done`, `Assign` and `Take` (plus `Open message`, `Reply` and AI draft controls for mail rows); closed rows carry the green **Done** chip and **Reopen** (**D**, **K**, **M**, **O**). |
