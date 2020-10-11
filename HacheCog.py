from enum import IntEnum

from discord.ext import commands

from hache import Hache, start_game


class State(IntEnum):
    NOT_STARTED = 0
    SIGNIN = 10
    STARTED = 20
    ENDED = 30


class HacheCog(commands.Cog):
    def __init__(self, bot):
        self.players = None
        self.master = None
        self.bot = bot
        self.hache = Hache()
        self.state = State.NOT_STARTED
        self.channel = None
        print('Bot started')

    @commands.command()
    async def start(self, ctx):
        if self.state == State.SIGNIN:
            await ctx.send('Les inscriptions sont en cours')
        elif self.state == State.STARTED:
            await ctx.send('Une partie est en cours')
        else:
            self.channel = ctx.message.channel.name
            self.state = State.SIGNIN
            self.players = []
            self.master = ctx.message.author.name
            await ctx.send('```!join pour jouer ```')

    @commands.command()
    async def join(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.SIGNIN:
            return
        player = ctx.message.author.name
        if len(self.players) >= 10:
            await ctx.send('Plus de places disponnibles, 10 joueurs max')
            return
        if player not in self.players:
            self.players.append(player)

    @commands.command()
    async def go(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if len(self.players) < 1:
            await ctx.send("Personne n\'est inscrit")
        else:
            self.state = State.STARTED
            self.master = ctx.message.author.name
            await ctx.send(
                "C'est parti mon kiki\nMaitre du jeu {}\nJoueurs: {}".format(self.master, ', '.join(self.players)))
            self.hache = start_game(self.players)
            await self.hache.ask_card(ctx)

    @commands.command()
    async def rouge(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.first_turn(ctx, 'rouge')

    @commands.command()
    async def noir(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.first_turn(ctx, 'noir')

    @commands.command(aliases=['+'])
    async def plus(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.second_turn(ctx, '+')

    @commands.command(aliases=['-'])
    async def moins(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.second_turn(ctx, '-')

    @commands.command(aliases=['='])
    async def egalite(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.third_turn(ctx, '=')
        await self.hache.second_turn(ctx, '=')

    @commands.command()
    async def inter(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.third_turn(ctx, 'inter')

    @commands.command()
    async def exter(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.third_turn(ctx, 'exter')

    @commands.command()
    async def pique(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.fourth_turn(ctx, 'pique')

    @commands.command()
    async def carreau(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.fourth_turn(ctx, 'carreau')

    @commands.command()
    async def trefle(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.fourth_turn(ctx, 'trefle')

    @commands.command()
    async def coeur(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            return
        await self.hache.fourth_turn(ctx, 'coeur')

    @commands.command(name='tire')
    async def tire(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if self.state != State.STARTED:
            await ctx.send('La partie n\'est pas commencée')
            return
        elif ctx.message.author.name != self.master:
            await ctx.send('Seul le maitre du jeu peut découvrir une carte')
        else:
            if len(self.hache.cards) == 0:
                await ctx.send('Plus de carte disponnible fin du H')
                self.state = State.ENDED
                self.hache = None
                return
            await self.hache.tire(ctx)
            if self.hache.drinkTurn == 13:
                self.state = State.ENDED
                self.hache = None

    @commands.command(name='stop')
    async def stop(self, ctx):
        if self.channel != ctx.message.channel.name:
            return
        if ctx.message.author.name != self.master:
            message = '{} t\'es pas le maitre du jeu sac à foutre.'.format(ctx.message.author.name)
        elif self.state == State.NOT_STARTED or self.state == State.ENDED:
            message = 'Pas de partie en cours, commencer une nouvelle partie avec !start'
        else:
            self.state = State.ENDED
            self.hache = None
            message = 'Partie terminée'
        await ctx.send(message)
