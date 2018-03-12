import json
import records

# User used to connect to the Mysql DB
from tqdm import tqdm

database_user = "duckhunt"

# Password for the user used to connect to the Mysql DB
database_password = "duckhunt"

# Name of the table used in the Mysql DB
database_name = "duckhunt"

# Name of the table used in the Mysql DB
database_address = "localhost"

# Name of the table used in the Mysql DB
database_port = 3306

database = records.Database(f'mysql://{database_user}:{database_password}'
                            f'@{database_address}:{database_port}'
                            f'/{database_name}?charset=utf8mb4')

with open("channels.json", "r") as f:
    to_import = json.load(f)

tr = database.transaction()

print("Starting")

for server_id in tqdm(to_import.keys()):
    server = to_import[server_id]
    if "admins" in server.keys():
        for admin in list(set(server["admins"])):
            #print(f"Add admin : {server_id}, {admin}")
            database.query("INSERT INTO admins (server_id, user_id) VALUES (:server_id, :user_id)", server_id=server_id, user_id=admin)

    if "settings" in server.keys():
        for setting in server["settings"].keys():

            if not setting in ["interactive_topscores_enabled", "global_scores", "pm_top"]: # Deleted settings
                value = server["settings"][setting]

                if setting == "language" and value.startswith("fr"):
                    value = "fr_FR"

                elif setting == "language" and value.startswith("en"):
                    value = "en_EN"

                #print(f"Add setting : {server_id}, {setting}->{value}")
                database.query(f"INSERT INTO prefs (server_id, {setting}) VALUES (:server_id, :value)"
                               f"ON DUPLICATE KEY UPDATE {setting}=:value",
                               server_id=server_id, value=value)



    else:
        database.query(f"INSERT INTO prefs (server_id) VALUES (:server_id)",
                       server_id=server_id)



    if "channels" in server.keys() and server["channels"] != []:
        if "settings" in server.keys() and "global_scores" in server["settings"].keys() and server["settings"]["global_scores"]:
            if len(server["channels"]) != 1:
                print(f"'Loosing' data for server {server_id}")

            channel_id = server["channels"][0]
            database.query("DELETE FROM channels WHERE channel = :channel_id AND server=:server_id;",
                           channel_id=channel_id, server_id=server_id)

            database.query("UPDATE channels SET channel = :channel_id WHERE server=:server_id AND channel=0",
                           channel_id=channel_id, server_id=server_id)
        else:
            for channel_id in server["channels"]:
                #print(f"Add channel : {server_id}, {channel_id}")
                database.query("INSERT INTO channels (server, channel, enabled) VALUES (:server_id, :channel_id, 0) "
                               "ON DUPLICATE KEY UPDATE enabled=1", server_id=server_id, channel_id=channel_id)



tr.commit()

print("Done")