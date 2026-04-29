from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from drop_in import get_events

app = FastAPI()

# UI page
@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>List Drop-In Sports - Toronto</h2>
    <form onsubmit="search(event)">
        <div style="margin-bottom:10px;">
            Start Date: <input type="date" id="start">
            &nbsp;&nbsp;&nbsp;
            End Date: <input type="date" id="end">
        </div>

        <div style="margin-bottom:10px;">
            Badminton or Pickleball:
            <select id="sport">
                <option value="both">Both</option>
                <option value="badminton">Badminton</option>
                <option value="pickleball">Pickleball</option>
            </select>
        </div>

        <button type="submit">Search</button>
    </form>

    <pre id="output"></pre>

    <script>
    async function search(e){
        e.preventDefault();
    
        const output = document.getElementById("output");
    
        output.innerHTML = "";
    
        // Optional: show loading state
        output.innerHTML = "<p>Loading...</p>";
    
        const start = document.getElementById("start").value;
        const end = document.getElementById("end").value;
        const sport = document.getElementById("sport").value;
    
        try {
            const res = await fetch(`/data?start_date=${start}&end_date=${end}&sport=${sport}`);
            const data = await res.json();
    
            // Clear loading
            output.innerHTML = "";
    
            if (!data.results || data.results.length === 0) {
                output.innerHTML = "<p>No results found.</p>";
                return;
            }
    
            data.results.forEach(fac => {
                const div = document.createElement("div");
                div.style.marginBottom = "20px";
    
                const title = document.createElement("h3");
                title.textContent = fac.facility;
                div.appendChild(title);
    
                const list = document.createElement("ul");
    
                fac.events.forEach(ev => {
                    const li = document.createElement("li");
                    li.textContent = `${ev.date} | ${ev.time} | ${ev.sport} | Age: ${ev.age}`;
                    list.appendChild(li);
                });
    
                div.appendChild(list);
                output.appendChild(div);
            });
    
        } catch (err) {
            output.innerHTML = `<p>Error: ${err.message}</p>`;
        }
    }
    </script>
    """

# ✅ API MUST BE DIFFERENT ROUTE
@app.get("/data")
def api(start_date: str, end_date: str, sport: str = "both"):
    return {"results": get_events(start_date, end_date, sport)}
