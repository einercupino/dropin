import requests
import json
from datetime import datetime, date
from typing import Optional, List, Dict, Any

def parse_json_smart(content: bytes):
    """
    Decode bytes into JSON, accounting for BOM markers and stray bytes.
    Returns a Python object or None if parsing fails.
    """
    # Detect BOM / encoding
    if content.startswith(b"\xff\xfe") or content.startswith(b"\xfe\xff"):
        text = content.decode("utf-16", errors="strict")
    elif content.startswith(b"\xef\xbb\xbf"):
        text = content.decode("utf-8-sig", errors="strict")
    else:
        # be forgiving; some endpoints send odd bytes
        text = content.decode("utf-8", errors="ignore")

    text = text.lstrip()

    # Find JSON start
    i1, i2 = text.find("["), text.find("{")
    starts = [i for i in (i1, i2) if i != -1]
    if not starts:
        return None
    text = text[min(starts):]

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None

def to_date(s: str) -> date:
    """Convert a YYYY-MM-DD string into a date object."""
    return datetime.strptime(s, "%Y-%m-%d").date()

def age_matches(event_age: str, age_filters: Optional[List[str]]) -> bool:
    """
    Determine if an event's age classification matches any of the provided filters.
    `age_filters` can be None, a single string, or a list of strings.
    """
    if not age_filters:
        return True
    if isinstance(age_filters, str):
        age_filters = [age_filters]

    ea = (event_age or "").lower()
    # mapping of shorthand to official strings
    shorthand_map = {
        "6+": "6 years and over",
        "17+": "17 years and over",
        "18+": "18 years and over",
        "19+": "19 years and over",
        "60+": "60 years and over",
        "16+": "16 years and over",
        "13-18": "13 - 18 years",
        "16-24": "16 - 24 years",
        "6-15": "6 - 15 years",
        "3-15": "3 - 15 years",
    }
    for af in age_filters:
        af = af.lower().strip()
        # exact city string
        if af == ea:
            return True
        # shorthand
        if af in shorthand_map and shorthand_map[af].lower() == ea:
            return True
        # family helper
        if af == "family":
            if any(x in ea for x in ["6 - 15 years", "3 - 15 years", "6 years and over"]):
                return True
        # fallback substring
        if af in ea:
            return True
    return False

def date_in_range(event_date: str, start: Optional[date], end: Optional[date]) -> bool:
    """Return True if the event date falls within the start and end date range."""
    if not event_date:
        return False
    d = to_date(event_date)
    if start and d < start:
        return False
    if end and d > end:
        return False
    return True

def badminton_only(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter events to only those that mention badminton."""
    return [e for e in events if "badminton" in e.get("c", "").lower()]

def pickleball_only(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter events to only those that mention pickleball."""
    return [e for e in events if "pickleball" in e.get("c", "").lower()]

def badminton_or_pickleball(events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Filter events to those that mention badminton or pickleball."""
    return [
        e for e in events
        if "badminton" in e.get("c", "").lower()
        or "pickleball" in e.get("c", "").lower()
    ]

def arcgis_get_facilities() -> List[Dict[str, str]]:
    """
    Fetch the list of facilities from Toronto's ArcGIS service.
    Returns a list of dicts with `locationid` and `name`.
    """
    url = (
        "https://services3.arcgis.com/b9WvedVPoizGfvfD/"
        "arcgis/rest/services/COT_Sports_Drop_In_View/FeatureServer/0/query"
    )
    params = {
        "where": "show_on_sports_map = 'Yes'",
        "outFields": "locationid,complexname",
        "returnGeometry": "false",
        "f": "json",
        "resultRecordCount": 1000,
        "resultOffset": 0,
    }
    facilities: List[Dict[str, str]] = []
    while True:
        try:
            r = requests.get(url, params=params, timeout=20)
            r.raise_for_status()
        except Exception:
            # If the request fails (e.g., network error or forbidden), abort and return what we have
            return facilities
        data = r.json()
        feats = data.get("features", [])
        if not feats:
            break
        for feat in feats:
            a = feat.get("attributes", {})
            loc = a.get("locationid")
            name = a.get("complexname")
            if loc and name:
                facilities.append({
                    "locationid": str(loc),
                    "name": name
                })   
        if len(feats) < params["resultRecordCount"]:
            break
        params["resultOffset"] += params["resultRecordCount"]
    return facilities

def toronto_get_schedule_events(locationid: str) -> List[Dict[str, Any]]:
    """
    Fetch the drop‑in schedule events for a given facility.
    Returns a list of event dicts.
    """
    url = f"https://www.toronto.ca/data/parks/live/dropin/sports/{locationid}.json"
    try:
        r = requests.get(url, timeout=20)
    except Exception:
        return []
    if r.status_code != 200:
        return []
    payload = parse_json_smart(r.content)
    if payload is None:
        return []
    if isinstance(payload, list) and payload and isinstance(payload[0], dict):
        return payload[0].get("r", [])
    if isinstance(payload, dict):
        return payload.get("r", [])
    return []

def filter_events(events: List[Dict[str, Any]],
                  start_date: Optional[str] = None,
                  end_date: Optional[str] = None,
                  age_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Filter events by date range and age filters.
    """
    start = to_date(start_date) if start_date else None
    end = to_date(end_date) if end_date else None
    out: List[Dict[str, Any]] = []
    for e in events:
        if not date_in_range(e.get("d"), start, end):
            continue
        if not age_matches(e.get("age", ""), age_filter):
            continue
        out.append(e)
    return out

def get_events(start_date: str, end_date: str, sport: str = "both") -> List[Dict[str, Any]]:
    """
    Return a list of facilities and their matching events based on the requested
    date range and sport type.
    :param start_date: ISO date (YYYY-MM-DD) of the first day to include.
    :param end_date: ISO date (YYYY-MM-DD) of the last day to include.
    :param sport: 'badminton', 'pickleball', or 'both'.
    """
    # Age filters: only include sessions suitable for ages 6+ through adult
    age_filter = ["6+", "16+", "17+", "18+", "19+"]
    facilities = arcgis_get_facilities()
    results: List[Dict[str, Any]] = []
    for f in facilities:
        events = toronto_get_schedule_events(f["locationid"])
        # filter by sport
        s = sport.lower()
        if s == "badminton":
            events = badminton_only(events)
        elif s == "pickleball":
            events = pickleball_only(events)
        else:
            events = badminton_or_pickleball(events)
        # filter by date and age
        events = filter_events(events, start_date=start_date, end_date=end_date, age_filter=age_filter)
        if events:
            results.append({
                "facility": f["name"],
                "locationid": f["locationid"],
                "events": [
                    {
                        "date": e.get("d"),
                        "time": e.get("t"),
                        "age": e.get("age") or "N/A",
                        "sport": e.get("c")
                    } for e in events
                ],
            })
    return results
