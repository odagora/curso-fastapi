from fastapi import FastAPI
from datetime import datetime
from zoneinfo import ZoneInfo

app = FastAPI()

TIME_ZONES = {
    "CO": "America/Bogota",
    "US": "America/New_York",
    "MX": "America/Mexico_City",
    "BR": "America/Sao_Paulo",
}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/time")
async def get_time():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time}


@app.get("/time/{country_code}")
async def get_time_by_country(country_code: str):
    country_code = country_code.upper()
    if country_code not in TIME_ZONES:
        return {"error": "Invalid country code"}

    time_zone = TIME_ZONES[country_code]
    current_time = datetime.now(ZoneInfo(time_zone)).strftime("%Y-%m-%d %H:%M:%S")
    return {"current_time": current_time, "country_code": country_code}
