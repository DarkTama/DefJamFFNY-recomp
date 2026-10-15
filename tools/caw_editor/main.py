"""Main executable entrypoint for the Standalone CAW Editor."""

import sys
import tkinter as tk
from tkinter import ttk

from .app import CawEditorApp


def main():
    root = tk.Tk()
    
    # Optional ttk styling
    try:
        style = ttk.Style(root)
        if "vista" in style.theme_names():
            style.theme_use("vista")
        elif "clam" in style.theme_names():
            style.theme_use("clam")
    except Exception:
        pass

    app = CawEditorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
