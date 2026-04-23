# Taskbar Pet

A desktop pet that sits at the bottom-left corner of your screen using a cube sprite.

## Run the Pet

```bash
python pet_final.py
```

Or use the batch file:
```bash
run_pet.bat
```

## Controls

- **Left-click**: Pet the cube (shows working animation)
- **Right-click**: Feed the cube (shows typing animation)
- **ESC**: Exit and save state

## States

The cube has the following animation states based on sprite file names:
- `idle` - Default resting state
- `typing` - Shown when feeding
- `working` - Shown when petting
- `error` - Available for future use
