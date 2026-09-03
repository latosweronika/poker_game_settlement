import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

from poker_game_settlement import dfs, resolve


#problem z defoultowymi wartosciami w spinboxach, trzeba je poprawić, wskakują 0 jak nie powinny

BG = "#F3F5F4"
PANEL = "#FFFFFF"
PANEL_LIGHT = "#F8FAF9"

TABLE = "#145A43"
TABLE_DARK = "#0C392B"

GOLD = "#B97828"
GOLD_LIGHT = "#D29445"

TEXT = "#1D2A26"
MUTED = "#63736D"

RED = "#D45C55"
GREEN = "#4DBB86"


def validate_players_number(value):
    if value == "":
        return True
    try:
        number = int(value)
        return 2 <= number <= 10
    except ValueError:
        return False

def validate_positive_integer(value):
    if value == "":
        return True
    try:
        number = int(value)
        return  number >= 0
    except ValueError:
        return False


def find_duplicate_names(names):
    seen_names = set()
    duplicate_names = set()

    for name in names:
        normalized_name = name.strip().casefold()
        if not normalized_name:
            continue
        if normalized_name in seen_names:
            duplicate_names.add(name.strip())
        seen_names.add(normalized_name)

    return duplicate_names


class SettlementGUI:
    def __init__(self, root):

        self.root = root
        root.title("Poker Settlement")
        self.root.geometry("860x660")
        self.root.minsize(520, 500)
        self.root.configure(bg=BG)

        style = ttk.Style(root)
        style.theme_use("clam")

        style.configure("TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Title.TLabel", background=BG, foreground=TABLE_DARK, font=("Georgia", 25, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Segoe UI", 9, "bold"))
        style.configure("Section.TLabel", background=PANEL, foreground=TABLE_DARK, font=("Segoe UI", 12, "bold"))
        style.configure("Value.TLabel", background=PANEL_LIGHT, foreground=TABLE_DARK, font=("Segoe UI", 10, "bold"), padding=(10, 7))
        style.configure("TableSection.TLabel", background=TABLE, foreground="#F8E6C8", font=("Segoe UI", 12, "bold"))
        style.configure("TEntry", fieldbackground=PANEL_LIGHT, foreground=TEXT, insertcolor=TEXT, bordercolor="#CBD6D1", lightcolor="#CBD6D1", darkcolor="#CBD6D1", padding=7)
        style.configure("OutName.TEntry", fieldbackground="#2F3F39", foreground="#E7F0EC", insertcolor="#E7F0EC", bordercolor="#2F3F39", lightcolor="#2F3F39", darkcolor="#2F3F39", padding=7)
        style.configure("OutFinal.TEntry", fieldbackground="#2F3F39", foreground="#E7F0EC", insertcolor="#E7F0EC", bordercolor="#2F3F39", lightcolor="#2F3F39", darkcolor="#2F3F39", padding=7)
        style.configure("TSpinbox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT, foreground=TEXT, insertcolor=TEXT, bordercolor="#CBD6D1", lightcolor="#CBD6D1", darkcolor="#CBD6D1", padding=10)
        style.configure("Settings.TEntry", fieldbackground=PANEL_LIGHT, foreground=TEXT, insertcolor=TEXT, bordercolor="#CBD6D1", lightcolor="#CBD6D1", darkcolor="#CBD6D1", padding=(12, 10))
        style.configure("Settings.TSpinbox", fieldbackground=PANEL_LIGHT, background=PANEL_LIGHT, foreground=TEXT, insertcolor=TEXT, bordercolor="#CBD6D1", lightcolor="#CBD6D1", darkcolor="#CBD6D1", padding=(12, 10))
        style.configure("TButton", background=GOLD, foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=(18, 10), borderwidth=0)
        style.map("TButton", background=[("active", GOLD_LIGHT), ("pressed", "#8E5A1F"), ("disabled", "#C7CFCA")])

        #
        self.main_container = tk.Frame(root, bg=BG)
        self.main_container.pack(fill="both",expand=True)

        # Start with edit screen
        self.show_edit_screen()

    def show_edit_screen(self):
        # Remove previous screen
        for widget in self.main_container.winfo_children():
            widget.destroy()

        header = tk.Frame( self.main_container, bg=BG)
        header.pack( fill="x")

        ttk.Label(
            header,
            text="♠  POKER SETTLEMENT  ♥",
            style="Title.TLabel"
        ).pack( pady=(20, 3))

        ttk.Label(
            header,
            text="CASH GAME MANAGER",
            style="Subtitle.TLabel"
        ).pack(pady=(0, 15))


        scroll_container = tk.Frame( self.main_container, bg=BG)
        scroll_container.pack( fill="both", expand=True)

        # canvas
        canvas = tk.Canvas( scroll_container, bg=BG, highlightthickness=0)
        canvas.pack( side="left", fill="both", expand=True)

        # Scrollbar
        scrollbar = ttk.Scrollbar( scroll_container, orient="vertical", command=canvas.yview)
        scrollbar.pack( side="right", fill="y")

        canvas.configure( yscrollcommand=scrollbar.set)

        # frame inside canvas
        self.scroll_frame = tk.Frame( canvas, bg=BG)
        canvas_window = canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")

        # Update scroll region
        def update_scroll_region(event=None):
            canvas.configure( scrollregion=canvas.bbox("all"))

        self.scroll_frame.bind("<Configure>",update_scroll_region)

        # Make inner frame same width as canvas
        def resize_inner_frame(event):
            canvas.itemconfig(canvas_window, width=event.width)

        canvas.bind( "<Configure>", resize_inner_frame)

        # Mouse wheel

        def mouse_wheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)),"units")

        canvas.bind_all("<MouseWheel>", mouse_wheel)


        settings_frame = tk.Frame(
            self.scroll_frame,
            bg=PANEL,
            padx=25,
            pady=22,
            highlightbackground="#DDE5E1",
            highlightthickness=1
        )

        settings_frame.pack(
            fill="x",
            padx=32,
            pady=(8, 12)
        )

        settings_frame.columnconfigure(1, weight=1)

        ttk.Label(
            settings_frame,
            text="♦  GAME SETTINGS",
            style="Section.TLabel"
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 15)
        )

        # Players

        ttk.Label(
            settings_frame,
            text="Players"
        ).grid(
            row=1,
            column=0,
            sticky="w",
            pady=5
        )

        current_value = tk.StringVar(value="2")

        vcmd = (self.root.register( validate_players_number), "%P")

        self.players_entry = ttk.Spinbox(
            settings_frame,
            from_=2,
            to=10,
            textvariable=current_value,
            wrap=True,
            width=16,
            style="Settings.TSpinbox",
            validate="key",
            validatecommand=vcmd
        )

        self.players_entry.grid(
            row=1,
            column=1,
            sticky="ew",
            pady=5
        )

        # Chips

        ttk.Label(
            settings_frame,
            text="Chips per buy-in"
        ).grid(
            row=2,
            column=0,
            sticky="w",
            pady=5
        )

        self.chip_entry = ttk.Entry(settings_frame, width=16, style="Settings.TEntry")

        self.chip_entry.grid(
            row=2,
            column=1,
            sticky="ew",
            pady=5
        )

        # Buy-in

        ttk.Label(
            settings_frame,
            text="Buy-in amount"
        ).grid(
            row=3,
            column=0,
            sticky="w",
            pady=5
        )

        self.buyin_entry = ttk.Entry(settings_frame, width=16, style="Settings.TEntry")

        self.buyin_entry.grid(
            row=3,
            column=1,
            sticky="ew",
            pady=5
        )

        # Create table

        self.create_table_button = ttk.Button(
            settings_frame,
            text="CREATE TABLE",
            command=self.create_table
        )

        self.create_table_button.grid(
            row=4,
            column=0,
            columnspan=2,
            pady=(15, 0)
        )

        self.table_frame = tk.Frame(
            self.scroll_frame,
            bg=TABLE,
            padx=25,
            pady=22,
            highlightbackground=TABLE_DARK,
            highlightthickness=1
        )

        self.table_frame.pack(
            fill="x",
            padx=32,
            pady=(0, 12)
        )


    def create_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        try:
            n = int(self.players_entry.get())

        except ValueError:
            messagebox.showerror("Invalid data", "Number of players must be between 2 and 10.")
            return

        if not 2 <= n <= 10:
            messagebox.showerror("Invalid data", "Number of players must be between 2 and 10.")
            return

        chip_count = self.chip_entry.get().strip()
        buy_in = self.buyin_entry.get().strip()

        if chip_count == "" or buy_in == "" or float(chip_count) <= 0 or float(buy_in) <= 0:
            messagebox.showerror("Invalid data", "Chip count and buy-in amount must be positive.")
            return

        chip_value = float(buy_in) / float(chip_count)
        self.chip_count = int(float(chip_count))


        settings_values = (
            (1, self.players_entry.get()),
            (2, chip_count),
            (3, buy_in),
            (4, f"{chip_value}"),
        )

        for row, value in settings_values:
            ttk.Label(
                self.players_entry.master,
                text=value,
                style="Value.TLabel"
            ).grid(row=row, column=1, sticky="ew", pady=5)

        self.players_entry.grid_remove()
        self.chip_entry.grid_remove()
        self.buyin_entry.grid_remove()

        ttk.Label(
            self.players_entry.master,
            text="Chip value"
        ).grid(row=4, column=0, sticky="w", pady=5)

        self.rows = [[]]
        self.buyin_values = [[]]
        self.game_start_rows = [0]

        ttk.Label(
            self.table_frame,
            text="♣️GAME TABLE nr 1",
            style="TableSection.TLabel"
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        headers = ["PLAYER", "FINAL CHIPS", "BUY INS"]

        for col, header in enumerate(headers):
            tk.Label(
                self.table_frame,
                text=header,
                bg=TABLE,
                fg="#BFE2D2",
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=1,
                column=col,
                padx=8,
                pady=5
            )

        buyin_vcmd = (self.root.register(validate_positive_integer), "%P")
        chips_vcmd = (self.root.register(validate_positive_integer), "%P")

        for i in range(n):
            name = ttk.Entry(self.table_frame)
            final = ttk.Entry(self.table_frame, validate="key", validatecommand=chips_vcmd)
            buyins_value = tk.StringVar(value="1")
            buyins = ttk.Spinbox(
                self.table_frame,
                from_=0,
                to=100,
                width=8,
                textvariable=buyins_value
            )
            name.grid(row=i + 2, column=0, padx=8, pady=4)
            final.grid(row=i + 2, column=1, padx=8, pady=4)
            buyins.grid(row=i + 2, column=2, padx=8, pady=4)
            buyins_value.set("1")

            self.rows[0].append([name, final, buyins])
            self.buyin_values[0].append(buyins_value)
            self.bind_input_navigation(name)
            self.bind_input_navigation(final)
            self.bind_input_navigation(buyins)

            final.bind("<KeyRelease>", lambda event, game=0: self.update_chip_status(event, game))
            # buyins.bind("<KeyRelease>", lambda event, game=0, name=name, final=final, value=buyins_value: self.update_added_player_state(game, name, final, value))
            # buyins.bind("<<Increment>>", lambda event, game=0, name=name, final=final, value=buyins_value: self.update_added_player_state(game, name, final, value))
            # buyins.bind("<<Decrement>>", lambda event, game=0, name=name, final=final, value=buyins_value: self.update_added_player_state(game, name, final, value))
            # buyins.bind("<KeyRelease>", lambda event, game=0: self.update_chip_status(event, game))
            # buyins.bind("<<Increment>>", lambda event, game=0: self.update_chip_status(event, game))
            # buyins.bind("<<Decrement>>", lambda event, game=0: self.update_chip_status(event, game))
            buyins_value.trace_add("write", lambda *_args, game=0, name=name, final=final, value=buyins_value: self.update_added_player_state(game, name, final, value))
            buyins_value.trace_add("write", lambda *_args, game=0: self.update_chip_status(game=game))
            self.update_player_row_state(name, final, buyins_value)

        self.chip_statuses = {0: tk.StringVar(value="0 / 0")}
        chip_status_frame = tk.Frame(self.table_frame, bg=TABLE)
        chip_status_frame.grid(
            row=0,
            column=4,
            rowspan=n + 3,
            padx=(35, 8),
            sticky="nsew"
        )

        tk.Label(
            chip_status_frame,
            text="CHIPS ON THE TABLE",
            bg=TABLE,
            fg="#BFE2D2",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(5, 8))

        tk.Label(
            chip_status_frame,
            textvariable=self.chip_statuses[0],
            bg=TABLE,
            fg="#BFE2D2",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        self.update_chip_status(game=0)

        
        self.add_player_button = ttk.Button(
            self.table_frame,
            text="+ ADD PLAYER",
            command=self.add_player
        )
        self.add_player_button.grid(row=n + 2, column=0, padx=6, pady=(15, 0))

        self.restart_button = ttk.Button(
            self.table_frame,
            text="↻ RESTART",
            command=self.show_edit_screen
        )
        self.restart_button.grid(row=n + 2, column=1, padx=6, pady=(15, 0))

        self.add_game_button = ttk.Button(
            self.table_frame,
            text="+ ADD GAME",
            command=self.add_game
        )
        self.add_game_button.grid(row=n + 2, column=2, padx=6, pady=(15, 0))

        self.resolve_button = ttk.Button(
            self.table_frame,
            text="⚡ RESOLVE",
            command=self.run_resolve
        )
        self.resolve_button.grid(row=n + 2, column=3, padx=6, pady=(15, 0))

        self.create_table_button.grid_remove()

    def validate_table_names(self):
        names = [name.get() for name, _, _ in self.rows[0]]
        duplicate_names = find_duplicate_names(names)
        if duplicate_names:
            duplicates = ", ".join(sorted(duplicate_names))
            messagebox.showerror(
                "Duplicate names",
                f"These player names are duplicated: {duplicates}."
            )
            return False
        return True

    def update_chip_status(self, event=None, game=0):
        if not hasattr(self, "chip_statuses") or game >= len(self.rows):
            return

        table_chips = 0
        table_buy_ins = 0
        for _, chips, buyins in self.rows[game]:
            try:
                table_chips += int(chips.get() or 0)
                table_buy_ins += int(buyins.get() or 0)
            except ValueError:
                continue

        expected_chips = table_buy_ins * self.chip_count
        self.chip_statuses[game].set(f"{table_chips} / {expected_chips}")

    def add_player(self):
        player_name = simpledialog.askstring("Add player", "Enter player name:", parent=self.root)
        if player_name is None:
            return

        player_name = player_name.strip()
        if player_name == "":
            messagebox.showerror("Missing data", "Enter a player name.")
            return

        existing_names = [name.get() for name, _, _ in self.rows[0]]
        if player_name.casefold() in {
            name.strip().casefold() for name in existing_names
        }:
            messagebox.showerror("Invalid data", "A player with this name already exists.")
            return

        games = len(self.rows)
        for game in range(games - 1, -1, -1):
            row_number = self.game_start_rows[game] + 2 + len(self.rows[game])

            for widget in self.table_frame.winfo_children():
                info = widget.grid_info()
                if info and int(info.get("row", -1)) >= row_number:
                    widget.grid_configure(row=int(info["row"]) + 1)

            is_current_game = game == games - 1
            buyins_default = "1" if is_current_game else "0"
            buyins_value = tk.StringVar(value=buyins_default)
            name = ttk.Entry(self.table_frame, state="readonly")
            name.configure(state="normal")
            name.insert(0, player_name)
            name.configure(state="readonly")
            final = ttk.Entry(self.table_frame, validate="key")
            buyins = ttk.Spinbox(
                self.table_frame,
                from_=0,
                to=100,
                width=8,
                textvariable=buyins_value
            )

            name.grid(row=row_number, column=0, padx=8, pady=4)
            final.grid(row=row_number, column=1, padx=8, pady=4)
            buyins.grid(row=row_number, column=2, padx=8, pady=4)

            self.rows[game].append([name, final, buyins])
            self.buyin_values[game].append(buyins_value)
            self.bind_input_navigation(name)
            self.bind_input_navigation(final)
            self.bind_input_navigation(buyins)
            self.game_start_rows[game + 1:] = [row + 1 for row in self.game_start_rows[game + 1:]]

            self.bind_player_row_state(game, name, final, buyins_value)
            final.bind("<KeyRelease>", lambda event, game=game: self.update_chip_status(event, game))
            final.bind("<FocusOut>", lambda event, game=game: self.update_chip_status(event, game))
            self.update_player_row_state(name, final, buyins_value)

            if not is_current_game:
                final.configure(state="disabled")


        self.update_table_buttons()
        for game in range(games):
            self.update_chip_status(game=game)

    def update_player_row_state(self, name_widget, final_widget, buyins_value):
        if buyins_value.get() == "0":
            name_widget.configure(style="OutName.TEntry")
            final_widget.configure(validate="none", style="OutFinal.TEntry", state="normal")
            if final_widget.get() != "not in the game":
                final_widget.delete(0, tk.END)
                final_widget.insert(0, "not in the game")
            final_widget.configure(state="disabled")
        else:
            name_widget.configure(style="TEntry")
            final_widget.configure(style="TEntry", state="normal", validate="key")
            if final_widget.get() == "not in the game":
                final_widget.delete(0, tk.END)

    def update_added_player_state(self, game, name_widget, final, buyins_value):
        self.update_player_row_state(name_widget, final, buyins_value)
        self.update_chip_status(game=game)

    def bind_player_row_state(self, game, name_widget, final_widget, buyins_value):
        buyins_value.trace_add(
            "write",
            lambda *_args, game=game, name_widget=name_widget, final_widget=final_widget, buyins_value=buyins_value: self.update_added_player_state(game, name_widget, final_widget, buyins_value)
        )

    def update_table_buttons(self):
        player_count = len(self.rows[0])
        last_game = len(self.rows) - 1
        buttons_row = self.game_start_rows[last_game] + player_count + 2
        self.add_player_button.grid(row=buttons_row, column=0, padx=6, pady=(15, 0))
        self.restart_button.grid(row=buttons_row, column=1, padx=6, pady=(15, 0))
        self.add_game_button.grid(row=buttons_row, column=2, padx=6, pady=(15, 0))
        self.resolve_button.grid(row=buttons_row, column=3, padx=6, pady=(15, 0))

    def add_game(self):
        np = len(self.rows[0])
        ng =int(len(self.rows))

        if not self.validate_table_names():
            return

        for i, (name, final, buyins) in enumerate(self.rows[0]):
            player_name = name.get().strip()
            final_value = final.get().strip()
            buyin_value = buyins.get().strip()

            if player_name == "":
                messagebox.showerror("Missing data", f"Player {i + 1}: enter a name.")
                name.focus()
                return

            if buyin_value == "":
                messagebox.showerror("Missing data", f"{player_name}: enter number of buy-ins.")
                buyins.focus()
                return

            if buyin_value != "0" and final_value == "":
                messagebox.showerror("Missing data", f"{player_name}: enter final chips.")
                final.focus()
                return

        start_row = self.game_start_rows[-1] + len(self.rows[-1]) + 7
        self.rows.append([])
        self.buyin_values.append([])
        self.game_start_rows.append(start_row)

        ttk.Label(
            self.table_frame,
            text=f"♣️GAME TABLE nr {ng + 1}",
            style="TableSection.TLabel"
        ).grid(row=start_row, column=0, columnspan=3, sticky="w", pady=(0, 15))

        headers = ["PLAYER", "FINAL CHIPS", "BUY INS"]

        for col, header in enumerate(headers):
            tk.Label(
                self.table_frame,
                text=header,
                bg=TABLE,
                fg="#BFE2D2",
                font=("Segoe UI", 9, "bold")
            ).grid(
                row=start_row + 1,
                column=col,
                padx=8,
                pady=5
            )

        buyin_vcmd = (self.root.register(validate_positive_integer), "%P")
        chips_vcmd = (self.root.register(validate_positive_integer), "%P")

        for i in range(np):
            name = ttk.Entry(self.table_frame, state="readonly")
            name.configure(state="normal")
            name.insert(0, self.rows[0][i][0].get())
            name.configure(state="readonly")

            final = ttk.Entry(self.table_frame, validate="key", validatecommand=chips_vcmd)
            previous_buyins = self.buyin_values[ng - 1][i].get() if ng > 0 else "1"
            if previous_buyins == "0":
                buyins_value = tk.StringVar(value="0")
            else:
                buyins_value = tk.StringVar(value="1")
            buyins = ttk.Spinbox(
                self.table_frame,
                from_=0,
                to=100,
                width=8,
                textvariable=buyins_value
            )

            name.grid(row=start_row + i + 2, column=0, padx=8, pady=4)
            final.grid(row=start_row + i + 2, column=1, padx=8, pady=4)
            buyins.grid(row=start_row + i + 2, column=2, padx=8, pady=4)

            self.rows[ng].append([name, final, buyins])
            self.buyin_values[ng].append(buyins_value)
            self.bind_input_navigation(name)
            self.bind_input_navigation(final)
            self.bind_input_navigation(buyins)

            self.bind_player_row_state(ng, name, final, buyins_value)
            final.bind("<KeyRelease>", lambda event, game=ng: self.update_chip_status(event, game))
            final.bind("<FocusOut>", lambda event, game=ng: self.update_chip_status(event, game))
            self.update_player_row_state(name, final, buyins_value)

            # final.bind("<KeyRelease>", lambda event, game=ng: self.update_chip_status(event, game))
            # buyins.bind("<KeyRelease>", lambda event, game=ng: self.update_chip_status(event, game))
            # buyins.bind("<<Increment>>", lambda event, game=ng: self.update_chip_status(event, game))
            # buyins.bind("<<Decrement>>", lambda event, game=ng: self.update_chip_status(event, game))

        self.chip_statuses[ng] = tk.StringVar(value="0 / 0")
        chip_status_frame = tk.Frame(self.table_frame, bg=TABLE)
        chip_status_frame.grid(
            row=start_row,
            column=4,
            rowspan=np + 3,
            padx=(35, 8),
            sticky="nsew"
        )

        tk.Label(
            chip_status_frame,
            text="CHIPS ON THE TABLE",
            bg=TABLE,
            fg="#BFE2D2",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(5, 8))

        tk.Label(
            chip_status_frame,
            textvariable=self.chip_statuses[ng],
            bg=TABLE,
            fg="#BFE2D2",
            font=("Segoe UI", 11, "bold")
        ).pack(anchor="w")

        self.update_chip_status(game=ng)
        buttons_row = start_row + np + 2
        self.add_player_button.grid(row=buttons_row, column=0, padx=6, pady=(15, 0))
        self.restart_button.grid(row=buttons_row, column=1, padx=6, pady=(15, 0))
        self.add_game_button.grid(row=buttons_row, column=2, padx=6, pady=(15, 0))
        self.resolve_button.grid(row=buttons_row, column=3, padx=6, pady=(15, 0))

    def bind_input_navigation(self, widget):
        widget.bind("<Return>", self.focus_next_input)
        widget.bind("<KP_Enter>", self.focus_next_input)
        if isinstance(widget, ttk.Spinbox):
            widget.bind("<MouseWheel>", lambda _event: "break")
            widget.bind("<Button-4>", lambda _event: "break")
            widget.bind("<Button-5>", lambda _event: "break")

    def focus_next_input(self, event):
        input_widgets = [
            widget
            for game_rows in self.rows
            for row in game_rows
            for widget in row
            if widget.instate(["!disabled", "!readonly"])
        ]
        try:
            next_index = input_widgets.index(event.widget) + 1
        except ValueError:
            return "break"

        if next_index < len(input_widgets):
            input_widgets[next_index].focus_set()
            input_widgets[next_index].selection_range(0, tk.END)
        return "break"


    def run_resolve(self):
        try:
            n = len(self.rows[0])

            if not self.validate_table_names():
                return

            chip_count = int( self.chip_entry.get())

            buy_in = int(self.buyin_entry.get())
            if chip_count <= 0:
                messagebox.showerror("Invalid data","Chips per buy-in must be greater than 0.")
                return

            if buy_in <= 0:
                messagebox.showerror("Invalid data","Buy-in amount must be greater than 0.")
                return

            chip_value = buy_in / chip_count

            record_table = []
            games = len(self.rows)
            for game in range(games):
                table_chips = 0
                table_buy_ins = 0

                for i, (name, final, buyins) in enumerate(self.rows[game]):

                    player_name = name.get().strip()
                    final_value = final.get().strip()
                    buyin_value = buyins.get().strip()

                    if player_name == "":
                        messagebox.showerror("Missing data",f"Player {i + 1}: enter a name.")
                        name.focus()
                        return

                    if buyin_value == "":
                        messagebox.showerror( "Missing data",f"{player_name}: enter number of buy-ins." )
                        buyins.focus()
                        return

                    if buyin_value == "0":
                        final_value = "0"
                    elif final_value == "":
                        messagebox.showerror("Missing data",f"{player_name}: enter final chips.")
                        final.focus()
                        return

                    final_value = int(final_value)
                    buyin_value = int(buyin_value)

                    if final_value < 0:
                        messagebox.showerror("Invalid data",f"{player_name}: final chips cannot be negative.")
                        final.focus()
                        return

                    if buyin_value < 0:
                        messagebox.showerror("Invalid data",f"{player_name}: buy-ins cannot be negative.")
                        buyins.focus()
                        return

                    table_chips += final_value
                    table_buy_ins += buyin_value

                    record_table.append(
                        [
                            player_name,
                            final_value,
                            buyin_value
                        ]
                    )

                if table_chips != table_buy_ins * chip_count:
                    messagebox.showerror("Invalid data", "The number of chips on the table doesn't add up.")
                    return

            total_record_table = []
            for player in range(n):
                player_records = record_table[player::n]
                total_record_table.append(
                    [
                        player_records[0][0],
                        sum(record[1] for record in player_records),
                        sum(record[2] for record in player_records)
                    ]
                )

            balances, transfers = resolve(
                total_record_table,
                n,
                chip_value,
                chip_count
            )

            self.show_result_screen(
                total_record_table,
                balances,
                transfers
            )

        except ValueError:
            messagebox.showerror("Invalid data","Please enter valid numbers.")

    def show_result_screen(self, record_table, balances, transfers):
        for widget in self.main_container.winfo_children():
            widget.destroy()

        header = tk.Frame( self.main_container, bg=BG, height=132)
        header.pack( fill="x", side="top")

        ttk.Label(header,  text="♠  SETTLEMENT  ♥", style="Title.TLabel").pack( pady=(25, 3))
        ttk.Label( header, text="FINAL RESULTS", style="Subtitle.TLabel").pack( pady=(0, 15))

        bottom_bar = tk.Frame(  self.main_container, bg=BG, height=70)
        bottom_bar.pack( fill="x", side="bottom", pady=(0, 8))
        bottom_bar.pack_propagate(False)

        ttk.Button(  bottom_bar,  text="←  NEW GAME",  command=self.show_edit_screen).pack(pady=14)

        center = tk.Frame(self.main_container, bg=BG)
        center.pack(fill="both", expand=True)


        canvas = tk.Canvas(center, bg=BG, highlightthickness=0 )

        scrollbar = ttk.Scrollbar(center, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
        scrollbar.pack(side="right", fill="y")

        result_frame = tk.Frame( canvas, bg=PANEL, padx=25, pady=20)

        canvas_window = canvas.create_window( (0, 0), window=result_frame, anchor="nw")

        def update_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        result_frame.bind("<Configure>", update_scroll)

        def resize_result(event):
            canvas.itemconfig( canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_result)


        output = tk.Text(
            result_frame,
            bg=TABLE_DARK,
            fg="#EAF4EF",
            insertbackground="#EAF4EF",
            font=("Consolas", 11),
            relief="flat",
            bd=0,
            padx=20,
            pady=20,
            height=15
        )

        output.pack(
            fill="both",
            expand=True
        )


        output.tag_configure(
            "gold",
            foreground=GOLD,
            font=("Consolas", 12, "bold")
        )

        output.tag_configure(
            "positive",
            foreground=GREEN,
            font=("Consolas", 11, "bold")
        )

        output.tag_configure(
            "negative",
            foreground=RED,
            font=("Consolas", 11, "bold")
        )

        output.insert(
            tk.END,
            "♦  BALANCES\n",
            "gold"
        )

        output.insert(
            tk.END,
            "────────────────────────────────────\n"
        )

        for i, balance in enumerate(balances):

            name = record_table[i][0]

            if balance > 0:

                output.insert(
                    tk.END,
                    f"{name:<20} +{balance:.2f}\n",
                    "positive"
                )

            elif balance < 0:

                output.insert(
                    tk.END,
                    f"{name:<20} {balance:.2f}\n",
                    "negative"
                )

            else:

                output.insert(
                    tk.END,
                    f"{name:<20} 0.00\n"
                )


        output.insert(
            tk.END,
            "\n♣  TRANSFERS\n",
            "gold"
        )

        output.insert(
            tk.END,
            "────────────────────────────────────\n"
        )

        if not transfers:
            output.insert(tk.END,"No transfers required.\n")

        else:

            for t in transfers:
                payer = record_table[t[1]][0]
                receiver = record_table[t[0]][0]
                amount = t[2]

                output.insert(
                    tk.END,
                    f"{payer:<15} → {receiver:<15} {amount:.2f}\n"
                )

        output.configure( state="disabled")

# start
root = tk.Tk()
app = SettlementGUI( root )
root.mainloop()