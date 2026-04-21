using System.ComponentModel;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;
using System.Windows.Media;
using TaskbarPet.Services;

namespace TaskbarPet;

public partial class MainWindow : Window
{
    private const int GWL_EXSTYLE = -20;
    private const int WS_EX_NOACTIVATE = 0x08000000;

    private static readonly uint TaskbarCreatedMsg =
        RegisterWindowMessage("TaskbarCreated");

    private HwndSource? _hwndSource;
    private TaskbarMonitor? _taskbarMonitor;
    private H.NotifyIcon.TaskbarIcon? _trayIcon;

    [DllImport("user32.dll")]
    static extern int GetWindowLong(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll")]
    static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    private static extern uint RegisterWindowMessage(string message);

    public MainWindow()
    {
        InitializeComponent();
        Loaded += OnLoaded;
    }

    private void OnLoaded(object sender, RoutedEventArgs e)
    {
        _trayIcon = (H.NotifyIcon.TaskbarIcon)FindResource("TrayIconResource");
        var workArea = SystemParameters.WorkArea;
        Left = workArea.Right - Width - 100;
        Top = workArea.Bottom - Height - 10;
    }

    protected override void OnSourceInitialized(EventArgs e)
    {
        base.OnSourceInitialized(e);

        // WS_EX_NOACTIVATE to prevent focus stealing
        var helper = new WindowInteropHelper(this);
        int exStyle = GetWindowLong(helper.Handle, GWL_EXSTYLE);
        SetWindowLong(helper.Handle, GWL_EXSTYLE, exStyle | WS_EX_NOACTIVATE);

        // Hook WndProc for TaskbarCreated message
        _hwndSource = HwndSource.FromHwnd(helper.Handle);
        _hwndSource.AddHook(WndProc);

        // Initialize taskbar monitoring
        _taskbarMonitor = new TaskbarMonitor(helper.Handle);
        _taskbarMonitor.PositionChanged += OnTaskbarPositionChanged;
        _taskbarMonitor.FullscreenChanged += OnFullscreenChanged;

        // Initial positioning based on current taskbar state
        RepositionWindow(_taskbarMonitor.GetTaskbarPosition());
    }

    private IntPtr WndProc(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
    {
        if (msg == TaskbarCreatedMsg)
        {
            // Explorer restarted — tray icon needs re-creation
            _trayIcon?.ForceCreate();
            handled = true;
        }
        return IntPtr.Zero;
    }

    protected override HitTestResult? HitTestCore(PointHitTestParameters hitTestParameters)
    {
        return null;
    }

    private void RepositionWindow(TaskbarPosition taskbarPos)
    {
        double targetLeft, targetTop;

        switch (taskbarPos.Edge)
        {
            case TaskbarMonitor.ABEdge.Bottom:
                targetLeft = taskbarPos.Right - Width - 50;
                targetTop = taskbarPos.Top + (taskbarPos.Bottom - taskbarPos.Top - Height) / 2;
                break;
            case TaskbarMonitor.ABEdge.Top:
                targetLeft = taskbarPos.Right - Width - 50;
                targetTop = taskbarPos.Bottom - Height + (taskbarPos.Bottom - taskbarPos.Top - Height) / 2;
                break;
            case TaskbarMonitor.ABEdge.Left:
                targetLeft = taskbarPos.Right - Width + (taskbarPos.Right - taskbarPos.Left - Width) / 2;
                targetTop = taskbarPos.Bottom - Height - 50;
                break;
            case TaskbarMonitor.ABEdge.Right:
                targetLeft = taskbarPos.Left + (taskbarPos.Right - taskbarPos.Left - Width) / 2;
                targetTop = taskbarPos.Bottom - Height - 50;
                break;
            default:
                targetLeft = SystemParameters.WorkArea.Right - Width - 50;
                targetTop = SystemParameters.WorkArea.Bottom - Height - 10;
                break;
        }

        // If auto-hide and taskbar is in resting (hidden) position, hide pet
        if (taskbarPos.AutoHide)
        {
            bool taskbarHidden = taskbarPos.Edge switch
            {
                TaskbarMonitor.ABEdge.Bottom => taskbarPos.Top >= (int)SystemParameters.PrimaryScreenHeight - 5,
                TaskbarMonitor.ABEdge.Top => taskbarPos.Bottom <= 5,
                TaskbarMonitor.ABEdge.Left => taskbarPos.Right <= 5,
                TaskbarMonitor.ABEdge.Right => taskbarPos.Left >= (int)SystemParameters.PrimaryScreenWidth - 5,
                _ => false
            };

            if (taskbarHidden)
            {
                Hide();
                return;
            }
            else
            {
                Show();
            }
        }

        Left = targetLeft;
        Top = targetTop;
    }

    private void OnTaskbarPositionChanged(TaskbarPosition newPos)
    {
        Dispatcher.Invoke(() => RepositionWindow(newPos));
    }

    private void OnFullscreenChanged(bool isFullscreen)
    {
        Dispatcher.Invoke(() =>
        {
            if (isFullscreen)
            {
                Topmost = false;
                Hide();
            }
            else
            {
                Topmost = true;
                Show();
                if (_taskbarMonitor != null)
                {
                    RepositionWindow(_taskbarMonitor.GetTaskbarPosition());
                }
            }
        });
    }

    // Tray menu event handlers
    private void OnFeedClicked(object sender, RoutedEventArgs e) { }
    private void OnPauseClicked(object sender, RoutedEventArgs e) { }
    private void OnSettingsClicked(object sender, RoutedEventArgs e) { }
    private void OnExitClicked(object sender, RoutedEventArgs e)
    {
        _trayIcon?.Dispose();
        Application.Current.Shutdown();
    }

    protected override void OnClosing(CancelEventArgs e)
    {
        _taskbarMonitor?.Dispose();
        _trayIcon?.Dispose();
        base.OnClosing(e);
    }
}
