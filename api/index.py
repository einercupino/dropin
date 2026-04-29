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
    <html>
    <head>
        <title>Drop-In Sports</title>

        <!-- 🔥 Nice modern font -->
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">

        <style>
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            body {
                font-family: 'Inter', sans-serif;
                background: #f5f7fa;
                padding: 30px;
                color: #333;
            }

            h2 {
                margin-bottom: 20px;
            }

            form {
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                width: 100%;
            }

            .row {
                display: flex;
                gap: 15px;
                margin-bottom: 15px;
            }

            label {
                font-weight: 600;
                font-size: 14px;
            }

            input, select {
                padding: 6px 8px;
                border-radius: 6px;
                border: 1px solid #ccc;
                margin-top: 5px;
                font-family: 'Inter', sans-serif;
            }

            button {
                background: #2563eb;
                color: white;
                border: none;
                padding: 10px 15px;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 600;
            }

            button:hover {
                background: #1d4ed8;
            }

            #output {
                margin-top: 25px;
                width: 100%;
            }

            .facility {
                width: 100%;
                box-sizing: border-box;
                background: white;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.05);
            }

            .facility h3 {
                margin-bottom: 8px;
            }

            .form-row {
                display: flex;
                gap: 15px;
                align-items: flex-end;
                flex-wrap: wrap; /* keeps it responsive */
            }
            
            .form-row div {
                display: flex;
                flex-direction: column;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h2>🏸 Drop-In Sports - Toronto</h2>
    
            <form onsubmit="search(event)">
                <div class="form-row">
                    
                    <div>
                        <label>Start Date</label><br>
                        <input type="date" id="start">
                    </div>
            
                    <div>
                        <label>End Date</label><br>
                        <input type="date" id="end">
                    </div>
            
                    <div>
                        <label>Badminton or Pickleball</label><br>
                        <select id="sport">
                            <option value="both">Both</option>
                            <option value="badminton">Badminton</option>
                            <option value="pickleball">Pickleball</option>
                        </select>
                    </div>
            
                    <div style="align-self: flex-end;">
                        <button type="submit">Search</button>
                    </div>
            
                </div>
            </form>
    
            <div id="output"></div>
        </div>
        
        <script>
        async function search(e){
            e.preventDefault();

            const output = document.getElementById("output");
            output.innerHTML = "<p>Loading...</p>";

            const start = document.getElementById("start").value;
            const end = document.getElementById("end").value;
            const sport = document.getElementById("sport").value;

            const res = await fetch(`/data?start_date=${start}&end_date=${end}&sport=${sport}`);
            const data = await res.json();

            output.innerHTML = "";

            if (!data.results || data.results.length === 0) {
                output.innerHTML = "<p>No results found.</p>";
                return;
            }

            data.results.forEach(fac => {
                const div = document.createElement("div");
                div.className = "facility";
            
                const title = document.createElement("h3");
                const link = document.createElement("a");
                const query = encodeURIComponent(fac.facility + " Toronto");
                
                link.href = `https://www.google.com/maps/search/?api=1&query=${query}`;
                link.target = "_blank";
                link.textContent = fac.facility;
                
                // 👇 separate pin
                const pin = document.createElement("span");
                pin.textContent = "📍 ";
                pin.style.marginRight = "5px";
                
                title.appendChild(pin);
                title.appendChild(link);
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
        }
        </script>

    </body>
    </html>
    """
# ✅ API MUST BE DIFFERENT ROUTE
@app.get("/data")
def api(start_date: str, end_date: str, sport: str = "both"):
    return {"results": get_events(start_date, end_date, sport)}
