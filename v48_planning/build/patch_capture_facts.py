"""Patch the excluded ZzMockupCapture*.cs facts in the v48 capture worktree.

Applies the drift fixes against origin/dev 8da7957ce and adds the v48 fixture
(send history, the Inspection report's frozen outcome, salvage and guide, custody
file names, a second Outgoing mailbox, a facts JSON per capture) and the
CaptureV48* facts. Each replacement must match exactly once. CRLF is kept.

Run: python -I -X utf8 patch_capture_facts.py <worktree>
"""
from __future__ import annotations

import pathlib
import sys

WORKTREE = pathlib.Path(sys.argv[1])
TESTS = WORKTREE / "tests" / "Pegasus.IntegrationTests"
CASE = TESTS / "ZzMockupCaptureCase.cs"
SUPPORT = TESTS / "ZzMockupCaptureSupport.cs"


def patch(path: pathlib.Path, edits: list[tuple[str, str]]) -> None:
    text = path.read_bytes().decode("utf-8").replace("\r\n", "\n")
    for old, new in edits:
        count = text.count(old)
        if count != 1:
            raise SystemExit(f"{path.name}: expected one match, found {count}:\n{old[:160]}")
        text = text.replace(old, new)
    path.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))


SUPPORT_EDITS = [
    (
        '''        foreach (Match lazy in Regex.Matches(html, "data-lazy=\\"([a-z0-9-]+)\\""))
        {
            var key = lazy.Groups[1].Value;
            await SaveAsync($"{name}.section-{key}", $"/Cases/{caseId:D}/Section?section={key}");
        }
    }
''',
        '''        // v48: an Inspection view page fetches its lazy sections in that view too.
        var view = Regex.Match(query, "[?&]view=([a-z]+)") is { Success: true } viewed
            ? "&view=" + viewed.Groups[1].Value
            : string.Empty;
        foreach (Match lazy in Regex.Matches(html, "data-lazy=\\"([a-z0-9-]+)\\""))
        {
            var key = lazy.Groups[1].Value;
            await SaveAsync($"{name}.section-{key}", $"/Cases/{caseId:D}/Section?section={key}{view}");
        }
    }

    /// <summary>v48: the fixture facts the mockup build reads beside the capture, as <c>{name}.facts.json</c>.</summary>
    public Task SaveJsonAsync(string name, object facts) =>
        File.WriteAllTextAsync(
            Path.Combine(directory, name + ".facts.json"),
            System.Text.Json.JsonSerializer.Serialize(
                facts, new System.Text.Json.JsonSerializerOptions { WriteIndented = true }));
''',
    ),
]

