import tkinter as tk
from tkinter import ttk, messagebox

from poker_game_settlement import dfs, resolve

BG = "#F0F0E6"
PANEL = "#F0F0E6"
PANEL_LIGHT = "#FFFDF3"

TABLE = "#0A6136"
TABLE_DARK = "#123524"

GOLD = "#9C1C1C"
GOLD_LIGHT = "#D94A4A"

TEXT = "#171615"
MUTED = "#F4F1DE"

RED = "#D94A4A"
GREEN = "#48C774"


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
        self.root.geometry("750x800")
        self.root.minsize(300, 300)
        self.root.configure(bg=BG)

        # style

        style = ttk.Style(root)
        style.theme_use("clam")

        # style.configure("TFrame", background=BG)
        style.configure("TLabel", background=BG, foreground=TEXT, font=("Arial", 11))
        style.configure("Title.TLabel", background=BG, foreground=GOLD, font=("Arial", 24, "bold"))
        style.configure("Subtitle.TLabel", background=BG, foreground=MUTED, font=("Arial", 10))
        style.configure("Section.TLabel", background=PANEL, foreground=GOLD, font=("Arial", 13, "bold"))
        style.configure("TEntry", fieldbackground="#E3E1E1", foreground=TEXT, insertcolor=TEXT, borderwidth = 0, padding=6)
        style.configure("TSpinbox", fieldbackground="#E3E1E1", foreground=TEXT, insertcolor=TEXT, borderwidth = 0, padding=6)
        style.configure("TButton", background=GOLD, foreground="#F4F1DE", font=("Arial", 10, "bold"), padding=(15, 8), borderwidth=0)
        style.map("TButton", background=[("active", GOLD_LIGHT), ("pressed", "#730800")])

        #
        self.main_container = tk.Frame(
            root,
            bg=BG
        )

        self.main_container.pack(
            fill="both",
            expand=True
        )

        # Start with edit screen

        self.show_edit_screen()

    def show_edit_screen(self):

        # Remove previous screen

        for widget in self.main_container.winfo_children():
            widget.destroy()

        header = tk.Frame(
            self.main_container,
            bg=BG
        )

        header.pack(
            fill="x"
        )

        ttk.Label(
            header,
            text="♠  POKER SETTLEMENT  ♥",
            style="Title.TLabel"
        ).pack(
            pady=(20, 3)
        )

        ttk.Label(
            header,
            text="CASH GAME MANAGER",
            style="Subtitle.TLabel"
        ).pack(
            pady=(0, 15)
        )


        scroll_container = tk.Frame(
            self.main_container,
            bg=BG
        )

        scroll_container.pack(
            fill="both",
            expand=True
        )

        # Canvas

        canvas = tk.Canvas(
            scroll_container,
            bg=BG,
            highlightthickness=0
        )

        canvas.pack(
            side="left",
            fill="both",
            expand=True
        )

        # Scrollbar

        scrollbar = ttk.Scrollbar(
            scroll_container,
            orient="vertical",
            command=canvas.yview
        )

        scrollbar.pack(
            side="right",
            fill="y"
        )

        canvas.configure(
            yscrollcommand=scrollbar.set
        )

        # Frame inside canvas

        self.scroll_frame = tk.Frame(
            canvas,
            bg=BG
        )

        canvas_window = canvas.create_window(
            (0, 0),
            window=self.scroll_frame,
            anchor="nw"
        )

        # Update scroll region

        def update_scroll_region(event=None):
            canvas.configure(
                scrollregion=canvas.bbox("all")
            )

        self.scroll_frame.bind(
            "<Configure>",
            update_scroll_region
        )

        # Make inner frame same width as canvas

        def resize_inner_frame(event):
            canvas.itemconfig(
                canvas_window,
                width=event.width
            )

        canvas.bind(
            "<Configure>",
            resize_inner_frame
        )

        # Mouse wheel

        def mouse_wheel(event):
            canvas.yview_scroll(
                int(-1 * (event.delta / 120)),
                "units"
            )

        canvas.bind_all(
            "<MouseWheel>",
            mouse_wheel
        )


        settings_frame = tk.Frame(
            self.scroll_frame,
            bg=PANEL,
            padx=25,
            pady=20
        )

        settings_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )

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

        current_value = tk.StringVar(
            value="2"
        )

        vcmd = (
            self.root.register(
                validate_players_number
            ),
            "%P"
        )

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

        self.chip_entry = ttk.Entry(
            settings_frame,
            width=10
        )

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

        self.buyin_entry = ttk.Entry(
            settings_frame,
            width=10
        )

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
            pady=20
        )

        self.table_frame.pack(
            fill="x",
            padx=30,
            pady=10
        )


    def create_table(self):

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        try:
            n = int(self.players_entry.get())

        except ValueError:
            messagebox.showerror("Invalid data", "Number of players must be between 2 and 10.")
            return

        self.rows = []

        ttk.Label(
            self.table_frame,
            text="♣️GAME TABLE",
            style="Section.TLabel"
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 15)
        )

        headers = ["PLAYER", "FINAL CHIPS", "BUY INS"]

        for col, header in enumerate(headers):
            tk.Label(
                self.table_frame,
                text=header,
                bg=TABLE,
                fg=BG,
                font=("Arial", 10, "bold")
            ).grid(
                row=1,
                column=col,
                padx=8,
                pady=5
            )

        buyin_vcmd = (self.root.register(validate_positive_integer),"%P")
        chips_vcmd = (self.root.register(validate_positive_integer),"%P")

        for i in range(n):
            name = ttk.Entry(self.table_frame)
            final = ttk.Entry(self.table_frame, validate="key", validatecommand=chips_vcmd)
            buyins = ttk.Spinbox(self.table_frame,from_=1, to=100, width=8, validate="key", validatecommand=buyin_vcmd)

            buyins.set("1")

            name.grid(
                row=i + 2,
                column=0,
                padx=8,
                pady=4
            )

            final.grid(
                row=i + 2,
                column=1,
                padx=8,
                pady=4
            )

            buyins.grid(
                row=i + 2,
                column=2,
                padx=8,
                pady=4
            )

            self.rows.append([name, final, buyins])

        # Buttons

        ttk.Button(
            self.table_frame,
            text="ADD GAME",
            command=self.add_game
        ).grid(
            row=n + 2,
            column=0,
            pady=(15, 0)
        )

        ttk.Button(
            self.table_frame,
            text="⚡ RESOLVE",
            command=self.run_resolve
        ).grid(
            row=n + 2,
            column=1,
            pady=(15, 0)
        )
        self.create_table_button.grid_remove()

    def add_game(self):

        for name, final, start in self.rows:

            try:

                final_val = int(
                    final.get()
                )

                start_val = int(
                    start.get()
                )

                final.delete(
                    0,
                    tk.END
                )

                start.delete(
                    0,
                    tk.END
                )

                final.insert(
                    0,
                    final_val
                )

                start.insert(
                    0,
                    start_val
                )

            except ValueError:
                pass


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

            for i, (name, final, buyins) in enumerate(self.rows):

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

                    # Final chips

                if final_value == "":
                    messagebox.showerror(
                        "Missing data",
                        f"{player_name}: enter final chips."
                    )

                    final.focus()
                    return
                    # Buy-ins

                if buyin_value == "":
                    messagebox.showerror(
                        "Missing data",
                        f"{player_name}: enter number of buy-ins."
                    )

                    buyins.focus()
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

                if buyin_value < 1:
                    messagebox.showerror(
                        "Invalid data",
                        f"{player_name}: buy-ins must be at least 1."
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

            balances, transfers = resolve(
                record_table,
                n,
                chip_value,
                chip_count
            )

            # Show result screen

            self.show_result_screen(
                record_table,
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
            height =100
        )

        header.pack(
            fill="x",
            side="top"
        )

        header.pack_propagate(False)

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

        center = tk.Frame( self.main_container, bg=BG)
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
            bg="#080C0A",
            fg=TEXT,
            insertbackground=TEXT,
            font=("Courier New", 11),
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
            font=("Courier New", 12, "bold")
        )

        output.tag_configure(
            "positive",
            foreground=GREEN,
            font=("Courier New", 11, "bold")
        )

        output.tag_configure(
            "negative",
            foreground=RED,
            font=("Courier New", 11, "bold")
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

        bottom_bar = tk.Frame(
            self.main_container,
            bg = BG,
            height= 75
        )

        bottom_bar.pack(
            fill = "x",
            side = "bottom"
        )

        bottom_bar.pack_propagate(False)

        new_game_button = ttk.Button(
            bottom_bar,
            text = "←  NEW GAME",
            command = self.show_edit_screen
        )
        new_game_button.pack(pady=18)

# start
root = tk.Tk()
app = SettlementGUI( root )
root.mainloop()