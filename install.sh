#!/bin/bash
PACKAGE_MANAGER=""

# Ensure the script is run with root privileges
if [[ $UID != 0 ]]; then
  echo "This script requires root privileges."
  echo "Please enter the root password to continue."
  exec sudo "$0" "$@"
else
  echo "Running with root privileges"
fi

# Detect available package manager
if command -v apt &>/dev/null; then
  PACKAGE_MANAGER="apt"
elif command -v apk &>/dev/null; then
  PACKAGE_MANAGER="apk"
elif command -v yum &>/dev/null; then
  PACKAGE_MANAGER="yum"
elif command -v pacman &>/dev/null; then
  PACKAGE_MANAGER="pacman"
else
  echo "Unsupported package manager. Please use a compatible distribution or update the installer script."
  exit 1
fi

if command -v termux-setup-storage; then
  echo "For termux, please use https://raw.githubusercontent.com/The-MoonTg-project/Moon-Userbot/main/termux-install.sh"
  exit 1
fi

# Install necessary packages based on detected package manager
case "$PACKAGE_MANAGER" in
  apt)
    apt update -y
    apt install python3 python3-venv git wget -y || exit 2
    ;;
  apk)
    apk update
    apk add python3 py3-virtualenv git wget || exit 2 # Packages here may be wrong, to verify
    ;;
  yum)
    yum update -y
    yum install python3 python3-venv git wget -y || exit 2 # Packages here may be wrong, to verify
    ;;
  pacman)
    pacman -S --noconfirm python python-virtualenv git wget || exit 2
    ;;
esac

# Clone repository if not exists
if [[ -d "Moon-Userbot" && "$(basename "$PWD")" != "Moon-Userbot" ]]; then
  cd Moon-Userbot || exit 2
elif [[ "$(basename "$PWD")" == "Moon-Userbot" ]]; then
  echo "Already in the correct repo, moving on."
else
  git clone https://github.com/The-MoonTg-project/Moon-Userbot || exit 2
  cd Moon-Userbot || exit 2
fi

if [[ -f ".env" ]] && [[ -f "my_account.session" ]]; then
  echo "It seems that Moon-Userbot is already installed. Exiting..."
  exit
fi
# Create a virtual environment inside the cloned repository and activate it
python3 -m venv venv
source venv/bin/activate

# Upgrade pip and install wheel and pillow
pip install -U pip wheel pillow

# Install Python requirements
pip install -U -r requirements.txt || exit 2
# Prompt for API_ID and API_HASH
echo
echo "Enter API_ID and API_HASH"
echo "You can get it here -> https://my.telegram.org/"
echo "Leave empty to use defaults (please note that using default keys is a **very bad idea** and significantly increases your ban chances)"
read -r -p "API_ID > " api_id

# Default API_ID and API_HASH
if [[ $api_id = "" ]]; then
  echo "You have chosen to use the default API_ID and API_HASH, which is strongly discouraged."
  echo "Please type 'I agree' to confirm that you understand the risks and still wish to proceed."
  read -r -p "Confirmation > " confirmation
  if [[ $confirmation = "I agree" ]]; then
    api_id="2040"
    api_hash="b18441a1ff607e10a989891a5462e627"
  else
    echo "Confirmation not provided. Exiting..."
    exit 1
  fi
else
  read -r -p "API_HASH > " api_hash
fi
# Prompt for PM PERMIT warn limit
# PM PERMIT warn limit is the number of messages a user can receive from others before giving them a warning
echo
echo "SET PM PERMIT warn limit"
#Now below is more clear version:
echo "Enter the number of messages others can send you before receiving a warning, and eventually a ban or leave empty for default (3)"
read -r -p "PM_LIMIT warn limit > " pm_limit

if [[ $pm_limit = "" ]]; then
  pm_limit="3"
  echo "Limit not provided by user; set to default"
fi

# Prompt for musicbot usage
echo
echo "Do you want to use musicbot? (y/N)"
read -r -p "MUSIC_BOT > " musicbot
if [[ $musicbot = "y" ]]; then
  echo
  echo "Enter SECOND_SESSION_STRING to be used by musicbot"
  read -r -p "SECOND_SESSION > " second_session
  if [[ $second_session = "" ]]; then
    echo "SECOND_SESSION not provided by user"
    second_session=""
  else
    echo
    echo "Please provide handler to be used by musicbot"
    read -r -p "MUSIC_HANDLER > " music_handler
    if [[ $music_handler = "" ]]; then
      echo "MUSIC_HANDLER not provided by user"
      music_handler=""
    fi
  fi
fi

# Prompt for various API keys
echo "Enter APIFLASH_KEY for webshot plugin"
echo "You can get it here -> https://apiflash.com/dashboard/access_keys"
read -r -p "APIFLASH_KEY > " apiflash_key

if [[ $apiflash_key = "" ]]; then
  echo "NOTE: API Not set; you'll get errors with webshot & ws module"
fi

echo
echo "Enter RMBG_KEY for remove background module"
echo "You can get it here -> https://www.remove.bg/dashboard#api-key"
read -r -p "RMBG_KEY > " rmbg_key

if [[ $rmbg_key = "" ]]; then
  echo "NOTE: API Not set; you'll not be able to use remove background modules"
fi

echo
echo "Enter VT_KEY for VirusTotal"
echo "You can get it here -> https://www.virustotal.com/"
read -r -p "VT_KEY > " vt_key

if [[ $vt_key = "" ]]; then
  echo "NOTE: API Not set; you'll not be able to use VirusTotal module"
fi

echo
echo "Enter GEMINI_KEY if you want to use AI"
echo "You can get it here -> https://makersuite.google.com/app/apikey"
read -r -p "GEMINI_KEY > " gemini_key

