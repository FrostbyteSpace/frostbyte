# Automatic launcher of the bot.
# Handles compiling, running, restarting, updating and adding launch arguments.

# Launch Arguments #
# Merged from index.py, launcher.py and compile.py #

# --production: Launches the bot in production mode.
# --staging: Launches the bot in staging mode.
# --pre: Launches the bot in pre-release mode.
# --debug: Launches the bot in debug mode. Provides more verbal output, however, can not be used if production is enabled, as irreversible changes can be made.
# --no-database: Disables the database. This simulates a database outage.
# --no-api: Disables all external API calls. This simulates a full internet outage. 
# --gui: Launches the bot in GUI mode. Provides real-time stats, charts, etc.
# --no-gui: Prevents the bot from launching in GUI mode.
# --suppress-events: Suppresses all events. This is NOT RECOMMENDED as this suppresses the error handler.
# --force: Forces the bot to launch. This is highly unrecommended as this can cause MAJOR unstability.
# --disallow-admin: Disallows the bot from running commands with the ``is_owner()`` check. Provides extra security however means that the bot can not run easy debug commands.
# --skip-clearing-temp: Skips clearing the temp folder. 
# --force-no-compile: Forces the bot to skip compiling. 
# --force-compile: Forces the bot to compile. 
# --skip-locale-update: Skips the locale update check.



import os
import sys
import requests
import subprocess
from dotenv import load_dotenv
from termcolor import colored, cprint
load_dotenv() # Load environment variables from .env file. Use as default values.

launch_args = [] # List of launch arguments to be passed to the bot.
compile_args = [] # List of compile arguments to be passed to the compiler.

# First, check if the user has specified any override arguments for GUI or no GUI.
for arg in sys.argv:
    if arg == "--gui":
        launch_args.append("--gui")
    elif arg == "--nogui":
        launch_args.append("--nogui")
        
# If no override arguments were specified, check if the user has specified a default in the .env file.
if len(launch_args) == 0:
    if os.getenv("LAUNCH_GUI") == "true":
        launch_args.append("--gui")
    elif os.getenv("LAUNCH_GUI") == "false":
        launch_args.append("--nogui")
        
# If no override arguments or .env file arguments were specified, default to GUI, depending on the OS.
# If it is Linux, default to no GUI. Otherwise, default to GUI.
if len(launch_args) == 0:
    if sys.platform == "linux":
        launch_args.append("--nogui")
    else:
        launch_args.append("--gui")
        
# Ping e621 and mongodb to check if they are online.
# If they are not, provide a warning and ask the user if they want to continue.
# If they do, add --force alongside --no-database and --no-api to the launch arguments.
# If they do not, exit the program.
hasFailed = False
try:
    requests.get("https://e621.net")
except requests.exceptions.ConnectionError:
    print("e621 is offline. Continuing may cause errors.")
    launch_args.append("--no-api")
    hasFailed = True
try:
    requests.get("https://mongodb.com")
except pymongo.errors.ServerSelectionTimeoutError:
    print("MongoDB is offline. Continuing may cause errors.")
    launch_args.append("--no-database")
    hasFailed = True
if hasFailed:
    if input("Do you want to continue? (y/n) ").lower() == "y":
        launch_args.append("--force")
    else:
        exit()

# Check if the user has specified any override arguments for prod, staging and pre.
# If they haven't, check if the user has specified a default in the .env file.
# If they haven't for either, default to staging.
for arg in sys.argv:
    if arg == "--production":
        launch_args.append("--production")
    elif arg == "--staging":
        launch_args.append("--staging")
    elif arg == "--pre":
        launch_args.append("--pre")
    
# As there is no way that launch_args can be empty, check if the last argument is not production, staging or pre.
if launch_args[-1] != "--production" and launch_args[-1] != "--staging" and launch_args[-1] != "--pre":
    if os.getenv("DEPLOYMENT") == "production":
        launch_args.append("--production")
    elif os.getenv("DEPLOYMENT") == "staging":
        launch_args.append("--staging")
    elif os.getenv("DEPLOYMENT") == "pre":
        launch_args.append("--pre")
    else:
        launch_args.append("--staging")
        
# If debug is specified, add it to the launch arguments.
if "--debug" in sys.argv:
    launch_args.append("--debug")
    cprint("Debug mode enabled. Any debug output will be shown like this.", "cyan", "on_white")
    # If production is specified, remove it from the launch arguments. And replace it with staging.
    if "--production" in launch_args:
        launch_args.remove("--production")
        launch_args.append("--staging")
        cprint("Debug mode cannot be used in production mode. Defaulting to staging.", "red", "on_white")
    
    
# If suppress-events is specified, add it to the launch arguments.
if "--suppress-events" in sys.argv:
    launch_args.append("--suppress-events")
    
# If force is specified, add it to the launch arguments.
# Add --force-no-compile to the compile arguments.
# And warn the user that this is not recommended.
if "--force" in sys.argv:
    launch_args.append("--force")
    compile_args.append("--force-no-compile")
    cprint("Force mode enabled. Expect major unstability.", "red", "on_black")
    
# If disallow-admin is specified, add it to the launch arguments.
if "--disallow-admin" in sys.argv:
    launch_args.append("--disallow-admin")
    
# If no-database is specified, add it to the launch arguments.
if "--no-database" in sys.argv:
    launch_args.append("--no-database")
    
# If no-api is specified, add it to the launch arguments.
if "--no-api" in sys.argv:
    launch_args.append("--no-api")
    
# If force-compile is specified, add it to the compile arguments.
if "--force-compile" in sys.argv:
    compile_args.append("--force-compile")
    
# If force-no-compile is specified, add it to the compile arguments.
if "--force-no-compile" in sys.argv:
    compile_args.append("--force-no-compile")
    
# If skip-locale-update is specified, add it to the compile arguments.
if "--skip-locale-update" in sys.argv:
    compile_args.append("--skip-locale-update")
    
# Few QoL things.
# If running on --staging, add --skip-locale-update to the compile arguments.
if "--staging" in launch_args:
    compile_args.append("--skip-locale-update")

# And now, compile the bot.
# If the user has specified --force-no-compile, skip compiling.
# If exit code is 1, the bot has failed to compile.
# Provide all the compile arguments to the compiler.
if "--force-no-compile" not in compile_args:
    exit_code = subprocess.call(["\"" + sys.executable + "\"", "compile.py"] + compile_args)
    if exit_code == 1:
        cprint("Bot failed to compile. Exiting.", "red", "on_white")
        exit()

# Clear ./temp/ of all files except for README.md.
for file in os.listdir("./temp"):
    if file != "README.md":
        os.remove("./temp/" + file)


# And finally, launch the bot.
# This should pass execution to the bot.
os.system("\"" + sys.executable + "\"" + " index.py " + " ".join(launch_args))