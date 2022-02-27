## UEK BLACKJACK
import random

COLORS = ["Pik", "Kier", "Trefl", "Karo"]
RANKS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
MAX_PLAYERS = 8
MAX_BALANCE = 1000
chip_balance = 0


class Card:
    def __init__(self, color, rank):
        self.color = color
        self.rank = rank
        self.is_ace = False

        if rank == "A":
            self.value = 11
            self.is_ace = True
        elif rank in ["K", "Q", "J"]:
            self.value = 10
        else:
            self.value = int(rank)

        self.visible = True

    def __str__(self):
        if self.visible:
            return f"[{self.color} | {self.rank}]"
        else:
            return f"[X] (karta ukryta)"

    def __repr__(self):
        return f"[{self.color} | {self.rank}]"

    def hide(self):
        self.visible = False

    def reveal(self):
        self.visible = True


class Hand:
    def __init__(self):
        self.hand = []

    def add_card(self, card):
        self.hand.append(card)
        return self.hand

    def get_value(self):
        ace = 0
        value = 0
        for card in self.hand:
            if card.is_ace:
                ace += 1
            value += card.value
        while value > 21 and ace:
            value -= 10
            ace -= 1
        return value


class Deck:
    def __init__(self):
        self.cards = [Card(color, rank) for color in COLORS for rank in RANKS]
        self.shuffle()

    def shuffle(self):
        random.shuffle(self.cards)

    def deal(self):
        return self.cards.pop(0)

    def __repr__(self):
        return self.cards


class Dealer(Hand):
    def __init__(self, name, deck):
        Hand.__init__(self)
        self.name = name
        self.deck = deck
        self.isOut = False

    def show_hand(self):
        for card in self.hand:
            print(card)

    def hit(self):
        print("Rozdaje karte")
        self.add_card(self.deck.deal())
        return self.hand

    def stand(self):
        print(f"{self.name} ma w rece {self.get_value()}")

    def check_over_21(self):
        if self.get_value() > 21:
            self.isOut = True
            print(f"{self.name} odpada, ma w rece {self.get_value()}")
        else:
            self.stand()

    def check_bust(self):
        if self.get_value() > 21:
            self.isOut = True
            print(f"{self.name} wypada z gry!")
        else:
            self.stand()


class Player(Dealer):
    def __init__(self, name, deck, bet):
        Dealer.__init__(self, name, deck)
        self.bet = bet
        self.isOut = False
        self.isSurrender = False
        self.isOutOfChips = False
        self.isSplit = False
        self.split = []


def play(player, deck):
    print(f"{player.name} : {player.show_hand()}")
    if player.name == "Dealer":
        while player.get_value() < 17:
            player.hit()
            player.show_hand()
        player.check_over_21()
    else:
        global chip_balance
        if chip_balance > player.bet and not player.isSplit:
            if player.hand[0].value == player.hand[1].value:
                choice = input_func(
                    "Hit, Stand, Podwoic stawke, Split czy Kapitulacja? (h/s/d/p/u) ",
                    str.lower,
                    range_=("h", "s", "d", "p", "u"),
                )
            else:
                choice = input_func(
                    "Hit, Stand, Podwoic stawke czy Kapitulacja? (h/s/d/u) ",
                    str.lower,
                    range_=("h", "s", "d", "u"),
                )
        else:
            choice = input_func(
                "Hit, Stand czy Kapitulacja? (h/s/u) ",
                str.lower,
                range_=("h", "s", "u"),
            )
        while choice == "h":
            player.hit()
            player.show_hand()
            if player.get_value() > 21:
                player.isBust = True
                print(f"{player.name} wypada z gry, ma w rece {player.get_value()}!")
                break
            choice = input_func("Hit czy Stand? (h/s) ", str.lower, range_=("h", "s"))

        if choice == "s":
            player.stand()

        if choice == "d":
            chip_balance -= player.bet
            player.bet *= 2
            print(f"Zetony = {chip_balance}")
            player.hit()
            player.show_hand()
            player.check_over_21()

        if choice == "u":
            player.isSurrender = True
            chip_balance += player.bet - player.bet / 2
            print(f"Zetony = {chip_balance}")

        if choice == "p":
            chip_balance -= player.bet
            print(f"Zetony = {chip_balance}")
            player.split.append(Player(" Split_1", deck, player.bet))
            player.split.append(Player(" Split_2", deck, player.bet))
            for p in player.split:
                p.add_card(player.hand.pop(0))
                p.add_card(deck.deal())
                p.isSplit = True
                play(p, deck)


