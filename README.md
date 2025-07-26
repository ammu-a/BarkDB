# BarkDB - Pet care services platform 

BarkDB is a Flask-based web application inspired by Rover.com. It allows pet owners to find, book, and review service providers in their local area. 
The platform includes analytics and tools for managing bookings, updating users and reviews.

---
## Tech Stack

 - Backend: Python, Flask
 - Database: MySQL
 - Frontend: HTML, Bootstrap

---

## Installation
### 1. Clone the Repository

```bash
git clone https://github.com/ammu-a/BarkDB.git
cd BarkDB
```
### 2. Set up the Environment
```bash
pip install -r requirements.txt
```
### 3. Configure Database

- Update the connect_db() function in app.py with your DB credentials
- Run schema.sql to create tables, triggers, views, and functions. Sample data is stored in data/ to populate tables
 
### 4. Run the App
```bash
python app.py
```
 App will be available at http://127.0.0.1:5000/

---
## Usage

Signup Flow:
	•	Users can sign up as Pet Owners or Service Providers
	•	Owners provide pet details
	•	Providers select location from dropdown and add experience

Booking:
	•	Owners can search by zipcode, service, and date
	•	Providers with no conflicting bookings are shown
	•	Once booked, confirmation shows BookingID and estimated cost

Analytics:
	•	View top providers by experience
	•	Track rolling bookings by service
	•	Revenue reports by city, pet type, and service

---
## Project Structure

![Project structure](/project_structure.png)

## Features

	•	Booking Conflict Checks using subqueries
	•	Dynamic filtering by zipcode, service, and dates
	•	SQL Analytics using:
	•	RANK(), DENSE_RANK(), ROW_NUMBER()
	•	ROLLUP for aggregations
	•	Moving averages using WINDOW functions

---
Created by [Ammu Anil](mailto:aanil1@hawk.illinoistech.edu) - feel free to contact me!

