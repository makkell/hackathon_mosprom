#!/usr/bin/env python3
"""
Скрипт для запуска Streamlit приложения анализа импорта РФ
"""

import subprocess
import sys
import os

def main():
    """Запускает Streamlit приложение"""
    try:
        # Проверяем наличие файла app.py
        if not os.path.exists('app.py'):
            print("❌ Файл app.py не найден!")
            print("Убедитесь, что вы находитесь в правильной директории.")
            sys.exit(1)
        
        print("🚀 Запуск приложения анализа импорта РФ...")
        print("📊 Откройте браузер по адресу: http://localhost:8501")
        print("⏹️  Для остановки нажмите Ctrl+C")
        print("-" * 50)
        
        # Запускаем Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Приложение остановлено пользователем")
    except Exception as e:
        print(f"❌ Ошибка при запуске: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
