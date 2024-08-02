from pathlib import Path

import PyInstaller.__main__

HERE = Path(__file__).parent.absolute()
ppcheck_path = str(HERE / "ppcheck.py")


def install():
    PyInstaller.__main__.run(
        [
            ppcheck_path,
            "--onefile",
            "--windowed",
            # other pyinstaller options...
        ]
    )
