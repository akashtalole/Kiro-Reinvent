---
name: vega-tv-ui-review
description: Review a Fire TV app screen built with React Native for Vega OS for 10-foot, remote-control use — focus order, D-pad navigation, focus visibility, back behaviour, text size, contrast and overscan. Use when building or reviewing a Fire TV / Vega OS screen or before recording a demo on the Vega Virtual Device.
license: MIT
---
# Vega TV UI review

1. Read the screen's components and list every focusable element in the order a D-pad user would reach it.
2. Go through [references/checklist.md](references/checklist.md) and report pass/fail with file:line and a concrete fix.
3. Run the app on the Vega Virtual Device (`vega run-app <vpkg> <app-id> -d VirtualDevice`) and walk the screen with the remote only — no mouse, no touch. Note any dead end.
4. For platform APIs and current component guidance, use Amazon's Vega docs (or Amazon Devices Builder Tools if installed); don't guess API names.
