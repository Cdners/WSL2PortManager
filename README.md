# WSL2-WSL2端口转发管理器

自行打包命令
pyinstaller --onefile --noconsole --add-data="ui_mainwindow.py;." --name="WSL2 端口转发管理器" main.py

参数说明:
  --onefile: 将程序打包成 单个 可执行文件。 如果你不使用此选项，PyInstaller 会创建一个包含可执行文件和依赖项的文件夹。
  --noconsole (或 --windowed): 阻止程序运行时出现控制台窗口（黑色命令行窗口）。 如果你的程序是 GUI 程序，通常需要使用此选项。
  --icon=icon.ico: 指定可执行文件的图标。 将 icon.ico 替换为你的图标文件名（如果使用了图标）。
  --add-data="ui_mainwindow.py;.": 将 ui_mainwindow.py 文件添加到打包结果中，并将其放在与可执行文件相同的目录下（. 表示当前目录）。 这是因为你的程序在运行时需要加载这个 UI 文件。 注意：在 Windows 上，路径分隔符是 ;，在 Linux/macOS 上是 :。
  --name="WSL2 端口转发管理器": 指定生成的可执行文件的名称。
  main.py: 主程序文件。
