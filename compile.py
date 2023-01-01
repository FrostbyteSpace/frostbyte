# This is a prerun script for the bot #
# So far, this script does the following:
# - Checks if the bot is running on a supported version of Python (3.9+)
# - Checks requirements.txt for any missing modules
# - Checks if the bot is running on a supported OS (Windows or Linux)
# - Checks if the database provided is valid
# - Checks if the bot is running on a supported version of Discord.py (2.0.0+)
# - Checks if the locales stored are older than 7 days old, and if so, replaces them with the latest ones from the website

import sys
import os
import subprocess
import importlib

pull_url = "https://frostbyte.jackelope.gay/internal/locales/"

# Step 1 #
if sys.version_info[0] < 3 or sys.version_info[1] < 9:
    print("Python 3.9 or higher is required to run this bot.")
    sys.exit(1)
    
# Step 2 #
try:
    # As I am ripping my hair out trying to prevent this from constantly reinstalling all modules, skip this step.
    # If you want to try and fix this, go ahead.
    pass
    # # Import every module in requirements.txt, and if it fails, install it.
    # # Remove version numbers from the module names.
    
    
    # for module in open("requirements.txt").read().splitlines():
    #     try:
    #         module = module.split("==")[0]
    #         module = module.split(">=")[0]
            
    #         importlib.import_module(module)
    #     except ModuleNotFoundError as e:
    #         print(e)
    #         subprocess.check_call([sys.executable, "-m", "pip", "install", module])
except Exception as e:
    print("Unable to check requirements.txt.")
    print("Please run `pip install -r requirements.txt` to install all required modules.")

    sys.exit(1)

# Step 3 #
if os.name != "nt" and os.name != "posix":
    print(f"Your operating system ({os.name}) is not supported.")
    sys.exit(1)

# Skip step 4 for now #

# Step 5 #
try:
    import discord
    if discord.__version__ < "2.0.0":
        print(f"Your version of discord.py ({discord.__version__}) is not supported.")
        sys.exit(1)
except:
    print("Unable to check discord.py version.")
    print("Please run `pip install -r requirements.txt` to install all required modules.")
    sys.exit(1)
    
# Step 6 #
try:
    # If the skip-locale-update argument is not present, check if the locales are older than 7 days old.
    # Otherwise, skip this step.
    if "--skip-locale-update" not in sys.argv:
        import requests
        import shutil
        import time
        
        # Check if the locales folder exists #
        if os.path.exists("locale"):
            # Check if the locales folder is older than 7 days old #
            if time.time() - os.path.getmtime("locales") > 604800:
                # Download the latest locales #
                print("Downloading latest locales...")
                response = requests.get(pull_url, stream=True)
                with open("locales.zip", "wb") as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response
                    
                # Delete the old locales folder #
                shutil.rmtree("locales")
                
                # Extract the new locales folder #
                import zipfile
                with zipfile.ZipFile("locales.zip", "r") as zip_ref:
                    zip_ref.extractall()
                    
                # Delete the zip file #
                os.remove("locales.zip")
                
                print("Locales updated.")
        else:
            # Download the latest locales #
            print("Downloading locales...")
            response = requests.get(pull_url, stream=True)
            with open("locales.zip", "wb") as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
                
            # Extract the locales folder #
            import zipfile
            with zipfile.ZipFile("locales.zip", "r") as zip_ref:
                zip_ref.extractall()
                
            # Delete the zip file #
            os.remove("locales.zip")
            
            print("Locales downloaded.")
    else:
        print("Skipping locale update.")
except:
    print("Unable to download locales.")
    sys.exit(1)

sys.exit(0)