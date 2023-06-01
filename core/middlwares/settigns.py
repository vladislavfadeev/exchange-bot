from environs import Env
from dataclasses import dataclass



@dataclass
class BotSettings:
    botToken: str
    adminId: int
    troubleStaffId : int
    troubleStaff: str
    devStaffId: int
    log_dir: str

@dataclass
class APISettings:
    baseUrl: str
    authToken: str

@dataclass
class StateStorage:
    host: str
    port: str
    db: str
    username: str
    passwd: str

@dataclass
class JobStorage:
    host: str
    port: str
    db: str
    username: str
    passwd: str


@dataclass
class Settings:
    botSetting: BotSettings
    apiSettings: APISettings
    stateStorage: StateStorage
    jobStorage: JobStorage
    


def get_settings(path: str):
    
    env = Env()
    env.read_env(path)

    return Settings(
        botSetting=BotSettings(
            botToken=env.str("TOKEN"),
            adminId=env.int("ADMIN_ID"),
            troubleStaff=env.str("TROUBLE_STAFF"),
            troubleStaffId=env.int("TROUBLE_STAFF_ID"),
            devStaffId=env.int("DEV_STAFF_ID"),
            log_dir=env.str("LOGFILE_DIR")
        ),
        apiSettings=APISettings(
            baseUrl=env.str("BASE_URL"),
            authToken=env.str("BACKEND_AUTH_TOKEN")
        ),
        stateStorage=StateStorage(
            host=env.str("STATE_REDIS_HOST"),
            port=env.str("STATE_REDIS_PORT"),
            db=env.str("STATE_REDIS_DB"),
            username=env.str("STATE_REDIS_USERNAME"),
            passwd=env.str("STATE_REDIS_PASSWD"),
        ),
        jobStorage=JobStorage(
            host=env.str("JOBS_REDIS_HOST"),
            port=env.str("JOBS_REDIS_PORT"),
            db=env.str("JOBS_REDIS_DB"),
            username=env.str("JOBS_REDIS_USERNAME"),
            passwd=env.str("JOBS_REDIS_PASSWD"),
        ),
    )


appSettings = get_settings('.env')

