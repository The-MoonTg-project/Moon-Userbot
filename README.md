# 🌕 Moon-Userbot

![Moon-Userbot](https://telegra.ph/file/0c37c2fb0f194cc1c0344.jpg)

[![Open Source Love](https://badges.frapsoft.com/os/v2/open-source.png?v=103)](https://github.com/The-MoonTg-project/Moon-Userbot)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-Yes-green)](https://github.com/The-MoonTg-project/Moon-Userbot/graphs/commit-activity)
[![CodeFactor](https://www.codefactor.io/repository/github/the-moontg-project/moon-userbot/badge)](https://www.codefactor.io/repository/github/the-moontg-project/moon-userbot)
[![DeepSource](https://app.deepsource.com/gh/The-MoonTg-project/Moon-Userbot.svg/?label=resolved+issues&show_trend=true&token=OOvfC-BCIsHOvBpsGHc_osHs)](https://app.deepsource.com/gh/The-MoonTg-project/Moon-Userbot/)
[![GitHub Forks](https://img.shields.io/github/forks/The-MoonTg-project/Moon-Userbot?&logo=github)](https://github.com/The-MoonTg-project/Moon-Userbot)
[![GitHub Stars](https://img.shields.io/github/stars/The-MoonTg-project/Moon-Userbot?&logo=github)](https://github.com/The-MoonTg-project/Moon-Userbot/stargazers)
[![Last commit](https://img.shields.io/github/last-commit/The-MoonTg-project/Moon-Userbot?&logo=github)](https://github.com/The-MoonTg-project/Moon-Userbot)
[![Size](https://img.shields.io/github/repo-size/The-MoonTg-project/Moon-Userbot?color=green)](https://github.com/The-MoonTg-project/Moon-Userbot)
[![Contributors](https://img.shields.io/github/contributors/The-MoonTg-project/Moon-Userbot?color=green)](https://github.com/The-MoonTg-project/Moon-Userbot/graphs/contributors)
[![License](https://img.shields.io/badge/License-GPL-pink)](https://github.com/The-MoonTg-project/Moon-Userbot/blob/main/LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://makeapullrequest.com)



***A Simple, Fast, Customizable, Ai powered Userbot for Telegram made after Dragon-Userbot abandoned***

> [!WARNING]
> The use of this Telegram Userbot is at your own risk, and you are solely responsible for any consequences that may arise from your use of this Userbot. The developer of this Userbot shall not be held liable for any damages or consequences that may occur as a result of your use of this software, whether such use is lawful, unlawful, or malicious. By using this Userbot, you acknowledge that you have read and understood this warning, and that you agree to comply with all applicable laws and regulations, and to use this software responsibly and ethically.

## 🤖 Ai powers

- Gemini Pro Ai [ ✅ ]
  - Ask/Chat with Ai
  - Get details from image
  - Cooking instructions
  - Ai Marketer
- Cohere Coral Ai [ ✅ ]
  - Ask/Chat with Ai
  - UP-TO Date Info
  - Site-Search Support
  - Chat History Support
- ChatGPT 3.5 Turbo [ ✅ ]
  - Ask/Chat with Ai
- SDXL [ ✅ ]
- DALL-E 3 [ ✅ ]
- Upscaling [✅]
- Text to Image [✅]

## 🚀 Installation

### 🏕️ Necessary Vars
 
 - `API_ID` - Get it from [my.telegram.org](https://my.telegram.org/)
 - `API_HASH` - Get it from [my.telegram.org](https://my.telegram.org/)
 - `PM_LIMIT` - set your pm permit warn limit
 - `DATABASE_URL` - ONLY for MongoDB, your mongodb url
 - `DATABASE_NAME` - set to `db.sqlite3` if want to use sqlite3 db else leave blank
 - `DATABASE_TYPE` - set to `sqlite3` if want to use sqlite3 db else leave blank

### ⛺ Optional Vars
 
 - `STRINGSESSION`
     - only If you want to use on cloud hosts use [string_gen.py](https://github.com/The-MoonTg-project/Moon-Userbot/blob/main/string_gen.py) to generate OR
[![Run on Repl.it](https://replit.com/badge)](https://replit.com/@ABHITHEMODDER/MoonUb-Session-Gen)
> [!IMPORTANT]
> `STRINGSESSION` is necessary for deployment through Docker/Cloud Host etc.
 
 - `APIFLASH_KEY` - ONLY,  If you want to use web screnshot plugin You can get it from [here](https://apiflash.com/dashboard/access_keys)
 
 - `RMBG_KEY` - ONLY, If you want to use removbg plugin You can get it from [here](https://www.remove.bg/dashboard#api-key)
 
 - `VT_KEY` - ONLY, If you want to use VirusTotal plugin You can get it from [here](https://www.virustotal.com/gui/)
 
 - `GEMINI_KEY` - ONLY, If you want to use gemini ai plugin You can get it from [here](https://makersuite.google.com/app/apikey)

- `COHERE_KEY` - ONLY, If you want to use cohere ai plugin You can get it from [here](https://dashboard.cohere.com/api-keys)

- `VCA_API_KEY` - ONLY, If you want to use ai tools like sdxl,upscale plugin You can get it from [here](https://github.com/VisionCraft-org/VisionCraft?tab=readme-ov-file#obtaining-an-api-key)

## ☁️ Cloud Host
| Koyeb | Heroku | Render |
|-------|--------|--------|
| [![Deploy To Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/The-MoonTg-project/Moon-Userbot&branch=main&name=moonub) | [![Deploy To Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy?template=https://github.com/The-MoonTg-project/moonub-cloud) | [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/The-MoonTg-project/Moon-Userbot) |

 
- **YT Video [How to deploy on Koyeb]**: <https://youtu.be/2m_yB7EllYc>

**For Detailed Guide refer to [wiki](https://github.com/The-MoonTg-project/Moon-Userbot/wiki/Installation#koyeb-free)**

## 🐳 Docker

You can either use `docker run` or `docker compose`.

## Prerequisites

- Docker
- Docker Compose (version 1.x for `docker-compose.yml`, version 2.x for `compose.yml`)
- Put your environment vars in `.env` file check [.env.dist](/.env.dist) for example format

### 👷‍♂️`docker run`:
We also push images to [Docker Hub](https://hub.docker.com/), so you can use the following commands to start and update the service:

  - Start:
    1. If you want to use normal image:
    ```shell
    docker run --env-file ./.env -d qbtaumai/moonuserbot:latest
    ```
    2. If you want to use image with flask web (only recommended for heroku/koyeb/render etc.):
    ```shell
    docker run --env-file ./.env -d qbtaumai/moonubcloud:latest-cloud
    ```
  - Updating:
    ```shell
    docker stop $(docker ps -q)
    ```
    then re-run the start command

### 🍟 `docker compose` [recommended]:

#### Docker Compose V1 (`docker-compose.yml`):
If you're using Docker Compose version 1.x, use the following commands to start and update the service:
  - Start:
    ```shell
    docker-compose -f docker-compose.yml up -d
    ```
  - Updating & running:
    ```shell
    docker-compose -f docker-compose.yml down && docker-compose -f docker-compose.yml pull && docker-compose -f docker-compose.yml up -d
    ```

#### Docker Compose V2 (`compose.yml`):
If you're using Docker Compose version 2.x, use the following commands to start and update the service:
  - Start:
    ```shell
    docker compose -f compose.yml up -d
    ```
  - Updating & running:
    ```shell
    docker compose -f compose.yml down && docker compose -f compose.yml pull && docker compose -f compose.yml up -d
    ```

> [!IMPORTANT]
> Make Sure you add appropriate env vars

## 🖥️ Local Host
## 🐧 Linux (WSL compatible)

### Install Git
There are instructions for installing on several different Unix distributions on the Git website, at https://git-scm.com/download/linux

### Clone the repo

```shell
git clone https://github.com/The-MoonTg-project/Moon-Userbot.git
```

### Installation

```shell
cd Moon-Userbot 
chmod +x install.sh
./install.sh
```

**Installer tested on:**
- Arch
- Debian
- Ubuntu
- WSL (APT based distros)

Feel free to test on other distros and let us know!

#### 📱 Termux 
> [!TIP]
> Use [GitHub](https://github.com/termux/termux-app/releases) version
-------------------------------------------------------------------------------

> **Full Installation instruction [Given here](https://telegra.ph/Moon-Userbot-Installation---Termux-02-09)**

> [!NOTE]
> If you choose MongoDB for your cloud then you need to setup `mongo_db_url`**

**Recommended: `sqlite`**

### 🐩 Contributions

Contributions of any type are welcome like `custom_modules` etc. Feel free to do pull-request's with your changes!

**Working on your first Pull Request?** You can learn how from this _free_ series [How to Contribute to an Open Source Project on GitHub](https://kcd.im/pull-request)

## 👨🏻‍💻 Support
* [Channel](https://t.me/moonuserbot) with latest news on the official telegram \[en\]
* [Modules Channel](https://t.me/moonub_modules) with custom modules \[en\]
* [Discussion](https://t.me/moonub_chat) in the official telegram chat \[en\]


## 👨🏻‍💼 Credits
* [Dragon-Userbot](https://github.com/Dragon-Userbot/Dragon-Userbot)
* [AbhiTheModder](https://github.com/AbhiTheModder)
 
### Written on [Pyrogram\[Pyrofork\]❤️](https://github.com/Mayuri-Chan/pyrofork) and [pytgcalls❤️](https://github.com/MarshalX/tgcalls/tree/main/pytgcalls)

## Disclaimer 
> [!WARNING]
> The use of this Telegram Userbot is entirely at your own risk. The developer of this Userbot is not responsible for any misuse, damage, or legal consequences that may arise from your use of this software.
>> It is your responsibility to ensure that you use this Userbot in accordance with all applicable laws and regulations, and that you do not engage in any activities that may cause harm to others or violate their privacy. This includes, but is not limited to, the use of this Userbot to send spam, harass others, or engage in any other form of unlawful or malicious activity.
>> The developer of this Userbot does not endorse or condone any such activities, and any such use of this software is strictly prohibited. By using this Userbot, you acknowledge that you are solely responsible for your own actions and that the developer of this Userbot shall not be held liable for any damages or consequences that may arise from your use of this software.
>> It is your responsibility to ensure that you have obtained all necessary permissions and consents before using this Userbot to interact with others, and that you respect their privacy and rights. The developer of this Userbot shall not be held liable for any breach of privacy or rights that may occur as a result of your use of this software.

## Licence

```plaintext
                    GNU GENERAL PUBLIC LICENSE
                        Version 3, 29 June 2007

  Copyright (C) 2007 Free Software Foundation, Inc. <https://fsf.org/>
  Everyone is permitted to copy and distribute verbatim copies
  of this license document, but changing it is not allowed.

                             Preamble

   The GNU General Public License is a free, copyleft license for
 software and other kinds of works.
```
