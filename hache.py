import random
import discord
from enum import IntEnum
from card import load_cards, Suit
from Player import Player


def start_game(players):
    cards = load_cards()
    hache = Hache()
    hache.cards = cards
    for player in players:
        hache.players.append(Player(player))
    return hache


class Turn(IntEnum):
    TOUR1 = 10
    TOUR2 = 20
    TOUR3 = 30
    TOUR4 = 40
    DRAW = 50


def card_symbol(number):
    if number == 1:
        return 'A'
    elif number == 2:
        return '2'
    elif number == 3:
        return '3'
    elif number == 4:
        return '4'
    elif number == 5:
        return '5'
    elif number == 6:
        return '6'
    elif number == 7:
        return '7'
    elif number == 8:
        return '8'
    elif number == 9:
        return '9'
    elif number == 10:
        return '10'
    elif number == 11:
        return 'J'
    elif number == 12:
        return 'Q'
    elif number == 13:
        return 'K'


def print_card(ctx, card):
    card_image = card_symbol(card.number)
    if card.suit == Suit.DIAMOND:
        card_image += ':diamonds:'
    elif card.suit == Suit.HEART:
        card_image += ':hearts:'
    elif card.suit == Suit.CLUB:
        card_image += '{}'.format(discord.utils.get(ctx.message.guild.emojis, name='white_club'))
    elif card.suit == Suit.SPADE:
        card_image += '{}'.format(discord.utils.get(ctx.message.guild.emojis, name='white_spade'))
    return card_image


def question(turn):
    if turn == Turn.TOUR1:
        return '!rouge ou !noir'
    elif turn == Turn.TOUR2:
        return '!+, !- ou !='
    elif turn == Turn.TOUR3:
        return '!inter, !exter ou !='
    elif turn == Turn.TOUR4:
        return '!pique, !carreau, !trefle, !coeur'
    else:
        return 'Oups!'


