"""Build #mailMessageDialog (_MessageDialog.cshtml) fragments and Inbox ledger rows for m1..m17.

In the live application (v41 Stage 2), clicking an e-mail row on /Inbox fetches
/Inbox/{id}?handler=Dialog and mounts #mailMessageDialog into [data-mail-dialog-root].
This module builds:
  - Today's #mailMessageDialog fragments (1080px split dialog with the 380px right-hand
    Decision sidebar and twelve Classification chips).
  - Proposal's #mailMessageDialog fragments (880px full-width reading dialog with the
    header sender/context strip and the streamlined #icon-settings cog menu where
    Email type is a single 1-step <select> combining Type and Case type).
  - Attachments, Thread and Reply / Reply all / Forward composer views for every message.
"""
from __future__ import annotations

import copy
import html as html_mod
import pathlib

from bs4 import BeautifulSoup, Tag

CAPTURED_INBOX = pathlib.Path(__file__).resolve().parent.parent / "captured-live" / "inbox"

# Streamlined 1-step Email type options (replaces the old clicky chip cloud + second Case type select).
EMAIL_TYPE_OPTIONS: list[tuple[str, str, str]] = [
    ("correspondence", "Correspondence", "Correspondence"),
    ("new-instruction:Inspection", "New instruction · Inspection", "New instruction · Inspection"),
    ("new-instruction:Audit", "New instruction · Audit", "New instruction · Audit"),
    ("new-instruction:InspectionAndAudit", "New instruction · Inspection and Audit", "New instruction · Inspection and Audit"),
    ("triage-request", "Triage request", "Triage request"),
    ("cancellation", "Cancellation", "Cancellation"),
]