def input_func(prompt, type_=None, min_=None, max_=None, range_=None):
    value = ""
    while True:
        value = input(prompt)
        if type_ is not None:
            try:
                value = type_(value)
            except ValueError:
                print("Sorry I don't understand.")
                continue
        if min_ is not None and value < min_:
            print(f"Wartosc nie moze byc mniejsza niz {min_}")
        elif max_ is not None and value > max_:
            print(f"Wartosc nie moze byc wieksza niz {max_}")
        elif range_ is not None and value not in range_:
            print(f"Wartosc musi zawierac sie w przedziale: {range_}")
        else:
            break
    return value


def report(player, dealer):
    global chip_balance
    if player.isSurrender:
        tag = "Zkapitulowal"
    elif player.isOutOfChips:
        tag = "Przegral"
    elif len(player.hand) == 2 and player.get_value() == 21 and not player.isSplit:
        tag = "blackjack"
        chip_balance += player.bet * 3
    elif dealer.isOut or (player.get_value() > dealer.get_value()):
        tag = "wygrana"
        chip_balance += player.bet * 2
    elif player.get_value() == dealer.get_value():
        tag = "push"
        chip_balance += player.bet
    else:
        tag = "przegral"
    print(f"{player.name}: {tag}    Balance:  {chip_balance} ")


def game():
    players = []
    global chip_balance
    deck = Deck()

    player_num = input_func(
        "\nProsze wybrac liczbe graczy: (1-8) ", int, 1, MAX_PLAYERS
    )

    print("Zaczynamy gre w BlackJacka...\n")

    for i in range(player_num):
        if chip_balance > 0:
            player_name = "Player_" + str(i + 1)
            print(f"{player_name}:")
            player_bet = input_func(
                "Przyjmujemy zaklad. Minimalny zaklad to 1 zeton. ",
                int,
                1,
                chip_balance,
            )
            chip_balance -= player_bet
            print(f"Zetony: {chip_balance}.")
            player = Player(player_name, deck, player_bet)
            players.append(player)
        else:
            print(f"\nLiczba graczy to {len(players)}. Braklo zetonow zeby zagrac.")
            break

    dealer = Dealer("Dealer", deck)

    for i in range(2):
        for player in players + [dealer]:
            player.add_card(deck.deal())

    dealer.hand[1].hide()
    print("\nDealer:")
    dealer.show_hand()
    print
    dealer.hand[1].reveal()

    for player in players + [dealer]:
        play(player, deck)
        print

    print("...Wyniki...\n")

    for player in players:
        if not player.split:
            report(player, dealer)
        else:
            print("{player.name}: split")
            for p in player.split:
                report(p, dealer)

    print(f"\nZetony to: {chip_balance}.\n")


if __name__ == "__main__":
    chip_balance = input_func(
        "\n UekBlackJack! Prosze wprowadzic liczbe zetonow do gry: (1-1000) ",
        int,
        1,
        1000,
    )
    while True:
        game()
        if chip_balance < 1:
            print("Skonczyly sie zetony")
            break
        proceed = input_func(
            "Zagrac jeszcze raz?? (t/n) ", str.lower, range_=("t", "n")
        )
        if proceed == "n":
            print("\nKasyno zaprasza ponownie!")
            break
