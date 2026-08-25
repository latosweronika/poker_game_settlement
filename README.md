# Poker Game Settlement

A desktop application for settling poker game results. The program calculates each player's balance and determines the minimum number of transfers needed to settle the session.

## Requirements

- Python
- Tkinter, which is usually included with Python

The project does not require any additional external libraries.

## Running the Application

Run the application from the project directory:

```powershell
python pokerGameGUI.py
```

## Usage

1. Enter the number of players, the number of chips per buy-in, and the buy-in value.
2. Click `CREATE TABLE`.
3. In the first table, enter the players' names, final chip counts, and number of buy-ins.
4. Click `ADD GAME` to add another game. Player names are copied and cannot be changed.
5. Enter the results and number of buy-ins for each additional game.
6. If a player did not participate in a particular game, set `BUY INS` to `0`. The `FINAL CHIPS` field will be disabled and `0` will be used in the balance calculation.
7. Click `RESOLVE` to view the total balances and suggested transfers.

The `RESTART` button clears the current session and starts a new settlement.

## Balance Calculation

Each player's data is summed across all games. The balance is calculated as follows:

```text
(total final chips - total buy-ins * chips per buy-in) * value of one chip
```

The DFS backtracking algorithm then finds a solution with the minimum number of transfers between players.

## Files

- `pokerGameGUI.py` - graphical user interface.
- `poker_game_settlement.py` - balance and transfer calculations.
