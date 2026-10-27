# Work Centre — panels

| Panel | Source | v42 Proposal |
| --- | --- | --- |
| Kind filter chips (`nav.wc-filters`) | `Pages/Shared/_WorkCentreBody.cshtml`, `Presentation/NeedsAttentionPresentation.cs` | Adds the `Query` kind chip (`data-wc-kind="query"`) (**P**). |
| Needs attention ledger (`#wc-panel-attention`) | `Pages/Shared/_WorkCentreBody.cshtml`, `Core/Operations/OperationsSnapshot.cs` | Adds one row per open query (`data-wc-row-kind="query"`): Unassigned open queries appear on the `Office` view with **Open query** (`/Cases/{id}?section=queries`) and **Take** (`/?handler=TakeQuery`); open queries assigned to the viewer appear in `Mine` with **Open query** (**P**). |
| Cases › Queries (`/Cases?stage=query`) | `Pages/Cases/Index.cshtml` | Unchanged: keeps one row per Case in the `Query` stage (**P**). |
