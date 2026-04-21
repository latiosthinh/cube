# State

## Current Phase
**Phase 1: Foundation — Window, Tray & Taskbar Integration**

## Project Status
- **Milestone:** v1.0 — Initial Build
- **Current Phase:** 1 of 3
- **Phase Status:** Not started

## Phase History

| Phase | Name | Status | Started | Completed |
|-------|------|--------|---------|-----------|
| 1 | Foundation — Window, Tray & Taskbar Integration | pending | — | — |
| 2 | Pet Life — Animation, States & Interaction | pending | — | — |
| 3 | Persistence, Selection & Settings | pending | — | — |

## Active Decisions

| Decision | Context | Outcome |
|----------|---------|---------|
| .NET 9.0 + WPF | Core framework selection | Confirmed in STACK.md |
| H.NotifyIcon.Wpf 2.4.1 | System tray library | Confirmed in STACK.md |
| System.Text.Json | Serialization | Confirmed in STACK.md |
| SHAppBarMessage P/Invoke | Taskbar position detection | Confirmed in STACK.md |
| AllowsTransparency + WindowStyle=None | Transparent window pattern | Confirmed in STACK.md |

## Open Questions

- Which 2-3 pet types for v1? (cat, dog, and a third?)
- Should we use pre-sliced PNG frames or sprite sheets?
- What resolution/DPI should pet assets target?

## Notes

- Research complete: STACK.md, FEATURES.md, PITFALLS.md written
- Architecture research agent did not complete — architecture patterns captured in STACK.md instead
- Key pitfall: `TaskbarCreated` message handling is critical for Phase 1
- Key pitfall: WPF transparent windows force software rendering — animation frame rate capping is essential