CASE_EDITS = [
    # Drift: CaseInstructionEmail carries the mailbox address.
    (
        '''    private static CaseInstructionEmail InstructionFrom(ApprovedMailbox mailbox) => new(
        Guid.NewGuid(), mailbox.Id, "immutable-1", null, null,''',
        '''    private static CaseInstructionEmail InstructionFrom(ApprovedMailbox mailbox) => new(
        Guid.NewGuid(), mailbox.Id, mailbox.Address, "immutable-1", null, null,''',
    ),
    # Drift: ReportInstructionMessage carries the sender address; a second Outgoing mailbox (R655).
    (
        '''                "claims@northline.example", [], "Claim for AB12CDE — rear impact"),
            Outcome: "repairable");
        return new(facts, [engineers], InstructionFrom(engineers));''',
        '''                "claims@northline.example", [], "Claim for AB12CDE — rear impact",
                "claims@northline.example"),
            Outcome: "repairable");
        return new(
            facts,
            [engineers, OutgoingMailbox("desk@collisionengineers.example")],
            InstructionFrom(engineers));''',
    ),
    (
        '''                ["noreply@northline.example", "copy@northline.example"],
                "Claim for AB12CDE — rear impact"),''',
        '''                ["noreply@northline.example", "copy@northline.example"],
                "Claim for AB12CDE — rear impact", "claims@northline.example"),''',
    ),
    # Drift: ICaseInstructionEmailQueries.SendFromAsync.
    (
        '''    private sealed class RigInstruction(Guid caseId, CaseInstructionEmail? instruction) : ICaseInstructionEmailQueries
    {
        public Task<CaseInstructionEmail?> GetAsync(Guid ownerCaseId, CancellationToken cancellationToken) =>
            Task.FromResult(ownerCaseId == caseId ? instruction : null);
    }''',
        '''    private sealed class RigInstruction(Guid caseId, CaseInstructionEmail? instruction, string? sendFrom)
        : ICaseInstructionEmailQueries
    {
        public Task<CaseInstructionEmail?> GetAsync(Guid ownerCaseId, CancellationToken cancellationToken) =>
            Task.FromResult(ownerCaseId == caseId ? instruction : null);

        public Task<string?> SendFromAsync(Guid ownerCaseId, CancellationToken cancellationToken) =>
            Task.FromResult(ownerCaseId == caseId ? sendFrom : null);
    }''',
    ),
    (
        '''            Substitute<ICaseInstructionEmailQueries>(services, new RigInstruction(store.CaseId, routed.Instruction));''',
        '''            Substitute<ICaseInstructionEmailQueries>(
                services, new RigInstruction(store.CaseId, routed.Instruction, routed.Facts.Rules.SendFromMailbox));''',
    ),
    # v48 fixture parameters.
    (
        '''        bool bare = false,
        IReadOnlyDictionary<string, string>? report = null)
    {
        var messageId = Guid.NewGuid();''',
        '''        bool bare = false,
        IReadOnlyDictionary<string, string>? report = null,
        CaseReportSendHistory? sendHistory = null,
        AssessmentReportOutcome? primaryOutcome = null,
        decimal? primarySalvage = null,
        ValuationSource? primaryGuide = null,
        bool primaryCompanions = false)
    {
        var messageId = Guid.NewGuid();''',
    ),
    (
        '''                primary = Generation(store.CaseId, Reference, CaseWorkKind.Primary, store.CaseId);''',
        '''                primary = Generation(
                    store.CaseId, Reference, CaseWorkKind.Primary, store.CaseId,
                    primaryCompanions ? feeNote : null,
                    primaryCompanions ? repairSpec : null,
                    primaryCompanions ? imagePack : null);''',
    ),
    (
        '''        var history = sent
            ? new CaseReportSendHistory(1, new DateOnly(2031, 5, 5), 1, SentAt, ["claims@northline.example"])
            : CaseReportSendHistory.None;''',
        '''        var history = sendHistory ?? (sent
            ? new CaseReportSendHistory(1, new DateOnly(2031, 5, 5), 1, SentAt, ["claims@northline.example"])
            : CaseReportSendHistory.None);''',
    ),
    (
        '''            5000m, "A Patterson", At.AddMinutes(30), "Accepted the guide value",
            "case-valuation-calculation/v1");
''',
        '''            5000m, "A Patterson", At.AddMinutes(30), "Accepted the guide value",
            "case-valuation-calculation/v1");
        // v48: the Inspection's own guide card and accepted value, read in the Inspection view
        // and frozen in its report, so the Audit view's Original report card names it.
        var cazana = new CaseValuation(
            Guid.NewGuid(), store.CaseId,
            new ValuationDetails(
                ValuationSource.Cazana, new DateOnly(2031, 5, 6), new TimeOnly(9, 20),
                80_000, 5000m, 4100m, new DateOnly(2031, 5, 1)),
            "A Patterson", At.AddMinutes(5));
        var cazanaApplied = applied with
        {
            Id = Guid.NewGuid(),
            GuideValuationId = cazana.ValuationId,
            GuideValuationStampUtc = cazana.RecordedAtUtc
        };
        var primaryOnCazana = audit && primaryGuide == ValuationSource.Cazana;
        if (audit && primary is not null && primaryOutcome is { } frozenOutcome)
        {
            primary = primary with
            {
                Snapshot = OriginalReport(
                    primary.Snapshot, frozenOutcome, primarySalvage, primaryGuide,
                    primaryOnCazana ? cazanaApplied.Id : applied.Id)
            };
        }
        var facts = new
        {
            subject = ReportDispatchPolicy.Subject(routed.Facts),
            reference = Reference,
            registration = Registration,
            sentCount = history.SentCount,
            artifacts = ArtifactFacts(current),
            other = audit && primary is not null
                ? new
                {
                    reference = primary.Snapshot.CaseReference,
                    gross = primary.Snapshot.Costs.Totals.Printed.Gross,
                    outcome = primary.Snapshot.Report.Outcome.ToString(),
                    salvageCategory = primary.Snapshot.Report.SalvageCategory,
                    salvageValue = primary.Snapshot.Report.SalvageValue,
                    engineerValue = primary.Snapshot.EngineerValue,
                    guide = primaryGuide is { } guideSource ? ValuationPolicy.SourceName(guideSource) : null,
                    artifacts = ArtifactFacts(primary)
                }
                : null
        };
''',
    ),
    (
        '''            Substitute<IListCaseValuations>(services, new RigValuations([guide, engineersValue]));
            Substitute<IListAppliedValuations>(services, new RigApplied([applied]));''',
        '''            Substitute<IListCaseValuations>(
                services, new RigValuations([guide, engineersValue], primaryOnCazana ? [cazana, engineersValue] : null));
            Substitute<IListAppliedValuations>(
                services, new RigApplied([applied], primaryOnCazana ? [cazanaApplied] : null));''',
    ),
    (
        '''        return new(store, Ports);
    }

    // -------------------------------------------------------------------- data''',
        '''        return new(store, Ports, facts);
    }

    /// <summary>
    /// v48: the Inspection report as it was generated, with the outcome, salvage, guide and
    /// basis the Original report card reads. A total loss carries a repair cost above the value.
    /// </summary>
    private static CaseReportGenerationSnapshot OriginalReport(
        CaseReportGenerationSnapshot snapshot,
        AssessmentReportOutcome outcome,
        decimal? salvage,
        ValuationSource? guide,
        Guid appliedId)
    {
        var totalLoss = outcome == AssessmentReportOutcome.TotalLoss;
        var guides = guide is { } source ? new ReportGuideSources([source]) : snapshot.Guides;
        var totals = snapshot.Costs.Totals;
        var costs = totalLoss
            ? snapshot.Costs with
            {
                Totals = totals with
                {
                    Printed = totals.Printed with { Net = 6_541.67m, Vat = 1_308.33m, Gross = 7_850m }
                }
            }
            : snapshot.Costs;
        return snapshot with
        {
            Costs = costs,
            AppliedValuationId = guide is null ? snapshot.AppliedValuationId : appliedId,
            Guides = guides,
            Report = snapshot.Report with
            {
                Outcome = outcome,
                SalvageCategory = totalLoss ? "S" : null,
                SalvageValue = totalLoss ? salvage : null,
                Costs = costs,
                Guides = guides
            }
        };
    }

    private static object[] ArtifactFacts(CaseReportGenerationRecord? generation) =>
        generation is null
            ? []
            : [.. generation.Artifacts.Select(artifact => new
            {
                kind = artifact.Kind.ToString(),
                status = artifact.Status.ToString(),
                fileName = artifact.FileName
            })];

    // -------------------------------------------------------------------- data''',
    ),
    (
        '''    private sealed record Setup(RecordingCaseDetailsStore Store, Action<IServiceCollection> Ports);''',
        '''    private sealed record Setup(RecordingCaseDetailsStore Store, Action<IServiceCollection> Ports, object? Facts = null);''',
    ),
    # Every artifact carries its live custody name (CaseReportGeneration.FileNameOf).
    (
        '''                .. record.Artifacts.Select(artifact => artifact with
                {
                    FileName = artifact.FileName?.Replace("CE_100", reference, StringComparison.Ordinal)
                })''',
        '''                .. record.Artifacts.Select(artifact => artifact with
                {
                    FileName = CustodyName(reference, artifact.Kind)
                })''',
    ),
    (
        '''    // --------------------------------------------------------------- delivery
''',
        '''    /// <summary>The name custody files a generation's artifact under (CaseReportGeneration.FileNameOf).</summary>
    private static string CustodyName(string reference, CaseReportArtifactKind kind) =>
        new string(reference.ToUpperInvariant().Select(character => char.IsLetterOrDigit(character) ? character : '_').ToArray())
        + "_" + kind switch
        {
            CaseReportArtifactKind.AssessmentReport => "report",
            CaseReportArtifactKind.FeeNote => "fee_note",
            CaseReportArtifactKind.RepairSpecification => "repair_specification",
            CaseReportArtifactKind.ImagePack => "images",
            _ => "document",
        } + ".pdf";

    // --------------------------------------------------------------- delivery
''',
    ),
    # Work-aware valuation rigs.
    (
        '''    private sealed class RigValuations(IReadOnlyList<CaseValuation> items) : IListCaseValuations
    {
        public Task<IReadOnlyList<CaseValuation>> ExecuteAsync(
            Guid caseId, CaseWorkSelector work, CancellationToken cancellationToken) =>
            Task.FromResult(items);
    }

    private sealed class RigApplied(IReadOnlyList<AppliedValuation> items) : IListAppliedValuations
    {
        public Task<IReadOnlyList<AppliedValuation>> ExecuteAsync(
            Guid caseId, CaseWorkSelector work, CancellationToken cancellationToken) =>
            Task.FromResult(items);
    }''',
        '''    private sealed class RigValuations(
        IReadOnlyList<CaseValuation> items,
        IReadOnlyList<CaseValuation>? primaryItems = null) : IListCaseValuations
    {
        public Task<IReadOnlyList<CaseValuation>> ExecuteAsync(
            Guid caseId, CaseWorkSelector work, CancellationToken cancellationToken) =>
            Task.FromResult(work == CaseWorkSelector.Primary && primaryItems is not null ? primaryItems : items);
    }

    private sealed class RigApplied(
        IReadOnlyList<AppliedValuation> items,
        IReadOnlyList<AppliedValuation>? primaryItems = null) : IListAppliedValuations
    {
        public Task<IReadOnlyList<AppliedValuation>> ExecuteAsync(
            Guid caseId, CaseWorkSelector work, CancellationToken cancellationToken) =>
            Task.FromResult(work == CaseWorkSelector.Primary && primaryItems is not null ? primaryItems : items);
    }''',
    ),
    # The v48 facts.
    (
        '''    // ----------------------------------------------------------------- harness
''',
        '''    // v48: the Send report dialog and the Original report card (4 November 2026). Every
    // companion is Confirmed so Generate report leaves the Report head and the send form stands.
    private static readonly CaseReportSendHistory Resend =
        new(1, new DateOnly(2031, 5, 5), 1, SentAt, ["claims@northline.example"], ["office@northline.example"]);

    [Fact]
    public async Task CaptureV48PlainEdit() => await RunAsync("v48-plain-edit", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: PlainDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed, repairSpec: CaseReportArtifactStatus.Confirmed,
            imagePack: CaseReportArtifactStatus.Confirmed);
        await CaptureV48Async(setup, "v48-plain-edit", "?section=report", editing: true);
    });

    [Fact]
    public async Task CaptureV48PlainRead() => await RunAsync("v48-plain-read", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: PlainDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed, repairSpec: CaseReportArtifactStatus.Confirmed,
            imagePack: CaseReportArtifactStatus.Confirmed);
        await CaptureV48Async(setup, "v48-plain-read", "?section=report", editing: false);
    });

    [Fact]
    public async Task CaptureV48RulesEdit() => await RunAsync("v48-rules-edit", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: RulesDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed);
        await CaptureV48Async(setup, "v48-rules-edit", "?section=report", editing: true);
    });

    [Fact]
    public async Task CaptureV48StopEdit() => await RunAsync("v48-stop-edit", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: StopDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed);
        await CaptureV48Async(setup, "v48-stop-edit", "?section=report", editing: true);
    });

    [Fact]
    public async Task CaptureV48MissingEdit() => await RunAsync("v48-missing-edit", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: MissingDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed, repairSpec: CaseReportArtifactStatus.Confirmed);
        await CaptureV48Async(setup, "v48-missing-edit", "?section=report", editing: true);
    });

    [Fact]
    public async Task CaptureV48ResendEdit() => await RunAsync("v48-resend-edit", async () =>
    {
        var setup = Build(
            CaseLifecycleState.ReportPreparation, delivery: PlainDelivery(),
            feeNote: CaseReportArtifactStatus.Confirmed, repairSpec: CaseReportArtifactStatus.Confirmed,
            imagePack: CaseReportArtifactStatus.Confirmed, sendHistory: Resend);
        await CaptureV48Async(setup, "v48-resend-edit", "?section=report", editing: true);
    });

    private static Setup AuditSetup(AssessmentReportOutcome outcome) => Build(
        CaseLifecycleState.ReportPreparation,
        CaseType.InspectionAndAudit,
        delivery: PlainDelivery(),
        feeNote: CaseReportArtifactStatus.Confirmed,
        repairSpec: CaseReportArtifactStatus.Confirmed,
        imagePack: CaseReportArtifactStatus.Confirmed,
        audit: true,
        primaryOutcome: outcome,
        primarySalvage: outcome == AssessmentReportOutcome.TotalLoss ? 1250m : null,
        primaryGuide: outcome == AssessmentReportOutcome.TotalLoss ? ValuationSource.Cazana : ValuationSource.Glasses,
        primaryCompanions: true);

    [Fact]
    public async Task CaptureV48AuditEdit() => await RunAsync("v48-audit-edit", async () =>
    {
        var setup = AuditSetup(AssessmentReportOutcome.TotalLoss);
        using var workspace = await EnterEngineerEditModeAsync(setup.Store, setup.Ports, keepDatabase: true);
        workspace.Client.DefaultRequestHeaders.Add("X-Pegasus-Edit-Lease", setup.Store.LeaseToken);
        var capture = new ZzMockupCapture(workspace.Client, Lane);
        await capture.SaveCaseAsync("v48-audit-edit", setup.Store.CaseId, "?section=report");
        await capture.SaveJsonAsync("v48-audit-edit", setup.Facts!);
        await capture.SaveCaseAsync("v48-audit-inspection", setup.Store.CaseId, "?section=report&view=inspection");
        await capture.SaveJsonAsync("v48-audit-inspection", setup.Facts!);
    });

    [Fact]
    public async Task CaptureV48AuditRead() => await RunAsync("v48-audit-read", async () =>
    {
        var setup = AuditSetup(AssessmentReportOutcome.TotalLoss);
        await CaptureV48Async(setup, "v48-audit-read", "?section=report", editing: false);
    });

    [Fact]
    public async Task CaptureV48AuditRepairable() => await RunAsync("v48-audit-repairable-read", async () =>
    {
        var setup = AuditSetup(AssessmentReportOutcome.Repairable);
        await CaptureV48Async(setup, "v48-audit-repairable-read", "?section=report", editing: false);
    });

    private static async Task CaptureV48Async(Setup setup, string name, string query, bool editing)
    {
        if (editing)
        {
            await CaptureEditingAsync(setup, name, query);
        }
        else
        {
            using var workspace = await OpenEngineerWorkspaceAsync(setup.Store, setup.Ports, keepDatabase: true);
            await new ZzMockupCapture(workspace.Client, Lane).SaveCaseAsync(name, setup.Store.CaseId, query);
        }

        using var client = new HttpClient();
        await new ZzMockupCapture(client, Lane).SaveJsonAsync(name, setup.Facts!);
    }

    // ----------------------------------------------------------------- harness
''',
    ),
]

# Round 2: the frozen report names the Case's own registration and reference, as a live
# generation would, so the other work's report is named "{Case/PO} AB12CDE ..." on the form.
CASE_EDITS_ROUND2 = [
    (
        """            Snapshot = record.Snapshot with { CaseReference = reference },""",
        """            Snapshot = record.Snapshot with
            {
                CaseReference = reference,
                Report = record.Snapshot.Report with
                {
                    OurReference = reference,
                    Vehicle = record.Snapshot.Report.Vehicle with { Registration = Registration }
                }
            },""",
    ),
]

if "--round2" in sys.argv:
    patch(CASE, CASE_EDITS_ROUND2)
    print("patched round 2", CASE.name)
else:
    patch(SUPPORT, SUPPORT_EDITS)
    patch(CASE, CASE_EDITS)
    print("patched", CASE.name, SUPPORT.name)
