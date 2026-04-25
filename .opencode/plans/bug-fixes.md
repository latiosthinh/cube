# Taskbar Pet - Bug Fixes

## Issues Fixed

### 1. Duplicate `_hide_menu` method (CRITICAL)
**Problem:** Two `_hide_menu` methods defined (lines 197-204 and 246-254)
**Fix:** Remove the first duplicate (lines 197-204), keep the second one with `menu_hover_active = False`

### 2. Welcome message timing (CRITICAL)
**Problem:** `current_time > 1000` compares epoch milliseconds (always ~1.7 trillion)
**Fix:** Use `self.root.after(1000, lambda: self.bubble.show_bubble('msg_welcome'))` in `__init__`

### 3. Menu hover flicker (CRITICAL)
**Problem:** 100ms delay too short when moving mouse from pet to menu
**Fix:** Change to 300ms show delay, 400ms hide delay

### 4. Bubble overlap (CRITICAL)
**Problem:** No check if bubble exists before showing new one
**Fix:** Add `if self.bubble: return` at start of `_show_bubble_impl`

### 5. Menu positioning off-screen
**Problem:** `y - 120` can place menu above screen
**Fix:** Use `max(10, self.y - 120)` and set explicit dimensions

### 6. Keyboard shortcuts unreliable
**Problem:** Depends on `menu_hover_active` which can desync
**Fix:** Add `_is_menu_visible()` helper checking both flags

### 7. Outdated print message
**Problem:** Says "Click menu button" but button removed
**Fix:** Update to "Hover cube or Alt+C for menu, 1-4 to select"

### 8. Bare except clauses
**Problem:** `except:` catches everything including KeyboardInterrupt
**Fix:** Change to `except Exception:`

---

## Code Changes

### main.py

#### Line 85 - Update print message
```python
# OLD:
print("Controls: Click menu button or use number keys 1-4")

# NEW:
print("Controls: Hover cube or Alt+C for menu, 1-4 to select")
```

#### Lines 96-117 - Fix hover timing and bare excepts
```python
# OLD:
def on_pet_enter(self, event):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
        except:
            pass
    self.menu_hover_timer = self.root.after(200, self._show_action_menu_delayed)

def on_pet_leave(self, event):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
            self.menu_hover_timer = None
        except:
            pass
    self.menu_hover_timer = self.root.after(100, self._hide_menu_delayed)

# NEW:
def on_pet_enter(self, event):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
        except Exception:
            pass
    self.menu_hover_timer = self.root.after(300, self._show_action_menu_delayed)

def on_pet_leave(self, event):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
            self.menu_hover_timer = None
        except Exception:
            pass
    self.menu_hover_timer = self.root.after(400, self._hide_menu_delayed)
```

#### Lines 140-182 - Fix menu positioning and bare excepts
```python
# OLD:
def _show_action_menu(self):
    self._hide_menu()
    self.menu_frame = tk.Toplevel(self.root)
    self.menu_frame.overrideredirect(True)
    self.menu_frame.wm_attributes("-topmost", True)
    
    menu_bg = tk.Frame(self.menu_frame, bg='white', relief='solid', borderwidth=1)
    menu_bg.pack(fill='both', expand=True)
    
    self.menu_frame.bind("<Enter>", lambda e: self._on_menu_enter())
    self.menu_frame.bind("<Leave>", lambda e: self._on_menu_leave())
    menu_bg.bind("<Enter>", lambda e: self._on_menu_enter())
    menu_bg.bind("<Leave>", lambda e: self._on_menu_leave())
    
    items = [
        ("1. Pet", self._action_pet),
        ("2. Feed", self._action_feed),
        ("3. Show idea list", self._action_ideas),
        ("4. Terminate", self.on_escape)
    ]
    
    for text, command in items:
        btn = tk.Button(menu_bg, text=text, bg='white', fg='black', 
                       activebackground='#e0e0e0', activeforeground='black',
                       padx=15, pady=5, anchor='w', cursor='hand2',
                       relief='flat', command=command)
        btn.pack(fill='x', padx=2, pady=2)
        btn.bind("<Enter>", lambda e: e.widget.config(bg='#e0e0e0'))
        btn.bind("<Leave>", lambda e: e.widget.config(bg='white'))
    
    menu_x = self.x + PET_WIDTH - 130
    menu_y = self.y - 120
    self.menu_frame.geometry(f"+{menu_x}+{menu_y}")
    
    self.bubble._destroy_bubble()

# NEW:
def _show_action_menu(self):
    self._hide_menu()
    self.menu_frame = tk.Toplevel(self.root)
    self.menu_frame.overrideredirect(True)
    self.menu_frame.wm_attributes("-topmost", True)
    
    menu_bg = tk.Frame(self.menu_frame, bg='white', relief='solid', borderwidth=1)
    menu_bg.pack(fill='both', expand=True)
    
    self.menu_frame.bind("<Enter>", lambda e: self._on_menu_enter())
    self.menu_frame.bind("<Leave>", lambda e: self._on_menu_leave())
    menu_bg.bind("<Enter>", lambda e: self._on_menu_enter())
    menu_bg.bind("<Leave>", lambda e: self._on_menu_leave())
    
    items = [
        ("1. Pet", self._action_pet),
        ("2. Feed", self._action_feed),
        ("3. Show idea list", self._action_ideas),
        ("4. Terminate", self.on_escape)
    ]
    
    for text, command in items:
        btn = tk.Button(menu_bg, text=text, bg='white', fg='black', 
                       activebackground='#e0e0e0', activeforeground='black',
                       padx=15, pady=5, anchor='w', cursor='hand2',
                       relief='flat', command=command)
        btn.pack(fill='x', padx=2, pady=2)
        btn.bind("<Enter>", lambda e: e.widget.config(bg='#e0e0e0'))
        btn.bind("<Leave>", lambda e: e.widget.config(bg='white'))
    
    menu_width = 130
    menu_height = 120
    menu_x = self.x + PET_WIDTH - menu_width
    menu_y = max(20, self.y - menu_height - 20)
    self.menu_frame.geometry(f"{menu_width}x{menu_height}+{menu_x}+{menu_y}")
    
    self.bubble._destroy_bubble()
```

