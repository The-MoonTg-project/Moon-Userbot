#!/usr/bin/env bash

# Define color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
INPUT='\033[1;30m'
NC='\033[0m' # No Color

PACKAGE_MANAGER=""

# Ensure the script is run with root privileges
if [[ $UID != 0 ]]; then
  printf "${YELLOW}This script requires root privileges.${NC}\n" # skipcq
  printf "Please enter the root password to continue.\n"
  exec sudo "$0" "$@"
else
  printf "${YELLOW}Running with root privileges${NC}\n" # skipcq
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
  printf "${RED}Unsupported package manager. Please use a compatible distribution or update the installer script.${NC}\n" # skipcq
  exit 1
fi

if command -v termux-setup-storage; then
  printf "${RED}For termux, please use https://raw.githubusercontent.com/The-MoonTg-project/Moon-Userbot/main/termux-install.sh${NC}\n" # skipcq
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
elif [[ "$(basename "$PWD")" == "Moon-Userbot" && -f ".env.dist" && -f "main.py" && -d "modules" ]]; then
  printf "${BLUE}Already inside the Moon-Userbot repo, proceeding...${NC}\n" # skipcq
else
  git clone https://github.com/The-MoonTg-project/Moon-Userbot || exit 2
  cd Moon-Userbot || exit 2
fi

if [[ -f ".env" ]] && [[ -f "my_account.session" ]]; then
  printf "${GREEN}It seems that Moon-Userbot is already installed. Exiting...${NC}\n" # skipcq
  exit
fi

# Prompt user if they want to proceed with creating a virtual environment
printf "${YELLOW}It's recommended to use a virtual environment for Python projects.${NC}\n" # skipcq
printf "Note: If your drive resources are very limited, you might consider not creating a virtual environment, but it shouldn't be rejected otherwise unless you know what you're doing.\n"
printf "If you're unsure, it's better to create a virtual environment.\n"
printf "${INPUT}Would you like to create a virtual environment? (Y/n)${NC} > " # skipcq
read -r create_venv

if [[ "$create_venv" != "n" ]] && [[ "$create_venv" != "N" ]]; then
  # Create a virtual environment inside the cloned repository and activate it
  python3 -m venv venv
  . venv/bin/activate

  # Upgrade pip and install wheel and pillow
  pip install -U pip wheel pillow
fi

if [ -d ".venv" ]; then
  . .venv/bin/activate
elif [ -d "venv" ]; then
  . venv/bin/activate
fi

# Install Python requirements
pip install -U -r requirements.txt || exit 2
# Prompt for API_ID and API_HASH
printf "Enter API_ID and API_HASH\n"
printf "You can get it here -> https://my.telegram.org/\n"
printf "Leave empty to use defaults (please note that using default keys is a ${RED}very bad idea${NC} and significantly increases your ban chances)\n" # skipcq
read -r -p "API_ID > " api_id

# Default API_ID and API_HASH
if [[ $api_id = "" ]]; then
  printf "${RED}You have chosen to use the default API_ID and API_HASH, which is strongly discouraged.${NC}\n" # skipcq
  printf "${YELLOW}Please type${NC} '${BLUE}I agree${NC}'${YELLOW} to confirm that you understand the risks and still wish to proceed.${NC}\n" # skipcq
  read -r -p "Confirmation > " confirmation
  if [[ $confirmation = "I agree" ]]; then
    api_id="2040"
    api_hash="b18441a1ff607e10a989891a5462e627"
  else
    printf "${RED}Confirmation not provided. Exiting...${NC}\n" # skipcq
    exit 1
  fi
else
  read -r -p "API_HASH > " api_hash
fi
# Prompt for PM PERMIT warn limit
# PM PERMIT warn limit is the number of messages a user can receive from others before giving them a warning, requires `antipm` plugin to be enabled
printf "SET PM PERMIT warn limit\n"
# Now below is more clear version:
printf "The number of messages others can send you before receiving a warning, and eventually a ban or leave empty for default (3), requires antipm plugin to be enabled\n"
read -r -p "PM_LIMIT warn limit > " pm_limit

if [[ $pm_limit = "" ]]; then
  pm_limit="3"
  printf "Limit not provided by user; set to default\n"
fi

# Prompt for musicbot usage
printf "Do you want to use musicbot? (y/N)"
read -r musicbot
if [[ $musicbot = "y" ]]; then
  printf "Enter SECOND_SESSION_STRING to be used by musicbot\n"
  read -r -p "SECOND_SESSION > " second_session
  if [[ $second_session = "" ]]; then
    printf "SECOND_SESSION not provided by user\n"
    second_session=""
  fi
fi

# Prompt for various API keys
printf "Enter APIFLASH_KEY for webshot plugin\n"
printf "You can get it here -> https://apiflash.com/dashboard/access_keys\n"
read -r -p "APIFLASH_KEY > " apiflash_key

