from flask import Flask, render_template, request, redirect, flash
import mysql.connector
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
app = Flask(__name__)
app.secret_key = 'supersecretkey'


def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="MyNewPassword123!",
        database="BarkDB"
    )

@app.route('/')
def main_menu():
    return render_template('main_menu.html')

@app.route('/view')
def view_menu():
    return render_template('view_menu.html')
#fixing the location dropdown
@app.route('/signup')
def signup_form():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT LocationID, Zipcode, City, Province FROM Location")
    locations = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('signup.html', locations=locations)

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    data.get('owner_name')  
    print (f"Signup form data: {request.form}")
    conn = connect_db()
    cur = conn.cursor()
    # todo db transaction
    cur.execute("INSERT INTO UserSignup (Email, Username, Password, UserType) VALUES (%s, %s, %s, %s)",
                (data["email"], data["username"], data["password"], data["user_type"]))
    db_user_id = cur.lastrowid
    user_info = {
            "user_id": db_user_id,
            "user_type": data["user_type"],
            "provider_id": None,
            "owner_id": None
      }
  
    if data["user_type"] == "owner":
        cur.execute("INSERT INTO PetOwner (UserID, OwnerName, PetType, Breed, PetName) VALUES (%s, %s, %s, %s, %s)",
                    (db_user_id, data["owner_name"], data["pet_type"], data["breed"], data["pet_name"]))
        owner_id = cur.lastrowid
        user_info["owner_id"] = owner_id
    elif data["user_type"] == "provider": 
        pets_at_home = data.get("pets_at_home", 0)
        children_at_home = data.get("children_at_home", 0)
        repeat_clients = data.get("repeat_clients", 0)
        location_id = int(data.get("location_id"))
        cur.execute("INSERT INTO ServiceProvider (UserID, ProviderName, LocationID, HomeType, YearsExperience, RepeatClients, PetsAtHome, ChildrenAtHome, AboutMe) VALUES  (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (db_user_id, data["provider_name"], data["location_id"], data["home_type"], data["experience"], repeat_clients, pets_at_home, children_at_home, data["about_me"]))
        provider_id = cur.lastrowid
        user_info["provider_id"] = provider_id
    conn.commit()
    return render_template("signup_success.html", info=user_info)
#commenting out because of syntax error
    #except Exception as e:
        #conn.rollback()
        #return f"<h3>Signup failed: {e}</h3><a href='/signup'>Try Again</a>"


    cur.close()
    conn.close()
 

@app.route('/view/<item>')
def view_item(item):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    if item == 'providers':
        cur.execute("SELECT * FROM ServiceProvider")
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        title = "All Service Providers"
    elif item == 'services':
        cur.execute("SELECT * FROM Services")
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        title = "All Services"
    elif item == 'reviews':
        cur.execute("SELECT * FROM Reviews")
        data = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
        title = "All Reviews"
    else:
        data = []
        columns = []
        title = "Invalid view option"

    cur.close()
    conn.close()
    return render_template('view_tables.html', title=title, data=data, columns=columns)

@app.route('/update', methods=['GET', 'POST'])
def update_provider():
    if request.method == 'GET':
        return render_template('update.html')
    try:
        provider_id = request.form['provider_id']
        fields = {
            'HomeType': request.form.get('home_type'),
            'ChildrenAtHome': request.form.get('children_at_home'),
            'YearsExperience': request.form.get('years_experience'),
            'PetsAtHome': request.form.get('pet_at_home'),
            'AboutMe': request.form.get('about_me')
        }
        conn = connect_db()
        cur = conn.cursor()
        updates = []
        values = []
        for key, value in fields.items():
            if value:
                updates.append(f"{key} = %s")
                values.append(value)
        values.append(provider_id)
        if updates:
            query = f"UPDATE ServiceProvider SET {', '.join(updates)} WHERE ProviderID = %s"
            cur.execute(query, tuple(values))
            conn.commit()
            flash("Provider info updated successfully!", "success")
        else:
            flash("No update fields provided.", "warning")
        cur.close()
        conn.close()
    except Exception as e:
        flash(f"Update error: {str(e)}", "danger")
    return redirect('/update')

@app.route('/delete')
def delete_menu():
    return render_template('delete.html')
    
@app.route('/delete_user_form', methods=['GET'])
def delete_user_form():
    return render_template('delete_user_form.html')

@app.route('/delete_booking_form', methods=['GET'])
def delete_booking_form():
    return render_template('delete_booking_form.html')
def delete_menu():
    return render_template('delete.html')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    try:
        userid = request.form['userid']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM PetOwner WHERE UserID = %s", (userid,))
        cur.execute("DELETE FROM ServiceProvider WHERE UserID = %s", (userid,))
        cur.execute("DELETE FROM UserSignup WHERE UserID = %s", (userid,))
        conn.commit()
        cur.close()
        conn.close()
        flash("User deleted successfully!", "success")
    except Exception as e:
        flash(f"User deletion failed: {str(e)}", "danger")
    return redirect('/delete_user_form')

@app.route('/delete_booking', methods=['POST'])
def delete_booking():
    try:
        bookingid = request.form['bookingid']
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("DELETE FROM Booking WHERE BookingID = %s", (bookingid,))
        conn.commit()
        cur.close()
        conn.close()
        flash("Booking deleted successfully!", "success")
    except Exception as e:
        flash(f"Booking deletion failed: {str(e)}", "danger")
    return redirect('/delete_booking_form')

@app.route('/add_review', methods=['GET'])
def add_review():
    return render_template('add_review.html')

@app.route('/submit_review', methods=['POST'])
def submit_review():
    booking_id = request.form['booking_id']
    rating = int(request.form['rating'])
    created_at = request.form['created_at']
    comment = request.form['comment']

    try:
        conn = connect_db()
        cur = conn.cursor(dictionary=True)

        cur.execute("SELECT EndDate FROM Booking WHERE BookingID = %s", (booking_id,))
        result = cur.fetchone()

        if not result:
            return "<h3>Invalid Booking ID</h3>"

        booking_end = result['EndDate']
        if datetime.strptime(created_at, '%Y-%m-%d').date() <= booking_end:
            return "<h3>CreatedAt must be after the EndDate of the booking.</h3>"

        cur.execute("""
            INSERT INTO Reviews (BookingID, Rating, CreatedAt, Comment)
            VALUES (%s, %s, %s, %s)
        """, (booking_id, rating, created_at, comment))

        conn.commit()
        cur.close()
        conn.close()
        return "<h3>Review submitted successfully!</h3><a href='/'>Return Home</a>"

    except Exception as e:
        return f"<h3>Error: {e}</h3>"
@app.route('/')
def home():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT ServiceID, ServiceName FROM Services")
    services = cur.fetchall()
    cur.execute("SELECT DISTINCT Zipcode FROM Location")
    zipcodes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('search_form.html', services=services, zipcodes=zipcodes)

@app.route('/search', methods=['POST'])
def search():
    zipcode = request.form['zipcode']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    service_id = request.form['service_id']

    try:
        conn = connect_db()
        cur = conn.cursor(dictionary=True)

        if zipcode == "ALL":
            zip_condition = ""
            values = [service_id, start_date, end_date, start_date, end_date]
        else:
            zip_condition = "l.Zipcode = %s AND "
            values = [zipcode, service_id, start_date, end_date, start_date, end_date]

        query = f""" 
            SELECT 
                sp.ProviderID,
                sp.ProviderName,
                us.Email,
                sp.HomeType,
                sp.YearsExperience,
                sp.ChildrenAtHome,
                rt.Rate AS ServiceRate,
                COUNT(r.ReviewID) AS total_reviews,
                ROUND(AVG(r.Rating), 2) AS avg_rating
            FROM ServiceProvider sp
            JOIN Location l ON sp.LocationID = l.LocationID
            JOIN UserSignup us ON sp.UserID = us.UserID
            JOIN Rate rt ON sp.ProviderID = rt.ProviderID
            LEFT JOIN Booking b ON sp.ProviderID = b.ProviderID
            LEFT JOIN Reviews r ON r.BookingID = b.BookingID
            WHERE {zip_condition} rt.ServiceID = %s
              AND sp.ProviderID NOT IN (
                  SELECT ProviderID FROM Booking
                  WHERE (%s BETWEEN StartDate AND EndDate)
                     OR (%s BETWEEN StartDate AND EndDate)
                     OR (StartDate BETWEEN %s AND %s)
              )
            GROUP BY 
                sp.ProviderID, sp.ProviderName, us.Email, 
                sp.HomeType, sp.YearsExperience, sp.ChildrenAtHome, rt.Rate
        """

        cur.execute(query, values)
        results = cur.fetchall()

        cur2 = conn.cursor(dictionary=True)
        cur2.execute("SELECT ServiceID, ServiceName FROM Services")
        services = cur2.fetchall()
        cur2.execute("SELECT DISTINCT Zipcode FROM Location")
        zipcodes = cur2.fetchall()

        cur.close()
        cur2.close()
        conn.close()

        return render_template('results.html', data=results, start_date=start_date, end_date=end_date, service_id=service_id,
                               services=services, zipcodes=zipcodes)

    except Exception as e:
        return f"<h3>Error: {e}</h3>"



@app.route('/search_form')
def search_form():
    try:
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT ServiceID, ServiceName FROM Services")
        services = cur.fetchall()
        cur.execute("SELECT DISTINCT Zipcode FROM Location")
        zipcodes = cur.fetchall()
        cur.close()
        conn.close()
        return render_template("search_form.html", services=services, zipcodes=zipcodes)
    except Exception as e:
        return f"<h3>Error: {e}</h3>"

@app.route('/show_query')
def show_query():
    q = """ 
        SELECT sp.ProviderID, sp.ProviderName, us.Email, sp.HomeType,
               sp.YearsExperience, sp.ChildrenAtHome, 
               COUNT(r.ReviewID) AS total_reviews,
               ROUND(AVG(r.Rating), 2) AS avg_rating
        FROM ServiceProvider sp
        JOIN Location l ON sp.LocationID = l.LocationID
        JOIN UserSignup us ON sp.UserID = us.UserID
        JOIN Rate rt ON sp.ProviderID = rt.ProviderID
        LEFT JOIN Booking b ON sp.ProviderID = b.ProviderID
        LEFT JOIN Reviews r ON b.BookingID = r.BookingID
        WHERE [Zip condition] rt.ServiceID = ?
          AND sp.ProviderID NOT IN (
              SELECT ProviderID FROM Booking
              WHERE ([start_date] BETWEEN StartDate AND EndDate)
                 OR ([end_date] BETWEEN StartDate AND EndDate)
                 OR (StartDate BETWEEN [start_date] AND [end_date])
          )
        GROUP BY sp.ProviderID 
    """
    return f"<pre>{q}</pre>"

@app.route('/book', methods=['POST'])
def book_sitter():
    provider_id = request.form['provider_id']
    owner_id = request.form['owner_id']
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    service_id = request.form['service_id']

    try:
        conn = connect_db()
        cur = conn.cursor(dictionary=True)
           # Step 1: Get RateID and Rate
        cur.execute("""
            SELECT RateID, Rate FROM Rate
            WHERE ProviderID = %s AND ServiceID = %s
        """, (provider_id, service_id))
        rate_info = cur.fetchone()

        if not rate_info:
            return "<h3>Error: Rate not found for this provider and service combination.</h3>"

        rate_id = rate_info["RateID"]
        discount_rate = 0.00  # Default (can change later)
        booking_status = "Confirmed"

        query = """
        INSERT INTO Booking (PetOwnerID, ProviderID, ServiceID, StartDate, EndDate, RateID, DiscountRate, BookingDate, BookingStatus)
        VALUES (%s, %s, %s, %s, %s, %s, %s, CURDATE(), %s)
        """
        cur.execute(query,  (owner_id, provider_id, service_id, start_date, end_date,rate_id, discount_rate, booking_status))
        booking_id = cur.lastrowid
        conn.commit()
        # call the function to calculate total price
        cur.execute("SELECT GetTotalBookingPrice(%s) AS TotalPrice", (booking_id,))
        total_price_row = cur.fetchone()
        total_price = total_price_row['TotalPrice'] if total_price_row else "N/A"
         #return confirmation page
        return render_template('booking_success.html',  info={
            "booking_id": booking_id,
            "provider_id": provider_id,
            "owner_id": owner_id,
            "start_date": start_date,
            "end_date": end_date,
            "service_id": service_id,
            "rate_info": rate_info,
            "total_price": total_price
        })
    except Exception as e:
        return f"<h3>Booking Error: {e}</h3>"
        cur.close()
        conn.close()
      

@app.route('/add_rate', methods=['GET', 'POST'])
def add_rate():
    conn = connect_db()
    cur = conn.cursor(dictionary=True)

    if request.method == 'POST':
        try:
            provider_id = request.form['provider_id']
            service_id = request.form['service_id']
            rate = request.form['rate']
            rate_type = request.form['rate_type']
            effective_date = request.form['effective_date']

            cur.execute("""
                INSERT INTO Rate (ProviderID, ServiceID, Rate, RateType, EffectiveDate)
                VALUES (%s, %s, %s, %s, %s)
            """, (provider_id, service_id, rate, rate_type, effective_date))
            conn.commit()
            flash("Rate added successfully!", "success")
            return redirect('/')
        except Exception as e:
            flash(f"Error: {e}", "danger")
            return redirect('/add_rate')

    # For GET: fetch all services
    cur.execute("SELECT DISTINCT s.ServiceID, s.ServiceName FROM Rate r JOIN Services s ON r.ServiceID = s.ServiceID")
    services = cur.fetchall()

    # Fetch distinct rate types from Rate table
    cur.execute("SELECT DISTINCT RateType FROM Rate")
    rate_types = [row["RateType"] for row in cur.fetchall()]

    cur.close()
    conn.close()
    return render_template('add_rate.html', services=services, rate_types=rate_types)
        
@app.route("/analytics")
def analytics():
    return render_template("analytics.html")

@app.route("/analytics/experience_rank")
def experience_rank():
    query = """
        SELECT ProviderID, ProviderName, YearsExperience,
            ROW_NUMBER() OVER (ORDER BY YearsExperience DESC) AS row_num,
            RANK() OVER (ORDER BY YearsExperience DESC) AS ranked,
            DENSE_RANK() OVER (ORDER BY YearsExperience DESC) AS dense_ranked
        FROM ServiceProvider;
     """
    return do_analytical_queries(query, query_name="experience_rank")

@app.route("/analytics/rate_rank")
def rate_rank():
    query = """
        SELECT r.RateID, s.ServiceName, r.rate,
        Rank() OVER (PARTITION BY r.ServiceID ORDER BY r.rate DESC) AS rate_rank
        FROM Rate r
        JOIN Services s ON r.ServiceID = s.ServiceID;
    """
    return do_analytical_queries(query, query_name="rate_rank")

@app.route("/analytics/rolling_bookings")
def rolling_bookings():
    query = """
        SELECT 
    ServiceID,
    ServiceName,
    BookingDate,
    COUNT(*) AS bookings,
    SUM(COUNT(*)) OVER (
        PARTITION BY ServiceID
        ORDER BY BookingDate
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS rolling_3_day_count
FROM (
    SELECT 
        b.ServiceID,
        s.ServiceName,
        DATE(b.StartDate) AS BookingDate
    FROM Booking b
    JOIN Services s ON b.ServiceID = s.ServiceID
) AS bookings_by_day
GROUP BY ServiceID, ServiceName, BookingDate
ORDER BY ServiceID, BookingDate;
    """
    return do_analytical_queries(query, query_name="rolling_bookings")

@app.route("/analytics/vancouver_totals")
def vancouver_totals():
    query = """
        SELECT l.City, b.StartDate, COUNT(*) OVER (PARTITION BY l.City ORDER BY b.StartDate) AS running_total
        FROM Booking b
        JOIN ServiceProvider sp ON b.ProviderID = sp.ProviderID
        JOIN Location l ON sp.LocationID = l.LocationID
        WHERE l.City = 'Vancouver'
    """
    return do_analytical_queries(query, query_name="vancouver_totals")

@app.route("/analytics/provider_totals")
def provider_totals():
    query = """
        SELECT b.ProviderID, sp.ProviderName, b.StartDate,
            COUNT(*) OVER (PARTITION BY b.ProviderID ORDER BY b.StartDate) AS running_total
        FROM Booking b
        JOIN ServiceProvider sp ON b.ProviderID = sp.ProviderID
    """
    return do_analytical_queries(query, query_name="provider_totals")

@app.route("/analytics/monthly_revenue")
def monthly_revenue():
    query = """
        SELECT 
    DATE_FORMAT(b.StartDate, '%Y-%m') AS Month,
    SUM(GetTotalBookingPrice(b.BookingID)) AS TotalRevenue
FROM Booking b
GROUP BY Month
ORDER BY Month;
    """ 
    return do_analytical_queries(query, query_name="monthly_revenue")   

@app.route("/analytics/revenue_rollup")
def revenue_rollup():
    query = """
       SELECT s.ServiceName,
    CASE WHEN GROUPING(l.City) = 1 THEN 'All Cities' ELSE l.City END AS City,
    SUM(GetTotalBookingPrice(b.BookingID)) AS Revenue
FROM Booking b
JOIN Services s ON b.ServiceID = s.ServiceID
JOIN ServiceProvider sp ON b.ProviderID = sp.ProviderID
JOIN Location l ON sp.LocationID = l.LocationID
JOIN PetOwner po ON b.PetOwnerID = po.PetOwnerID
GROUP BY s.ServiceName, l.City WITH ROLLUP;
    """
    return do_analytical_queries(query, query_name="revenue_rollup")

@app.route("/analytics/revenue_moving_avg")
def revenue_moving_avg():
    query = """
        SELECT 
    l.City, 
    b.StartDate,
    ROUND(AVG(GetTotalBookingPrice(b.BookingID)) OVER (
        PARTITION BY l.City
        ORDER BY b.StartDate
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg
FROM Booking b
JOIN ServiceProvider sp ON b.ProviderID = sp.ProviderID
JOIN Location l ON sp.LocationID = l.LocationID;
    """
    return do_analytical_queries(query, query_name="revenue_moving_avg")

def do_analytical_queries(query, query_name=None):
    conn = connect_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(query)
    data = cur.fetchall()
    cols = cur.column_names
    cur.close()
    conn.close()
    return render_template("view_results.html", query=query, data=data, cols=cols, query_name=query_name)

if __name__ == '__main__':
    app.run(debug=True)

