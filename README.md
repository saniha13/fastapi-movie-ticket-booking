# FastAPI CineStar Movie Ticket Booking System

## Project Description
This is a FastAPI backend project developed as part of the internship final assignment.  
It simulates a real-world movie ticket booking system.


## Features
### Day 1 – GET APIs
- Home route
- Get all movies
- Get movie by ID
- Movies summary
- Get all bookings

### Day 2 – POST + Validation
- Create booking using Pydantic
- Input validation (seats, phone, etc.)
- Error handling

### Day 3 – Helper Functions
- find_movie()
- calculate_ticket_cost()
- filter_movies_logic()

### Day 4 – CRUD Operations
- Add movie
- Update movie
- Delete movie
- Duplicate check
- 404 handling

### Day 5 – Workflow
- Seat hold system
- Confirm booking
- Release hold

### Day 6 – Advanced APIs
- Search
- Sort
- Pagination
- Combined browse endpoint


## Tech Stack
- FastAPI
- Python
- Uvicorn
- Pydantic


## How to Run

1. Install dependencies:
pip install -r requirements.txt

2. Run server:
uvicorn main:app --reload

3. Open Swagger:
http://127.0.0.1:8000/docs


## Screenshots
All outputs are available in the screenshots file.


## Author
Saniha R B
