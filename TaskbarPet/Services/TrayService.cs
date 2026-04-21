using System.Windows;
using System.Windows.Controls;
using System.Windows.Media.Imaging;
using H.NotifyIcon;

namespace TaskbarPet.Services;

public class TrayService : IDisposable
{
    private readonly TaskbarIcon _trayIcon;
    private readonly Window _ownerWindow;

    public TrayService(Window ownerWindow)
    {
        _ownerWindow = ownerWindow;
        _trayIcon = new TaskbarIcon
        {
            IconSource = new BitmapImage(new Uri("pack://application:,,,/Assets/tray-icon.ico")),
            ToolTipText = "Taskbar Pet",
            MenuActivation = H.NotifyIcon.Core.PopupActivationMode.LeftOrRightClick
        };
        _trayIcon.ContextMenu = CreateContextMenu();
        _trayIcon.ForceCreate();
    }

    public void HandleTaskbarCreated()
    {
        _trayIcon.ForceCreate();
    }

    public TaskbarIcon TrayIcon => _trayIcon;

    private ContextMenu CreateContextMenu()
    {
        var menu = new ContextMenu();

        var feedItem = new MenuItem { Header = "Feed" };
        feedItem.Click += (s, e) => OnFeedClicked();
        menu.Items.Add(feedItem);

        var pauseItem = new MenuItem { Header = "Pause" };
        pauseItem.Click += (s, e) => OnPauseClicked();
        menu.Items.Add(pauseItem);

        menu.Items.Add(new Separator());

        var settingsItem = new MenuItem { Header = "Settings" };
        settingsItem.Click += (s, e) => OnSettingsClicked();
        menu.Items.Add(settingsItem);

        var exitItem = new MenuItem { Header = "Exit" };
        exitItem.Click += (s, e) => OnExitClicked();
        menu.Items.Add(exitItem);

        return menu;
    }

    private void OnFeedClicked() { /* Placeholder — wired in Phase 2 */ }
    private void OnPauseClicked() { /* Placeholder — toggle pet animation */ }
    private void OnSettingsClicked() { /* Placeholder — wired in Phase 3 */ }
    private void OnExitClicked()
    {
        _trayIcon.Dispose();
        Application.Current.Shutdown();
    }

    public void Dispose()
    {
        _trayIcon.Dispose();
    }
}
