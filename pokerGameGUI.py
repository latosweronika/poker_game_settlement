import tkinter as tk
from tkinter import ttk, messagebox

from poker_game_settlement import dfs, resolve

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


class SettlementGUI:
    def __init__(self, root):

        self.root = root
        root.title("Poker Settlement")
        self.root.geometry("820x660")
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
        style.configure("TSpinbox", fieldbackground=PANEL_LIGHT, foreground=TEXT, insertcolor=TEXT, bordercolor="#CBD6D1", lightcolor="#CBD6D1", darkcolor="#CBD6D1", padding=7)
        style.configure("TButton", background=GOLD, foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=(18, 9), borderwidth=0)
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
            width=8,
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

        self.chip_entry = ttk.Entry( settings_frame,width=10)

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

        self.buyin_entry = ttk.Entry( settings_frame, width=10)

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
            buyins = ttk.Spinbox(self.table_frame, from_=1, to=100, width=8, validate="key", validatecommand=buyin_vcmd)

            buyins.set("1")

            name.grid(row=i + 2, column=0, padx=8, pady=4)
            final.grid(row=i + 2, column=1, padx=8, pady=4)
            buyins.grid(row=i + 2, column=2, padx=8, pady=4)

            self.rows[0].append([name, final, buyins])

        self.restart_button = ttk.Button(
            self.table_frame,
            text="↻ RESTART",
            command=self.show_edit_screen
        )
        self.restart_button.grid(row=n + 2, column=0, pady=(15, 0))

        self.add_game_button = ttk.Button(
            self.table_frame,
            text="+ ADD GAME",
            command=self.add_game
        )
        self.add_game_button.grid(row=n + 2, column=1, pady=(15, 0))

        self.resolve_button = ttk.Button(
            self.table_frame,
            text="⚡ RESOLVE",
            command=self.run_resolve
        )
        self.resolve_button.grid(row=n + 2, column=2, pady=(15, 0))

        self.create_table_button.grid_remove()

    def add_game(self):
        np = int(self.players_entry.get())
        ng =int(len(self.rows))
        start_row = ng * (np + 6)
        self.rows.append([])

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
            buyins_value = tk.StringVar(value="1")
            buyins = ttk.Spinbox(
                self.table_frame,
                from_=0,
                to=100,
                width=8,
                textvariable=buyins_value,
                validate="key",
                validatecommand=buyin_vcmd
            )

            def update_final_state(*_args, final=final, buyins_value=buyins_value):
                if buyins_value.get() == "0":
                    final.configure(state="normal")
                    final.delete(0, tk.END)
                    final.configure(state="disabled")
                else:
                    final.configure(state="normal")

            buyins_value.trace_add("write", update_final_state)

            name.grid(row=start_row + i + 2, column=0, padx=8, pady=4)
            final.grid(row=start_row + i + 2, column=1, padx=8, pady=4)
            buyins.grid(row=start_row + i + 2, column=2, padx=8, pady=4)

            self.rows[ng].append([name, final, buyins])

            buttons_row = start_row + np + 2
            self.restart_button.grid(row=buttons_row, column=0, pady=(15, 0))
            self.add_game_button.grid(row=buttons_row, column=1, pady=(15, 0))
            self.resolve_button.grid(row=buttons_row, column=2, pady=(15, 0))


    def run_resolve(self):
        try:
            n = int( self.players_entry.get())

            chip_count = int( self.chip_entry.get())

            buy_in = int(self.buyin_entry.get())
            if chip_count <= 0:
                messagebox.showerror(
                    "Invalid data",
                    "Chips per buy-in must be greater than 0."
                )

                return

            if buy_in <= 0:
                messagebox.showerror(
                    "Invalid data",
                    "Buy-in amount must be greater than 0."
                )

                return

            chip_value = buy_in / chip_count

            record_table = []
            games = len(self.rows)
            for game in range(games):
                for i, (name, final, buyins) in enumerate(self.rows[game]):

                    player_name = name.get().strip()
                    final_value = final.get().strip()
                    buyin_value = buyins.get().strip()

                    # Name

                    if player_name == "":
                        messagebox.showerror(
                            "Missing data",
                            f"Player {i + 1}: enter a name."
                        )
                        name.focus()
                        return

                        # Buy-ins

                    if buyin_value == "":
                        messagebox.showerror(
                            "Missing data",
                            f"{player_name}: enter number of buy-ins."
                        )

                        buyins.focus()
                        return

                    if buyin_value == "0":
                        final_value = "0"
                    elif final_value == "":
                        messagebox.showerror(
                            "Missing data",
                            f"{player_name}: enter final chips."
                        )

                        final.focus()
                        return

                    final_value = int(final_value)
                    buyin_value = int(buyin_value)

                    if final_value < 0:
                        messagebox.showerror(
                            "Invalid data",
                            f"{player_name}: final chips cannot be negative."
                        )
                        final.focus()
                        return

                    if buyin_value < 0:
                        messagebox.showerror(
                            "Invalid data",
                            f"{player_name}: buy-ins cannot be negative."
                        )

                        buyins.focus()
                        return

                    record_table.append(
                        [
                            player_name,
                            final_value,
                            buyin_value
                        ]
                    )

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

            # Show result screen

            self.show_result_screen(
                total_record_table,
                balances,
                transfers
            )

        except ValueError:
            messagebox.showerror(
                "Invalid data",
                "Please enter valid numbers."
            )

    def show_result_screen(self, record_table, balances, transfers):
        # Clear current screen
        for widget in self.main_container.winfo_children():
            widget.destroy()

        header = tk.Frame(
            self.main_container,
            bg=BG,
            height=132
        )

        header.pack(
            fill="x",
            side="top"
        )

        ttk.Label(
            header,
            text="♠  SETTLEMENT  ♥",
            style="Title.TLabel"
        ).pack(
            pady=(25, 3)
        )

        ttk.Label(
            header,
            text="FINAL RESULTS",
            style="Subtitle.TLabel"
        ).pack(
            pady=(0, 15)
        )

        bottom_bar = tk.Frame(
            self.main_container,
            bg=BG,
            height=70
        )

        bottom_bar.pack(
            fill="x",
            side="bottom",
            pady=(0, 8)
        )

        bottom_bar.pack_propagate(False)

        ttk.Button(
            bottom_bar,
            text="←  NEW GAME",
            command=self.show_edit_screen
        ).pack(pady=14)

        center = tk.Frame(self.main_container, bg=BG)
        center.pack(fill="both", expand=True)


        canvas = tk.Canvas(center, bg=BG, highlightthickness=0 )

        scrollbar = ttk.Scrollbar(center, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True, padx=(30, 0), pady=10)
        scrollbar.pack(side="right", fill="y")

        result_frame = tk.Frame(
            canvas,
            bg=PANEL,
            padx=25,
            pady=20
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=result_frame,
            anchor="nw"
        )

        def update_scroll(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        result_frame.bind("<Configure>", update_scroll)

        def resize_result(event):
            canvas.itemconfig( canvas_window, width=event.width)

        canvas.bind("<Configure>", resize_result)

        # Text output

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

        # Text styles

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

            output.insert(
                tk.END,
                "No transfers required.\n"
            )

        else:

            for t in transfers:
                payer = record_table[t[1]][0]
                receiver = record_table[t[0]][0]
                amount = t[2]

                output.insert(
                    tk.END,
                    f"{payer:<15} → {receiver:<15} {amount:.2f}\n"
                )

        output.configure(
            state="disabled"
        )

# start
root = tk.Tk()
app = SettlementGUI( root )
root.mainloop()