# Rich fixtures across All, No Case Found and Dismissed scopes.
FIXTURES: dict[str, dict] = {
    "m1": {
        "default_id": "e6fdec5c-c0f7-478e-a5b5-be72f2cfcef6",
        "sender": "instructions@northline.example",
        "sender_name": "Northline Instructions",
        "principal": "Northline",
        "mailbox": "instructions@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "New instruction — MA59 BDY — rear impact",
        "excerpt": "Please instruct an engineer to inspect our insured vehicle following a rear impact on 24 September.",
        "body": (
            "Please instruct an engineer to inspect our insured vehicle following a rear impact on 24 September.\n"
            "The vehicle is at the policyholder's address (Ford Focus, registration MA59 BDY). "
            "Two initial photographs from the policyholder are attached."
        ),
        "date": "13 Oct 2026",
        "clock": "09:14",
        "time": "13 Oct 2026 09:14",
        "iso": "2026-10-13T09:14:00.0000000+01:00",
        "decided": "13 Oct 2026 09:16",
        "category": "New instruction",
        "code": "new-instruction",
        "type_value": "new-instruction:Inspection",
        "type_label": "New instruction · Inspection",
        "short_type": "New instruction",
        "work_type_sub": "Inspection",
        "case_ref": None,
        "case_id": None,
        "vehicle": "Ford Focus · MA59 BDY",
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("all", "no_case_found"),
        "unread": True,
        "attachments": [
            ("rear-quarter.jpg", "image/jpeg", "1.2 MB", "Pending Case"),
            ("odometer.jpg", "image/jpeg", "400 KB", "Pending Case"),
        ],
        "thread": ["m1", "m5"],
    },
    "m13": {
        "default_id": "a1300000-0000-4000-8000-000000000013",
        "sender": "triage@qdos.example",
        "sender_name": "QDOS Triage Desk",
        "principal": "QDOS",
        "mailbox": "instructions@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Triage request — BK21 XYZ — total loss check",
        "excerpt": "Early total-loss triage requested on BK21 XYZ before recovery to storage.",
        "body": (
            "Please carry out an early triage review on BK21 XYZ (Peugeot 208).\n"
            "First notification of loss summary is attached; please confirm whether the vehicle is a likely total loss before recovery."
        ),
        "date": "13 Oct 2026",
        "clock": "08:36",
        "time": "13 Oct 2026 08:36",
        "iso": "2026-10-13T08:36:00.0000000+01:00",
        "decided": "13 Oct 2026 08:37",
        "category": "Triage request",
        "code": "triage-request",
        "type_value": "triage-request",
        "type_label": "Triage request",
        "short_type": "Triage request",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": "Peugeot 208 · BK21 XYZ",
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("all", "no_case_found"),
        "unread": True,
        "attachments": [
            ("fnol-summary.pdf", "application/pdf", "185 KB", "Pending Triage"),
        ],
        "thread": ["m13"],
    },
    "m2": {
        "default_id": "9d1e6d82-99a6-4a87-bc4d-3a2df59efe0f",
        "sender": "claims@northline.example",
        "sender_name": "Northline Claims",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Update — QDOS26214 — repair authority",
        "excerpt": "Repair authority is attached. Please proceed on QDOS26214 and confirm the engineer.",
        "body": "Repair authority is attached. Please proceed on QDOS26214 and confirm the engineer.",
        "date": "13 Oct 2026",
        "clock": "08:02",
        "time": "13 Oct 2026 08:02",
        "iso": "2026-10-13T08:02:00.0000000+01:00",
        "decided": "13 Oct 2026 08:04",
        "category": "Case update",
        "code": "case-update",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "Ford Focus · MA59 BDY",
        "suggested_case": None,
        "query_state": "offer",
        "query_assignee": None,
        "scopes": ("all",),
        "unread": False,
        "attachments": [
            ("repair-authority.pdf", "application/pdf", "210 KB", "Attached to QDOS26214"),
        ],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m14": {
        "default_id": "a1400000-0000-4000-8000-000000000014",
        "sender": "settlements@qdos.example",
        "sender_name": "QDOS Settlements",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "PAV dispute — QDOS26190 — PO16DDF valuation challenge",
        "excerpt": "The policyholder disputes the pre-accident valuation figure of £8,450; three market adverts attached.",
        "body": (
            "The policyholder disputes the pre-accident valuation figure of £8,450 on QDOS26190 (Mercedes A180 PO16DDF).\n"
            "Three comparable retail adverts supplied by the policyholder are attached for the engineer's review."
        ),
        "date": "13 Oct 2026",
        "clock": "06:15",
        "time": "13 Oct 2026 06:15",
        "iso": "2026-10-13T06:15:00.0000000+01:00",
        "decided": "13 Oct 2026 06:16",
        "category": "Query",
        "code": "query",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": "QDOS26190",
        "case_id": "2dc71cf4-debc-403d-be99-241d73c16bd2",
        "vehicle": "Mercedes A180 · PO16 DDF",
        "suggested_case": None,
        "query_state": "open",
        "query_assignee": "e.mawdsley",
        "scopes": ("all",),
        "unread": True,
        "attachments": [
            ("market-comparables.pdf", "application/pdf", "540 KB", "Attached to QDOS26190"),
        ],
        "thread": ["m14"],
    },
    "m11": {
        "default_id": "23707566-25cb-4004-ae26-604014fb2a95",
        "sender": "claims@meridian.example",
        "sender_name": "Meridian Claims",
        "principal": "Meridian",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Cancellation — QDOS26220",
        "excerpt": "Please cancel the instruction on QDOS26220. The claim has been withdrawn.",
        "body": "Please cancel the instruction on QDOS26220. The claim has been withdrawn by the insured.",
        "date": "13 Oct 2026",
        "clock": "04:48",
        "time": "13 Oct 2026 04:48",
        "iso": "2026-10-13T04:48:00.0000000+01:00",
        "decided": "13 Oct 2026 04:50",
        "category": "Cancellation",
        "code": "cancellation",
        "type_value": "cancellation",
        "type_label": "Cancellation",
        "short_type": "Cancellation",
        "work_type_sub": None,
        "case_ref": "QDOS26220",
        "case_id": "bee37ce3-c710-4a5b-8e2c-67e8ed6ad8cb",
        "vehicle": "Vauxhall Corsa · LK21 ABC",
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("all",),
        "unread": True,
        "attachments": [],
        "thread": ["m11"],
    },
    "m12": {
        "default_id": "83cf8571-6828-488f-b0e3-ab69c09cab24",
        "sender": "claims@northline.example",
        "sender_name": "Northline Claims",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Re: QDOS26214 — thank you",
        "excerpt": "Thank you for the report on QDOS26214.",
        "body": "Thank you for the report on QDOS26214. We have passed the findings to the policyholder.",
        "date": "13 Oct 2026",
        "clock": "04:03",
        "time": "13 Oct 2026 04:03",
        "iso": "2026-10-13T04:03:00.0000000+01:00",
        "decided": "13 Oct 2026 04:05",
        "category": "Case update",
        "code": "case-update",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "Ford Focus · MA59 BDY",
        "suggested_case": None,
        "query_state": "offer",
        "query_assignee": None,
        "scopes": ("all",),
        "unread": True,
        "attachments": [],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m4": {
        "default_id": "62334696-72a8-4bb9-9815-f8c76bb24d73",
        "sender": "claims@northline.example",
        "sender_name": "Northline Claims",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Query — QDOS26214 — hire charges",
        "excerpt": "Please explain the hire charges on the report for QDOS26214.",
        "body": "Please explain the hire charges on the report for QDOS26214. The credit hire company has queried the 14-day period.",
        "date": "12 Oct 2026",
        "clock": "11:20",
        "time": "12 Oct 2026 11:20",
        "iso": "2026-10-12T11:20:00.0000000+01:00",
        "decided": "12 Oct 2026 11:22",
        "category": "Query",
        "code": "query",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "Ford Focus · MA59 BDY",
        "suggested_case": None,
        "query_state": "open",
        "query_assignee": "Unassigned",
        "scopes": ("all",),
        "unread": False,
        "attachments": [],
        "thread": ["m2", "m12", "m4", "m6"],
    },
    "m15": {
        "default_id": "a1500000-0000-4000-8000-000000000015",
        "sender": "instructions@connexus.example",
        "sender_name": "Connexus Instructions",
        "principal": "Connexus",
        "mailbox": "instructions@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Instruction — PCH26102 — EF56 GHJ — bodyshop audit & inspection",
        "excerpt": "Combined inspection and Audatex estimate audit for BMW 320d EF56 GHJ.",
        "body": (
            "Please carry out an inspection and Audatex estimate audit on PCH26102 (BMW 320d, EF56 GHJ).\n"
            "The repairer's Audatex pack and instruction sheet are attached."
        ),
        "date": "12 Oct 2026",
        "clock": "09:45",
        "time": "12 Oct 2026 09:45",
        "iso": "2026-10-12T09:45:00.0000000+01:00",
        "decided": "12 Oct 2026 09:46",
        "category": "New instruction",
        "code": "new-instruction",
        "type_value": "new-instruction:InspectionAndAudit",
        "type_label": "New instruction · Inspection and Audit",
        "short_type": "New instruction",
        "work_type_sub": "Inspection and Audit",
        "case_ref": "PCH26102",
        "case_id": "8a63804e-c66d-4725-a5db-312d9870311e",
        "vehicle": "BMW 320d · EF56 GHJ",
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("all",),
        "unread": False,
        "attachments": [
            ("instruction-sheet.pdf", "application/pdf", "145 KB", "Attached to PCH26102"),
            ("audatex-estimate.pdf", "application/pdf", "490 KB", "Attached to PCH26102"),
        ],
        "thread": ["m15"],
    },
    "m3": {
        "default_id": "483d0560-44c8-4a82-bfe8-4aaafddc0910",
        "sender": "Sender not recorded",
        "sender_name": "Sender not recorded",
        "principal": None,
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Please see attached",
        "excerpt": "Photographs attached. No reference in the message.",
        "body": "Photographs attached. No reference in the message.",
        "date": "12 Oct 2026",
        "clock": "17:48",
        "time": "12 Oct 2026 17:48",
        "iso": "2026-10-12T17:48:00.0000000+01:00",
        "decided": "12 Oct 2026 17:50",
        "category": "Unclassified",
        "code": "unclassified",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": None,
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [
            ("IMG_0001.jpg", "image/jpeg", "900 KB", "No Case Found"),
            ("IMG_0002.jpg", "image/jpeg", "870 KB", "No Case Found"),
            ("IMG_0003.jpg", "image/jpeg", "880 KB", "No Case Found"),
        ],
        "thread": ["m3"],
    },
    "m5": {
        "default_id": "045b9b39-e285-4203-bb0f-fcdadca338f5",
        "sender": "photos@northline.example",
        "sender_name": "Northline Photos",
        "principal": "Northline",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Images — MA59 BDY",
        "excerpt": "Further photographs of the rear quarter and the odometer.",
        "body": "Further photographs of the rear quarter and the odometer for MA59 BDY.",
        "date": "11 Oct 2026",
        "clock": "15:05",
        "time": "11 Oct 2026 15:05",
        "iso": "2026-10-11T15:05:00.0000000+01:00",
        "decided": "11 Oct 2026 15:07",
        "category": "Images received",
        "code": "images-received",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": "MA59 BDY",
        "suggested_case": "QDOS26214",
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [
            ("rear-quarter-2.jpg", "image/jpeg", "1.1 MB", "No Case Found"),
            ("odometer-2.jpg", "image/jpeg", "380 KB", "No Case Found"),
        ],
        "thread": ["m1", "m5"],
    },
    "m7": {
        "default_id": "8e72669b-d126-4139-ade9-045c5033448a",
        "sender": "accounts@northline.example",
        "sender_name": "Northline Accounts",
        "principal": "Northline",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Remittance advice — October",
        "excerpt": "Please find attached our remittance advice for October.",
        "body": "Please find attached our remittance advice for October.",
        "date": "13 Oct 2026",
        "clock": "07:41",
        "time": "13 Oct 2026 07:41",
        "iso": "2026-10-13T07:41:00.0000000+01:00",
        "decided": "13 Oct 2026 07:43",
        "category": "Billing",
        "code": "billing",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": None,
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [],
        "thread": ["m7"],
    },
    "m8": {
        "default_id": "eb10d65e-a0ab-4fd1-861b-f4b1e74a6d3a",
        "sender": "news@toolvendor.example",
        "sender_name": "ToolVendor Digest",
        "principal": None,
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Your October product update",
        "excerpt": "New diagnostic tools are now available. View our catalogue online.",
        "body": "New diagnostic tools are now available. View our catalogue online.",
        "date": "13 Oct 2026",
        "clock": "06:30",
        "time": "13 Oct 2026 06:30",
        "iso": "2026-10-13T06:30:00.0000000+01:00",
        "decided": "13 Oct 2026 06:32",
        "category": "Not client related",
        "code": "not-client-related",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": None,
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [],
        "thread": ["m8"],
    },
    "m9": {
        "default_id": "cd1db358-5da7-4fc2-8dad-2505b651d980",
        "sender": "alex@collisionengineers.co.uk",
        "sender_name": "Alex (Collision Engineers)",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "FW: QDOS26214 — engineer note",
        "excerpt": "Forwarding for the file. Engineer's note on the rear quarter.",
        "body": "Forwarding for the file. Engineer's note on the rear quarter of MA59 BDY.",
        "date": "13 Oct 2026",
        "clock": "05:55",
        "time": "13 Oct 2026 05:55",
        "iso": "2026-10-13T05:55:00.0000000+01:00",
        "decided": "13 Oct 2026 05:57",
        "category": "Internal CC",
        "code": "internal-cc",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": "MA59 BDY",
        "suggested_case": "QDOS26214",
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [],
        "thread": ["m9"],
    },
    "m10": {
        "default_id": "7d660597-3f9f-46b3-94a8-a0b1c1cb05df",
        "sender": "claims@northline.example",
        "sender_name": "Northline Claims",
        "principal": "Northline",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Possible instruction — LK21 ABC",
        "excerpt": "We may need an inspection on LK21 ABC next week. We will confirm.",
        "body": "We may need an inspection on LK21 ABC next week. We will confirm once the policyholder responds.",
        "date": "13 Oct 2026",
        "clock": "05:12",
        "time": "13 Oct 2026 05:12",
        "iso": "2026-10-13T05:12:00.0000000+01:00",
        "decided": "13 Oct 2026 05:14",
        "category": "Pre-instruction",
        "code": "pre-instruction",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": "LK21 ABC",
        "suggested_case": "QDOS26220",
        "query_state": None,
        "query_assignee": None,
        "scopes": ("no_case_found",),
        "unread": True,
        "attachments": [],
        "thread": ["m10"],
    },
    "m16": {
        "default_id": "a1600000-0000-4000-8000-000000000016",
        "sender": "autotest@meridian.example",
        "sender_name": "Meridian Claims (Auto-reply)",
        "principal": "Meridian",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Automatic reply: Out of office until 16 October",
        "excerpt": "Thank you for your e-mail. I am away from the office until 16 October.",
        "body": "Thank you for your e-mail. I am away from the office until 16 October. For urgent claims please contact claims@meridian.example.",
        "date": "11 Oct 2026",
        "clock": "09:00",
        "time": "11 Oct 2026 09:00",
        "iso": "2026-10-11T09:00:00.0000000+01:00",
        "decided": "11 Oct 2026 09:01",
        "category": "Unclassified",
        "code": "unclassified",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": None,
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("dismissed",),
        "unread": False,
        "attachments": [],
        "thread": ["m16"],
    },
    "m17": {
        "default_id": "a1700000-0000-4000-8000-000000000017",
        "sender": "noreply@bodyshopdigest.example",
        "sender_name": "Bodyshop Weekly Digest",
        "principal": None,
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "desk@collisionengineers.co.uk",
        "subject": "Weekly bodyshop & repair network bulletin — Issue 41",
        "excerpt": "Parts supply lead times, paint index updates and industry news for October.",
        "body": "Parts supply lead times, paint index updates and industry news for October. Unsubscribe at any time.",
        "date": "10 Oct 2026",
        "clock": "16:20",
        "time": "10 Oct 2026 16:20",
        "iso": "2026-10-10T16:20:00.0000000+01:00",
        "decided": "10 Oct 2026 16:21",
        "category": "Not client related",
        "code": "not-client-related",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": None,
        "case_id": None,
        "vehicle": None,
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": ("dismissed",),
        "unread": False,
        "attachments": [],
        "thread": ["m17"],
    },
    "m6": {
        "default_id": "d06bad64-1077-4aaa-aadb-46edc1e8438c",
        "sender": "desk@collisionengineers.co.uk",
        "sender_name": "Collision Engineers",
        "principal": "QDOS",
        "mailbox": "desk@collisionengineers.co.uk",
        "to": "claims@northline.example",
        "subject": "Re: QDOS26214 — engineer's report",
        "excerpt": "The engineer's report is attached.",
        "body": "The engineer's report for QDOS26214 (Ford Focus MA59 BDY) is attached.",
        "date": "10 Oct 2026",
        "clock": "14:11",
        "time": "10 Oct 2026 14:11",
        "iso": "2026-10-10T14:11:00.0000000+01:00",
        "decided": "10 Oct 2026 14:11",
        "category": "Unclassified",
        "code": "unclassified",
        "type_value": "correspondence",
        "type_label": "Correspondence",
        "short_type": "Correspondence",
        "work_type_sub": None,
        "case_ref": "QDOS26214",
        "case_id": "85de4c48-ed02-445f-a2ce-d97a087c19dd",
        "vehicle": "Ford Focus · MA59 BDY",
        "suggested_case": None,
        "query_state": None,
        "query_assignee": None,
        "scopes": (),
        "unread": False,
        "attachments": [
            ("QDOS26214_report.pdf", "application/pdf", "640 KB", "Sent"),
        ],
        "thread": ["m2", "m12", "m4", "m6"],
    },
}


