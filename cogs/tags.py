import asyncio
import typing

import discord
from discord.ext import commands
from discord.ext.commands.cooldowns import BucketType


class Tag(commands.Cog, description="Module related to managing tags"):
    def __init__(self, bot):
        self.bot = bot
        self.emoji = 836841762315436042

    async def cog_check(self, ctx):
        if ctx.guild:
            return True

        await ctx.send("Tags can only be used inside guilds!!")
        return False

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx):
        if not ctx.invoked_subcommand:
            await ctx.reply(
                embed=self.bot.embed(
                    description=f"Use `{ctx.prefix}tag create` to create tags \n Use `{ctx.prefix}tag list` to list all the tags",
                    colorful=False,
                )
            )

    @tag.command()
    async def show(self, ctx, query: str):
        async with self.bot.db.acquire() as conn:
            async with conn.transaction():
                data = await conn.fetchrow("SELECT * FROM tags WHERE name=$1", query)
        if data["author"] != ctx.author.id and data["public"] is False:
            return await ctx.send(
                embed=self.bot.embed(
                    description=f"This tag is not public!! Ask <@{data['author']}> for information on this"
                )
            )

        embed = self.bot.embed(description=data["content"], title=data["name"])
        embed.set_author(
            name=self.bot.get_user(data["author"]).display_name,
            icon_url=self.bot.get_user(data["author"]).avatar_url,
        )

        if data["public"] is False:
            await ctx.send(
                "The information has been dmed to as you made it a private tag..."
            )
            return await ctx.author.send(embed=embed)

        return await ctx.send(embed=embed)

    @tag.command()
    async def delete(self, ctx, query: str):
        def checkM(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author

        try:
            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    await conn.fetchrow("SELECT id FROM tags WHERE name=$1", query)
                    if not conn:
                        return await ctx.send("Tag not found!!")

                    await ctx.send(
                        "Are you Sure you want to delete this tag forever? (y/n)"
                    )
                    choice = await self.bot.wait_for("message", check=checkM)

                    if not choice == "y":
                        return await ctx.reply("Aborting")
                    else:
                        conn.execute("DELETE FROM tags WHERE name=$1", query)

        except asyncio.TimeoutError:
            return await ctx.reply("You did not respond in time")

    @commands.cooldown(1, 10, BucketType.user)
    @tag.command()
    async def create(
        self, ctx, name: typing.Optional[str], content: typing.Optional[str]
    ):
        def checkM(message: discord.Message):
            return message.channel == ctx.channel and message.author == ctx.author

        try:
            if not name:
                await ctx.send("Give me a title for the tag")
                name = await self.bot.wait_for("message", check=checkM)
                name = name.content

            await ctx.send(f"Give me the content for {name}")
            content = await self.bot.wait_for("message", check=checkM)
            content = content.content

            await ctx.send(
                f"Do you want anyone else to access the tag? reply `yes` or reply the list of users else reply `no` "
            )
            allowed_users = await self.bot.wait_for("message", check=checkM)
            public = True if allowed_users.content == "yes" else False
            allowed_users = (
                [ctx.author.id]
                if not allowed_users.mentions
                else [id.id for id in allowed_users.mentions]
            )

            async with self.bot.db.acquire() as conn:
                async with conn.transaction():
                    await conn.execute(
                        """INSERT INTO tags(author, content, allowed, name, gid, public)
                        VALUES($1, $2, $3, $4, $5);""",
                        ctx.author.id,
                        content,
                        allowed_users,
                        name,
                        ctx.guild.id,
                        public,
                    )

            await ctx.reply("The tag has been successfully added!!")

        except asyncio.TimeoutError:
            return await ctx.reply("You did not respond in time")


def setup(bot):
    bot.add_cog(Tag(bot))
