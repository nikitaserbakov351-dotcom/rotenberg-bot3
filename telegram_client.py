import asyncio
import logging
import random
import sys
from typing import Optional
from datetime import datetime

from telethon import TelegramClient, events
from telethon.tl.functions.messages import SendReactionRequest
from telethon.tl.types import ReactionEmoji, PeerUser
from telethon.errors import FloodWaitError

from brain import RotenbergBrain

logger = logging.getLogger(__name__)


class TelegramClientHandler:
    """Обработчик Telegram-клиента"""

    def __init__(self, config, brain: RotenbergBrain):
        self.config = config
        self.brain = brain
        self.client: Optional[TelegramClient] = None
        self.is_running = True
        self.me = None

    async def start(self):
        """Запуск клиента"""
        try:
            print("🔧 Инициализация Telegram клиента...")

            self.client = TelegramClient(
                session=self.config.SESSION_NAME,
                api_id=self.config.API_ID,
                api_hash=self.config.API_HASH,
                device_model="RotenbergBot",
                system_version="Linux",
                app_version="2.0.0",
                lang_code="ru",
                system_lang_code="ru"
            )

            print("✅ Клиент создан")

            # Настройка обработчиков
            self.setup_handlers()

            # Подключение
            print("📡 Подключаюсь к Telegram...")
            await self.client.connect()

            # Проверка авторизации
            if not await self.client.is_user_authorized():
                print("\n🔐 ТРЕБУЕТСЯ АВТОРИЗАЦИЯ")
                print("=" * 40)
                await self._perform_login()
            else:
                print("✅ Уже авторизован")

            # Получаем информацию о себе
            self.me = await self.client.get_me()
            print(f"\n✅ АВТОРИЗОВАН КАК: {self.me.first_name} (@{self.me.username})")
            print("=" * 40)

            # Запускаем фоновые задачи
            asyncio.create_task(self._keep_alive())

            # Информационное сообщение
            print("\n🚀 БОТ ЗАПУЩЕН И ГОТОВ К РАБОТЕ!")
            print("👉 Напишите вашему аккаунту в Telegram")
            print("💬 Бот будет отвечать в стиле Романа Ротенберга")
            print("⏹️  Для остановки нажмите Ctrl+C")
            print("=" * 40 + "\n")

            # Бесконечный цикл ожидания
            await self._run_forever()

        except Exception as e:
            logger.error(f"❌ Ошибка запуска: {e}")
            raise

    def setup_handlers(self):
        """Настройка обработчиков событий"""

        @self.client.on(events.NewMessage(incoming=True))
        async def message_handler(event):
            await self._handle_message(event)

        @self.client.on(events.MessageEdited(incoming=True))
        async def edit_handler(event):
            if random.random() < 0.2:  # 20% шанс ответить на правку
                await event.reply("Поправляешь? Ясно...")

    async def _perform_login(self):
        """Процедура авторизации"""
        try:
            phone = input("Введите номер телефона (например, +79161234567): ").strip()

            await self.client.send_code_request(phone)
            print("✅ Код отправлен в Telegram")

            code = input("Введите код из Telegram: ").strip()

            await self.client.sign_in(phone, code)
            print("✅ Авторизация успешна!")

        except Exception as e:
            if "two" in str(e).lower():
                password = input("Включена 2FA. Введите пароль: ")
                await self.client.sign_in(password=password)
                print("✅ Авторизация с 2FA успешна!")
            else:
                print(f"❌ Ошибка: {e}")
                raise

    async def _handle_message(self, event):
        """Обработка входящих сообщений"""
        try:
            print(f"\n🔍 DEBUG: Начало обработки сообщения")

            # Пропускаем служебные сообщения
            if not event.message:
                print("❌ DEBUG: event.message отсутствует")
                return

            if event.message.out:
                print("❌ DEBUG: Это наше исходящее сообщение")
                return

            # Получаем информацию об отправителе
            print(f"🔍 DEBUG: Получаю информацию об отправителе...")
            sender = await event.get_sender()
            if not sender:
                print("❌ DEBUG: Не удалось получить информацию об отправителе")
                return

            # Логируем
            msg_preview = event.message.text[:80] + "..." if len(event.message.text) > 80 else event.message.text
            print(f"📩 DEBUG: От {sender.first_name} ({sender.id}): {msg_preview}")

            # Имитируем печатание
            typing_delay = random.uniform(
                self.config.TYPING_DELAY_MIN,
                self.config.TYPING_DELAY_MAX
            )
            print(f"⏳ DEBUG: Имитирую печатание ({typing_delay:.1f} сек)...")
            await asyncio.sleep(typing_delay)

            # Генерируем ответ
            print(f"🧠 DEBUG: Генерирую ответ...")
            try:
                response = self.brain.get_response(
                    user_message=event.message.text,
                    user_name=sender.first_name
                )
                print(f"✅ DEBUG: Ответ сгенерирован: {response[:100]}...")
            except Exception as brain_error:
                print(f"❌ DEBUG: Ошибка brain.get_response: {brain_error}")
                response = "Сейчас мыслями на тренировке. Повтори вопрос."

            # Отправляем ответ
            print(f"📤 DEBUG: Отправляю ответ...")
            try:
                await event.reply(response)
                print(f"✅ DEBUG: Ответ отправлен успешно")

                # Ставим реакцию (70% шанс)
                if random.random() < 0.7:
                    await self._send_reaction(event.message)
                    print(f"👍 DEBUG: Реакция поставлена")

                # Отмечаем как прочитанное
                await event.message.mark_read()
                print(f"👁️ DEBUG: Сообщение отмечено как прочитанное")

            except FloodWaitError as e:
                print(f"⏳ DEBUG: FloodWait: жду {e.seconds} секунд")
                await asyncio.sleep(e.seconds)
                await event.reply(response)
            except Exception as send_error:
                print(f"❌ DEBUG: Ошибка отправки: {send_error}")
                raise

        except Exception as e:
            print(f"🔥 КРИТИЧЕСКАЯ ОШИБКА: {e}")
            print(f"🔥 Тип ошибки: {type(e).__name__}")
            import traceback
            print(f"🔥 Трассировка:\n{traceback.format_exc()}")

            logger.error(f"Ошибка обработки: {e}", exc_info=True)

            # Пробуем отправить более конкретное сообщение об ошибке
            try:
                await event.reply(f"Ошибка типа {type(e).__name__}. Проверь логи.")
            except:
                pass  # Если и это не получается, просто игнорируем

    async def _send_reaction(self, message):
        """Отправляет реакцию на сообщение"""
        try:
            reactions = [
                ReactionEmoji(emoticon='👍'),
                ReactionEmoji(emoticon='❤️'),
                ReactionEmoji(emoticon='😂'),
                ReactionEmoji(emoticon='😮'),
                ReactionEmoji(emoticon='😢'),
                ReactionEmoji(emoticon='👏'),
                ReactionEmoji(emoticon='🔥'),
                ReactionEmoji(emoticon='🎯'),
            ]

            await self.client(SendReactionRequest(
                peer=message.peer_id,
                msg_id=message.id,
                reaction=[random.choice(reactions)]
            ))
        except Exception as e:
            logger.debug(f"Не удалось поставить реакцию: {e}")

    async def _keep_alive(self):
        """Поддержание соединения"""
        while self.is_running:
            try:
                await asyncio.sleep(random.randint(200, 400))
                # Простое действие для поддержания связи
                if self.client and self.client.is_connected():
                    await self.client.get_me()
            except Exception as e:
                logger.debug(f"Keep alive: {e}")
                await asyncio.sleep(30)

    async def _run_forever(self):
        """Основной цикл работы"""
        try:
            while self.is_running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            pass

    async def stop(self):
        """Корректная остановка"""
        self.is_running = False
        if self.client:
            await self.client.disconnect()
        logger.info("🛑 Бот остановлен")