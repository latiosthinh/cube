# Technology Stack

**Project:** Taskbar Pet
**Researched:** 2026-04-21

## Recommended Stack

### Core Framework
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| .NET | 9.0 (current STS) | Runtime | Latest stable with C# 13, best WPF performance, active security patches. .NET 8.0 is the LTS alternative if long-term support without upgrades is preferred. |
| WPF | Built into .NET 9 | UI framework | Native Windows desktop rendering, excellent transparency support, mature animation system, zero additional dependencies. |

### System Tray
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| H.NotifyIcon.Wpf | 2.4.1 | System tray icon | Modern, actively maintained (last release Dec 2025), supports .NET 10, Windows 11 Efficiency Mode, NativeAOT/trimming support, pure WPF (no WinForms dependency), dynamic icon generation, 742 GitHub stars. Direct continuation of Hardcodet. |

### Serialization / Persistence
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| System.Text.Json | Built into .NET 9 | Pet state save/load | Zero dependencies, fastest JSON serializer in .NET ecosystem, source generators for AOT compatibility, built into the runtime. Perfect for small pet state files (hunger, mood, level, position). |

### Image / Animation
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| WPF Image + BitmapFrame | Built into .NET | Sprite sheet rendering | Native PNG support with transparency, `BitmapFrame.Create()` for loading individual frames from sprite sheets, hardware-accelerated rendering via DirectX. |
| WPF Storyboard + DoubleAnimation | Built into .NET | Frame-by-frame animation | Built-in timing system, `DoubleAnimation` for position/opacity, `ObjectAnimationUsingKeyFrames` for switching `Image.Source` between sprite frames, `RepeatBehavior` for looping walk cycles. |
| WriteableBitmap (optional) | Built into .NET | Runtime sprite extraction | If sprite sheets need runtime slicing, `WriteableBitmap` enables pixel-level manipulation without external libraries. |

### Taskbar Position Detection
| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| P/Invoke `SHAppBarMessage` | Windows API (shell32.dll) | Detect taskbar position/size | The authoritative way to query taskbar location (top/bottom/left/right), dimensions, and auto-hide state. Required because WPF has no built-in taskbar API. Use `ABM_GETTASKBARPOS` with `APPBARDATA`. |
| P/Invoke `SystemParametersInfo` | Windows API (user32.dll) | Detect auto-hide, work area | `SPI_GETWORKAREA` gives the usable desktop area excluding the taskbar. Combined with `SHAppBarMessage` for full taskbar awareness. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not |
|----------|-------------|-------------|---------|
| System Tray | H.NotifyIcon.Wpf 2.4.1 | Hardcodet.NotifyIcon.Wpf 2.0.1 | Hardcodet is the original (966 stars, 8.2M downloads) but last release was Oct 2024. H.NotifyIcon is the active continuation with .NET 10 support, Efficiency Mode, and NativeAOT. Both work; H.NotifyIcon is the forward-looking choice. |
| System Tray | H.NotifyIcon.Wpf 2.4.1 | WinForms NotifyIcon | WinForms NotifyIcon requires interop with Windows Forms, adds unnecessary dependency, and lacks WPF-native features like custom XAML tooltips and popups. |
| Runtime | .NET 9.0 | .NET 8.0 LTS | .NET 8 is LTS (supported until Nov 2026) and valid if you need maximum stability. .NET 9 has better performance, C# 13 features, and is actively patched. For a desktop pet app, .NET 9's improvements outweigh LTS concerns. |
| Serialization | System.Text.Json | Newtonsoft.Json | Newtonsoft.Json is legacy. System.Text.Json is faster, built-in, and the Microsoft-recommended path. Newtonsoft adds a 700KB dependency for no benefit in this use case. |
| Serialization | System.Text.Json | BinaryFormatter | BinaryFormatter is obsolete and deprecated due to security vulnerabilities. Never use it. |
| Animation | WPF Storyboard | SkiaSharp | SkiaSharp is overkill for a 2D cartoon pet. It adds complexity, requires manual render loops, and loses WPF's declarative XAML animation benefits. Only consider if you need complex skeletal animation or particle effects. |
| Animation | WPF Storyboard | Live2D Cubism SDK | Live2D is for anime-style 2D skeletal animation. Overkill for a cartoon taskbar pet, adds significant binary size (~10MB+), and requires licensing for commercial use. |
| Architecture | Single transparent WPF Window | Multiple layered windows | Multiple windows add complexity for z-ordering, synchronization, and hit-testing. A single `AllowsTransparency=True` window with layered content is simpler and more performant. |