def load_ids() -> dict[str, str]:
    ids: dict[str, str] = {k: fx["default_id"] for k, fx in FIXTURES.items()}
    notes = CAPTURED_INBOX / "notes.txt"
    if notes.exists():
        for line in notes.read_text(encoding="utf-8").splitlines():
            parts = line.strip().split("\t")
            if len(parts) == 2:
                ids[parts[0]] = parts[1]
    return ids


def _frag(markup: str) -> Tag:
    soup = BeautifulSoup(f"<div>{markup}</div>", "lxml")
    return soup.div


def _normalize_icons(root: Tag) -> None:
    for use in root.select("use[href]"):
        href = use["href"]
        if "lucide-sprite" in href and "#" in href:
            use["href"] = "#" + href.split("#", 1)[1]


def _synthesize_message_page(key: str, msg_id: str, template_body: Tag, template_id: str) -> Tag:
    """Create a synthetic Message.cshtml body for fixtures without a captured message-mX.html."""
    fx = FIXTURES[key]
    raw = str(template_body).replace(template_id, msg_id)
    doc = BeautifulSoup(raw, "lxml").body
    for h in doc.select("header.page-header h1, header.record-head h2"):
        h.string = fx["subject"]
    spans = doc.select("header.record-head .record-identity > span")
    if len(spans) >= 3:
        spans[0].string = fx["sender"]
        t = spans[2].select_one("time")
        if t is not None:
            t["datetime"] = fx["iso"]
            t.string = fx["time"]
    body_div = doc.select_one(".mail-body")
    if body_div is not None:
        body_div.clear()
        for line in fx["body"].split("\n"):
            p = BeautifulSoup(f"<p>{html_mod.escape(line)}</p>", "lxml").p
            body_div.append(p)
    # Case row in Decision
    for row in doc.select("section.mail-decision .decision-row"):
        sp = row.find("span")
        if sp and sp.get_text(" ", strip=True) == "Case":
            st = row.find("strong")
            if st is not None:
                st.clear()
                if fx["case_ref"] and fx["case_id"]:
                    st.attrs.pop("class", None)
                    st.append(_frag(f'<a href="/Cases/{fx["case_id"]}">{fx["case_ref"]}</a>').a)
                else:
                    st["class"] = ["quiet"]
                    st.string = "None"
    # Attachments tab badge
    att_tab = doc.select_one('nav.tabs a[href*="section=attachments"]')
    if att_tab is not None:
        att_tab.clear()
        att_tab.append("Attachments")
        if fx["attachments"]:
            att_tab.append(_frag(f' <span class="tab-count">{len(fx["attachments"])}</span>').span)
    # Classification chips in Today
    chips = doc.select_one("#mailClassificationForm .mail-chips")
    if chips is not None:
        all_opts = [
            ("new-instruction", "New instruction"),
            ("triage-request", "Triage request"),
            ("pre-instruction", "Pre-instruction"),
            ("images-received", "Images received"),
            ("case-update", "Case update"),
            ("cancellation", "Cancellation"),
            ("query", "Query"),
            ("billing", "Billing"),
            ("general", "General"),
            ("not-client-related", "Not client related"),
            ("internal-cc", "Internal CC"),
            ("unclassified", "Unclassified"),
        ]
        chips.clear()
        for code, label in all_opts:
            if code == fx["code"]:
                chips.append(_frag(
                    '<button type="button" class="chip" aria-pressed="true">'
                    '<svg class="icon" aria-hidden="true"><use href="#icon-check"></use></svg>'
                    f'<span>{label}</span></button>'
                ).button)
            else:
                chips.append(_frag(
                    f'<button type="submit" class="chip" name="ClassificationKey" value="{code}" '
                    f'aria-pressed="false" data-busy-label="Saving…">{label}</button>'
                ).button)
    # Footer offered action for synthetic fixtures
    foot = doc.select_one(".dialog-foot")
    if foot is not None:
        if key == "m5":
            foot.append(_frag(
                '<button class="btn btn--dark" type="button" data-offered-action="RegisterImages" '
                'data-dialog-open="messageRegisterImagesDialog">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-image"></use></svg>'
                '<span>Register images</span></button>'
            ).button)
        elif key == "m13":
            foot.append(_frag(
                '<button class="btn btn--dark" type="button" data-offered-action="OpenTriage" '
                'data-dialog-open="messageTriageDialog">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-clipboard-list"></use></svg>'
                '<span>Open the Triage</span></button>'
            ).button)
        elif key == "m14":
            foot.append(_frag(
                f'<form method="post" action="/Inbox/{msg_id}?handler=CreateQueryResponse">'
                '<button class="btn btn--dark" type="submit" data-busy-label="Drafting…">'
                '<svg class="icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>'
                '<span>Draft reply with AI</span></button></form>'
            ).form)
    _normalize_icons(doc)
    return doc


