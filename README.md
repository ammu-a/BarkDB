# BarkDB - Pet care services platform 

BarkDB is a Flask-based web application inspired by Rover.com. It allows pet owners to find, book, and review service providers in their local area. 
The platform includes analytics and tools for managing bookings, updating users and reviews.

---
## Tech Stack

 **Backend**: Python, Flask
 **Database**: MySQL
 **Frontend**: HTML, Bootstrap
---

## Installation
### 1. Clone the Repository

```bash
git clone https://github.com/ammu-a/BarkDB.git
cd BarkDB
npm install
```
### 2. Set up Python Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
### 3. Configure Database
	•	Create a MySQL database named BarkDB
	•	Update the connect_db() function in app.py with your DB credentials
	•	use schema.sql, data/ for creating tables and inserting data
 
### 4. Run the App
```bash
python app.py
```
---
## Usage

Explain how to use your project, with code examples if possible.


---
## Project Structure
├── static/style.css      # Static assets  
├── templates/            # HTML templates (Jinja2)
│   ├── main_menu.html
│   ├── signup.html
│   ├── view_results.html
│   ├── ...            
├── requirements.txt      # Python dependencies
|__ app.py                # Main Flask application 
├── README.md             #You are here!


## Features

SQL Features
	•	Booking Conflict Check
	•	Dynamic Filtering (Zipcode, Service, Dates)
	•	SQL Analytics with RANK(), ROLLUP, and Moving Averages
---


Created by [Ammu Anil](mailto:aanil1@hawk.illinoistech.edu) - feel free to contact me!