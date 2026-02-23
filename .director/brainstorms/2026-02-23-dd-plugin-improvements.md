# Brainstorm: Due Diligence Plugin Improvements

**Date:** 2026-02-23

## Summary

### Key Ideas
- The PDF vision fallback threshold (50 chars/page) is too low -- scanned-as-image PDFs with font encoding noise produce gibberish that passes the threshold (e.g., 51.7 and 78.5 chars/page of nonsense text)
- A dual approach is needed: raise the scanned detection threshold to ~150-200 chars/page AND add a text quality check that detects gibberish regardless of character volume
- The gap between problem files (max 78.5 chars/page) and the lowest successful pdfplumber extraction (731.5 chars/page) gives massive headroom -- no risk of false positives from raising the threshold
- Aligning the vision fallback threshold with the existing `_HIGH_CONFIDENCE_CHARS_PER_PAGE` (200) makes conceptual sense: if pdfplumber can't produce high-confidence text density, let vision take a look
- The client summary agent's tone is "really direct" per team feedback -- the tone guidance literally says "Professional and direct" and the agent follows that faithfully
- The tone shift should go from "here's what's wrong" to "we're interested, and here's what we need to feel confident" -- curiosity-based framing rather than prosecutorial
- Both the client summary template and agent file need tone changes since they reinforce each other

### Decisions Made
- Use both approaches for PDF fallback: raise the `_SCANNED_CHARS_PER_PAGE_THRESHOLD` to ~150-200 AND add a gibberish quality check as a second net
- Soften the client summary tone across both `templates/client-summary-template.md` and `agents/client-summary-agent.md` -- shift from "direct" to "approachable" with curiosity-based questioning and appreciation-first framing

## Highlights

The conversation started with Noah describing two issues found during a real due diligence run on the MattSanders opportunity. The first was a 32-page executed lease PDF that converted to gibberish (`$)' ##* !$%` repeated on every page) because pdfplumber treated it as text even though it was a scanned image. The vision fallback mechanism exists and works -- 9 files in the same run were correctly routed to claude_vision -- but this file's 51.7 avg chars/page barely exceeded the 50-character threshold.

A second problem file (a 2-page renewal amendment at 78.5 chars/page) revealed a different failure mode: pdfplumber extracted real text (DocuSign envelope metadata) but missed the actual document content underneath the image layer. This showed that threshold alone catches both cases, but a quality check provides a safety net for gibberish at any volume.

Analyzing all 24 converted files from the run revealed a clean separation: every successful pdfplumber extraction had 731+ chars/page, while the two failures had 51.7 and 78.5. This massive gap means raising the threshold anywhere from 100-700 is safe, with 150-200 being the sensible range.

On the client summary tone, reading the actual generated CLIENT_SUMMARY.md made the feedback concrete. The recommendation opens with "The site presents fundamental issues that prevent Data Canopy from moving forward" -- no appreciation for the opportunity before the concerns. Questions include phrases like "No deal evaluation can proceed without this information" -- demand language rather than curiosity. The template's Writing Style section literally instructs "Professional and direct," which the agent follows faithfully. The fix is straightforward: update the tone guidance in both files to shift from "direct" to "approachable," add instructions to lead with appreciation, use curiosity framing ("Can you help us understand..." instead of demands), and soften Next Steps language ("It would be helpful to see..." instead of "Provide...").

## Suggested Next Action

These are two concrete, well-scoped changes. Run `/director:quick "Raise PDF scanned detection threshold to 200 and add gibberish quality check in dc-due-diligence/converters/pdf.py"` to handle the first one, then `/director:quick "Soften client summary tone in dc-due-diligence agents/client-summary-agent.md and templates/client-summary-template.md -- shift from direct to approachable with curiosity-based framing"` for the second.