## Installation

```bash
# Create WPF project
dotnet new wpf -n TaskbarPet -f net9.0
cd TaskbarPet

# System tray integration
dotnet add package H.NotifyIcon.Wpf --version 2.4.1
```

## Architecture Patterns

### Transparent Pet Window

```xml
<!-- PetWindow.xaml -->
<Window x:Class="TaskbarPet.PetWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        WindowStyle="None"
        AllowsTransparency="True"
        Background="Transparent"
        ShowInTaskbar="False"
        Topmost="True"
        ResizeMode="NoResize"
        SizeToContent="WidthAndHeight">
    <Image x:Name="PetImage" Stretch="None" />
</Window>
```

**Critical:** `AllowsTransparency="True"` **requires** `WindowStyle="None"`. This is enforced by WPF and will throw `InvalidOperationException` otherwise. (Source: Microsoft Learn, `Window.AllowsTransparency` property docs)

### Click-Through Handling

For areas of the pet that should not intercept mouse clicks (e.g., transparent padding around the sprite):

```csharp
// Make specific UI elements click-through
petElement.IsHitTestVisible = false;

// Or handle at window level with custom hit testing
protected override HitTestResult HitTestCore(PointHitTestParameters hitTestParameters)
{
    var point = hitTestParameters.HitPoint;
    // Check if point hits opaque pixel in the sprite
    return IsPixelOpaque(point) 
        ? new PointHitTestResult(this, point) 
        : null; // null = click passes through to desktop
}
```

### Taskbar Position Detection (P/Invoke)

```csharp
using System.Runtime.InteropServices;

[StructLayout(LayoutKind.Sequential)]
public struct RECT { public int Left, Top, Right, Bottom; }

[StructLayout(LayoutKind.Sequential)]
public struct APPBARDATA
{
    public int cbSize;
    public IntPtr hWnd;
    public int uCallbackMessage;
    public int uEdge;
    public RECT rc;
    public IntPtr lParam;
}

public enum ABEdge : int { Left = 0, Top, Right, Bottom }

[DllImport("shell32.dll")]
static extern IntPtr SHAppBarMessage(int dwMessage, ref APPBARDATA pData);

public static RECT GetTaskbarRect()
{
    var data = new APPBARDATA { cbSize = Marshal.SizeOf<APPBARDATA>() };
    SHAppBarMessage(0x00000005, ref data); // ABM_GETTASKBARPOS
    return data.rc;
}
```

### Pet State Serialization

```csharp
using System.Text.Json;

public record PetState(
    string PetType,
    int Hunger,
    int Happiness,
    int Energy,
    int Level,
    DateTime LastFed,
    DateTime LastSlept,
    double PositionX
);

// Save
var json = JsonSerializer.Serialize(state, new JsonSerializerOptions 
{ 
    WriteIndented = true,
    PropertyNamingPolicy = JsonNamingPolicy.CamelCase 
});
await File.WriteAllTextAsync("pet-state.json", json);

// Load
var state = JsonSerializer.Deserialize<PetState>(
    await File.ReadAllTextAsync("pet-state.json"));
```

### Sprite Animation with Storyboard

