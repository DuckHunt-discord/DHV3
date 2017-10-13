# Self-Hosting the bot

**DISCLAIMER: THE BOT IS NOT EXPLICITLY BUILT FOR SELF-HOSTING. IF YOU RUN INTO ISSUES, ONLY LIMITED SUPPORT WILL BE AVAILABLE.**

# Requirements

 - Python 3.5 / 3.6
 - MySQL Server
 - git

Additionally, the bot has only been tested on Linux.

# Installation

## Bot

1. Clone the repository using `git clone https://github.com/DuckHunt-discord/DHV2.git DuckHunt`
2. Navigate into the source folder using `cd DuckHunt`
3. Install the dependencies using `python3 -m pip install -r requirements.txt`

## MySQL

1. Create a User and a Database for DuckHunt. 
2. Run the following SQL queries to create the necessary data structure: https://hastebin.com/uhetaxozel.sql

# Configuration

To configure the bot, you will need to edit two files.

- Create a `credentials.json` file in the application root folder.  
Content:  
```
{
   "token": "BOT_TOKEN",
   "client_id": "BOT ID",
   "bots_key": "API KEY FOR DISCORD BOTS",
   "mysql_user": "SQL USERNAME",
   "mysql_pass": "SQL PASSWORD",
   "mysql_host": "SQL CONNECTION URL",
   "mysql_port": "SQL SERVER PORT",
   "mysql_db": "SQL DB NAME"    
}
```

- Open the file `cogs/util/checks.py` and set the Owner ID to your User ID.

At the time of writing this there is an issue with the bot 
where it will disconnect from the SQL Server if nobody uses it for 8 hours. 
You can fix this by adding `?autoReconnect=true` to the SQL Host parameter.

# Running the bot

Once you have everything set up you can run the bot with `python3 bot.py`.

If you need to be able to close the shell afterwards, you can run the bot using `nohup python3 bot.py &`.
This will automatically save log output to `nohup.out`.