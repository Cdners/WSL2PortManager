import sys
import subprocess
import re
import logging
import traceback
import chardet  # 导入 chardet
from PySide6.QtWidgets import (QApplication, QMainWindow, QTableWidget,
                               QTableWidgetItem, QMessageBox, QLineEdit,
                               QPushButton, QVBoxLayout, QWidget, QLabel,
                               QFormLayout, QDialog, QHeaderView,
                               QDialogButtonBox, QStyledItemDelegate,
                               QSizePolicy)  # 导入 QSizePolicy
from PySide6.QtCore import Qt, QProcess, QSize, Signal, QObject
from PySide6.QtGui import QIcon, QColor, QPalette
from ui_mainwindow import Ui_MainWindow

# 配置日志记录
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        # logging.FileHandler("wsl_portproxy.log"),  # 输出到文件 (可选)
    ]
)
logger = logging.getLogger(__name__)

# ------------------------------
# 日志与命令执行辅助
# ------------------------------

class _LogEmitter(QObject):
    """Qt 信号发射器（用于跨线程/跨模块把日志安全地送到 UI）。"""

    message = Signal(str)


class QtPlainTextLogHandler(logging.Handler):
    """将 Python logging 输出同步到 Qt 的 QPlainTextEdit。

    参数:
        emitter: Qt 信号发射器，接收格式化后的文本。
    """

    def __init__(self, emitter: _LogEmitter):
        super().__init__()
        self._emitter = emitter

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self._emitter.message.emit(msg)
        except Exception:
            # 日志系统内部出错不能再抛异常，避免递归
            pass


def _decode_bytes(data: bytes) -> str:
    """将命令输出的 bytes 解码为字符串（优先使用 chardet 检测）。

    参数:
        data: 命令输出的原始 bytes。

    返回:
        解码后的字符串（保证不抛异常）。
    """

    if not data:
        return ""
    try:
        result = chardet.detect(data)
        encoding = result.get("encoding")
        confidence = result.get("confidence", 0.0) or 0.0
        if encoding and confidence > 0.7:
            return data.decode(encoding, errors="replace")
    except Exception:
        pass
    return data.decode("utf-8", errors="replace")


