using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;

namespace TaskbarPet.Services;

public class TaskbarMonitor : IDisposable
{
    public event Action<TaskbarPosition>? PositionChanged;
    public event Action<bool>? FullscreenChanged;

    private readonly HwndSourceHook _hook;
    private readonly IntPtr _hwnd;
    private TaskbarPosition _lastPosition;
    private bool _lastFullscreen;
    private readonly System.Windows.Threading.DispatcherTimer _pollTimer;

    public TaskbarMonitor(IntPtr hwnd)
    {
        _hwnd = hwnd;
        _hook = WndProc;
        _lastPosition = GetTaskbarPosition();
        _lastFullscreen = IsFullscreenActive();

        // Poll every 2 seconds as fallback for position changes
        // (ABN_POSCHANGED notifications are unreliable on Win11)
        _pollTimer = new System.Windows.Threading.DispatcherTimer(
            TimeSpan.FromSeconds(2),
            System.Windows.Threading.DispatcherPriority.Normal,
            (s, e) => Poll(),
            System.Windows.Threading.Dispatcher.CurrentDispatcher);
        _pollTimer.Start();
    }

    public TaskbarPosition GetTaskbarPosition()
    {
        var data = new APPBARDATA { cbSize = Marshal.SizeOf<APPBARDATA>() };
        SHAppBarMessage(ABM_GETTASKBARPOS, ref data);

        var state = SHAppBarMessage(ABM_GETSTATE, ref data);
        bool autoHide = (state.ToInt64() & ABS_AUTOHIDE) != 0;

        return new TaskbarPosition(
            Left: data.rc.Left,
            Top: data.rc.Top,
            Right: data.rc.Right,
            Bottom: data.rc.Bottom,
            Edge: (ABEdge)data.uEdge,
            AutoHide: autoHide);
    }

    public bool IsFullscreenActive()
    {
        var foreground = GetForegroundWindow();
        if (foreground == IntPtr.Zero || foreground == _hwnd) return false;

        GetWindowRect(foreground, out var rect);
        return rect.Right - rect.Left >= (int)SystemParameters.VirtualScreenWidth &&
               rect.Bottom - rect.Top >= (int)SystemParameters.VirtualScreenHeight;
    }

    private void Poll()
    {
        var newPos = GetTaskbarPosition();
        var newFullscreen = IsFullscreenActive();

        bool positionChanged = newPos != _lastPosition;
        bool fullscreenChanged = newFullscreen != _lastFullscreen;

        if (positionChanged)
        {
            _lastPosition = newPos;
            PositionChanged?.Invoke(newPos);
        }

        if (fullscreenChanged)
        {
            _lastFullscreen = newFullscreen;
            FullscreenChanged?.Invoke(newFullscreen);
        }
    }

    private IntPtr WndProc(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
    {
        // ABN_POSCHANGED = 0x006
        // ABN_STATECHANGE = 0x004
        if (msg == 0x006 || msg == 0x004)
        {
            Poll();
        }
        return IntPtr.Zero;
    }

    public void Dispose()
    {
        _pollTimer.Stop();
    }

    // P/Invoke declarations
    private const int ABM_GETTASKBARPOS = 0x00000005;
    private const int ABM_GETSTATE = 0x00000004;
    private const int ABS_AUTOHIDE = 0x00000001;

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
    private static extern IntPtr SHAppBarMessage(int dwMessage, ref APPBARDATA pData);

    [DllImport("user32.dll")]
    private static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);
}

public record TaskbarPosition(int Left, int Top, int Right, int Bottom, TaskbarMonitor.ABEdge Edge, bool AutoHide);
