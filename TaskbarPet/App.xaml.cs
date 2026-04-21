using System.Windows;

namespace TaskbarPet;

public partial class App : Application
{
    protected override void OnStartup(StartupEventArgs e)
    {
        base.OnStartup(e);
        ShutdownMode = ShutdownMode.OnExplicitShutdown;
        var mainWindow = new MainWindow();
        mainWindow.Show();
    }
}