def page_to_dialog_wrapper(page_body: Tag, key: str, msg_id: str, *, composing_mode: str | None = None) -> Tag:
    """Convert a Message.cshtml body into a wrapper <div> holding #mailMessageDialog + nested dialogs."""
    fx = FIXTURES[key]
    doc = copy.copy(page_body)
    _normalize_icons(doc)
    article = doc.select_one("article.record")
    tabs = article.select_one("nav.tabs")
    rec_body = article.select_one("div.record-body")
    foot = article.select_one("div.dialog-foot")

    inner_hdr = rec_body.select_one(".mail-read > .mail-header")
    if inner_hdr is not None:
        inner_hdr.decompose()
    rec_body["class"] = ["dialog-body"]

    dismiss_form = foot.select_one("form[data-message-dismissal]") if foot else None
    if dismiss_form is not None and dismiss_form.select_one("[data-mail-next-id]") is None:
        dismiss_form.append(_frag('<input type="hidden" name="next" value="" data-mail-next-id>').input)

    if composing_mode:
        label_map = {"reply": "Reply", "reply-all": "Reply all", "forward": "Forward"}
        prefix = f"{label_map.get(composing_mode, 'Reply')} · "
        title_html = (
            f'<div class="mail-dialog-title">'
            f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
            f'{html_mod.escape(prefix + fx["subject"])}</h2></div>'
        )
        tools_html = (
            '<span class="mail-dialog-tools">'
            '<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button></span>'
        )
        composer = rec_body.select_one("form#mailComposerForm")
        if composer is not None:
            composer["class"] = ["stack", "mail-compose"]
            ph = composer.select_one(".panel-head")
            if ph is not None:
                ph.decompose()
            pb = composer.select_one(".panel-body")
            if pb is not None:
                pb["class"] = ["stack"]
            br = composer.select_one(".button-row")
            if br is not None:
                br.decompose()
            split = rec_body.select_one(".mail-split")
            if split is not None:
                split.decompose()
        tabs = None
        foot = _frag(
            f'<div class="dialog-foot">'
            f'<a class="btn" href="/Inbox/{msg_id}" data-mail-dialog-link>Cancel</a>'
            f'<button type="submit" form="mailComposerForm" class="btn btn--dark" data-busy-label="Sending…">'
            f'<svg class="icon" aria-hidden="true"><use href="#icon-send"></use></svg><span>Send</span></button>'
            f'</div>'
        ).div
    else:
        title_html = (
            f'<div class="mail-dialog-title">'
            f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
            f'{html_mod.escape(fx["subject"])}</h2>'
            f'<p class="mail-route">From {html_mod.escape(fx["sender"])} · To {html_mod.escape(fx["to"])} · '
            f'<time datetime="{fx["iso"]}">{fx["time"]}</time></p></div>'
        )
        tools_html = (
            '<span class="mail-dialog-tools">'
            '<span class="cluster mail-dialog-nav">'
            '<button type="button" class="icon-button" data-mail-previous aria-label="Previous message" title="Previous message">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-chevron-left"></use></svg></button>'
            '<button type="button" class="icon-button" data-mail-next aria-label="Next message" title="Next message">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-chevron-right"></use></svg></button>'
            '</span>'
            '<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
            '<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button>'
            '</span>'
        )

    wrapper = _frag(
        f'<div id="mailMessageDialog" class="dialog-backdrop" data-dialog="mailMessageDialog" '
        f'data-mail-message="{msg_id}" data-mail-key="{key}" hidden>'
        f'<section class="dialog dialog--mail" role="dialog" aria-modal="true" aria-labelledby="mailMessageDialog_title">'
        f'<div class="dialog-head">{title_html}{tools_html}</div>'
        f'</section></div>'
    )
    section = wrapper.select_one("section.dialog--mail")
    if tabs is not None:
        section.append(tabs.extract())
    section.append(rec_body.extract())
    if foot is not None:
        section.append(foot.extract() if foot.parent else foot)

    for nested in doc.select("main .dialog-backdrop, body > .dialog-backdrop"):
        nid = nested.get("id") or ""
        if nid in ("linkCaseDialog", "changeLinkedCaseDialog", "unlinkCaseDialog",
                   "messageTriageDialog", "messageRegisterImagesDialog"):
            wrapper.append(nested.extract())
    return wrapper


