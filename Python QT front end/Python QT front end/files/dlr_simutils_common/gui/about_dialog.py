import pathlib

import qtpy
from qtpy import QtCore, QtGui, QtWidgets, QtNetwork

import dlr_simutils_common
import dlr_simutils_common.core.diter


def _format_copyright_year(start_year):
    current_year = QtCore.QDate.currentDate().year()
    if current_year <= start_year:
        return f"{start_year}"
    else:
        return f"{start_year}-{current_year}"


def _get_diter_executable():
    if dlr_simutils_common.core.diter.diter_exe is None:
        return "N/A"

    # Try to shorten executable path as relative to dlr_simutils_common package directory, if possible
    exe_path = dlr_simutils_common.core.diter.diter_exe
    try:
        pkg_dir = pathlib.Path(dlr_simutils_common.__file__).parent.parent
        exe_path = exe_path.relative_to(pkg_dir)
    except ValueError:
        pass

    return str(exe_path)


def _get_diter_executable_version():
    if dlr_simutils_common.core.diter.diter_exe is None:
        return "N/A"

    try:
        import subprocess
        version_string = subprocess.check_output(
            [dlr_simutils_common.core.diter.diter_exe, '--version'],
            stdin=subprocess.DEVNULL,
            text=True,
        )
    except Exception:
        version_string = "N/A (error)"

    return version_string


def _get_package_version(package_name, version_attr='__version__'):
    try:
        import importlib
        package = importlib.import_module(package_name)
        return getattr(package, version_attr)
    except ImportError:
        return None  # Package not available
    except Exception:
        return "N/A"


def _qt_bindings_info():
    if qtpy.API_NAME.startswith('PySide'):
        # PySide2 or PySide6
        return (
            qtpy.API_NAME,
            qtpy.PYSIDE_VERSION,
            f"https://pypi.org/project/{qtpy.API_NAME}",
            "GNU LGPL v2.1",
            "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
        )
    else:
        # PyQt5 or PyQt6
        return (
            qtpy.API_NAME,
            qtpy.PYQT_VERSION,
            f"https://pypi.org/project/{qtpy.API_NAME}",
            "GNU GPL v3",
            "https://www.gnu.org/licenses/gpl-3.0.html",
        )


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.setWindowTitle("About...")
        self.resize(600, 500)

        layout = QtWidgets.QVBoxLayout(self)

        # Rudimentary light/dark theme detection (for light/dark logo version)
        # NOTE: works only with palette-based colors, not with stylesheets!
        darkTheme = self.palette().color(
            QtGui.QPalette.Normal,
            QtGui.QPalette.WindowText,
        ).lightnessF() >= 0.5

        # Tab widget
        tabWidget = QtWidgets.QTabWidget()
        tabWidget.setTabPosition(QtWidgets.QTabWidget.West)
        layout.addWidget(tabWidget)

        # Button box
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close, QtCore.Qt.Horizontal)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # *** Tab page: version ***
        pageWidget = QtWidgets.QWidget()
        pageLayout = QtWidgets.QVBoxLayout(pageWidget)
        tabWidget.addTab(pageWidget, "Version")

        # Text field
        textBrowser = QtWidgets.QTextBrowser()
        textBrowser.setReadOnly(True)
        pageLayout.addWidget(textBrowser)

        # Construct text
        logo_variant_filename = "logo-operato-white.svg" if darkTheme else "logo-operato-black.svg"
        logo_file = dlr_simutils_common.RESOURCES_DIR / logo_variant_filename
        copyright_year = _format_copyright_year(2023)

        app = QtCore.QCoreApplication.instance()
        application_name = app.applicationName()
        application_version = app.applicationVersion()

        diter_executable = _get_diter_executable()
        diter_executable_version = _get_diter_executable_version()

        text = "<center>"
        text += f"<h1>{application_name}</h1>"
        text += "<p>"
        text += f"<h2>v{application_version}</h2>"
        text += "</p>"
        text += f"<p><img src=\"{str(logo_file)}\" width=\"250\" /></p>"
        text += f"<p>Copyright (C) {copyright_year}, Operato</p>"
        text += "<a href=\"https://operato.eu\">https://operato.eu</a>"
        text += "</center>"
        text += "<br/>"
        text += "<h2>DiTeR information</h2>"
        text += "<p>"
        text += f"<b>DiTeR executable:</b> {diter_executable}<br/>"
        text += f"<b>DiTeR version string:</b> {diter_executable_version}"
        text += "</p>"

        textBrowser.setHtml(text)
        textBrowser.setOpenExternalLinks(True)

        # *** Tab page: libraries ***
        pageWidget = QtWidgets.QWidget()
        pageLayout = QtWidgets.QVBoxLayout(pageWidget)

        tabWidget.addTab(pageWidget, "Libraries")

        entries = (
            _qt_bindings_info(),
            (
                "Qt",
                qtpy.QT_VERSION,
                "https://qt-project.org",
                "GNU LGPL v2.1",
                "https://www.gnu.org/licenses/old-licenses/lgpl-2.1.html",
            ),
            (
                "OpenSSL",
                QtNetwork.QSslSocket.sslLibraryVersionString(),
                "http://www.openssl.org",
                "OpenSSL License",
                "http://www.openssl.org/source/license.html"
            ),
            (
                "numpy",
                _get_package_version("numpy"),
                "https://numpy.org",
                "BSD-3-Clause license",
                "https://github.com/numpy/numpy/blob/main/LICENSE.txt",
            ),
            (
                "pandas",
                _get_package_version("pandas"),
                "https://pandas.pydata.org",
                "BSD-3-Clause license",
                "https://github.com/pandas-dev/pandas/blob/main/LICENSE",
            ),
            (
                "matplotlib",
                _get_package_version("matplotlib"),
                "https://matplotlib.org/",
                "Matplotlib license (PSF-compatible)",
                "https://matplotlib.org/stable/users/project/license.html",
            ),
            (
                "qtmodern",
                _get_package_version("qtmodern"),
                "https://github.com/gmarull/qtmodern",
                "MIT",
                "https://matplotlib.org/stable/users/project/license.html",
            ),
            (
                "qdarkstyle",
                _get_package_version("qdarkstyle"),
                "https://github.com/ColinDuquesnoy/QDarkStyleSheet",
                "MIT",
                "https://github.com/ColinDuquesnoy/QDarkStyleSheet/blob/master/LICENSE.rst",
            ),
        )

        # Text field
        textBrowser = QtWidgets.QTextBrowser()
        textBrowser.setReadOnly(True)
        textBrowser.setOpenExternalLinks(True)
        pageLayout.addWidget(textBrowser)

        # Construct text
        text = "This software is built using the following 3rd party libraries:"
        text += "<br/>"
        for name, version, url, license_name, license_url in entries:
            if version is None:
                continue

            text += "<p>"
            text += f"<b>{name}</b><br/>"
            text += f"Version: {version}<br/>"
            text += f"Web page: <a href=\"{url}\">{url}</a><br/>"
            text += f"License: <a href=\"{license_url}\">{license_name}</a><br/>"
            text += "</p>"

        textBrowser.setHtml(text)
