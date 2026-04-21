# Taskbar Pet

## What This Is

A Windows desktop application featuring a virtual pet that lives on the taskbar. The pet walks along the taskbar, gets hungry and asks to be fed, shows emotions, sleeps, and plays mini-games with the user. Think Tamagotchi meets desktop companion, rendered in a cartoon/smooth art style.

## Core Value

A delightful, low-friction virtual pet that brings joy to the user's daily computer use by living naturally on the Windows taskbar — responding to attention, showing personality through moods, and creating an emotional bond through consistent presence.

## Context

- **Platform:** Windows desktop (taskbar area only)
- **Tech Stack:** C# / WPF
- **Visual Style:** Cartoon / smooth animations
- **Pet Variety:** Multiple pet types selectable at setup
- **Persistence:** Local save files — pet state (hunger, mood, level) persists between restarts
- **Controls:** System tray icon with menu (feed, pause, settings, exit)

## Key Behaviors

- Pet walks along the taskbar, exploring left and right
- Pet gets hungry over time and requests food (visual/audio cue)
- User can feed the pet through interaction or tray menu
- Pet displays mood states: happy, sad, sleepy, playful, hungry
- Pet has a sleep/rest cycle — falls asleep after being idle
- Mini-games and interactions: click to pet, play with the pet
- Multiple pet types available to choose from

## Constraints

- Must stay within the taskbar bounds (not full desktop roaming)
- Should be lightweight — minimal CPU/memory impact
- Smooth animations without jank
- Works on Windows 10/11

## Out of Scope

- Full desktop roaming (taskbar only for v1)
- Online/multiplayer features
- Cloud sync of pet state
- In-app purchases or monetization

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| C# / WPF | Native Windows, best taskbar integration, good animation support | Selected |
| Local save files | Simple, no server needed, instant load | Selected |
| Taskbar-only | Focused scope, cleaner UX, less complex | Selected |
| Multiple pet types | Replayability, user choice | Selected |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-21 after initialization*
