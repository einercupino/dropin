from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from drop_in import get_events

app = FastAPI()

# 👉 Serve your frontend here
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
    <head><title>Drop-In Sports</title></head>
    <body>
        <h2>Find Drop-In Sports</h2>

        <form onsubmit="search(event)">
            Start Date: <input type="date" id="start"><br><br>
            End Date: <input type="date" id="end"><br><br>

            Sport:
            <select id="sport">
                <option value="both">Both</option>
                <option value="badminton">Badminton</option>
                <option value="pickleball">Pickleball</option>
            </select><br><br>

            <button type="submit">Search</button>
        </form>

        <pre id="output"></pre>

        <script>
        async function search(e){
            e.preventDefault();
        
            const start = document.getElementById("start").value;
            const end = document.getElementById("end").value;
            const sport = document.getElementById("sport").value;
        
            console.log("Searching:", start, end, sport);
        
            try {
                const res = await fetch(`/api?start_date=${start}&end_date=${end}&sport=${sport}`);
                console.log("Response status:", res.status);
        
                const data = await res.json();
                console.log("Data:", data);
        
                document.getElementById("output").textContent =
                    JSON.stringify(data, null, 2);
        
            } catch (err) {
                console.error(err);
                document.getElementById("output").textContent = "Error: " + err.message;
            }
        }
        </script>
    </body>
    </html>
    """

# 👉 API endpoint
@app.get("/api")
def api(start_date: str, end_date: str, sport: str = "both"):
    return {"results": get_events(start_date, end_date, sport)}