if [[ $gemini_key = "" ]]; then
  echo "NOTE: API Not set; you'll not be able to use Gemini AI modules"
fi

echo
echo "Enter COHERE_KEY if you want to use AI"
echo "You can get it here -> https://dashboard.cohere.com/api-keys"
read -r -p "COHERE_KEY > " cohere_key

if [[ $cohere_key = "" ]]; then
  echo "NOTE: API Not set; you'll not be able to use Coral AI modules"
fi

echo
echo "Enter VCA_API_KEY for aiutils"
echo "Learn How to Get One --> https://github.com/VisionCraft-org/VisionCraft?tab=readme-ov-file#obtaining-an-api-key"
read -r -p "VCA_API_KEY > " vca_api_key

if [[ $vca_api_key = "" ]]; then
  echo "NOTE: API Not set; you'll not be able to use aiutils module/plugins"
fi


echo
while true; do
  # Prompt for database type and database URL if MongoDB is selected
  echo
  echo "Choose database type:"
  echo "[1] MongoDB db_url"
  echo "[2] MongoDB localhost"
  echo "[3] Sqlite (default)"
  read -r -p "> " db_type

  case $db_type in
    1)
      echo "Please enter db_url"
      echo "You can get it here -> https://mongodb.com/atlas"
      read -r -p "> " db_url
      db_name=Moon_Userbot
      db_type=mongodb
      break
      ;;
    2)
      if ! command -v apt &>/dev/null; then
        echo "This option requires apt package manager, which is not available on your system."
        echo "Please choose a different database type."
        continue
      fi

      if systemctl status mongodb; then
        wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
        source /etc/os-release
        echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu ${UBUNTU_CODENAME}/mongodb-org/5.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
        apt update
        apt install mongodb -y
        systemctl daemon-reload
        systemctl enable mongodb
      fi
      systemctl start mongodb

      db_url=mongodb://localhost:27017
      db_name=Moon_Userbot
      db_type=mongodb
      break
      ;;
    *)
      db_name=db.sqlite3
      db_type=sqlite3
      break
      ;;
    *)
      echo "Invalid choice!"
      ;;
  esac
done

# Generate .env file with collected variables
cat > .env << EOL
API_ID=${api_id}
API_HASH=${api_hash}
STRINGSESSION=
# sqlite/sqlite3 or mongo/mongodb
DATABASE_TYPE=${db_type}
# file name for sqlite3, database name for mongodb
DATABASE_NAME=${db_name}
# only for mongodb
DATABASE_URL=${db_url}
APIFLASH_KEY=${apiflash_key}
RMBG_KEY=${rmbg_key}
VT_KEY=${vt_key}
GEMINI_KEY=${gemini_key}
VCA_API_KEY=${vca_api_key}
COHERE_KEY=${cohere_key}
PM_LIMIT=${pm_limit}
SECOND_SESSION=${second_session}
MUSIC_HANDLER=${music_handler}
EOL

# Adjust the ownership of the Moon-Userbot directory
chown -R $SUDO_USER:$SUDO_USER .



su -c "python3 install.py ${install_type}" $SUDO_USER || exit 3

# Configure the bot based on selected installation type
while true; do
  # Prompt for installation type and execute accordingly
  echo
  echo "Choose installation type:"
  echo "[1] PM2"
  echo "[2] Systemd service"
  echo "[3] Custom (default)"
  read -r -p "> " install_type

  case $install_type in
    1)
      if ! command -v apt &>/dev/null; then
        echo "This option requires apt package manager, which is not available on your system."
        echo "Please choose a different installation type."
        continue
      fi

      if ! command -v pm2 &>/dev/null; then
        curl -fsSL https://deb.nodesource.com/setup_17.x | bash
        apt install nodejs -y
        npm install pm2 -g
        su -c "pm2 startup" $SUDO_USER
        env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u $SUDO_USER --hp /home/$SUDO_USER
      fi
      su -c "pm2 start main.py --name Moon --interpreter python3" $SUDO_USER
      su -c "pm2 save" $SUDO_USER

      echo
      echo "============================"
      echo "Great! Moon-Userbot installed successfully and running now!"
      echo "Installation type: PM2"
      echo "Start with: \"pm2 start Moon\""
      echo "Stop with: \"pm2 stop Moon\""
      echo "Process name: Moon"
      echo "============================"
      break
      ;;
    2)
      cat > /etc/systemd/system/Moon.service << EOL
[Unit]
Description=Service for Moon Userbot
[Service]
Type=simple
ExecStart=$(which python3) ${PWD}/main.py
WorkingDirectory=${PWD}
Restart=always
User=${SUDO_USER}
Group=${SUDO_USER}
[Install]
WantedBy=multi-user.target
EOL
      systemctl daemon-reload
      systemctl start Moon
      systemctl enable Moon

      echo
      echo "============================"
      echo "Great! Moon-Userbot installed successfully and running now!"
      echo "Installation type: Systemd service"
      echo "Start with: \"sudo systemctl start Moon\""
      echo "Stop with: \"sudo systemctl stop Moon\""
      echo "============================"
      break
      ;;
    3)
      echo
      echo "============================"
      echo "Great! Moon-Userbot installed successfully!"
      echo "Installation type: Custom"
      echo "Start with: \"python3 main.py\""
      echo "============================"
      break
      ;;
    *)
      echo "Invalid choice! Please enter 1, 2, or 3."
      ;;
  esac
done

# Adjust the ownership of the Moon-Userbot directory again as a final step
chown -R $SUDO_USER:$SUDO_USER .