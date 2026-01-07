import asyncio
import logging
import sys
import signal
from pathlib import Path

# Добавляем текущую директорию в путь
sys.path.append(str(Path(__file__).parent))

from config import Config
from brain import RotenbergBrain
from telegram_client import TelegramClientHandler


def setup_logging():
    """Настройка логирования"""
    logging.basicConfig(
        level=logging.DEBUG,  # Было INFO, меняем на DEBUG
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S',
        handlers=[
            logging.FileHandler('rotenberg_bot_debug.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    # НЕ уменьшаем логи telethon
    # logging.getLogger('telethon').setLevel(logging.WARNING)  # Закомментируйте эту строку!
    logging.getLogger('telethon').setLevel(logging.WARNING)


async def main():
    """Основная функция запуска"""
    print("=" * 60)
    print("🚀 TELEGRAM БОТ 'РОМАН РОТЕНБЕРГ' - ЗАПУСК")
    print("=" * 60)

    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 1. Проверяем конфигурацию
        print("1. 🔍 Проверяю конфигурацию...")
        Config.validate()
        print("   ✅ Конфигурация OK")

        # 2. Инициализируем мозг бота
        print("2. 🧠 Инициализирую базу знаний (300+ фраз)...")
        brain = RotenbergBrain()
        print("   ✅ База знаний загружена")

        # 3. Создаём клиент Telegram
        print("3. 📱 Создаю Telegram клиент...")
        client = TelegramClientHandler(Config, brain)
        print("   ✅ Клиент создан")

        # 4. Настраиваем обработчик Ctrl+C
        def signal_handler(sig, frame):
            print("\n⚠️  Получен сигнал остановки...")
            asyncio.create_task(shutdown(client))

        signal.signal(signal.SIGINT, signal_handler)

        # 5. Запускаем бота
        print("\n▶️  ЗАПУСКАЮ БОТА...")
        print("   (это может занять несколько секунд)")

        await client.start()

    except ValueError as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("\n📝 СОЗДАЙТЕ ФАЙЛ .env С ТАКИМ СОДЕРЖИМЫМ:")
        print("API_ID=ваш_api_id")
        print("API_HASH=ваш_api_hash")
        print("SESSION_NAME=rotenberg_session")
        print("\n🔗 Получите API на: https://my.telegram.org")

    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        print(f"\n💥 Ошибка: {e}")


async def shutdown(client: TelegramClientHandler):
    """Корректное завершение работы"""
    print("\n🛑 Завершаю работу бота...")
    await client.stop()
    print("✅ Работа завершена. До свидания!")
    sys.exit(0)


if __name__ == "__main__":
    # Настройка asyncio для Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

    # Запуск
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Завершено пользователем")
    except Exception as e:
        print(f"\n💥 Неожиданная ошибка: {e}")
        sys.exit(1)