if [[ $apiflash_key = "" ]]; then
  printf "NOTE: API Not set; you'll get errors with webshot & ws module\n"
fi

printf "Enter RMBG_KEY for remove background module\n"
printf "You can get it here -> https://www.remove.bg/dashboard#api-key\n"
read -r -p "RMBG_KEY > " rmbg_key

if [[ $rmbg_key = "" ]]; then
  printf "NOTE: API Not set; you'll not be able to use remove background modules\n"
fi

printf "Enter VT_KEY for VirusTotal\n"
printf "You can get it here -> https://www.virustotal.com/\n"
read -r -p "VT_KEY > " vt_key

if [[ $vt_key = "" ]]; then
  printf "NOTE: API Not set; you'll not be able to use VirusTotal module\n"
fi

printf "Enter GEMINI_KEY if you want to use AI\n"
printf "You can get it here -> https://makersuite.google.com/app/apikey\n"
read -r -p "GEMINI_KEY > " gemini_key

if [[ $gemini_key = "" ]]; then
  printf "NOTE: API Not set; you'll not be able to use Gemini AI modules\n"
fi

printf "Enter COHERE_KEY if you want to use AI"
printf "You can get it here -> https://dashboard.cohere.com/api-keys\n"
read -r -p "COHERE_KEY > " cohere_key

if [[ $cohere_key = "" ]]; then
  printf "NOTE: API Not set; you'll not be able to use Coral AI modules\n"
fi

while true; do
  # Prompt for database type and database URL if MongoDB is selected
  printf "${YELLOW}Choose database type:${NC}\n" # skipcq
  printf "[1] MongoDB db_url\n"
  printf "[2] MongoDB localhost\n"
  printf "[3] Sqlite (default)\n"
  read -r -p "> " db_type

  case $db_type in
  1)
    printf "Please enter db_url\n"
    printf "You can get it here -> https://mongodb.com/atlas\n"
    read -r -p "> " db_url
    db_name=Moon_Userbot
    db_type=mongodb
    break
    ;;
  2)
    if ! command -v apt &>/dev/null; then
      printf "This option requires apt package manager, which is not available on your system.\n"
      printf "Please choose a different database type.\n"
      continue
    fi

    if systemctl status mongodb; then
      wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | apt-key add -
      source /etc/os-release
      printf "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu %s/mongodb-org/5.0 multiverse\n" "${UBUNTU_CODENAME}" | tee /etc/apt/sources.list.d/mongodb-org-5.0.list
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
  3)
    db_name=db.sqlite3
    db_type=sqlite3
    break
    ;;
  *)
    printf "${RED}Invalid choice!${NC}\n" # skipcq
    ;;
  esac
done

# Generate .env file with collected variables
cat >.env <<EOL
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
COHERE_KEY=${cohere_key}
PM_LIMIT=${pm_limit}
SECOND_SESSION=${second_session}
EOL

# Adjust the ownership of the Moon-Userbot directory
chown -R $SUDO_USER:$SUDO_USER .

# Configure the bot based on selected installation type
while true; do
  # Prompt for installation type and execute accordingly
  printf "${YELLOW}Choose installation type:${NC}\n" # skipcq
  printf "[1] PM2\n"
  printf "[2] Systemd service\n"
  printf "[3] Custom (default)\n"
  read -r -p "> " install_type

  case $install_type in
  1)
    if ! command -v apt &>/dev/null; then
      printf "This option requires apt package manager, which is not available on your system.\n"
      printf "Please choose a different installation type.\n"
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

    printf "${GREEN}============================\\n" # skipcq
    printf "Great! Moon-Userbot installed successfully and running now!\n"
    printf "Installation type: PM2\n"
    printf "Start with: \"pm2 start Moon\"\n"
    printf "Stop with: \"pm2 stop Moon\"\n"
    printf "Process name: Moon\n"
    printf "============================${NC}\n" # skipcq
    break
    ;;
  2)
    cat >/etc/systemd/system/Moon.service <<EOL
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

    printf "${GREEN}============================\\n" # skipcq
    printf "Great! Moon-Userbot installed successfully and running now!\n"
    printf "Installation type: Systemd service\n"
    printf "Start with: \"sudo systemctl start Moon\"\n"
    printf "Stop with: \"sudo systemctl stop Moon\"\n"
    printf "============================${NC}\n" # skipcq
    break
    ;;
  3)
    printf "${GREEN}============================\\n" # skipcq
    printf "Great! Moon-Userbot installed successfully!\n"
    printf "Installation type: Custom\n"
    printf "Start with: \"python3 main.py\"\n"
    printf "============================${NC}\n" # skipcq
    break
    ;;
  *)
    printf "Invalid choice! Please enter 1, 2, or 3."
    ;;
  esac
done

su -c "python3 install.py ${install_type}" $SUDO_USER || exit 3

# Adjust the ownership of the Moon-Userbot directory again as a final step
chown -R $SUDO_USER:$SUDO_USER .
