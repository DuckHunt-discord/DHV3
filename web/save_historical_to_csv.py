import os
import urllib.request
import json


def add_to_csv(file_name, values, columns):
    with open(file_name, "a") as f:
        if os.stat(file_name).st_size == 0:
            f.write(",".join(columns) + "\n")

        f.write(",".join(map(str, values)) + "\n")


def get_from_api(endpoint):
    with urllib.request.urlopen("http://duckhunt.api-d.com:6872/" + endpoint) as url:
        return json.loads(url.read().decode())


add_to_csv("user_count.csv", get_from_api("user_count"), ["time", "users"])
add_to_csv("guild_count.csv", get_from_api("guild_count"), ["time", "guilds"])
add_to_csv("enabled_channels_count.csv", get_from_api("enabled_channels_count"), ["time", "channels"])
add_to_csv("memory_usage.csv", get_from_api("memory_usage"), ["time", "memory_used"])
add_to_csv("latency.csv", get_from_api("latency"), ["time", "latency", "discord_ping"])
