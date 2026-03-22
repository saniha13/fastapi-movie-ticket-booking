from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import Optional, List

app = FastAPI()

# ---------------- DATA ----------------

movies = [
    {"id": 1, "title": "Avengers", "genre": "Action", "language": "English", "duration_mins": 180, "ticket_price": 300, "seats_available": 50},
    {"id": 2, "title": "Titanic", "genre": "Drama", "language": "English", "duration_mins": 195, "ticket_price": 250, "seats_available": 40},
    {"id": 3, "title": "Joker", "genre": "Drama", "language": "English", "duration_mins": 150, "ticket_price": 200, "seats_available": 30},
    {"id": 4, "title": "RRR", "genre": "Action", "language": "Telugu", "duration_mins": 180, "ticket_price": 280, "seats_available": 60},
    {"id": 5, "title": "KGF", "genre": "Action", "language": "Kannada", "duration_mins": 170, "ticket_price": 270, "seats_available": 45},
    {"id": 6, "title": "The Conjuring", "genre": "Horror", "language": "English", "duration_mins": 120, "ticket_price": 220, "seats_available": 35}
]

bookings = []
booking_counter = 1
holds = []
hold_counter = 1

# ---------------- MODELS ----------------

class BookingRequest(BaseModel):
    customer_name: str = Field(..., min_length=2)
    movie_id: int = Field(..., gt=0)
    seats: int = Field(..., gt=0, le=10)
    phone: str = Field(..., min_length=10)
    seat_type: str = "standard"
    promo_code: str = ""

class NewMovie(BaseModel):
    title: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    language: str = Field(..., min_length=2)
    duration_mins: int = Field(..., gt=0)
    ticket_price: int = Field(..., gt=0)
    seats_available: int = Field(..., gt=0)

# ---------------- HELPERS ----------------

def find_movie(movie_id):
    for m in movies:
        if m["id"] == movie_id:
            return m
    return None

def calculate_ticket_cost(base_price, seats, seat_type, promo_code):
    multiplier = 1
    if seat_type == "premium":
        multiplier = 1.5
    elif seat_type == "recliner":
        multiplier = 2

    original = base_price * seats * multiplier

    discount = 0
    if promo_code == "SAVE10":
        discount = 0.1
    elif promo_code == "SAVE20":
        discount = 0.2

    final = original * (1 - discount)

    return original, final

def filter_movies_logic(data, genre=None, language=None, max_price=None, min_seats=None):
    result = data
    if genre is not None:
        result = [m for m in result if m["genre"].lower() == genre.lower()]
    if language is not None:
        result = [m for m in result if m["language"].lower() == language.lower()]
    if max_price is not None:
        result = [m for m in result if m["ticket_price"] <= max_price]
    if min_seats is not None:
        result = [m for m in result if m["seats_available"] >= min_seats]
    return result

# ---------------- Q1 ----------------

@app.get("/")
def home():
    return {"message": "Welcome to CineStar Booking"}

# ---------------- Q2 ----------------

@app.get("/movies")
def get_movies():
    total_seats = sum(m["seats_available"] for m in movies)
    return {"movies": movies, "total": len(movies), "total_seats_available": total_seats}

# ---------------- Q5 ----------------

@app.get("/movies/summary")
def summary():
    genres = {}
    for m in movies:
        genres[m["genre"]] = genres.get(m["genre"], 0) + 1

    return {
        "total_movies": len(movies),
        "most_expensive": max(movies, key=lambda x: x["ticket_price"]),
        "cheapest": min(movies, key=lambda x: x["ticket_price"]),
        "total_seats": sum(m["seats_available"] for m in movies),
        "genre_count": genres
    }



# ---------------- Q4 ----------------

@app.get("/bookings")
def get_bookings():
    total_revenue = sum(b["final_cost"] for b in bookings)
    return {"bookings": bookings, "total": len(bookings), "total_revenue": total_revenue}

# ---------------- Q8 ----------------

