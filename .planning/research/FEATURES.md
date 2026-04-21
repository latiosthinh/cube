# Feature Landscape

**Domain:** Windows desktop virtual pet (taskbar-focused)
**Researched:** 2026-04-21
**Sources:** VPet GitHub (5.9k stars, 1,191 commits), VPet Steam (50,708 reviews, 95% positive), Wikipedia Virtual Pet article, Steam desktop pet ecosystem (222+ titles), Tamagotchi/Digimon history

## Table Stakes

Features users expect from any desktop virtual pet. Missing these = product feels incomplete or broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Animated pet sprite on screen** | Core premise — without animation it's a static image, not a pet | Medium | PNG sprite sheets or frame-based animation; VPet supports 384 animations (32 types × 4 states × 3 variants) |
| **Click/tap interaction (pet, pick up)** | Users expect to touch the pet and get a reaction | Low | Short-term interactivity: click head = head-pat animation, click body = speech/dialogue, drag = pick up and move |
| **Hunger/needs system** | Tamagotchi established this in 1996; VPet, Neopets, all virtual pets have it | Medium | Hunger, thirst, stamina, mood decay over time; visible through behavior not UI bars (modern pattern per Wikipedia) |
| **Feeding the pet** | Direct response to hunger; core gameplay loop | Medium | Food/drink/medicine categories; instant + over-time stat restoration; VPet uses "Betterbuy" shop UI |
| **Sleep/rest cycle** | Pets need to rest; users expect day/night or idle sleep behavior | Low | Pet falls asleep after idle period; reduces stamina exertion, promotes recovery |
| **Emotion/mood display** | Users expect the pet to show feelings through animation, not text | Medium | Happy, sad, sleepy, hungry, playful states expressed through body language and facial expressions |
| **System tray icon with controls** | Windows desktop app convention; users need pause/exit/settings | Low | Right-click tray menu: feed, pause, settings, exit |
| **Save/load pet state** | Users expect persistence across restarts; losing progress = uninstall | Low | Local save file with hunger, mood, level, affinity, money, EXP |
| **Pet walks/moves autonomously** | Screen mate pattern since Neko (1989); pet should feel alive | Medium | VPet: wandering, spacing out, squatting, wall-climbing; movement triggered after interaction cycles |
| **Pet speaks/dialogue bubbles** | Communication without message boxes; modern virtual pet pattern | Low | Speech text triggered by interaction; VPet supports custom dialogue via Workshop |
| **Multiple pet types to choose from** | User choice and replayability; PROJECT.md explicitly requires this | Medium | Different sprites, animations, possibly different stat profiles |
| **Lightweight resource usage** | Desktop pet runs alongside other apps; high CPU = users kill it | Low | VPet minimum: 200 MB RAM, 2-core CPU; target <1% CPU idle |

## Differentiators

Features that set Taskbar Pet apart. Not expected, but highly valued when present.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Taskbar-specific locomotion** | Most desktop pets roam the full screen; taskbar-only is a unique constraint that creates novel behaviors | High | Pet walks left/right along taskbar, interacts with taskbar elements (start button, system tray, pinned apps); this is the core differentiator |
| **Mini-games triggered from taskbar** | Play with your pet in short bursts; fits the "low-friction" value proposition | High | Click-to-play mini-games that don't disrupt workflow; VPet has work/study mini-games |
| **Pet reacts to system events** | Pet notices when you open apps, receive notifications, idle too long — creates "companion" feeling | High | Hook into Windows events: app focus changes, notification arrivals, idle detection; makes pet feel aware of your activity |
| **Affinity/relationship system** | Hidden stat that grows with interaction; unlocks special behaviors/dialogue; creates emotional bond | Medium | VPet has hidden "Affinity" stat; high affinity triggers special dialogs, better health, unique animations |
| **Level/progression system** | Pet grows over time; gives long-term engagement hook beyond basic care | Medium | VPet: EXP from learning/working, levels unlock new abilities (work at Lv10, research at Lv15), raise affinity cap |
| **Work/earn money mechanic** | Pet can "work" to earn in-game currency; creates economic loop for buying items | Medium | VPet: "Prepping" and "Live" work modes; money buys food, drinks, furniture via Workshop |
| **Custom shortcuts/quick actions** | Power user feature; launch apps, run commands, keyboard shortcuts from pet menu | Medium | VPet supports custom shortcuts with web pages, executables, keyboard macros |
| **Personality traits per pet type** | Different pets have different behaviors, preferences, animation sets — not just cosmetic | Medium | Cat might sleep more, dog might be more active; creates meaningful choice beyond aesthetics |
| **Health/sickness system** | Neglect has consequences; pet gets sick on low health, can't work/study; adds stakes | Low | VPet: hidden health stat affected by hunger/thirst/mood; sickness disables activities |
| **Pinch/squeeze interaction** | Novel tactile interaction; VPet added this as Steam Award voting reward | Low | Long-press on face triggers pinch animation; memorable, shareable moment |

