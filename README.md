# 👁️ Discord Logger Bot — Python

Full-coverage server activity logger with **hybrid commands** (prefix + slash `/`) and dual **public/private** log channels.

---

## 🚀 Setup

### 1. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 2. Create `.env`
```bash
cp .env.example .env
# Open .env and paste your bot token
```

### 3. Enable Privileged Intents
In [Discord Developer Portal](https://discord.com/developers/applications) → Your App → Bot:
- ✅ Server Members Intent
- ✅ Presence Intent  
- ✅ Message Content Intent

### 4. Run
```bash
python bot.py
```

---

## 📱 Running on Android (Termux)

```bash
pkg update && pkg upgrade
pkg install python
pip install -r requirements.txt
python bot.py
```

---

## ⚙️ Commands (all work as prefix AND `/` slash)

| Command | Description |
|---|---|
| `setprefix <prefix>` | Change prefix for this server |
| `setlogchannel public #ch` | Set public log channel |
| `setlogchannel private #ch` | Set private log (auto-locked) |
| `whitelist add @role/@user` | Grant private log access |
| `whitelist remove @role/@user` | Revoke private log access |
| `lockprivate` | Re-apply private channel lock |
| `logevents` | List all events with 🟢/🔴 status |
| `disableevent <name>` | Disable a specific event |
| `enableevent <name>` | Re-enable a disabled event |
| `logconfig` | View current config |
| `loghelp` | Full help menu |

---

## 📋 All 27 Logged Events

`member_join` `member_leave` `member_ban` `member_unban` `nickname_change`
`role_update` `member_timeout` `voice_state` `channel_create` `channel_delete`
`channel_update` `role_create` `role_delete` `emoji_update` `sticker_update`
`invite_create` `invite_delete` `server_update` `thread_create` `thread_delete`
`webhook_update` `scheduled_event` `reactions` `message_edit` `message_delete`
`bulk_delete` `presence_update`

---

## 🔒 Private Channel Logic

`setlogchannel private #channel` automatically:
- Denies `@everyone` view + read history
- Grants bot full access
- Grants whitelisted roles/users read-only access
- Use `whitelist add @role` to give staff access
