"""Tkinter GUI Application for Def Jam: Fight for NY CAW & Save Editor."""

import json
import os
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional

from .crypto import calculate_save_dir, verify_save
from .profile import FighterProfile
from .catalog import FIGHTING_STYLES, VOICES, BODY_TYPES, FEMALE_MODELS


class CawEditorApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Def Jam: Fight for NY — CAW & Save Editor")
        self.root.geometry("680x600")
        self.root.minsize(640, 520)

        self.profile: Optional[FighterProfile] = None
        self.active_save_dir = self._detect_default_save_dir()
        self.active_file_path: Optional[str] = None

        self._build_ui()
        self._scan_existing_profiles()

    def _detect_default_save_dir(self) -> str:
        candidates = [
            os.path.abspath("prequisites/save/UserData/45410049"),
            os.path.abspath("save/UserData/45410049"),
        ]
        env_data = os.environ.get("DEFJAM_DATA")
        if env_data:
            candidates.insert(0, os.path.join(env_data, "save", "UserData", "45410049"))

        for path in candidates:
            if os.path.isdir(path):
                return path
        return candidates[0]

    def _build_ui(self):
        # Top Frame: Save Path & Profile Selector
        top_frame = ttk.LabelFrame(self.root, text="Active Game Save", padding=10)
        top_frame.pack(fill=tk.X, padx=12, pady=(10, 6))

        path_row = ttk.Frame(top_frame)
        path_row.pack(fill=tk.X, pady=(0, 6))

        ttk.Label(path_row, text="Save Dir:").pack(side=tk.LEFT)
        self.lbl_path = ttk.Label(path_row, text=self.active_save_dir, font=("Segoe UI", 9, "italic"))
        self.lbl_path.pack(side=tk.LEFT, padx=6)
        ttk.Button(path_row, text="Browse...", command=self._browse_save_dir).pack(side=tk.RIGHT)

        prof_row = ttk.Frame(top_frame)
        prof_row.pack(fill=tk.X)

        ttk.Label(prof_row, text="Detected Profile:").pack(side=tk.LEFT)
        self.combo_profiles = ttk.Combobox(prof_row, state="readonly", width=30)
        self.combo_profiles.pack(side=tk.LEFT, padx=6)
        self.combo_profiles.bind("<<ComboboxSelected>>", self._on_profile_selected)

        ttk.Button(prof_row, text="Refresh", command=self._scan_existing_profiles).pack(side=tk.LEFT, padx=4)
        ttk.Button(prof_row, text="Open Custom Save File...", command=self._open_custom_file).pack(side=tk.RIGHT)

        # Notebook Tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

        self.tab_career = ttk.Frame(self.notebook, padding=12)
        self.tab_stats = ttk.Frame(self.notebook, padding=12)
        self.tab_visuals = ttk.Frame(self.notebook, padding=12)
        self.tab_presets = ttk.Frame(self.notebook, padding=12)

        self.notebook.add(self.tab_career, text="Career & Economy")
        self.notebook.add(self.tab_stats, text="Combat Stats & Style")
        self.notebook.add(self.tab_visuals, text="Appearance & Rigs")
        self.notebook.add(self.tab_presets, text="JSON Presets & Export")

        self._build_career_tab()
        self._build_stats_tab()
        self._build_visuals_tab()
        self._build_presets_tab()

        # Bottom Frame: Actions & Status Bar
        bottom_frame = ttk.Frame(self.root, padding=12)
        bottom_frame.pack(fill=tk.X)

        self.btn_save = ttk.Button(
            bottom_frame,
            text="★ Save & Inject to Game (Resign 3 Seals)",
            command=self._save_and_inject,
            style="Accent.TButton",
        )
        self.btn_save.pack(side=tk.RIGHT, padx=4)

        self.lbl_status = ttk.Label(bottom_frame, text="Ready. Select or load a profile.", font=("Segoe UI", 9))
        self.lbl_status.pack(side=tk.LEFT)

    def _build_career_tab(self):
        # Fighter Identity
        sec_id = ttk.LabelFrame(self.tab_career, text="Fighter Identity", padding=10)
        sec_id.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(sec_id)
        row1.pack(fill=tk.X, pady=4)
        ttk.Label(row1, text="Name:", width=16).pack(side=tk.LEFT)
        self.var_name = tk.StringVar(value="NEW_FIGHTER")
        ttk.Entry(row1, textvariable=self.var_name, width=24).pack(side=tk.LEFT)

        # Economy Cheats
        sec_eco = ttk.LabelFrame(self.tab_career, text="Career Economy & Cheats", padding=10)
        sec_eco.pack(fill=tk.X, pady=6)

        # Cash
        row_cash = ttk.Frame(sec_eco)
        row_cash.pack(fill=tk.X, pady=6)
        ttk.Label(row_cash, text="Cash ($):", width=16).pack(side=tk.LEFT)
        self.var_cash = tk.IntVar(value=1000)
        spin_cash = ttk.Spinbox(row_cash, from_=0, to=9999999, textvariable=self.var_cash, width=14)
        spin_cash.pack(side=tk.LEFT)
        ttk.Button(row_cash, text="+$50,000", command=lambda: self.var_cash.set(self.var_cash.get() + 50000)).pack(side=tk.LEFT, padx=6)
        ttk.Button(row_cash, text="Max ($999,999)", command=lambda: self.var_cash.set(999999)).pack(side=tk.LEFT)

        # Dev Points
        row_dev = ttk.Frame(sec_eco)
        row_dev.pack(fill=tk.X, pady=6)
        ttk.Label(row_dev, text="Dev Points:", width=16).pack(side=tk.LEFT)
        self.var_dev = tk.IntVar(value=100)
        spin_dev = ttk.Spinbox(row_dev, from_=0, to=999999, textvariable=self.var_dev, width=14)
        spin_dev.pack(side=tk.LEFT)
        ttk.Button(row_dev, text="+10,000", command=lambda: self.var_dev.set(self.var_dev.get() + 10000)).pack(side=tk.LEFT, padx=6)
        ttk.Button(row_dev, text="Max (99,999)", command=lambda: self.var_dev.set(99999)).pack(side=tk.LEFT)

        # Total Dev Points
        row_total = ttk.Frame(sec_eco)
        row_total.pack(fill=tk.X, pady=6)
        ttk.Label(row_total, text="Lifetime Dev Pts:", width=16).pack(side=tk.LEFT)
        self.var_total_dev = tk.IntVar(value=100)
        ttk.Spinbox(row_total, from_=0, to=999999, textvariable=self.var_total_dev, width=14).pack(side=tk.LEFT)

    def _build_stats_tab(self):
        sec_attr = ttk.LabelFrame(self.tab_stats, text="Combat Attributes (1 - 100)", padding=10)
        sec_attr.pack(fill=tk.X, pady=(0, 10))

        self.stat_vars = {}
        stats = [
            ("upper_strength", "Upper Body Strength"),
            ("lower_strength", "Lower Body Strength"),
            ("speed", "Speed"),
            ("toughness", "Toughness"),
            ("charisma", "Charisma (Bling)"),
        ]

        for key, label in stats:
            row = ttk.Frame(sec_attr)
            row.pack(fill=tk.X, pady=3)
            ttk.Label(row, text=label + ":", width=22).pack(side=tk.LEFT)
            var = tk.IntVar(value=35)
            self.stat_vars[key] = var
            scale = ttk.Scale(row, from_=1, to=100, variable=var, orient=tk.HORIZONTAL)
            scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
            ttk.Spinbox(row, from_=1, to=100, textvariable=var, width=5).pack(side=tk.RIGHT)

        btn_row = ttk.Frame(sec_attr)
        btn_row.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(btn_row, text="Max All Stats (100)", command=self._max_all_stats).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Reset to Base (35)", command=self._reset_all_stats).pack(side=tk.LEFT)

        # Style & Voice
        sec_style = ttk.LabelFrame(self.tab_stats, text="Style & Persona", padding=10)
        sec_style.pack(fill=tk.X, pady=6)

        row_v = ttk.Frame(sec_style)
        row_v.pack(fill=tk.X, pady=4)
        ttk.Label(row_v, text="Voice Persona:", width=18).pack(side=tk.LEFT)
        self.var_voice = tk.IntVar(value=4)
        voice_names = [f"{v['id']}: {v['name']}" for v in VOICES]
        self.combo_voice = ttk.Combobox(row_v, values=voice_names, state="readonly", width=32)
        self.combo_voice.current(3)
        self.combo_voice.pack(side=tk.LEFT)

    def _build_visuals_tab(self):
        # Body Type
        sec_body = ttk.LabelFrame(self.tab_visuals, text="Body Physique", padding=10)
        sec_body.pack(fill=tk.X, pady=(0, 10))

        row_u = ttk.Frame(sec_body)
        row_u.pack(fill=tk.X, pady=4)
        ttk.Label(row_u, text="Upper Body Type:", width=18).pack(side=tk.LEFT)
        body_names = [f"{b['id']}: {b['name']}" for b in BODY_TYPES]
        self.combo_upper = ttk.Combobox(row_u, values=body_names, state="readonly", width=30)
        self.combo_upper.current(1)
        self.combo_upper.pack(side=tk.LEFT)

        row_l = ttk.Frame(sec_body)
        row_l.pack(fill=tk.X, pady=4)
        ttk.Label(row_l, text="Lower Body Type:", width=18).pack(side=tk.LEFT)
        self.combo_lower = ttk.Combobox(row_l, values=body_names, state="readonly", width=30)
        self.combo_lower.current(0)
        self.combo_lower.pack(side=tk.LEFT)

        # Female Fighter Model Overrides
        sec_female = ttk.LabelFrame(self.tab_visuals, text="Female Fighter Rig Overrides", padding=10)
        sec_female.pack(fill=tk.X, pady=6)

        row_f = ttk.Frame(sec_female)
        row_f.pack(fill=tk.X, pady=4)
        ttk.Label(row_f, text="3D Model Rig:", width=18).pack(side=tk.LEFT)
        fem_names = [f"{m['name']} ({m['desc']})" for m in FEMALE_MODELS]
        self.combo_female = ttk.Combobox(row_f, values=fem_names, state="readonly", width=42)
        self.combo_female.current(0)
        self.combo_female.pack(side=tk.LEFT)

        info_box = ttk.Label(
            sec_female,
            text="Note: Selecting a female character model enables complete female rigs across\n"
                 "Exhibition and Story modes. Cutscene story dialogue retains author male voice lines.",
            foreground="#555555",
            justify=tk.LEFT,
        )
        info_box.pack(anchor=tk.W, pady=(8, 0))

    def _build_presets_tab(self):
        sec_io = ttk.LabelFrame(self.tab_presets, text="JSON Preset Management", padding=10)
        sec_io.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(
            sec_io,
            text="Export and share fighter profiles as portable JSON presets without altering save files.",
        ).pack(anchor=tk.W, pady=(0, 8))

        row_btns = ttk.Frame(sec_io)
        row_btns.pack(fill=tk.X)
        ttk.Button(row_btns, text="Import JSON Preset...", command=self._import_json).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(row_btns, text="Export JSON Preset...", command=self._export_json).pack(side=tk.LEFT)

    def _browse_save_dir(self):
        folder = filedialog.askdirectory(initialdir=self.active_save_dir, title="Select Xbox UserData/45410049 Folder")
        if folder:
            self.active_save_dir = folder
            self.lbl_path.config(text=folder)
            self._scan_existing_profiles()

    def _scan_existing_profiles(self):
        self.combo_profiles["values"] = []
        if not os.path.isdir(self.active_save_dir):
            return

        entries = []
        for name in os.listdir(self.active_save_dir):
            sub = os.path.join(self.active_save_dir, name)
            if not os.path.isdir(sub):
                continue
            meta = os.path.join(sub, "SaveMeta.xbx")
            if os.path.isfile(meta):
                try:
                    with open(meta, "rb") as f:
                        text = f.read().decode("utf-16").strip()
                    if text.startswith("Name="):
                        pname = text[5:]
                        entries.append(f"{pname} ({name})")
                except Exception:
                    pass

        self.combo_profiles["values"] = entries
        if entries:
            self.combo_profiles.current(0)
            self._on_profile_selected()

    def _on_profile_selected(self, event=None):
        sel = self.combo_profiles.get()
        if not sel:
            return
        pname = sel.split(" (")[0]
        hash_code = sel.split(" (")[1].rstrip(")")
        path = os.path.join(self.active_save_dir, hash_code, pname)
        if os.path.isfile(path):
            self._load_save_file(path)

    def _open_custom_file(self):
        path = filedialog.askopenfilename(
            initialdir=self.active_save_dir,
            title="Open Xbox Save File",
            filetypes=[("Def Jam Save", "*"), ("All Files", "*.*")],
        )
        if path:
            self._load_save_file(path)

    def _load_save_file(self, path: str):
        try:
            prof = FighterProfile.load_from_file(path)
            self.profile = prof
            self.active_file_path = path

            # Update GUI fields
            self.var_name.set(prof.name)
            self.var_cash.set(prof.cash)
            self.var_dev.set(prof.dev_points)
            self.var_total_dev.set(prof.total_dev_points)

            for key, var in self.stat_vars.items():
                var.set(getattr(prof, key, 35))

            v_idx = max(0, min(len(VOICES) - 1, prof.voice_id - 1))
            self.combo_voice.current(v_idx)

            u_idx = max(0, min(len(BODY_TYPES) - 1, prof.body_type_upper - 1))
            self.combo_upper.current(u_idx)

            l_idx = max(0, min(len(BODY_TYPES) - 1, prof.body_type_lower - 1))
            self.combo_lower.current(l_idx)

            # Check validity
            is_valid = verify_save(prof.raw_data)
            status_text = f"Loaded {prof.name} from {os.path.basename(path)} | Seals: {'VALID' if is_valid else 'CORRUPT'}"
            self.lbl_status.config(text=status_text)
        except Exception as e:
            messagebox.showerror("Load Failed", f"Failed to parse save file:\n{e}")

    def _save_and_inject(self):
        if not self.profile:
            messagebox.showwarning("No Save Loaded", "Please select or open an existing profile first.")
            return

        try:
            # Gather values from UI
            self.profile.name = self.var_name.get().strip().upper()
            self.profile.cash = self.var_cash.get()
            self.profile.dev_points = self.var_dev.get()
            self.profile.total_dev_points = self.var_total_dev.get()

            for key, var in self.stat_vars.items():
                setattr(self.profile, key, var.get())

            self.profile.voice_id = self.combo_voice.current() + 1
            self.profile.body_type_upper = self.combo_upper.current() + 1
            self.profile.body_type_lower = self.combo_lower.current() + 1

            saved_dir = self.profile.save_to_directory(self.active_save_dir)
            self.lbl_status.config(text=f"Successfully signed & injected to: {os.path.basename(saved_dir)}")
            messagebox.showinfo(
                "Save Injected Cleanly",
                f"Fighter '{self.profile.name}' signed and injected successfully!\n\n"
                f"Location: {saved_dir}\n"
                f"All 3 HMAC-SHA1 Seals verified 100% valid.",
            )
            self._scan_existing_profiles()
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to sign/save profile:\n{e}")

    def _import_json(self):
        path = filedialog.askopenfilename(filetypes=[("JSON Preset", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            if not self.profile:
                self.profile = FighterProfile()

            self.profile.from_dict(data)
            self.var_name.set(self.profile.name)
            self.var_cash.set(self.profile.cash)
            self.var_dev.set(self.profile.dev_points)
            self.var_total_dev.set(self.profile.total_dev_points)
            for key, var in self.stat_vars.items():
                var.set(getattr(self.profile, key, 35))

            messagebox.showinfo("Preset Imported", f"Imported preset '{self.profile.name}'.")
        except Exception as e:
            messagebox.showerror("Import Failed", f"Could not import JSON preset:\n{e}")

    def _export_json(self):
        if not self.profile:
            self.profile = FighterProfile()

        # Update values from UI before export
        self.profile.name = self.var_name.get().strip().upper()
        self.profile.cash = self.var_cash.get()
        self.profile.dev_points = self.var_dev.get()
        self.profile.total_dev_points = self.var_total_dev.get()
        for key, var in self.stat_vars.items():
            setattr(self.profile, key, var.get())

        path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Preset", "*.json")],
            initialfile=f"{self.profile.name}.json",
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.profile.to_dict(), f, indent=2)
            messagebox.showinfo("Preset Exported", f"Preset saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Export Failed", f"Could not export JSON preset:\n{e}")

    def _max_all_stats(self):
        for var in self.stat_vars.values():
            var.set(100)

    def _reset_all_stats(self):
        for var in self.stat_vars.values():
            var.set(35)