## Anti-Features

Features to explicitly NOT build for v1.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| **Full desktop roaming** | PROJECT.md explicitly scopes to taskbar-only; full roaming adds massive complexity (window occlusion, multi-monitor, z-order conflicts) | Focus on rich taskbar behaviors; can expand to desktop in v2 |
| **Online/multiplayer features** | Adds server infrastructure, networking complexity, privacy concerns; desktop pets are inherently personal/solitary | Keep it local-first; if social features are desired later, consider local network discovery only |
| **Cloud sync of pet state** | Requires backend, authentication, offline handling; contradicts "lightweight" value | Local save files only; if users want backup, export/import save file |
| **In-app purchases or monetization** | PROJECT.md explicitly out of scope; desktop pet users expect free or one-time purchase | Free app; if monetization is desired later, cosmetic pet skins only |
| **Complex stat management UI** | Users don't want to manage spreadsheets; modern virtual pets show state through behavior, not bars | Use visual/audio cues (pet rubs belly = hungry, yawns = sleepy) instead of numeric displays |
| **Pet death/perma-death** | Tamagotchi's death mechanic caused school bans and user frustration; modern pets avoid this | Pet gets sad/sick but never dies; consequences are behavioral, not terminal |
| **Breeding/reproduction** | Adds enormous complexity (genetics, pairing, offspring management); not core to taskbar companion experience | Focus on single pet relationship; can add multiple pets later as separate companions |
| **AI chat/conversation** | Adds API costs, latency, complexity; not core to the delight loop | Use pre-written dialogue pools with contextual triggers; AI could be v3+ feature |
| **3D rendering** | PROJECT.md specifies cartoon/smooth 2D; 3D adds GPU requirements, animation complexity | 2D sprite-based animation with smooth transitions; matches VPet's successful approach |

## Feature Dependencies

```
Animated pet sprite → Click interaction → Emotion display (pet reacts to clicks with emotions)
Hunger/needs system → Feeding system → Food items (need food catalog to feed)
Hunger/needs system → Sleep cycle → Stamina recovery (sleep restores stamina affected by needs)
Save/load state → All stateful features (hunger, mood, level, affinity, money, EXP)
Pet walks autonomously → Taskbar bounds constraint (movement must respect taskbar geometry)
Multiple pet types → Animated pet sprite (each type needs its own animation set)
Level/progression → EXP system → Work/Learn mechanics (sources of EXP)
Affinity system → Click interaction → Dialogue system (high affinity unlocks special dialogue)
Health system → Hunger/Thirst/Mood (health is derived from these stats)
Work/earn money → Money system → Feeding system (money buys food)
Mini-games → Click interaction → Pet state awareness (games should reflect current pet mood/energy)
System event reactions → Windows event hooks → Emotion display (events trigger emotional responses)
Custom shortcuts → System tray menu → Taskbar integration (shortcuts launch from pet context)
```

## MVP Recommendation

**Phase 1 — Core Pet Presence (Must Have)**
1. Animated pet sprite walking along taskbar
2. Click interaction (pet, pick up, move)
3. Hunger/needs system with decay over time
4. Feeding system (basic food items)
5. Sleep/rest cycle
6. Emotion display (happy, sad, sleepy, hungry)
7. System tray icon with basic controls
8. Save/load pet state
9. One pet type (cat or dog as default)

**Phase 2 — Personality & Progression (Should Have)**
10. Multiple pet types (2-3 options at setup)
11. Mood system with more states (playful, hungry, tired)
12. Affinity/relationship system
13. Level/EXP progression
14. Health/sickness system
15. Dialogue/speech bubbles

**Phase 3 — Engagement Loop (Nice to Have)**
16. Work/earn money mechanic
17. Mini-games (1-2 simple games)
18. Custom shortcuts
19. System event reactions
20. Pinch/squeeze interaction

**Defer to v2:**
- Desktop roaming (beyond taskbar)
- Additional pet types (beyond initial 2-3)
- Advanced mini-games
- Workshop/mod support
- System event reactions (complex Windows hooks)

## Sources

- **VPet GitHub** (github.com/LorisYounger/VPet) — 5.9k stars, 1,191 commits, detailed tutorial with 11 interaction types and 8 stat categories — HIGH confidence
- **VPet Steam** (store.steampowered.com/app/1920960) — 50,708 reviews, 95% positive, free-to-play with Workshop support — HIGH confidence
- **Wikipedia: Virtual Pet** — Common features taxonomy, history from Neko (1989) to modern mobile pets, design trends — HIGH confidence
- **Steam Desktop Pet Search** — 222+ titles including VPet-Simulator, Desktop Pet Project, Pocket Waifu, Tiny Friends — MEDIUM confidence (surface-level data)
- **PROJECT.md** — Taskbar Pet scope, constraints, and key decisions — HIGH confidence