def build_attachments_view(dialog_wrapper: Tag, key: str, msg_id: str) -> Tag:
    """Return a copy of dialog_wrapper showing the Attachments tab."""
    fx = FIXTURES[key]
    clone = copy.copy(dialog_wrapper)
    for tab in clone.select("nav.tabs a.tab"):
        if "section=attachments" in tab.get("href", ""):
            tab["aria-current"] = "page"
        else:
            tab.attrs.pop("aria-current", None)
    body = clone.select_one(".dialog-body")
    body.clear()
    if not fx["attachments"]:
        body.append(_frag('<div class="empty"><p>This message has no attachments.</p></div>').div)
    else:
        rows_html = []
        for fname, mime, size, outcome in fx["attachments"]:
            tone = "green" if outcome.startswith(("Attached", "Sent")) else "amber"
            rows_html.append(
                f'<tr data-attachment-outcome="{html_mod.escape(outcome)}">'
                f'<td><strong>{html_mod.escape(fname)}</strong></td>'
                f'<td>{html_mod.escape(mime)}</td>'
                f'<td class="tabular">{size}</td>'
                f'<td><span class="attachment-outcome"><span class="status status--{tone}">{html_mod.escape(outcome)}</span></span></td>'
                f'<td class="row-actions"><button type="button" class="btn btn--small" data-preview-attachment="{html_mod.escape(fname)}">Open file</button></td>'
                f'</tr>'
            )
        body.append(_frag(
            '<div class="table-wrap message-attachments">'
            '<table class="table table--compact" data-message-attachments>'
            '<thead><tr><th scope="col">File</th><th scope="col">Type</th><th scope="col">Size</th>'
            '<th scope="col">Outcome</th><th scope="col"><span class="sr-only">Open</span></th></tr></thead>'
            f'<tbody>{"".join(rows_html)}</tbody></table></div>'
        ).div)
    return clone