class Hache:
    def __init__(self):
        self.cards = None
        self.players = []
        self.currentPlayer = 0
        self.drink = 1
        self.drinkTurn = 1
        self.turn_iter = iter(list(Turn))
        self.turn = next(self.turn_iter)

    async def ask_card(self, ctx):
        player = self.players[self.currentPlayer]
        message = '```{} {}```\n'.format(player.name, question(self.turn))
        emojis = []
        for card in player.cards:
            emojis.append(print_card(ctx, card))
        if len(emojis) > 0:
            message += 'Tes cartes: ' + ' '.join(emojis)
        await ctx.send(message)

    async def first_turn(self, ctx, response):
        if self.turn != Turn.TOUR1:
            return
        player = self.players[self.currentPlayer]
        if ctx.message.author.name != player.name:
            print('not {} turn'.format(ctx.message.author))
            return
        else:
            card = self.draw_card()
            player.cards.append(card)
            message = print_card(ctx, card) + '\n'
            if (response == 'noir' and card.isBlack()) or (response == 'rouge' and card.isRed()):
                message += '{} tu donnes 1 gorgée'
            else:
                message += '{} tu prends 1 gorgée'
            await ctx.send(message.format(player.name))
            await self.next_player(ctx)

    async def second_turn(self, ctx, response):
        if self.turn != Turn.TOUR2:
            return
        player = self.players[self.currentPlayer]
        if ctx.message.author.name != player.name:
            print('not {} turn'.format(ctx.message.author))
            return
        else:
            card = self.draw_card()
            first_card = player.cards[0]
            player.cards.append(card)
            message = print_card(ctx, card) + '\n'
            if (response == '+' and card.number > first_card.number) or (
                    response == '-' and card.number < first_card.number):
                message += '{} tu donnes 2 gorgées'
            elif response.lower() == '=' and card.number == first_card.number:
                message += '{} tu donnes 4 gorgées'
            else:
                message += '{} tu prends 2 gorgées'
            await ctx.send(message.format(player.name))
            await self.next_player(ctx)

    async def third_turn(self, ctx, response):
        if self.turn != Turn.TOUR3:
            return
        player = self.players[self.currentPlayer]
        if ctx.message.author.name != player.name:
            print('not {} turn'.format(ctx.message.author))
            return
        else:
            card = self.draw_card()
            first_card = player.cards[0]
            second_card = player.cards[1]
            player.cards.append(card)
            message = print_card(ctx, card) + '\n'
            inter = first_card.number < card.number < second_card.number or second_card.number < card.number < first_card.number
            if card.number == first_card.number or card.number == second_card.number:
                message += '{} tu donnes 6 gorgées'
            elif (response == 'inter' and inter) or (response == 'exter' and not inter):
                message += '{} tu donnes 3 gorgées'
            else:
                message += '{} tu prends 3 gorgées'
            await ctx.send(message.format(player.name))
            await self.next_player(ctx)

    async def fourth_turn(self, ctx, response):
        if self.turn != Turn.TOUR4:
            return
        player = self.players[self.currentPlayer]
        if ctx.message.author.name != player.name:
            print('not {} turn'.format(ctx.message.author))
            return
        else:
            card = self.draw_card()
            player.cards.append(card)
            message = print_card(ctx, card) + '\n'
            if response == card.suit.value:
                message += '{} tu donnes 4 gorgées'
            else:
                message += '{} tu prends 4 gorgées'
            await ctx.send(message.format(player.name))
            await self.next_player(ctx)

    async def tire(self, ctx):
        if self.turn != Turn.DRAW:
            return
        drinkers = []
        good_card = ''
        draw_cards = []
        while len(drinkers) == 0:
            card = self.draw_card()
            if card is None:
                await ctx.send('Plus de cartes fin du H')
                return
            drinkers = self.find_drinkers(card)
            if len(drinkers) == 0:
                draw_cards.append(print_card(ctx, card))
            else:
                good_card = print_card(ctx, card)
        message = ''
        if len(draw_cards) > 0:
            message = 'Cartes moisies {}'.format(' '.join(draw_cards)) + '\n'
        if good_card is not None:
            message += good_card + '\n'
        if self.drinkTurn % 2 == 0:
            message += self.take(drinkers)
            self.drink += 1
        else:
            message += self.give(drinkers)
        self.drinkTurn += 1
        await ctx.send(message)
        if self.drinkTurn == 13:
            await ctx.send('Partie terminée')

    def take(self, drinkers):
        message = ''
        if len(drinkers) == 1:
            message += '{} tu prends {}'.format(drinkers[0], self.gegor())
        else:
            message += '{} vous prennez {}'.format(', '.join(drinkers), self.gegor())
        return message

    def give(self, drinkers):
        message = ''
        if len(drinkers) == 1:
            message += '{} tu donnes {}'.format(drinkers[0], self.gegor())
        else:
            message += '{} vous donnez {}'.format(', '.join(drinkers), self.gegor())
        return message

    def find_drinkers(self, new_card):
        drinkers = []
        for player in self.players:
            for card in player.cards:
                if new_card.number == card.number:
                    drinkers.append(player.name)
                    break
        return drinkers

    async def next_player(self, ctx):
        if self.is_last_player():
            self.turn = next(self.turn_iter)
            if self.turn == Turn.DRAW:
                await ctx.send('Fin de tirage, tout le monde a ses cartes')
                message = ''
                for player in self.players:
                    emojis = []
                    for card in player.cards:
                        emojis.append(print_card(ctx, card))
                    message += player.name + ': ' + ' '.join(emojis) + '\n'
                await ctx.send(message)
                return
            else:
                self.currentPlayer = 0
        else:
            self.currentPlayer += 1
        await self.ask_card(ctx)

    def is_last_player(self):
        return self.currentPlayer == len(self.players) - 1

    def good_player(self, author):
        player = self.players[self.currentPlayer]
        print(author.name != player.name)
        if author.name != player.name:
            return False
        else:
            return True

    def draw_card(self):
        card_number = len(self.cards)
        if card_number == 0:
            return None
        index = random.randint(0, card_number) - 1
        return self.cards.pop(index)

    def gegor(self):
        if self.drink == 1:
            message = '{} gorgée'.format(self.drink)
        elif self.drink == 6:
            message = 'un cul sec'
        else:
            message = '{} gorgées'.format(self.drink)
        return message
