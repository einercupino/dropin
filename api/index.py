from fastapi import FastAPI
from drop_in import get_events

app = FastAPI()

@app.get("/")
def root(start_date: str, end_date: str, sport: str = "both"):
    try:
        results = get_events(start_date, end_date, sport)
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}