#### Lines 184-195 - Fix bare excepts
```python
# OLD:
def _on_menu_enter(self):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
            self.menu_hover_timer = None
        except:
            pass

def _on_menu_leave(self):
    self.menu_hover_timer = self.root.after(300, self._hide_menu_delayed)

# NEW: (same logic, just fix except)
def _on_menu_enter(self):
    if self.menu_hover_timer:
        try:
            self.root.after_cancel(self.menu_hover_timer)
            self.menu_hover_timer = None
        except Exception:
            pass

def _on_menu_leave(self):
    self.menu_hover_timer = self.root.after(300, self._hide_menu_delayed)
```

#### Lines 197-204 - REMOVE THIS DUPLICATE METHOD
Delete lines 197-204 entirely (the first `_hide_menu` definition)

#### Lines 206-221 - Fix keyboard shortcuts
```python
# OLD:
def on_key_press(self, event):
    if event.keysym == 'Escape':
        self.on_escape(event)
    elif event.char == '1':
        if self.menu_hover_active or self.menu_frame:
            self._action_pet()
    elif event.char == '2':
        if self.menu_hover_active or self.menu_frame:
            self._action_feed()
    elif event.char == '3':
        if self.menu_hover_active or self.menu_frame:
            self._action_ideas()
    elif event.char == '4':
        if self.menu_hover_active or self.menu_frame:
            self.on_escape(event)

# NEW:
def on_key_press(self, event):
    if event.keysym == 'Escape':
        self.on_escape(event)
    elif event.char == '1' and self._is_menu_visible():
        self._action_pet()
    elif event.char == '2' and self._is_menu_visible():
        self._action_feed()
    elif event.char == '3' and self._is_menu_visible():
        self._action_ideas()
    elif event.char == '4' and self._is_menu_visible():
        self.on_escape(event)

def _is_menu_visible(self):
    return self.menu_hover_active or self.menu_frame is not None
```

#### Lines 246-254 - Fix bare except in _hide_menu
```python
# OLD:
def _hide_menu(self):
    self.menu_hover_active = False
    if self.menu_frame:
        try:
            self.menu_frame.destroy()
        except:
            pass
        self.menu_frame = None

# NEW:
def _hide_menu(self):
    self.menu_hover_active = False
    if self.menu_frame:
        try:
            self.menu_frame.destroy()
        except Exception:
            pass
        self.menu_frame = None
```

#### Lines 356-364 - Fix welcome message timing
```python
# OLD:
def state_display_loop(self):
    import time
    current_time = time.time() * 1000
    
    if not self.welcome_shown and current_time > 1000:
        self.bubble.show_bubble('msg_welcome')
        self.welcome_shown = True

# NEW: Remove welcome logic from here entirely
def state_display_loop(self):
    import time
    current_time = time.time() * 1000
    
    # Don't show state messages when menu is active
    if not self.menu_hover_active and not self.state.is_sleeping and not self.state.is_eating and self.pet.animation_state == 'idle':
```

#### Add to __init__ after line 82 - Welcome message
```python
# Add after: self.root.after(100, self._force_position)
self.root.after(1000, lambda: self.bubble.show_bubble('msg_welcome'))
```

---

### bubble.py

#### Line 55 - Add bubble overlap prevention
```python
# OLD:
def _show_bubble_impl(self, message_id_or_text, duration=2000, on_typing_complete=None):
    """Internal bubble display implementation"""
    # Resolve from unified REGISTRY

# NEW:
def _show_bubble_impl(self, message_id_or_text, duration=2000, on_typing_complete=None):
    """Internal bubble display implementation"""
    # Prevent overlapping bubbles
    if self.bubble is not None:
        return
    
    # Resolve from unified REGISTRY
```
