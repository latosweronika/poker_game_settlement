# game settlement problem, calculate the minimum number of money transfers
# needed to settle all balances
# the algorithm uses dfs with backtracking to explore
# different possible combinations of transfers

def dfs(balances, transfers):

    # if all balances are zero
    if all(x == 0 for x in balances):
        return transfers.copy()
    # player who still has non-zero balance
    i = next(i for i, x in enumerate(balances) if x != 0)

    best = None

    for j in range(i + 1, len(balances)):
        # players must have opposite balances
        if balances[i] * balances[j] >= 0:
            continue

        amount = min(abs(balances[i]), abs(balances[j]))

        old_i = balances[i]
        old_j = balances[j]

        if balances[i] > 0:
            balances[i] -= amount
            balances[j] += amount
            result = dfs(balances, transfers + [(i, j, amount)])
        else:
            balances[i] += amount
            balances[j] -= amount
            result = dfs(balances, transfers + [(j, i, amount)])

        # solution with the smallest number of transfers
        if result is not None:
            if best is None or len(result) < len(best):
                best = result

        # restore the previous state
        balances[i] = old_i
        balances[j] = old_j

    return best

def print_transfers(record_table, transfers):
    print("Transfers to be made:")
    for transfer in transfers:
        print(f"{record_table[int(transfer[1])][0]} -> {record_table[int(transfer[0])][0]}: {transfer[2]}")
    print("")


def resolve(record_table, number_of_players, chip_value, chip_count):
    G = []

    for player in range(number_of_players):
        balance = (record_table[player][1] - record_table[player][2]* chip_count )* chip_value
        G.append(balance)

    # print("balance: ")
    # for player in range(number_of_players):
    #     print(f"{record_table[player][0]}: {G[player]}")
    # print("")
    transfers = dfs(G,[])
    # print_transfers(record_table, transfers)
    return G, transfers

def main():
    number_of_players = int(input("Enter the number of players (max 10): "))
    chip_count = int(input("Enter the number of chips per buy-in: "))
    buy_in = int(input("Enter the buy-in amount: "))

    if number_of_players > 10: number_of_players = 10
    record_table = [["", 0, 0] for _ in range(number_of_players)]


    for i in range(number_of_players):
        record_table[i][0] = str(input(f"Enter the name of player {i + 1}: "))
    print("")
    while True:
        for i in range(number_of_players):
            record_table[i][1] += int(input(f"Enter {record_table[i][0]}'s final chip count: "))
            record_table[i][2] += int(input(f"Enter {record_table[i][0]}'s starting chip count: "))

        flag = str(input("another game?(t/f): "))
        print("")
        if flag == "f":
            break


    resolve( record_table, number_of_players, buy_in / chip_count)