import csv
from datetime import datetime
from pathlib import Path



def build_player_balance_history(csv_files):
	games = []
	for csv_file in csv_files:
		loaded = load_game_from_csv(csv_file)
		if not loaded["balances"]:
			continue
		games.append({
			"label": loaded["display_date"] or loaded["saved_at"] or Path(csv_file).stem,
			"balances": loaded["balances"],
		})

	players = []
	for game in games:
		for entry in game["balances"]:
			player_name = (entry.get("player") or "").strip()
			if player_name and player_name not in players:
				players.append(player_name)

	series = {player: [] for player in players}
	for game in games:
		balances_by_player = {}
		for entry in game["balances"]:
			player_name = (entry.get("player") or "").strip()
			if not player_name:
				continue
			balance_value = entry.get("balance")
			if balance_value in (None, ""):
				continue
			try:
				balances_by_player[player_name] = float(balance_value)
			except (TypeError, ValueError):
				continue
		for player in players:
			if player in balances_by_player:
				series[player].append([game["label"], balances_by_player[player]])
			else:
				series[player].append([game["label"], 0.0])

	return {"players": players, "series": series}



def _format_saved_at(value):
	if not value:
		return ""
	try:
		return datetime.fromisoformat(value.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S")
	except ValueError:
		return str(value)



def list_saved_games(csv_dir=None):
	output_directory = Path(csv_dir) if csv_dir is not None else Path(__file__).resolve().parent / "previous_games"
	output_directory.mkdir(parents=True, exist_ok=True)

	saved_games = []
	for csv_path in sorted(output_directory.glob("*.csv")):
		with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
			rows = list(csv.DictReader(csv_file))
		saved_at = rows[0].get("saved_at", "") if rows else ""
		saved_games.append({
			"path": csv_path,
			"filename": csv_path.name,
			"saved_at": saved_at,
			"display_date": _format_saved_at(saved_at),
		})

	return saved_games



def load_game_from_csv(csv_path):
	path = Path(csv_path)
	data = {
		"path": str(path),
		"saved_at": "",
		"display_date": "",
		"settings": {},
		"games": [],
		"balances": [],
		"transfers": [],
	}

	with path.open("r", newline="", encoding="utf-8-sig") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			if not row:
				continue
			saved_at = (row.get("saved_at") or "").strip()
			if saved_at and not data["saved_at"]:
				data["saved_at"] = saved_at
				data["display_date"] = _format_saved_at(saved_at)

			section = (row.get("section") or "").strip().upper()
			if section == "SETTINGS":
				for key in ["chip_count", "buy_in", "chip_value"]:
					value = row.get(key)
					if value not in (None, ""):
						data["settings"][key] = value
			elif section == "GAME":
				data["games"].append({
					"game": row.get("game"),
					"player": row.get("player"),
					"final_chips": row.get("final_chips"),
					"buy_ins": row.get("buy_ins"),
				})
			elif section == "BALANCE":
				player_name = (row.get("player") or "").strip()
				balance_value = row.get("balance")
				if not player_name:
					for key in ["player", "payer", "receiver"]:
						candidate = (row.get(key) or "").strip()
						if candidate:
							player_name = candidate
							break
				if balance_value in (None, ""):
					for key in ["balance", "final_chips", "amount"]:
						candidate = row.get(key)
						if candidate not in (None, ""):
							balance_value = candidate
							break
				data["balances"].append({
					"player": player_name,
					"balance": balance_value,
				})
			elif section == "TRANSFER":
				data["transfers"].append({
					"payer": row.get("payer"),
					"receiver": row.get("receiver"),
					"amount": row.get("amount"),
				})

	return data



def save_game_to_csv(games, record_table, balances, transfers, chip_count, buy_in, chip_value):
	output_directory = Path(__file__).resolve().parent / "previous_games"
	output_directory.mkdir(parents=True, exist_ok=True)

	timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
	output_path = output_directory / f"game_{timestamp}.csv"
	fieldnames = [
		"saved_at",
		"section",
		"game",
		"player",
		"final_chips",
		"buy_ins",
		"balance",
		"payer",
		"receiver",
		"amount",
		"chip_count",
		"buy_in",
		"chip_value",
	]

	with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
		writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
		writer.writeheader()
		saved_at = datetime.now().isoformat(timespec="seconds")
		writer.writerow({
			"saved_at": saved_at,
			"section": "SETTINGS",
			"chip_count": chip_count,
			"buy_in": buy_in,
			"chip_value": chip_value,
		})

		for game_number, game_rows in enumerate(games, start=1):
			for player, final_chips, buy_ins in game_rows:
				writer.writerow({
					"saved_at": saved_at,
					"section": "GAME",
					"game": game_number,
					"player": player,
					"final_chips": final_chips,
					"buy_ins": buy_ins,
				})

		for player_record, balance in zip(record_table, balances):
			writer.writerow({
				"saved_at": saved_at,
				"section": "BALANCE",
				"player": player_record[0],
				"balance": balance,
			})

		for receiver_index, payer_index, amount in transfers or []:
			writer.writerow({
				"saved_at": saved_at,
				"section": "TRANSFER",
				"payer": record_table[payer_index][0],
				"receiver": record_table[receiver_index][0],
				"amount": amount,
			})

	return output_path