@app.post("/bookings")
def create_booking(data: BookingRequest):
    global booking_counter

    movie = find_movie(data.movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < data.seats:
        raise HTTPException(400, "Not enough seats")

    original, final = calculate_ticket_cost(movie["ticket_price"], data.seats, data.seat_type, data.promo_code)

    movie["seats_available"] -= data.seats

    booking = {
        "booking_id": booking_counter,
        "customer_name": data.customer_name,
        "movie": movie["title"],
        "seats": data.seats,
        "seat_type": data.seat_type,
        "original_cost": original,
        "final_cost": final
    }

    bookings.append(booking)
    booking_counter += 1

    return booking

# ---------------- Q10 ----------------

@app.get("/movies/filter")
def filter_movies(genre: Optional[str] = None, language: Optional[str] = None, max_price: Optional[int] = None, min_seats: Optional[int] = None):
    return {"movies": filter_movies_logic(movies, genre, language, max_price, min_seats)}

# ---------------- Q11 ----------------

@app.post("/movies", status_code=201)
def add_movie(movie: NewMovie):
    if any(m["title"].lower() == movie.title.lower() for m in movies):
        raise HTTPException(400, "Movie already exists")

    new = movie.dict()
    new["id"] = len(movies) + 1
    movies.append(new)
    return new

# ---------------- Q12 ----------------

@app.put("/movies/{movie_id}")
def update_movie(movie_id: int, ticket_price: Optional[int] = None, seats_available: Optional[int] = None):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if ticket_price is not None:
        movie["ticket_price"] = ticket_price
    if seats_available is not None:
        movie["seats_available"] = seats_available

    return movie

# ---------------- Q13 ----------------

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if any(b["movie"] == movie["title"] for b in bookings):
        raise HTTPException(400, "Cannot delete movie with bookings")

    movies.remove(movie)
    return {"message": "Deleted"}

# ---------------- Q14 ----------------

@app.post("/seat-hold")
def hold_seats(customer_name: str, movie_id: int, seats: int):
    global hold_counter

    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")

    if movie["seats_available"] < seats:
        raise HTTPException(400, "Not enough seats")

    movie["seats_available"] -= seats

    hold = {"hold_id": hold_counter, "customer_name": customer_name, "movie_id": movie_id, "seats": seats}
    holds.append(hold)
    hold_counter += 1

    return hold

@app.get("/seat-hold")
def get_holds():
    return {"holds": holds}

# ---------------- Q15 ----------------

@app.post("/seat-confirm/{hold_id}")
def confirm_hold(hold_id: int):
    global booking_counter

    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(404, "Hold not found")

    movie = find_movie(hold["movie_id"])

    booking = {
        "booking_id": booking_counter,
        "customer_name": hold["customer_name"],
        "movie": movie["title"],
        "seats": hold["seats"],
        "final_cost": hold["seats"] * movie["ticket_price"]
    }

    bookings.append(booking)
    holds.remove(hold)
    booking_counter += 1

    return booking

@app.delete("/seat-release/{hold_id}")
def release_hold(hold_id: int):
    hold = next((h for h in holds if h["hold_id"] == hold_id), None)
    if not hold:
        raise HTTPException(404, "Hold not found")

    movie = find_movie(hold["movie_id"])
    movie["seats_available"] += hold["seats"]

    holds.remove(hold)
    return {"message": "Hold released"}

# ---------------- Q16 ----------------

@app.get("/movies/search")
def search(keyword: str):
    result = [m for m in movies if keyword.lower() in m["title"].lower() or keyword.lower() in m["genre"].lower() or keyword.lower() in m["language"].lower()]
    if not result:
        return {"message": "No movies found"}
    return {"movies": result, "total_found": len(result)}

# ---------------- Q17 ----------------

@app.get("/movies/sort")
def sort_movies(sort_by: str = "ticket_price", order: str = "asc"):
    if sort_by not in ["ticket_price", "title", "duration_mins", "seats_available"]:
        raise HTTPException(400, "Invalid sort field")

    return {"movies": sorted(movies, key=lambda x: x[sort_by], reverse=(order == "desc"))}

# ---------------- Q18 ----------------

@app.get("/movies/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    total = len(movies)
    return {
        "total": total,
        "total_pages": -(-total // limit),
        "movies": movies[start:start+limit]
    }

# ---------------- Q19 ----------------

@app.get("/bookings/search")
def booking_search(customer_name: str):
    return {"bookings": [b for b in bookings if customer_name.lower() in b["customer_name"].lower()]}

@app.get("/bookings/sort")
def booking_sort(sort_by: str = "final_cost"):
    return {"bookings": sorted(bookings, key=lambda x: x[sort_by])}

@app.get("/bookings/page")
def booking_page(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    return {"bookings": bookings[start:start+limit]}

# ---------------- Q20 ----------------

@app.get("/movies/browse")
def browse(keyword: Optional[str] = None, genre: Optional[str] = None, language: Optional[str] = None, sort_by: str = "ticket_price", order: str = "asc", page: int = 1, limit: int = 3):
    result = movies

    if keyword:
        result = [m for m in result if keyword.lower() in m["title"].lower()]

    result = filter_movies_logic(result, genre, language)

    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))

    start = (page - 1) * limit
    return {"movies": result[start:start+limit]}

# ---------------- Q3 ----------------

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    movie = find_movie(movie_id)
    if not movie:
        raise HTTPException(404, "Movie not found")
    return movie
