# 🐾 Taskbar Pet - Cube Edition

A charming desktop companion that lives in your taskbar! Meet **Cube**, your pixel-perfect pet with personality.

![Cube Pet](assets/cube/idle_0.png)

## ✨ Features

- **Always on Top** - Cube stays visible above all windows
- **Interactive Animations** - Reacts to your clicks with unique animations
- **Speech Bubbles** - Cute messages with typing effect using custom font
- **Low Resource** - Lightweight Python + Tkinter
- **Fully Customizable** - Edit animations, messages, and timing via JSON

## 🎮 Controls

| Action | Effect |
|--------|--------|
| **Left Click** | Pet Cube → Happy typing animation + random message |
| **Right Click** | Feed Cube → Working animation for 5 seconds |
| **Spam Click (3+)** | Annoyed Cube → Error mode for 5 seconds |
| **ESC** | Save & Exit |

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.8+
Pillow (PIL)
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run the Pet
```bash
python main.py
```

Or use the batch file (Windows):
```bash
run_pet.bat
```

## 📁 Project Structure

```
Taskbar_Pet/
├── main.py              # Main application entry point
├── config.py            # All configuration constants
├── state.py             # Pet stats & persistence
├── messages.py          # Unified registry loader
├── pet.py               # Sprite rendering & animations
├── bubble.py            # Speech bubble system
├── message_registry.json # All animations & messages config
├── requirements.txt     # Python dependencies
└── assets/
    ├── cube/            # Cube sprite frames
    ├── font/            # CuteFont-Regular.ttf
    └── ...              # Other pet assets
```

## 🎨 Customization

### Add New Messages

Edit `message_registry.json`:

```json
{
  "registry": {
    "msg_custom_01": {
      "text": "Your message here!",
      "frames": 2,
      "frame_delay": 200,
      "total_time": null,
      "display_time": 1500
    }
  }
}
```

Then add sprite frames:
- `assets/cube/msg_custom_01_0.png`
- `assets/cube/msg_custom_01_1.png`

### Animation Config

```json
{
  "working": {
    "text": "",
    "frames": 2,
    "frame_delay": 200,      // ms per frame
    "total_time": 5000       // ms before returning to idle (null = loop)
  }
}
```

### Change Pet Type

In `pet_config.json` or by deleting it to reset:
```json
{
  "pet_type": "cube"  // or cat, dog, bunny
}
```

## 🖼️ Sprite Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| **Base Animation** | `{state}_{frame}.png` | `idle_0.png`, `typing_1.png` |
| **Message Sprite** | `{msg_id}_{frame}.png` | `msg_pet_01_0.png` |

## 🛠️ Configuration

All timing and behavior in `message_registry.json`:

- **frame_delay**: Animation speed (ms per frame)
- **total_time**: Auto-cancel animation (null = loop forever)
- **display_time**: Bubble visible duration after typing

## 💾 Auto-Save

Cube automatically saves state every 30 seconds:
- Hunger, Happiness, Energy, Health
- Last fed time
- Position

## 🎯 State Stats

| Stat | Description |
|------|-------------|
| **Hunger** | Increases over time, decreases when fed |
| **Happiness** | Increases when petted |
| **Energy** | Decreases over time |
| **Health** | Increases when petted |

## 📝 Message Registry Fields

| Field | Type | Description |
|-------|------|-------------|
| `text` | string | Message to display (empty for base animations) |
| `frames` | int | Number of sprite frames |
| `frame_delay` | int | Milliseconds per frame |
| `total_time` | int/null | Total animation duration (null = loop) |
| `display_time` | int | Bubble display time after typing (messages only) |

## 🌟 Tips

- Cube appears at **bottom-left** of your screen
- Chat bubbles appear every 15-30 seconds during idle
- Spam clicking makes Cube angry (but only for 5 seconds!)
- All messages use **CuteFont** (24px) for that perfect pixel look

## 🤝 Contributing

Want to add more pets or animations? Feel free to:
1. Fork the repo
2. Add your sprites to `assets/`
3. Update `message_registry.json`
4. Submit a PR!

## 📄 License

MIT License - Do whatever you want with Cube! 🎉

---

**Made with ❤️ and Python**

*Cube is waiting for you at the bottom-left corner!* 🐾
