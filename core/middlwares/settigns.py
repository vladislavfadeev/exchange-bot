from environs import Env
from dataclasses import dataclass
from aiogram.types import Message



@dataclass
class BotSettings:
    botToken: str
    adminId: int
    troubleStaffId : int
    troubleStaff: str

@dataclass
class APISettings:
    baseUrl: str
    authToken: str


@dataclass
class Settings:
    botSetting: BotSettings
    apiSettings: APISettings


def get_settings(path: str):
    
    env = Env()
    env.read_env(path)

    return Settings(
        botSetting = BotSettings(
            botToken=env.str("TOKEN"),
            adminId=env.int("ADMIN_ID"),
            troubleStaff=env.str("TROUBLE_STAFF"),
            troubleStaffId=env.int("TROUBLE_STAFF_ID")
        ),
        apiSettings = APISettings(
            baseUrl=env.str("BASE_URL"),
            authToken=env.str("BACKEND_AUTH_TOKEN"),

        )
    )


appSettings = get_settings('.env')



class MainMSG():

    def __init__(self, msg = None):
        self._msg = msg

    @property
    def msg(self):
        return self._msg
    
    @msg.setter
    def msg(self, msg):
        if isinstance(msg, Message):
            self._msg = msg
        else:
            self._msg = None
            # raise ValueError('main_msg can only be an instance of a class Message')

mainMsg = MainMSG()