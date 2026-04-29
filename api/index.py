from fastapi import FastAPI
from drop_in import get_events

app = FastAPI()

@app.get("/")
def root(start_date: str, end_date: str, sport: str = "both"):
    return {"results": get_events(start_date, end_date, sport)}
