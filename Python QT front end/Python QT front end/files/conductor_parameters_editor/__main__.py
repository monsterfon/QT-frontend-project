import os
import pathlib

# If no preferred Qt API is already set, use PyQt6
if 'QT_API' not in os.environ:
    os.environ['QT_API'] = 'pyqt6'

import os
print("Current Working Directory:", os.getcwd())

import conductor_parameters_editor
import conductor_parameters_editor.application
import dlr_simutils_common.application


def main(root_dir=pathlib.Path('.')):
    return dlr_simutils_common.application.main(
        application_window_type=conductor_parameters_editor.application.ApplicationWindow,
        application_name="Conductor parameters editor",
        application_description="Conductor parameters editor",
        application_version=conductor_parameters_editor.__version__,
        root_dir=root_dir
    )