def build_thread_view(dialog_wrapper: Tag, key: str, msg_id: str, ids: dict[str, str]) -> Tag:
    """Return a copy of dialog_wrapper showing the Thread tab."""
    fx = FIXTURES[key]
    clone = copy.copy(dialog_wrapper)
    for tab in clone.select("nav.tabs a.tab"):
        if "section=thread" in tab.get("href", ""):
            tab["aria-current"] = "page"
        else:
            tab.attrs.pop("aria-current", None)
    body = clone.select_one(".dialog-body")
    body.clear()
    thread_keys = fx.get("thread") or [key]
    if len(thread_keys) <= 1:
        body.append(_frag('<div class="empty"><p>No other message in this conversation is kept here.</p></div>').div)
    else:
        for tkey in thread_keys:
            tfx = FIXTURES[tkey]
            tid = ids[tkey]
            current = ' aria-current="page"' if tkey == key else ""
            body.append(_frag(
                f'<a class="row-button" href="/Inbox/{tid}" data-mail-dialog-link{current}>'
                f'<span class="row-top"><span class="row-title">{html_mod.escape(tfx["sender"])}</span>'
                f'<span class="row-time"><time datetime="{tfx["iso"]}">{tfx["time"]}</time></span></span>'
                f'<span class="row-title">{html_mod.escape(tfx["subject"])}</span></a>'
            ).a)
    return clone