def run_powershell(command: str) -> tuple[int, str, str]:
    """执行 PowerShell 命令并返回结果（无窗口）。

    参数:
        command: PowerShell 命令文本（建议是一条完整的 -Command 内容）。

    返回:
        (return_code, stdout_text, stderr_text)
    """

    process = subprocess.Popen(
        [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-Command",
            command,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW,
    )
    stdout, stderr = process.communicate()
    return process.returncode, _decode_bytes(stdout), _decode_bytes(stderr)


def firewall_rule_display_name(listen_port: str) -> str:
    """生成防火墙规则显示名。

    参数:
        listen_port: Windows 监听端口（字符串数字）。

    返回:
        规则 DisplayName，例如: WSL-8080-LAN
    """

    return f"WSL-{listen_port}-LAN"


def ensure_firewall_rule_private_public(listen_port: str) -> tuple[bool, str]:
    """确保存在“公用/专用”的入站放行规则（TCP/LocalPort）。

    设计说明:
        - 先 Remove 再 New，保证幂等；重复执行不会累积多条重复规则。
        - Profile 使用 Private,Public（你提到的“公用/专用”）。

    参数:
        listen_port: Windows 监听端口（字符串数字）。

    返回:
        (ok, message)
    """

    name = firewall_rule_display_name(listen_port)
    ps = (
        f'Remove-NetFirewallRule -DisplayName "{name}" -ErrorAction SilentlyContinue; '
        f'New-NetFirewallRule -DisplayName "{name}" -Direction Inbound -Protocol TCP '
        f'-LocalPort {listen_port} -Action Allow -Profile Private,Public'
    )
    code, out, err = run_powershell(ps)
    ok = code == 0
    msg = out.strip() if ok else (err.strip() or out.strip() or f"PowerShell 返回码: {code}")
    return ok, msg


def remove_firewall_rule(listen_port: str) -> tuple[bool, str]:
    """删除防火墙规则（按 DisplayName）。

    参数:
        listen_port: Windows 监听端口（字符串数字）。

    返回:
        (ok, message)
    """

    name = firewall_rule_display_name(listen_port)
    ps = f'Remove-NetFirewallRule -DisplayName "{name}" -ErrorAction SilentlyContinue'
    code, out, err = run_powershell(ps)
    ok = code == 0
    msg = out.strip() if ok else (err.strip() or out.strip() or f"PowerShell 返回码: {code}")
    return ok, msg


# 自定义 ItemDelegate
class CustomItemDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        if index.column() == 4:
            option.foregroundRole = QPalette.Text
            option.palette.setColor(QPalette.Text, QColor("red"))

class AddRuleDialog(QDialog):
    ruleAdded = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加规则")
        self.listen_port = QLineEdit()
        self.listen_port.setPlaceholderText("Windows 端口 (例如 8080)")
        self.listen_address = QLineEdit("0.0.0.0")
        self.connect_port = QLineEdit()
        self.connect_port.setPlaceholderText("WSL2 端口 (例如 1996)")
        self.connect_address = QLineEdit()
        self.connect_address.setPlaceholderText("WSL2 IP")
        self.get_wsl_ip()

        form_layout = QFormLayout()
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        form_layout.setRowWrapPolicy(QFormLayout.DontWrapRows)
        form_layout.setLabelAlignment(Qt.AlignLeft)
        form_layout.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        form_layout.setSpacing(10)
        form_layout.addRow("监听端口:", self.listen_port)
        form_layout.addRow("监听地址:", self.listen_address)
        form_layout.addRow("连接端口:", self.connect_port)
        form_layout.addRow("连接地址:", self.connect_address)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        form_layout.addRow(button_box)
        self.setLayout(form_layout)
        self.setMinimumWidth(450)  # 增加最小宽度
        self.resize(500, 250)  # 调整默认大小

    def get_wsl_ip(self):
        logger.debug("进入 get_wsl_ip")
        process = QProcess()
        process.start("wsl", ["hostname", "-I"])
        process.waitForFinished()
        if process.exitCode() != 0:
            error_msg = process.readAllStandardError().data().decode()
            logger.error(f"获取 WSL2 IP 失败: {error_msg}")
            QMessageBox.warning(self, "错误", "获取 WSL2 IP 失败: " + error_msg)
            return
        ip_output = process.readAllStandardOutput().data().decode().strip()

        if ip_output:
            # 只取第一个 IP 地址
            first_ip = ip_output.split()[0]
            self.connect_address.setText(first_ip)
            logger.debug(f"获取到 WSL2 IP: {first_ip}")
        else:
            logger.warning("无法自动获取 WSL2 IP 地址，请手动输入。")
            QMessageBox.warning(self, "错误", "无法自动获取 WSL2 IP 地址，请手动输入。")
        logger.debug("退出 get_wsl_ip")

    def get_data(self):
        logger.debug("进入 get_data")
        listen_port = self.listen_port.text().strip()
        listen_address = self.listen_address.text().strip()
        connect_port = self.connect_port.text().strip()
        connect_address = self.connect_address.text().strip()

        if not (listen_port.isdigit() and connect_port.isdigit() and listen_address and connect_address):
            error_msg = "输入无效，请检查端口和地址是否正确。"
            logger.warning(error_msg)
            QMessageBox.warning(self, "错误", error_msg)
            return None
        logger.debug(f"获取到数据：listenPort={listen_port}, listenAddress={listen_address}, connectPort={connect_port}, connectAddress={connect_address}")
        logger.debug("退出 get_data")
        return {
            "listenPort": listen_port,
            "listenAddress": listen_address,
            "connectPort": connect_port,
            "connectAddress": connect_address,
        }

    def accept(self):
        logger.debug("进入 accept")
        data = self.get_data()
        if data:
            self.ruleAdded.emit(data)
            super().accept()
        logger.debug("退出 accept")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("WSL2 端口转发管理器")
        self.setWindowIcon(QIcon("icon.png"))

        # 右侧多日志看板初始化
        self._log_emitter = _LogEmitter()
        self._log_emitter.message.connect(self._append_app_log)
        self._install_ui_log_handler()

        # 设置左右分栏比例（左：规则，右：日志）
        try:
            self.ui.splitterMain.setStretchFactor(0, 3)
            self.ui.splitterMain.setStretchFactor(1, 2)
        except Exception:
            pass

        # 连接信号和槽
        self.ui.pushButtonRefresh.clicked.connect(self.load_rules)
        self.ui.pushButtonAdd.clicked.connect(self.show_add_dialog)

        # 设置表格样式
        self.ui.tableWidgetRules.setAlternatingRowColors(True)
        self.ui.tableWidgetRules.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.ui.tableWidgetRules.setSelectionBehavior(QTableWidget.SelectRows)
        self.ui.tableWidgetRules.setItemDelegate(CustomItemDelegate())
        # 设置表头高度
        self.ui.tableWidgetRules.verticalHeader().setDefaultSectionSize(30)  # 调整行高
        self.ui.tableWidgetRules.horizontalHeader().setFixedHeight(35) # 表头高度

        # 只在初始化时设置一次表头标签
        self.ui.tableWidgetRules.setColumnCount(5)
        self.ui.tableWidgetRules.setHorizontalHeaderLabels([
            "监听端口", "监听地址", "连接端口", "连接地址", "操作"
        ])

        self.load_rules()

    def _install_ui_log_handler(self) -> None:
        """将 Python logging 输出接入到右侧“应用日志”看板。"""

        handler = QtPlainTextLogHandler(self._log_emitter)
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)

    def _append_app_log(self, text: str) -> None:
        """追加一行到“应用日志”面板（自动滚动）。

        参数:
            text: 单行日志文本。
        """

        try:
            self.ui.plainTextEditAppLog.appendPlainText(text)
            cursor = self.ui.plainTextEditAppLog.textCursor()
            cursor.movePosition(cursor.End)
            self.ui.plainTextEditAppLog.setTextCursor(cursor)
        except Exception:
            pass

    def _append_cmd_log(self, text: str) -> None:
        """追加内容到“命令输出”面板。

        参数:
            text: 输出文本（可多行）。
        """

        try:
            self.ui.plainTextEditCmdLog.appendPlainText(text)
        except Exception:
            pass

    def _append_ps_log(self, text: str) -> None:
        """追加内容到 PowerShell 面板。

        参数:
            text: PowerShell 输出文本（可多行）。
        """

        try:
            self.ui.plainTextEditPsLog.appendPlainText(text)
        except Exception:
            pass

    def show_add_dialog(self):
        logger.debug("进入 show_add_dialog")
        dialog = AddRuleDialog(self)
        dialog.ruleAdded.connect(self.add_rule)
        dialog.exec()
        logger.debug("退出 show_add_dialog")

    def load_rules(self):
        logger.debug("进入 load_rules")
        self.clear_error()
        try:
            # 先获取原始字节数据
            raw_output = subprocess.check_output(
                ["netsh", "interface", "portproxy", "show", "v4tov4"],
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            # 使用 chardet 检测编码
            result = chardet.detect(raw_output)
            encoding = result['encoding']
            confidence = result['confidence']
            logger.debug(f"检测到的编码：{encoding} (置信度：{confidence})")


            # 如果置信度足够高，则使用检测到的编码解码
            if encoding and confidence > 0.7:  # 可以调整置信度阈值
                output = raw_output.decode(encoding)
            else:
                logger.warning(f"编码检测失败或置信度低，尝试使用 UTF-8 解码。")
                output = raw_output.decode("utf-8", errors="replace")  # 尝试 UTF-8，并替换错误字符
            rules = self.parse_rules(output)
            self.display_rules(rules)
            logger.debug(f"加载到规则：{rules}")

        except subprocess.CalledProcessError as e:
            logger.error(f"加载规则失败：{e.output.decode(encoding, errors='replace') if encoding else e.output}")
            self.show_error(f"加载规则失败：{e.output.decode(encoding, errors='replace') if encoding else e.output}") # 也尝试解码错误信息
        except Exception as ex:
            logger.exception(f"加载规则失败：{ex}")
            self.show_error(f"加载规则失败：{ex}")
        logger.debug("退出 load_rules")
    def parse_rules(self, output):
        logger.debug("进入 parse_rules")
        rules = []
        lines = output.splitlines()

        # 找到数据开始的行 (跳过标题行)
        data_start_index = 0
        for i, line in enumerate(lines):
            if "----" in line:  # 假设数据行上方有一行分隔符
                data_start_index = i + 1
                break

        # 解析数据行（严格按 4 列：listen_address listen_port connect_address connect_port）
        # 示例（中文系统）:
        # 0.0.0.0         8080        172.29.223.44   1996
        row_pattern = re.compile(
            r"^\s*(?P<listen_address>\d{1,3}(?:\.\d{1,3}){3})\s+"
            r"(?P<listen_port>\d+)\s+"
            r"(?P<connect_address>\d{1,3}(?:\.\d{1,3}){3})\s+"
            r"(?P<connect_port>\d+)\s*$"
        )

        for line in lines[data_start_index:]:
            text = line.strip()
            if not text:
                continue

            match = row_pattern.match(text)
            if match:
                rules.append({
                    "listenPort": match.group("listen_port"),
                    "listenAddress": match.group("listen_address"),
                    "connectPort": match.group("connect_port"),
                    "connectAddress": match.group("connect_address"),
                })
                continue

            # 兜底解析：遇到格式稍有变化时，尽量按 split 的前 4 列解析
            parts = text.split()
            if len(parts) >= 4 and parts[1].isdigit() and parts[3].isdigit():
                rules.append({
                    "listenPort": parts[1],
                    "listenAddress": parts[0],
                    "connectPort": parts[3],
                    "connectAddress": parts[2],
                })

        logger.debug(f"解析到的规则：{rules}")
        logger.debug("退出 parse_rules")
        return rules

    def display_rules(self, rules):
        logger.debug("进入 display_rules")
        self.ui.tableWidgetRules.setRowCount(len(rules))

        for row, rule in enumerate(rules):
            for col, key in enumerate(
                    ["listenPort", "listenAddress", "connectPort", "connectAddress"]):
                item = QTableWidgetItem(rule[key])
                item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.ui.tableWidgetRules.setItem(row, col, item)

            delete_button = QPushButton("删除")
            delete_button.clicked.connect(
                lambda checked, r=row: self.delete_rule(r))
            self.ui.tableWidgetRules.setCellWidget(row, 4, delete_button)

        #  不再自动调整列宽
        # self.ui.tableWidgetRules.resizeColumnsToContents()
        logger.debug("退出 display_rules")

    def add_rule(self, data):
        logger.debug(f"进入 add_rule，数据：{data}")
        self.clear_error()
        encoding = None  # 初始化 encoding
        try:
            self._append_cmd_log(
                "执行: netsh interface portproxy add v4tov4 "
                f"listenport={data['listenPort']} listenaddress={data['listenAddress']} "
                f"connectport={data['connectPort']} connectaddress={data['connectAddress']}"
            )
            # 获取原始输出
            process = subprocess.Popen(
                [
                    "netsh", "interface", "portproxy", "add", "v4tov4",
                    f"listenport={data['listenPort']}",
                    f"listenaddress={data['listenAddress']}",
                    f"connectport={data['connectPort']}",
                    f"connectaddress={data['connectAddress']}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )
            stdout, stderr = process.communicate()
             # 检测编码
            result = chardet.detect(stdout or stderr) # 有可能成功, 但是输出在stderr
            encoding = result['encoding']
            confidence = result['confidence']
            logger.debug(f"检测到的编码：{encoding} (置信度：{confidence})")

            if process.returncode != 0:
                 if encoding and confidence > 0.7:
                    error_msg = stderr.decode(encoding, errors="replace")
                 else:
                    error_msg = stderr.decode("utf-8", errors="replace")
                 self.show_error(f"添加规则失败：{error_msg}")
                 logger.error(f"添加规则失败：{error_msg}")
                 self._append_cmd_log(f"失败: {error_msg}")
                 return
            if encoding and confidence > 0.7:
                output = stdout.decode(encoding)
            else:
                output = stdout.decode('utf-8', errors='replace')
            logger.info(f"添加规则成功：{output}")
            if output.strip():
                self._append_cmd_log(output.strip())

            # 添加防火墙规则（公用/专用）
            self._append_ps_log(f'执行: New-NetFirewallRule (Private,Public) 端口 {data["listenPort"]}')
            ok, msg = ensure_firewall_rule_private_public(data["listenPort"])
            if ok:
                self._append_ps_log(f"成功: {firewall_rule_display_name(data['listenPort'])}")
                if msg:
                    self._append_ps_log(msg)
            else:
                self._append_ps_log(f"失败: {firewall_rule_display_name(data['listenPort'])}")
                if msg:
                    self._append_ps_log(msg)

        except Exception as ex:
            logger.exception(f"添加规则失败：{ex}")
            self.show_error(f"添加规则失败：{ex}")
            self._append_cmd_log(f"异常: {ex}")
            return
        finally:
            self.load_rules()
        logger.debug("退出 add_rule")

    def delete_rule(self, row):
        logger.debug(f"进入 delete_rule，行号：{row}")

        listen_port = self.ui.tableWidgetRules.item(row, 0).text()
        listen_address = self.ui.tableWidgetRules.item(row, 1).text()
        logger.info(f"预备删除的端口: {listen_port} 地址: {listen_address}")
        reply = QMessageBox.question(
            self, "确认删除",
            f"确定要删除端口 {listen_port} 上的规则吗？",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.clear_error()
            encoding = None
            try:
                self._append_cmd_log(
                    "执行: netsh interface portproxy delete v4tov4 "
                    f"listenport={listen_port} listenaddress={listen_address}"
                )
                process = subprocess.Popen(
                    [
                        "netsh", "interface", "portproxy", "delete", "v4tov4",
                        f"listenport={listen_port}",
                        f"listenaddress={listen_address}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
                stdout, stderr = process.communicate()
                result = chardet.detect(stdout or stderr)
                encoding = result['encoding']
                confidence = result['confidence']

                if process.returncode != 0:
                    if encoding and confidence > 0.7:
                        error_msg = stderr.decode(encoding, errors="replace")
                    else:
                        error_msg = stderr.decode("utf-8", errors="replace")
                    self.show_error(f"删除规则失败：{error_msg}")
                    self._append_cmd_log(f"失败: {error_msg}")
                    return
                if encoding and confidence > 0.7:
                    output = stdout.decode(encoding)
                else:
                    output = stdout.decode('utf-8', errors='replace')
                logger.info(f"删除规则成功：{output}")
                if output.strip():
                    self._append_cmd_log(output.strip())

                # 删除防火墙规则（按 DisplayName）
                self._append_ps_log(f'执行: Remove-NetFirewallRule -DisplayName "{firewall_rule_display_name(listen_port)}"')
                ok, msg = remove_firewall_rule(listen_port)
                if ok:
                    self._append_ps_log(f"成功: {firewall_rule_display_name(listen_port)}")
                    if msg:
                        self._append_ps_log(msg)
                else:
                    self._append_ps_log(f"失败: {firewall_rule_display_name(listen_port)}")
                    if msg:
                        self._append_ps_log(msg)
            except Exception as ex:
                logger.exception(f"删除规则失败：{ex}")
                self.show_error(f"删除规则失败：{ex}")
                self._append_cmd_log(f"异常: {ex}")
                return
            finally:
                self.load_rules()
        logger.debug("退出 delete_rule")

    def show_error(self, message):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        tb_str = traceback.format_exception(exc_type, exc_value, exc_traceback)
        tb_str = "".join(tb_str)

        error_text = f"{message}\n\nTraceback:\n{tb_str}"
        self.ui.errorLabel.setText(error_text)
        self.ui.errorLabel.setStyleSheet("color: red;")

    def clear_error(self):
        self.ui.errorLabel.setText("")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f5f5f5; /* 更浅的背景色 */
            font-family: "Segoe UI", "Microsoft YaHei", sans-serif; /* 更现代的字体 */
        }
        QPushButton {
            padding: 8px 16px;
            border: 1px solid #aaa; /* 更细的边框 */
            border-radius: 4px;
            background-color: #f0f0f0; /* 浅灰色背景 */
            color: #333; /* 深灰色文本 */
            font-size: 14px; /* 稍大的字号 */
        }
        QPushButton:hover {
            background-color: #e0e0e0; /* 悬停时更浅的背景 */
            border-color: #888;
        }
        QPushButton:pressed {
            background-color: #ccc;
        }
        QPushButton#pushButtonAdd { /* 为“添加”按钮设置特殊样式 */
            background-color: #4CAF50; /* 绿色背景 */
            color: white;
            border: none;
        }
        QPushButton#pushButtonAdd:hover {
            background-color: #45a049;
        }
        QPushButton#pushButtonAdd:pressed {
            background-color: #367c39;
        }
        QTableWidget {
            gridline-color: #ccc;
            alternate-background-color: #f9f9f9; /* 更浅的交替行颜色 */
            selection-background-color: #a8d1ff; /* 更柔和的选择颜色 */
            font-size: 13px;
            border: 1px solid #aaa;
        }
        QHeaderView::section {
            background-color: #ddd;
            padding: 6px; /* 增加表头内边距 */
            border: 1px solid #999;
            font-weight: bold;
            font-size: 14px;
        }
        QDialog {
            background-color: #f5f5f5;
        }
        QLabel#errorLabel{
            color: red;
            font-size: 14px;
        }
        QLineEdit {
            padding: 5px;
            border: 1px solid #aaa;
            border-radius: 4px;
            font-size: 14px;
        }
        QTableWidget::item:selected { /* 选中单元格的样式 */
            color: black; /* 确保选中时文本颜色为黑色 */
        }

    """)
    window = MainWindow()
    window.resize(900, 500)  # 调整窗口大小
    window.show()
    sys.exit(app.exec())