import logging
import asyncio
import os
from telebot.async_telebot import AsyncTeleBot
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


class HealthCheckWorker:

    def __init__(self):
        self.hosts = None
        self.bot_token = None
        self.chat_id = None

    def get_hosts(self):
        hostnames = os.getenv("WORKER_HOSTS")
        if hostnames:
            self.hosts = hostnames.split(",")

    def get_notification_channel(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")

    async def healthcheck(self):
        self.get_hosts()
        self.get_notification_channel()

        while True:
            if not self.hosts:
                logging.info("Hosts not found")
                return

            for host in self.hosts:
                status = await check_ping(host)
                if "Active" in status:
                    logging.info("Host %s is %s", host, status)
                    message = f"❗️Host {host} is not available"
                    await self.send_notification(message)
                await asyncio.sleep(5)

    async def send_notification(self, message):
        await send_message(self.bot_token, self.chat_id, message)


async def check_ping(hostname: str):
    response = os.popen(f"ping -c 4 {hostname} ").read()
    return "Error" if response == 0 else "Active"


async def send_message(token: str, chat_id: str, message: str):
    bot = AsyncTeleBot(token)
    await bot.send_message(chat_id, message)


if __name__ == '__main__':
    healthcheck_worker = HealthCheckWorker()
    loop = asyncio.get_event_loop_policy().new_event_loop()
    loop.create_task(healthcheck_worker.healthcheck())
    loop.run_forever()