def build_compose_view(key: str, msg_id: str, mode: str, *, proposal: bool, ai_draft: bool = False) -> Tag:
    """Build a Reply / Reply all / Forward composer dialog wrapper for key."""
    fx = FIXTURES[key]
    label_map = {"reply": "Reply", "reply-all": "Reply all", "forward": "Forward"}
    label = label_map.get(mode, "Reply")
    subj_prefix = "FW: " if mode == "forward" else "Re: "
    subj = fx["subject"] if fx["subject"].startswith(("Re:", "FW:")) else subj_prefix + fx["subject"]
    case_ref = fx["case_ref"] or ""
    route_html = (
        '<div class="field"><label for="CorrespondenceTo">To</label>'
        '<input id="CorrespondenceTo" name="CorrespondenceTo" type="text" value=""></div>'
        if mode == "forward"
        else f'<p class="mail-route">From desk@collisionengineers.co.uk · To {html_mod.escape(fx["sender"])}</p>'
    )
    ai_banner = (
        '<div class="notice" role="status" data-ai-draft="72329218-8fe1-441c-8628-9e540bdc738f">'
        '<svg class="icon" aria-hidden="true"><use href="#icon-sparkles"></use></svg>'
        '<span><span class="src-tag src-tag--ai">AI</span> Draft prepared by Claude · Edit before sending</span></div>'
        if ai_draft else ""
    )
    body_text = (
        "Dear Northline Claims,\n\nThank you for your e-mail of 12 October. The hire charges on the report "
        "for QDOS26214 cover 14 days at the agreed daily rate while the vehicle was off the road awaiting parts.\n\n"
        "Kind regards,\nCollision Engineers"
        if ai_draft else ""
    )
    show_query_tick = mode in ("reply", "reply-all") and (
        (proposal and fx.get("query_state") == "open") or (not proposal and fx["case_ref"] in ("QDOS26214", "QDOS26190"))
    )
    tick_label = "Mark query done" if proposal else "Also resolve query"
    tick_checked = " checked" if ai_draft or fx.get("query_state") == "open" else ""
    query_tick_html = (
        f'<div class="field"><label>'
        f'<input type="checkbox" id="ResolveQuery" name="ResolveQuery" value="true" data-resolve-query{tick_checked}>'
        f' {tick_label}</label></div>'
        if show_query_tick else ""
    )
    return _frag(
        f'<div id="mailMessageDialog" class="dialog-backdrop" data-dialog="mailMessageDialog" '
        f'data-mail-message="{msg_id}" data-mail-key="{key}" hidden>'
        f'<section class="dialog dialog--mail" role="dialog" aria-modal="true" aria-labelledby="mailMessageDialog_title">'
        f'<div class="dialog-head">'
        f'<div class="mail-dialog-title">'
        f'<h2 id="mailMessageDialog_title" class="wrap" tabindex="-1" data-dialog-initial-focus>'
        f'{html_mod.escape(label + " · " + fx["subject"])}</h2></div>'
        f'<span class="mail-dialog-tools">'
        f'<button type="button" class="dialog-close" data-dialog-close aria-label="Close dialog">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-x"></use></svg></button></span>'
        f'</div>'
        f'<div class="dialog-body">'
        f'<form method="post" id="mailComposerForm" action="/Inbox/{msg_id}?handler={label.replace(" ", "")}&amp;dialog=true" class="stack mail-compose">'
        f'<div class="stack">'
        f'<input type="hidden" name="compose" value="{mode}">'
        f'<div class="mail-compose-route">{route_html}'
        f'<div class="field case-picker" data-case-picker data-case-picker-fill '
        f'data-case-picker-url="/Inbox/{msg_id}?handler=CorrespondenceCaseOptions">'
        f'<label for="CorrespondenceCaseReference">Case / PO</label>'
        f'<input id="CorrespondenceCaseReference" name="CorrespondenceCaseReference" type="text" '
        f'value="{html_mod.escape(case_ref)}" maxlength="100" autocomplete="off" role="combobox" '
        f'aria-autocomplete="list" aria-expanded="false" aria-controls="message-case-options">'
        f'<div id="message-case-options" class="case-picker-options" data-case-picker-options hidden></div>'
        f'</div></div>'
        f'<div class="field"><label for="CorrespondenceSubject">Subject</label>'
        f'<input id="CorrespondenceSubject" name="CorrespondenceSubject" type="text" value="{html_mod.escape(subj)}"></div>'
        f'{ai_banner}'
        f'<div class="field"><label for="CorrespondenceBody">Message</label>'
        f'<textarea id="CorrespondenceBody" name="CorrespondenceBody" rows="8">{html_mod.escape(body_text)}</textarea></div>'
        f'{query_tick_html}'
        f'</div></form></div>'
        f'<div class="dialog-foot">'
        f'<a class="btn" href="/Inbox/{msg_id}" data-mail-dialog-link>Cancel</a>'
        f'<button type="submit" form="mailComposerForm" class="btn btn--dark" data-busy-label="Sending…">'
        f'<svg class="icon" aria-hidden="true"><use href="#icon-send"></use></svg><span>Send</span></button>'
        f'</div></section></div>'
    )


def mount_dialog_on_inbox(inbox_body: Tag, dialog_wrapper: Tag, msg_id: str) -> None:
    """Pin the message's row on the Inbox list and mount dialog_wrapper into [data-mail-dialog-root]."""
    for row in inbox_body.select("[data-mail-row]"):
        if row.get("data-mail-row") == msg_id:
            row["aria-current"] = "true"
        else:
            row.attrs.pop("aria-current", None)
    mount = inbox_body.select_one("[data-mail-dialog-root]")
    if mount is None:
        return
    mount.clear()
    clone = copy.copy(dialog_wrapper)
    dialog = clone.select_one("#mailMessageDialog")
    if dialog is not None:
        dialog.attrs.pop("hidden", None)
        dialog["data-dialog-open-on-load"] = "true"
    for child in list(clone.contents):
        if isinstance(child, Tag):
            mount.append(child.extract())
