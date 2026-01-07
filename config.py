import os
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()


class Config:
    """Настройки бота"""
    API_ID = int(os.getenv('API_ID', 0))
    API_HASH = os.getenv('API_HASH', '')
    SESSION_NAME = os.getenv('SESSION_NAME', 'rotenberg_session')

      # ДОБАВЬ ЭТУ СТРОКУ ↓↓↓
    SESSION_STRING = os.getenv('SESSION_STRING', '')
    
    # Настройки ответов
    TYPING_DELAY_MIN = 0.5  # Минимальная задержка перед ответом (сек)
    TYPING_DELAY_MAX = 4.5  # Максимальная задержка

    @classmethod
    def validate(cls):
        """Проверка настроек"""
        if not cls.API_ID or cls.API_ID == 0:
            raise ValueError("❌ API_ID не найден в .env файле")
        if not cls.API_HASH:
            raise ValueError("❌ API_HASH не найден в .env файле")

        print("✅ Конфигурация загружена успешно")

    
    # ... остальное без изменений
