# Activate virtual environment and show status
.\venv\Scripts\activate
Write-Host "Virtual environment activated! Django version:" -ForegroundColor Green
python -m django --version
Write-Host "
Ready to run: python manage.py runserver" -ForegroundColor Yellow