```xml
<!-- Walk cycle: cycle through 4 sprite frames -->
<ObjectAnimationUsingKeyFrames 
    Storyboard.TargetName="PetImage"
    Storyboard.TargetProperty="Source"
    RepeatBehavior="Forever"
    Duration="0:0:0.4">
    <DiscreteObjectKeyFrame KeyTime="0:0:0.0" 
        Value="{StaticResource Frame1}" />
    <DiscreteObjectKeyFrame KeyTime="0:0:0.1" 
        Value="{StaticResource Frame2}" />
    <DiscreteObjectKeyFrame KeyTime="0:0:0.2" 
        Value="{StaticResource Frame3}" />
    <DiscreteObjectKeyFrame KeyTime="0:0:0.3" 
        Value="{StaticResource Frame4}" />
</ObjectAnimationUsingKeyFrames>
```

### System Tray Integration (H.NotifyIcon.Wpf)

```xml
<Window xmlns:tb="clr-namespace:H.NotifyIcon;assembly=H.NotifyIcon.Wpf">
    <tb:TaskbarIcon
        x:Name="TrayIcon"
        IconSource="/Assets/tray-icon.ico"
        ToolTipText="Taskbar Pet"
        MenuActivation="LeftOrRightClick"
        PopupActivation="DoubleClick">
        <tb:TaskbarIcon.ContextMenu>
            <ContextMenu>
                <MenuItem Header="Feed" Command="{Binding FeedCommand}" />
                <MenuItem Header="Pause" Command="{Binding PauseCommand}" />
                <Separator />
                <MenuItem Header="Settings" Command="{Binding SettingsCommand}" />
                <MenuItem Header="Exit" Command="{Binding ExitCommand}" />
            </ContextMenu>
        </tb:TaskbarIcon.ContextMenu>
    </tb:TaskbarIcon>
</Window>
```

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| .NET/WPF version | HIGH | Verified against dotnet.microsoft.com download pages (April 2026 releases) |
| H.NotifyIcon.Wpf | HIGH | Verified against NuGet (v2.4.1, Dec 2025) and GitHub README |
| Hardcodet.NotifyIcon.Wpf | HIGH | Verified against NuGet (v2.0.1, Oct 2024) and GitHub README |
| AllowsTransparency + WindowStyle=None | HIGH | Verified against Microsoft Learn API docs |
| System.Text.Json | HIGH | Built into .NET, official Microsoft recommendation |
| SHAppBarMessage P/Invoke | HIGH | Standard Windows API, documented on MSDN for decades |
| WPF Storyboard animation | HIGH | Verified against Microsoft Learn Animation Overview |
| Click-through via HitTestCore override | MEDIUM | Standard WPF pattern, verified through API docs but not tested in this specific use case |
| WriteableBitmap for sprite slicing | MEDIUM | Valid API but alternative approach (pre-sliced PNGs) may be simpler |

## Sources

- Microsoft Learn: Window.AllowsTransparency Property — https://learn.microsoft.com/en-us/dotnet/api/system.windows.window.allowstransparency
- Microsoft Learn: Animation Overview (WPF) — https://learn.microsoft.com/en-us/dotnet/desktop/wpf/graphics-multimedia/animation-overview
- H.NotifyIcon.Wpf NuGet — https://www.nuget.org/packages/H.NotifyIcon.Wpf (v2.4.1)
- H.NotifyIcon GitHub — https://github.com/HavenDV/H.NotifyIcon
- Hardcodet.NotifyIcon.Wpf NuGet — https://www.nuget.org/packages/Hardcodet.NotifyIcon.Wpf (v2.0.1)
- Hardcodet NotifyIcon GitHub — https://github.com/hardcodet/wpf-notifyicon
- .NET 9.0 Download — https://dotnet.microsoft.com/en-us/download/dotnet/9.0
- .NET 8.0 Download — https://dotnet.microsoft.com/en-us/download/dotnet/8.0
