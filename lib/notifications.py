import discord
import lib.utilities as utilities
from lib.models import ConfigOption

class Notifications():
    def __init__(self, config):
        self.config = config

    def build_stats(player):
        utilities.dlog("Building stats embed")
        embed = discord.Embed(title=" ".join(['Stats for', player.name]), color=0x00ff00)
        embed.add_field(name="KD", value=player.kd, inline=True)
        embed.add_field(name="Wins", value=player.wins, inline=True)
        embed.add_field(name="Kills", value=player.kills, inline=True)
        embed.add_field(name="Rounds", value=player.roundsPlayed, inline=True)
        embed.add_field(name="Longest Kill", value=str(round(player.longestKill)) + "m", inline=True)
        embed.add_field(name="Team Kills", value=player.teamKills, inline=True)
        embed.add_field(name="Season playtime", value=str(round(player.timeSurvived / 60 / 60)) + " hours", inline=True)
        embed.add_field(name="Top 10", value=str(round((player.top10s / player.roundsPlayed) * 100.0)) + "%", inline=True)
        embed.add_field(name="Headshots", value=str(round((player.headshotKills / player.kills) * 100.0)) + "%", inline=True)
        return embed

    def build_match(self, match, members):
        if match == None:
            return
        elif match['roster'].won:
            roster = match['roster']
            url = utilities.get_match_telemetry_link(match)

            embed = discord.Embed(title=" ".join(["Chicken Dinner With", str(roster.total_kills), "Kills"]), url=url, color=0x00ff00)

            for participant in roster.participants:
                member = utilities.get_member(members, participant.name)
                mention = "**" + participant.name + "**"
                if member:
                    mention = member.mention
                embed.add_field(name="Player Overview", value=" ".join([mention, "\n", str(participant.stats.kills), "kills\n", str(participant.stats.DBNOs), "DBNOs\n", str(round(participant.stats.damageDealt)), "damage\n", str(participant.stats.headshotKills), "headshots\n", str(round(participant.stats.timeSurvived / 60)), "minutes alive"]), inline=True)

            if match['match'].isCustomMatch:
                embed.set_footer(text=" ".join(["Custom Match -", utilities.get_map_name(match['match'].mapName), "- PUBG-BOT"]))
            else:
                embed.set_footer(text=" ".join(["Regular Match -", utilities.get_map_name(match['match'].mapName), "- PUBG-BOT"]))

            utilities.dlog("Building chicken dinner embed")

            return {
                "embeds": [embed],
                "type": ConfigOption.notification_channel_win
            }
        elif match['roster'].rank <= self.config.MIN_RANK:
            roster = match['roster']
            url = utilities.get_match_telemetry_link(match)

            embed = discord.Embed(title=" ".join(["Ranked #" + str(roster.rank), "With", str(roster.total_kills), "Kills"]), url=url, color=0x00ff00)

            for participant in roster.participants:
                member = utilities.get_member(members, participant.name)
                mention = "**" + participant.name + "**"
                if member:
                    mention = member.mention
                embed.add_field(name="Player Overview", value=" ".join([mention, "\n", str(participant.stats.kills), "kills\n", str(participant.stats.DBNOs), "DBNOs\n", str(round(participant.stats.damageDealt)), "damage\n", str(participant.stats.headshotKills), "headshots\n", str(round(participant.stats.timeSurvived / 60)), "minutes alive"]), inline=True)

            if match['match'].isCustomMatch:
                embed.set_footer(text=" ".join(["Custom Match -", utilities.get_map_name(match['match'].mapName), "- PUBG-BOT"]))
            else:
                embed.set_footer(text=" ".join(["Regular Match -", utilities.get_map_name(match['match'].mapName), "- PUBG-BOT"]))

            utilities.dlog("Building high rank embed")

            return {
                "embeds": [embed],
                "type": ConfigOption.notification_channel_high_rank
            }
        else:
            return None

    def build_stream(self, twitch_reports, time_limit):
        embeds = []

        for key, player in twitch_reports.items():
            report_amount = len(player['reports'])

            utilities.dlog("Building stream report embed")
            if report_amount == 1:
                report = player['reports'][0]
                link = "".join(["https://pubg.report/streams/", report['MatchID'], "/", str(report['AttackID'])])
                embed = discord.Embed(title="PUBG Report", url=link, color=0x00ff00)
                embed.add_field(name=" ".join([report['Killer'], "has been streamed killing", report['Victim']]), value="Weapon: WeapG36C_C", inline=True)
                embeds.append(embed)
            elif report_amount > 1:
                link = "".join(["https://pubg.report/streams/", player['id'], "/"])
                embed = discord.Embed(title="PUBG Report", url=link, color=0x00ff00)
                embed.add_field(name=" ".join([player['name'], "has", str(report_amount), "new reports in the last", str(time_limit), "days"]), value=" ".join([str(player['knocks']), "knocks and", str(player['downs']), "downs"]), inline=True)
                embed.set_footer(text="PUBG-BOT")
                embeds.append(embed)

        if len(embeds) > 0:
            return {
                "embeds": embeds,
                "type": ConfigOption.notification_channel_stream_report
            }
        else:
            return None
