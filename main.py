"""Entry point for hosts that run a file directly (not `python -m unitext`).

Point the panel's Entry File / STARTUP_FILE at this file.
"""

from unitext.bot import main

if __name__ == "__main__":
    main()
