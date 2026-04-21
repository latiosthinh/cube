# Requirements

## v1 Requirements

### CORE-01: Pet Window Foundation
- [ ] **CORE-01**: App launches a transparent WPF window that renders on top of the taskbar
- [ ] **CORE-02**: Window is click-through for non-pet areas (only pet sprite intercepts clicks)
- [ ] **CORE-03**: Window dynamically tracks taskbar position (bottom/top/left/right) and repositions on changes
- [ ] **CORE-04**: Window hides automatically when a fullscreen application is active
- [ ] **CORE-05**: Window handles auto-hide taskbar state correctly

### CORE-02: System Tray & Lifecycle
- [ ] **TRAY-01**: System tray icon with context menu (Feed, Pause, Settings, Exit)
- [ ] **TRAY-02**: Tray icon survives Explorer restart (handles TaskbarCreated message)
- [ ] **TRAY-03**: Clean tray icon removal on app exit (no ghost icons)
- [ ] **TRAY-04**: App minimizes to tray on window close (does not quit)

### CORE-03: Pet Rendering & Animation
- [ ] **ANIM-01**: Pet sprite renders with transparent background (PNG sprite sheets)
- [ ] **ANIM-02**: Walk animation cycles through frames as pet moves along taskbar
- [ ] **ANIM-03**: Idle animation (breathing, looking around) when pet is stationary
- [ ] **ANIM-04**: Eating animation plays when pet is fed
- [ ] **ANIM-05**: Sleeping animation plays when pet is resting
- [ ] **ANIM-06**: Animation frame rate is capped (30fps active, 2fps idle, 0fps sleeping) to keep CPU < 2%

### CORE-04: Pet State Machine & Needs
- [ ] **STATE-01**: Pet has hunger stat that decays over time
- [ ] **STATE-02**: Pet has happiness stat affected by interaction and feeding
- [ ] **STATE-03**: Pet has energy stat that depletes with activity and recovers during sleep
- [ ] **STATE-04**: Pet autonomously transitions between states: walking, idle, hungry, sleeping, eating
- [ ] **STATE-05**: Pet visually communicates needs through behavior (not stat bars) — e.g., drooping when hungry, yawning when sleepy
- [ ] **STATE-06**: Pet falls asleep after being idle for a configurable duration
- [ ] **STATE-07**: Pet wakes up from sleep when interacted with or after rest period

### CORE-05: User Interaction
- [ ] **INTER-01**: Clicking the pet triggers a reaction animation (happy response)
- [ ] **INTER-02**: Dragging the pet repositions it along the taskbar
- [ ] **INTER-03**: Feeding the pet (via click or tray menu) plays eating animation and restores hunger
- [ ] **INTER-04**: Pet displays dialogue/speech bubbles for contextual messages (hungry, happy, sleepy)

### CORE-06: State Persistence
- [ ] **SAVE-01**: Pet state (hunger, happiness, energy, position, pet type) saves to local JSON file
- [ ] **SAVE-02**: State is loaded on app startup, restoring the pet's condition
- [ ] **SAVE-03**: Saves are atomic (write to temp, then replace) to prevent corruption
- [ ] **SAVE-04**: State advances based on elapsed time since last save (pet gets hungrier while app was closed)
- [ ] **SAVE-05**: State saves on app exit and on a periodic timer (every 30 seconds)

### CORE-07: Pet Selection
- [ ] **SELECT-01**: First launch shows a pet selection screen (2-3 pet types to choose from)
- [ ] **SELECT-02**: Each pet type has its own sprite sheet and animation set
- [ ] **SELECT-03**: Selected pet type is saved and loaded on subsequent launches

### CORE-08: Settings
- [ ] **SETTINGS-01**: Settings panel accessible from tray menu
- [ ] **SETTINGS-02**: Configurable: sleep idle duration, notification frequency, which monitor's taskbar to use
- [ ] **SETTINGS-03**: Settings persist across restarts

## v2 Requirements (Deferred)

- [ ] **V2-01**: Mini-games (1-2 simple games playable from taskbar)
- [ ] **V2-02**: Level/EXP progression system
- [ ] **V2-03**: Affinity/relationship system with hidden stat
- [ ] **V2-04**: Work/earn money mechanic
- [ ] **V2-05**: Pet reacts to system events (app focus, notifications, idle)
- [ ] **V2-06**: Health/sickness system
- [ ] **V2-07**: Additional pet types beyond initial 2-3
- [ ] **V2-08**: Pinch/squeeze interaction (long-press animation)

## Out of Scope

- **Full desktop roaming** — PROJECT.md explicitly scopes to taskbar-only; adds massive complexity
- **Online/multiplayer features** — Desktop pets are inherently personal/solitary
- **Cloud sync of pet state** — Contradicts lightweight value; local save files only
- **In-app purchases or monetization** — Free app per PROJECT.md
- **Pet death/perma-death** — Causes user frustration; consequences are behavioral, not terminal
- **AI chat/conversation** — Pre-written dialogue pools only; AI could be v3+
- **3D rendering** — PROJECT.md specifies 2D cartoon/smooth style
- **Breeding/reproduction** — Enormous complexity, not core to taskbar companion experience

## Traceability

| Requirement | Phase | Success Criteria |
|-------------|-------|-----------------|
| CORE-01 | Phase 1 | Transparent window renders on taskbar, click-through works |
| CORE-02 | Phase 1 | Tray icon present, survives Explorer restart |
| CORE-03 | Phase 2 | Pet animates walking, idle, eating, sleeping on taskbar |
| CORE-04 | Phase 2 | Pet transitions between states autonomously, shows needs visually |
| CORE-05 | Phase 2 | Click, drag, feed interactions work correctly |
| CORE-06 | Phase 3 | State persists across restarts, advances on elapsed time |
| CORE-07 | Phase 3 | Pet selection screen on first launch, multiple pet types |
| CORE-08 | Phase 3 | Settings panel configurable and persistent |
