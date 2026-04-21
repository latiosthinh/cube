# Domain Pitfalls: Windows Taskbar Virtual Pet

**Domain:** Windows desktop virtual pet (taskbar-resident, C#/WPF)
**Researched:** 2026-04-21

## Critical Pitfalls

Mistakes that cause rewrites or major user-facing failures.

### Pitfall 1: Not Handling Taskbar Recreation (Explorer Restart)

**What goes wrong:** Windows Explorer restarts (crash, update, user kill/restart) and the taskbar is recreated. The pet's notification area icon disappears, the pet window loses its taskbar position binding, and the app is effectively orphaned — running but invisible or misplaced.

**Why it happens:** The Shell broadcasts a `TaskbarCreated` registered window message when the taskbar is recreated. Most desktop apps never listen for this. On Windows 10, this message also fires when the DPI of the primary display changes.

**Consequences:**
- System tray icon vanishes — user has no way to access settings, feed, or exit
- Pet window may be positioned at stale coordinates that no longer match the taskbar
- User perceives app as crashed; kills it via Task Manager

**Prevention:**
```csharp
// Register for the TaskbarCreated message at startup
private static readonly uint TaskbarCreatedMsg = 
    RegisterWindowMessage("TaskbarCreated");

protected override void WndProc(ref Message m)
{
    if (m.Msg == TaskbarCreatedMsg)
    {
        ReinitializeTrayIcon();
        RequeryTaskbarPosition();
    }
    base.WndProc(ref m);
}
```
- Always handle `TaskbarCreated` by re-adding the tray icon via `Shell_NotifyIcon(NIM_ADD, ...)`
- Re-query taskbar position via `SHAppBarMessage(ABM_GETTASKBARPOS, ...)`
- **Phase mapping:** Phase — Taskbar Integration & Positioning

**Warning signs:** Restart Explorer (`taskkill /f /im explorer.exe && start explorer`) during testing. If tray icon doesn't come back, this pitfall is active.

---

### Pitfall 2: Assuming Taskbar Position, Size, and Orientation Are Fixed

**What goes wrong:** Hardcoding the assumption that the taskbar is always at the bottom of the primary monitor, always 40px tall, and always horizontal. Users can dock it to top, left, right, or auto-hide it. Multi-monitor setups have taskbars on different monitors with different sizes.

**Why it happens:** Developer tests only on their own machine with default taskbar configuration.

**Consequences:**
- Pet renders off-screen or floating in the middle of the desktop
- Pet clips into taskbar buttons or system tray
- Pet disappears entirely on auto-hide taskbar (positioned in dead zone)

**Prevention:**
- **Never** hardcode taskbar position or size
- Use `SHAppBarMessage(ABM_GETTASKBARPOS, ref appBarData)` to get the actual taskbar rectangle at runtime and on every `ABN_STATECHANGE` / `ABN_POSCHANGED` notification
- Register as an app bar (`ABM_NEW`) to receive position change notifications, OR poll `SystemParametersInfo(SPI_GETWORKAREA)` periodically
- Handle all four edges: `ABE_BOTTOM`, `ABE_TOP`, `ABE_LEFT`, `ABE_RIGHT`
- On multi-monitor: determine which monitor has the primary taskbar (or let user choose)
- **Phase mapping:** Phase — Taskbar Integration & Positioning

**Warning signs:** Pet looks correct on dev machine but testers report "pet is floating in the middle of my screen" or "pet is cut off."

---

### Pitfall 3: WPF Animation Causing Sustained High CPU Usage

**What goes wrong:** Using WPF's `DispatcherTimer` or composition-target animations that fire at 60fps continuously, even when the pet is idle/sleeping. WPF animations keep the composition thread active, and a constantly repainting transparent window can consume 5-15% of a CPU core — unacceptable for a "lightweight" desktop companion.

**Why it happens:** WPF's animation system is designed for rich UIs, not idle-friendly overlays. Developers use `DoubleAnimation` with `RepeatBehavior="Forever"` for idle animations (breathing, tail wagging) without realizing the composition thread never sleeps.

**Consequences:**
- Laptop battery drain (users notice in Task Manager)
- Fan noise on idle desktop
- Thermal throttling on low-end machines
- User uninstalls due to "this app uses too much CPU"

**Prevention:**
- Use `Rendering` event (`CompositionTarget.Rendering`) only when animation is actually needed — unsubscribe when idle
- For idle animations (sleeping, breathing), use a low-frequency `DispatcherTimer` (1-2fps) instead of 60fps composition animations
- Implement animation budgets: active state = 30fps, idle = 2fps, sleeping = 0fps (static frame)
- Use `Timeline.DesiredFrameRateProperty` to cap animation frame rates
- Profile with WPF Performance Suite / Visual Studio Diagnostic Tools
- **Phase mapping:** Phase — Animation System & Pet States

**Warning signs:** Task Manager shows >2% CPU sustained when pet is doing nothing. WPF Perforator shows constant render passes.

---

### Pitfall 4: Ignoring DPI Scaling and Per-Monitor DPI Awareness

**What goes wrong:** App declares itself as DPI-unaware or system-DPI-aware, causing the pet to be blurry, incorrectly sized, or mispositioned on high-DPI displays (125%, 150%, 200% scaling). On Windows 10/11 with per-monitor DPI, moving the pet window between monitors with different DPI causes it to be scaled by DWM (blurry) or positioned incorrectly.

**Why it happens:** WPF is DPI-aware by default at the system level, but per-monitor DPI v2 requires explicit manifest configuration and runtime handling. Many WPF apps don't set the correct DPI awareness mode.

**Consequences:**
- Pet appears blurry or pixelated on high-DPI displays
- Pet is the wrong physical size (too tiny on 4K, too huge on 1080p)
- Pet position calculations are wrong because pixel coordinates don't match logical coordinates
- On Windows 10, the `TaskbarCreated` message fires on DPI change — if unhandled, tray icon is lost

**Prevention:**
- Set per-monitor DPI awareness v2 in app manifest:
```xml
<dpiAwareness xmlns="urn:schemas-microsoft-com:compatibility.v1">PerMonitorV2</dpiAwareness>
```
- In WPF, handle `DpiChanged` event on windows to recalculate taskbar position and resize pet assets
- Store all pet dimensions in logical (DPI-independent) units, convert to physical only for rendering
- Test at 100%, 125%, 150%, and 200% DPI scaling
- **Phase mapping:** Phase — Taskbar Integration & Positioning (DPI handling), Phase — Asset Pipeline (DPI-aware assets)

**Warning signs:** Pet looks crisp on dev machine but blurry on a colleague's laptop. Position is wrong after dragging window between monitors.

---

### Pitfall 5: Always-On-Top Conflicts with Fullscreen Applications

**What goes wrong:** The pet window is set to `Topmost = true` unconditionally, causing it to render on top of fullscreen games, video players, and presentations. This is extremely annoying and will cause immediate uninstalls.

**Why it happens:** The pet needs to stay above the taskbar, so developers set `Topmost = true` globally without considering fullscreen scenarios.

**Consequences:**
- Pet overlays fullscreen games (obscuring HUD elements, gameplay)
- Pet overlays video players and presentations
- Users perceive the app as malware/adware behavior
- Immediate negative reviews and uninstalls

**Prevention:**
- Detect fullscreen foreground window and lower pet's z-order:
```csharp
// Check if foreground window is fullscreen
var foreground = GetForegroundWindow();
GetWindowRect(foreground, out var rect);
bool isFullscreen = (rect.Width >= SystemParameters.VirtualScreenWidth && 
                     rect.Height >= SystemParameters.VirtualScreenHeight);
this.Topmost = !isFullscreen;
```
- Use `SetWindowPos` with `HWND_TOPMOST` / `HWND_NOTOPMOST` dynamically
- Hook `WM_ACTIVATE` / `WM_SIZE` on foreground window changes (via `SetWinEventHook`)
- Provide a user setting: "Hide during fullscreen" (default: ON)
- Consider using `WS_EX_NOACTIVATE` so the pet window never steals focus
- **Phase mapping:** Phase — Window Management & Z-Order

**Warning signs:** Pet visible over a fullscreen YouTube video or game during testing.

---

### Pitfall 6: Not Handling Auto-Hide Taskbar

**What goes wrong:** The pet is positioned at the taskbar's auto-hide "resting" position (off-screen edge), but when the user hovers to reveal the taskbar, the pet doesn't move with it. Or worse, the pet prevents the taskbar from auto-hiding because it occupies the taskbar region.

**Why it happens:** Auto-hide taskbar has two states: hidden (taskbar rect is off-screen) and shown (taskbar rect is on-screen). The pet needs to track this state and reposition accordingly.

**Consequences:**
- Pet is invisible when taskbar is auto-hidden
- Pet blocks taskbar auto-hide (user can't hide taskbar)
- Pet flickers or jumps when taskbar slides in/out

**Prevention:**
- Query taskbar state via `SHAppBarMessage(ABM_GETSTATE, ...)`:
  - `ABS_AUTOHIDE` flag indicates auto-hide is enabled
  - `ABS_ALWAYSONTOP` flag indicates always-on-top mode
- Subscribe to `ABN_STATECHANGE` notifications for state changes
- When auto-hide is active: position pet at the screen edge where taskbar hides, and move it with the taskbar when it slides out
- Alternatively: hide the pet entirely when taskbar is auto-hidden and taskbar is in hidden state
- **Phase mapping:** Phase — Taskbar Integration & Positioning

**Warning signs:** Enable auto-hide on taskbar. Pet stays visible floating at screen edge when taskbar is hidden, or pet disappears and never comes back.

---

### Pitfall 7: Transparent Window Performance and Visual Artifacts

**What goes wrong:** WPF transparent windows (`AllowsTransparency="True"`, `WindowStyle="None"`) have known performance issues: they force software rendering for the entire window, don't support hardware acceleration, and can show visual artifacts (black borders, stale pixels, incorrect alpha blending) especially with animated content.

**Why it happens:** `AllowsTransparency="True"` in WPF switches the window to a layered window (`WS_EX_LAYERED`) rendered entirely on the CPU. Every frame is composited in software, which is slow for animations.

**Consequences:**
- Animation jank and dropped frames even on powerful hardware
- Black or white borders around the pet (alpha blending artifacts)
- High CPU usage (see Pitfall 3)
- Inconsistent rendering across Windows versions

**Prevention:**
- Option A: Use `AllowsTransparency="True"` but minimize animated area — keep pet sprite small, use pre-rendered frames, cap frame rate aggressively
- Option B: Use a non-transparent window with a chroma-key background (e.g., magenta `#FF00FF`) and rely on DWM composition — better performance but less clean edges
- Option C: Use `UpdateLayeredWindow` via P/Invoke for frame-by-frame bitmap rendering — best performance for sprite animation but more complex
- For WPF specifically: set `RenderOptions.BitmapScalingMode="NearestNeighbor"` for pixel art, or `"HighQuality"` for smooth art
- Test on both Windows 10 and 11 — DWM composition behavior differs
- **Phase mapping:** Phase — Window Management & Z-Order, Phase — Animation System & Pet States

**Warning signs:** Pet animation stutters at 60fps. Black halo visible around pet edges. CPU spikes during animation.

---

## Moderate Pitfalls

### Pitfall 8: Multi-Monitor Taskbar Ambiguity

**What goes wrong:** On Windows 10/11 with multiple monitors, each monitor can have its own taskbar. The app assumes a single taskbar and positions the pet on the wrong monitor, or the pet jumps between monitors unpredictably.

**Prevention:**
- Detect all monitors via `System.Windows.Forms.Screen.AllScreens` or `EnumDisplayMonitors`
- Let user choose which monitor's taskbar the pet lives on (settings)
- Default to primary monitor (`Screen.PrimaryScreen`)
- Handle monitor disconnect/reconnect — pet should relocate, not vanish
- **Phase mapping:** Phase — Taskbar Integration & Positioning

---

### Pitfall 9: System Tray Icon Not Cleaning Up on Exit

**What goes wrong:** App crashes or is killed, leaving a "ghost" tray icon that only disappears when the user hovers over it. Or, on app restart, duplicate tray icons appear.

**Prevention:**
- Clean up tray icon in `Application.Exit` and `ProcessExit` handlers
- Use `Shell_NotifyIcon(NIM_DELETE, ...)` in a `finally` block or `App.OnExit`
- Handle `AppDomain.CurrentDomain.ProcessExit` and `AppDomain.CurrentDomain.UnhandledException`
- Use unique GUID-based icon identification (Windows 7+) to prevent duplicates
- **Phase mapping:** Phase — System Tray & Lifecycle

---

### Pitfall 10: Save File Corruption from Improper Persistence

**What goes wrong:** Pet state (hunger, mood, level) is saved to a local file, but the save is not atomic. If the app crashes mid-write or Windows shuts down unexpectedly, the save file is corrupted and the user loses all progress.

**Prevention:**
- Use atomic writes: write to temp file, then `File.Replace` or `Move` to target path
- Serialize with a format that includes a checksum/version (JSON with schema version)
- Keep a backup of the last known-good save
- Save on a timer (every 30s) AND on state changes AND on app exit
- Handle `SessionEnding` event for graceful Windows shutdown saves
- **Phase mapping:** Phase — State Persistence & Save System

---

### Pitfall 11: Pet Blocking Taskbar Interactions

**What goes wrong:** The pet window is positioned over taskbar buttons or the system tray, intercepting mouse clicks that should go to the taskbar. User can't click Start, can't access system tray icons, can't click pinned apps.

**Prevention:**
- Use `WS_EX_NOACTIVATE` extended window style so the pet window never receives focus or blocks clicks to windows beneath it
- Handle mouse events on the pet window and explicitly pass through clicks that aren't on the pet sprite (hit-testing)
- Keep pet window sized to the pet sprite only — don't use a full taskbar-height window
- In WPF: set `Background="Transparent"` and handle `HitTest` manually, or use `IsHitTestVisible="False"` on non-pet areas
- **Phase mapping:** Phase — Window Management & Z-Order, Phase — User Interaction System

---

### Pitfall 12: Notification/Alert Fatigue

**What goes wrong:** The pet constantly demands attention — hungry notifications, sleep notifications, mood changes — using system tray balloon tips, sounds, or visual cues. Users find it annoying and either mute the app or uninstall it.

**Prevention:**
- Implement cooldown periods between notifications (minimum 5-10 minutes)
- Respect Windows "Focus Assist" / "Do Not Disturb" mode — suppress non-critical notifications
- Use subtle visual cues on the pet itself (drooping ears, sleepy eyes) instead of balloon popups
- Make notification frequency configurable in settings
- Never play sounds without explicit user opt-in
- **Phase mapping:** Phase — Pet State Machine & Needs System

---

### Pitfall 13: Windows 11 Taskbar Differences Not Accounted For

**What goes wrong:** Windows 11 rewrote the taskbar in XAML/WinUI and changed several behaviors. The app works on Windows 10 but breaks on Windows 11 due to differences in taskbar window class names, positioning, or notification area behavior.

**Why it happens:** Windows 10 taskbar window class is `Shell_TrayWnd`. Windows 11 uses `Shell_TrayWnd` but the internal structure changed — the notification area is now `SystemTrayFrame` (WinUI), and taskbar positioning APIs may return different results.

**Consequences:**
- Pet positioned incorrectly on Windows 11
- System tray icon not visible or not clickable on Windows 11
- Taskbar position queries return stale or wrong data

**Prevention:**
- Detect Windows version via `RuntimeInformation.OSDescription` or `Environment.OSVersion`
- Test on both Windows 10 (22H2+) and Windows 11 (22H2+)
- Use `SHAppBarMessage` (documented API) rather than undocumented window enumeration
- Be aware that Windows 11 taskbar cannot be moved to top/left/right edges — only bottom (but don't assume this; use the API)
- **Phase mapping:** Phase — Taskbar Integration & Positioning

---

### Pitfall 14: Animation Frame Timing Drift

**What goes wrong:** Using `DispatcherTimer` with fixed intervals for animation frames causes drift over time. The pet's walk cycle, for example, gradually desyncs from the intended speed, or animations run faster/slower depending on system load.

**Prevention:**
- Use `CompositionTarget.Rendering` for frame-synced animations (tied to display refresh)
- For non-frame-critical animations, use `Stopwatch`-based delta time rather than fixed intervals
- Implement a game-loop pattern: `Update(deltaTime)` → `Render()` with actual elapsed time
- **Phase mapping:** Phase — Animation System & Pet States

---

## Minor Pitfalls

### Pitfall 15: Hardcoded Pet Asset Paths

**What goes wrong:** Pet sprite/animation assets are loaded from hardcoded relative paths. When the app is installed via ClickOnce, MSIX, or a custom installer, the working directory changes and assets fail to load.

**Prevention:**
- Use `AppDomain.CurrentDomain.BaseDirectory` or `Assembly.GetExecutingAssembly().Location` to resolve asset paths
- Mark assets as `Content` with `Copy to Output Directory` in the project file
- **Phase mapping:** Phase — Asset Pipeline

### Pitfall 16: Not Handling Windows Lock / Session Switch

**What goes wrong:** Pet continues animating and consuming resources when the user locks their computer (Win+L) or switches sessions. Or, pet state (hunger) continues to advance while the user is away, making the pet appear neglected.

**Prevention:**
- Subscribe to `SystemEvents.SessionSwitch` — pause animations and state advancement on `SessionLock`
- On `SessionUnlock`, calculate elapsed time and advance pet state appropriately (e.g., pet got hungrier while user was away)
- **Phase mapping:** Phase — Pet State Machine & Needs System

### Pitfall 17: Accessibility Not Considered

**What goes wrong:** The pet is purely visual with no accessibility support. Screen readers can't detect it, keyboard users can't interact with it, and high contrast mode makes it invisible.

**Prevention:**
- Ensure system tray icon has descriptive tooltip text
- Provide keyboard-accessible context menu from tray icon
- Test with Windows High Contrast mode
- **Phase mapping:** Phase — System Tray & Lifecycle (tray menu), later phase for accessibility polish

---

## Phase-Specific Warnings

| Phase Topic | Likely Pitfall | Mitigation |
|-------------|---------------|------------|
| Taskbar Integration & Positioning | Pitfalls 2, 4, 6, 8, 13 | Use `SHAppBarMessage` exclusively, handle `TaskbarCreated`, test all taskbar positions/DPI/multi-monitor |
| Window Management & Z-Order | Pitfalls 5, 7, 11 | `WS_EX_NOACTIVATE`, dynamic `Topmost`, transparent window perf testing |
| Animation System & Pet States | Pitfalls 3, 7, 14 | Frame-rate capping, `CompositionTarget` unsubscribe, delta-time updates |
| System Tray & Lifecycle | Pitfalls 1, 9 | `TaskbarCreated` handler, cleanup on all exit paths |
| Pet State Machine & Needs System | Pitfalls 12, 16 | Notification cooldowns, `SessionSwitch` handling, Focus Assist detection |
| State Persistence & Save System | Pitfall 10 | Atomic writes, backup saves, `SessionEnding` handler |
| Asset Pipeline | Pitfalls 4, 15 | DPI-aware asset loading, path resolution via assembly location |
| User Interaction System | Pitfall 11 | Hit-testing, click-through for non-pet areas |

## Sources

- Microsoft Docs: [The Taskbar (Win32)](https://learn.microsoft.com/en-us/windows/win32/shell/taskbar) — `TaskbarCreated` message, `ABM_GETTASKBARPOS`, `ABM_GETSTATE`, notification area APIs
- Microsoft Docs: [WPF Performance Considerations](https://learn.microsoft.com/en-us/dotnet/desktop/wpf/graphics-multimedia/performance) — `AllowsTransparency` software rendering, animation frame rates
- Microsoft Docs: [DPI Awareness in WPF](https://learn.microsoft.com/en-us/windows/win32/hidpi/high-dpi-desktop-application-development-on-windows) — Per-monitor DPI v2, manifest configuration
- Microsoft Docs: [SHAppBarMessage function](https://learn.microsoft.com/en-us/windows/win32/api/shellapi/nf-shellapi-shappbarmessage) — Taskbar position and state queries
- Community knowledge: Desktop overlay application patterns, WPF layered window performance characteristics