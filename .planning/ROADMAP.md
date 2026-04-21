# Roadmap

## Phase 1: Foundation — Window, Tray & Taskbar Integration
**Goal:** A transparent WPF window that lives on the taskbar with a system tray icon, handles taskbar positioning, and survives Explorer restarts.

**Requirements:** CORE-01, CORE-02

**Success Criteria:**
1. App launches and shows a transparent window positioned correctly on the taskbar (bottom/top/left/right)
2. Clicks pass through non-pet areas of the window to the taskbar beneath
3. System tray icon appears with Feed, Pause, Settings, Exit menu items
4. Restarting Windows Explorer (`taskkill /f /im explorer.exe && start explorer`) restores the tray icon and repositions the window
5. Window hides when a fullscreen app is active, reappears when fullscreen exits
6. Window handles auto-hide taskbar state correctly

**Depends on:** None

**UI hint:** yes

**Pitfall Warnings:** Pitfalls 1, 2, 4, 5, 6, 8, 9, 11, 13

---

## Phase 2: Pet Life — Animation, States & Interaction
**Goal:** A living pet that walks along the taskbar, shows emotions, gets hungry, sleeps, eats, and responds to user interaction.

**Requirements:** CORE-03, CORE-04, CORE-05

**Success Criteria:**
1. Pet sprite renders with transparent background and walks left/right along the taskbar with a walk animation cycle
2. Pet shows idle animation (breathing/looking around) when stationary
3. Pet autonomously transitions between states: walking → idle → hungry → sleeping → eating
4. Hunger stat decays over time; pet visually communicates hunger (drooping, speech bubble saying "hungry")
5. Clicking the pet triggers a happy reaction animation
6. Dragging the pet repositions it along the taskbar
7. Feeding the pet (via click or tray menu) plays eating animation and restores hunger stat
8. Pet falls asleep after idle period, shows sleeping animation, wakes up on interaction
9. CPU usage stays below 2% when pet is idle (verified in Task Manager)

**Depends on:** Phase 1

**UI hint:** yes

**Pitfall Warnings:** Pitfalls 3, 7, 11, 12, 14

---

## Phase 3: Persistence, Selection & Settings
**Goal:** Pet state persists across restarts, users can choose from multiple pet types, and a settings panel is available.

**Requirements:** CORE-06, CORE-07, CORE-08

**Success Criteria:**
1. Pet state (hunger, happiness, energy, position, pet type) is saved to JSON every 30 seconds and on app exit
2. On app startup, pet state is loaded and the pet appears in its last known condition
3. Save files are atomic — killing the app mid-save does not corrupt the file
4. Pet state advances based on elapsed time since last save (e.g., pet is hungrier after being closed for hours)
5. First launch shows a pet selection screen with 2-3 pet types to choose from
6. Each pet type has its own sprite sheet and animation set (walk, idle, eat, sleep, happy)
7. Settings panel accessible from tray menu with configurable: sleep idle duration, notification frequency, monitor selection
8. Settings persist across restarts

**Depends on:** Phase 2

**UI hint:** yes

**Pitfall Warnings:** Pitfalls 10, 15, 16

---

## Coverage Validation

| Requirement | Mapped | Phase |
|-------------|--------|-------|
| CORE-01 | ✓ | Phase 1 |
| CORE-02 | ✓ | Phase 1 |
| CORE-03 | ✓ | Phase 2 |
| CORE-04 | ✓ | Phase 2 |
| CORE-05 | ✓ | Phase 2 |
| CORE-06 | ✓ | Phase 3 |
| CORE-07 | ✓ | Phase 3 |
| CORE-08 | ✓ | Phase 3 |

**All 8 requirement groups mapped. 100% coverage.**
