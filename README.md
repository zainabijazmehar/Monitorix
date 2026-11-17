
<p align="center">
  <img src="assets/monitorix-logo.png" width="420" alt="Monitorix Logo">
</p>

<h1 align="center">Monitorix</h1>

<p align="center"><em>Monitor • Detect • Respond</em></p>

A professional Discord monitoring and security analysis tool designed to track, store, and analyze server activities efficiently.

## 📌 About Monitorix

Monitorix is a security-focused monitoring system that helps administrators observe Discord server activity, maintain historical records, and generate useful reports.

It provides a centralized monitoring environment with database-backed storage and a professional command-line interface for managing monitoring operations.

## ✨ Features

- Discord server activity monitoring
- Real-time event tracking
- SQLite database integration
- Message history management
- Search and analysis capabilities
- Statistics generation
- Report generation
- Backup and restore support
- Professional CLI interface
- Secure configuration management

## ⚙️ Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/zainabijazmehar/Monitorix.git
```

Move into the project directory:

```bash
cd Monitorix
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Open `.env` and add your required configuration values.

Example:

```env
DISCORD_TOKEN=your_discord_bot_token
```

### 5. Run Monitorix

```bash
python main.py
```

## 🚀 Usage

After launching Monitorix, the CLI interface will start.

Available commands:

- `status` - Displays system and monitoring status.
- `messages` - Shows monitored messages.
- `history` - Displays stored activity history.
- `channels` - Shows monitored channels.
- `help` - Displays available commands.
- `exit` - Closes Monitorix safely.

## 🔐 Security Notes

- Never share your `.env` file.
- Keep your Discord bot token private.
- Use proper permissions when deploying the bot.
- Regularly backup your database.

## 👩‍💻 Author

**Zainab Ijaz**

Cybersecurity | Network Security Enthusiast

## 📄 License

This project is developed for educational and security research purposes.

