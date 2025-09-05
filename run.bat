@echo off
cd /d "H:\Github Repositories\pokebot"

:: Activate virtual environment
call venv\Scripts\activate

:: Ensure on main branch
git checkout main

:: Stage all changes
git add .

:: Commit only if there are changes
git diff --cached --quiet || git commit -m "Auto-commit before running bot"

:: Push to GitHub
git push origin main

:: Run the bot
python bot.py

pause
