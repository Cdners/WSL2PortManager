# WSL2 端口转发管理器

这是一个用于管理 WSL2 端口转发规则的图形界面程序。

## 打包说明

要将此程序打包成可执行文件，请使用 PyInstaller：

1.  安装 PyInstaller：
    ```bash
    pip install pyinstaller
    ```

2.  使用以下命令打包程序：

    **Windows:**

    ```bash
    pyinstaller --onefile --noconsole --icon=icon.ico --add-data="ui_mainwindow.py;." --name="WSL2 端口转发管理器" main.py
    ```

    **Linux/macOS:**

    ```bash
    pyinstaller --onefile --noconsole --icon=icon.ico --add-data="ui_mainwindow.py:." --name="WSL2 端口转发管理器" main.py
    ```

    **参数说明:**

    *   `--onefile`: 将程序打包成单个可执行文件。
    *   `--noconsole`: 运行时不显示控制台窗口。
    *   `--icon=icon.ico`:  设置可执行文件的图标,不使用不要加否则打包出错 (可选)。
    *   `--add-data`:  添加额外的数据文件。
        *   对于 Windows： `--add-data="ui_mainwindow.py;."`
        *   对于 Linux/macOS： `--add-data="ui_mainwindow.py:."`
    *   `--name`:  指定可执行文件的名称。
    *   `main.py`:  你的主程序文件。

3.  打包完成后，可执行文件将在 `dist` 文件夹中找到。
