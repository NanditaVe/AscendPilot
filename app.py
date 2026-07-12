import os

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import mysql.connector
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = "ascendpilot_secret_key_validation_token"

# ==================== FLASK-MAIL CONFIGURATION ====================
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'team.ascendpilot@gmail.com'
app.config['MAIL_PASSWORD'] = 'ascendpilot2026'
app.config['MAIL_DEFAULT_SENDER'] = ('AscendPilot Team', 'team.ascendpilot@gmail.com')

mail = Mail(app)

# Database Configuration Connection Utility
def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            user=os.environ.get("DB_USER", "root"),
            password=os.environ.get("DB_PASSWORD", "nandita"), 
            database=os.environ.get("DB_NAME", "ascendpilot"),
            # Cloud port mapping handles remote dynamic port from environment variables
            port=int(os.environ.get("DB_PORT", 3306)),
            # Cloud databases (Aiven) demand active SSL parameters validation
            ssl_disabled=False
        )
    except Exception as e:
        print("Database Connection Error:", e)
        return None

# ==================== MAIN HOME REGISTRY ROUTE ====================
@app.route("/")
def index():
    return render_template("maindesk.html")

# ==================== LOGIN PAGES LAYOUTS ====================
@app.route("/login")
def login_page():
    return render_template("login.html") 

@app.route("/admin")
def admin_page():
    return render_template("admin.html") 

# ==================== AUTHENTICATION: STUDENT LOGIN & REGISTER ====================
@app.route("/api/auth/login", methods=["POST"])
def api_login():
    try:
        data = request.get_json()
        email = data.get("email", "").strip().lower()
        password = data.get("password")

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database linkage failure!"}), 500

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        user_record = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if user_record:
            session['user_id'] = user_record['user_id'] 
            session['email'] = user_record['email']
            session['first_name'] = user_record['first_name']
            session['last_name'] = user_record['last_name']
            return jsonify({"success": True, "message": "Authentication successful!"})
        
        return jsonify({"success": False, "message": "Invalid credentials!"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    try:
        data = request.get_json()
        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        email = data.get("email", "").strip().lower()
        password = data.get("password")

        if not first_name or not email or not password:
            return jsonify({"success": False, "message": "Required parameters are incomplete!"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database connection lost!"}), 500

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"success": False, "message": "Email already registered!"}), 409

        query = "INSERT INTO users (first_name, last_name, email, password_hash) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (first_name, last_name, email, password))
        conn.commit()
        
        cursor.close()
        conn.close()
        return jsonify({"success": True, "message": "Account created successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== DYNAMIC ADMIN LOGIN AUTHENTICATION ====================
@app.route("/api/admin-login", methods=["POST"])
def api_admin_login():
    try:
        data = request.get_json()
        uid = data.get("uid", "").strip()
        password = data.get("password")

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database linkage failure!"}), 500

        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM admins WHERE admin_id = %s AND password_hash = %s"
        cursor.execute(query, (uid, password))
        admin_record = cursor.fetchone()
        
        cursor.close()
        conn.close()

        if admin_record:
            session['admin_logged_in'] = True
            session['admin_user'] = admin_record['admin_id']
            return jsonify({"success": True, "message": "Authentication successful!"})
        
        return jsonify({"success": False, "message": "Invalid Admin credentials!"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== ADVANCED AI LEAD QUALIFICATION & SCORING PIPELINE ====================
def compute_ai_lead_score(lead_record):
    """
    EFOS Core Business Architecture Logic Layer Validation Matrix.
    Phase 3 Algorithm Pattern to compute weights dynamically.
    """
    interest_score = 0
    education_score = 0
    engagement_score = 0

    # 1. Interest-Based Rule Validation
    course_interest = str(lead_record.get('course_interest', '')).upper()
    if "BTECH" in course_interest or "AI" in course_interest or "COMPUTING" in course_interest:
        interest_score += 20  # Premium Engineering Systems
    elif "DATA" in course_interest or "SCIENCE" in course_interest:
        interest_score += 15
    else:
        interest_score += 10

    # 2. Education-Based Rule Validation
    qualification = str(lead_record.get('qualification', ''))
    if "12th Completed Student" in qualification:
        education_score += 20  # Direct Higher Secondary Engineering Prospects
    elif "Pursuing Graduation" in qualification or "Diploma Holder" in qualification:
        education_score += 15
    else:
        education_score += 10

    # 3. Structural Engagement Validation Matrix
    # Simulated weights tracking interaction footprints (Brochure Downloads, Form OTP Syncs)
    engagement_score += 15  # Downloaded Brochures Buffer
    engagement_score += 20  # Visited platform tracking thresholds

    total_score = interest_score + education_score + engagement_score
    return min(total_score, 100)

@app.route("/api/admin/fetch-leads")
def api_fetch_leads():
    if not session.get('admin_logged_in'):
        return jsonify({"success": False, "message": "Unauthorized Access!"}), 401

    conn = get_db_connection()
    if not conn:
        return jsonify({"success": False, "message": "Database linkage breakdown!"}), 500

    try:
        cursor = conn.cursor(dictionary=True)
        
        # Pull transactional metadata linking users credentials and status lead scores
        query = """
            SELECT user_id, full_name, phone, location as city, qualification, 
                   form_status, ai_score, 'Website Form' as source, 
                   'Admission in BTech' as course_interest, created_at
            FROM student_leads
            ORDER BY ai_score DESC
        """
        cursor.execute(query)
        leads = cursor.fetchall()
        
        processed_leads = []
        for lead in leads:
            # Dynamically inject computed real-time metrics aligning baseline tables
            computed_score = compute_ai_lead_score({
                "course_interest": lead['course_interest'],
                "qualification": lead['qualification']
            })
            
            # Save computational telemetry back to matrix arrays
            lead['ai_score'] = computed_score
            
            # Categorize Leads Dynamic Labels
            if computed_score >= 71:
                lead['category'] = "🔥 HOT LEAD"
            elif computed_score >= 41:
                lead['category'] = "⚡ WARM LEAD"
            else:
                lead['category'] = "❄️ COLD LEAD"
                
            processed_leads.append(lead)
            
        cursor.close()
        conn.close()
        return jsonify({"success": True, "leads": processed_leads})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== ROUTE REGISTRATION FOR REDESIGNED INTERFACES ====================
@app.route("/admin/leads-registry")
def admin_leads_registry_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_page'))
    return render_template("admin_leads.html")

@app.route("/api/admin/generate-message", methods=["POST"])
def api_admin_generate_message():
    """
    Phase 4 AI Personalization Logic Interface.
    Generates dynamic prompt outputs matching student tracking payloads.
    """
    data = request.get_json()
    name = data.get("name", "Student")
    interest = data.get("interest", "Higher Education")
    city = data.get("city", "India")
    
    # Custom Context Template Processing matching Real Business Context
    whatsapp_content = f"Hi {name},\n\nI noticed you're exploring Admissions in {interest} from {city}. EFOS offers an industry-oriented {interest} Program with 100% Placement Assistance, practical projects, corporate mentorship, and elite certification.\n\nWould you like to learn more?"
    
    return jsonify({"success": True, "message": whatsapp_content})

# ==================== ADMIN SYSTEM INTERFACE GATEWAYS ====================
@app.route("/admin/dashboard")
def admin_dashboard_page():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_page'))
    return render_template("admin_dashboard.html")

# ==================== DYNAMIC MOCK EMAIL OTP MODULE ====================
@app.route("/api/send-email-otp", methods=["POST"])
def api_send_email_otp():
    data = request.get_json()
    email = data.get("email", "").strip()
    if not email:
        return jsonify({"success": False, "message": "Email cannot be blank!"}), 400
    return jsonify({"success": True, "message": "OTP dispatched successfully."})

# ==================== STUDENT LEAD PROFILE SYNCHRONIZATION ====================
@app.route("/api/register-lead", methods=["POST"])
def api_register_lead():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Unauthorized!"}), 401

        data = request.get_json()
        mode = data.get("mode", "create")
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        city = data.get("city", "").strip()
        qualification = data.get("qualification", "").strip()

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database linkage failure!"}), 500
        
        cursor = conn.cursor(dictionary=True)
        parent_user_id = session.get('user_id')

        if mode == "create":
            query = """
                INSERT INTO student_leads (user_id, full_name, phone, location, qualification, form_status, ai_score)
                VALUES (%s, %s, %s, %s, %s, 'Submitted', 95)
            """
            cursor.execute(query, (parent_user_id, name, phone, city, qualification))
        else:
            query = """
                UPDATE student_leads 
                SET full_name = %s, location = %s, qualification = %s
                WHERE user_id = %s
            """
            cursor.execute(query, (name, city, qualification, parent_user_id))

        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"success": True, "message": "Profile synced successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== MENTOR SLOT BOOKING WITH AUTO-OVERWRITE ====================
@app.route("/api/book-mentor-slot", methods=["POST"])
def api_book_mentor_slot():
    try:
        if 'user_id' not in session:
            return jsonify({"success": False, "message": "Session unauthorized!"}), 401

        data = request.get_json()
        student_name = data.get("name", "").strip()
        booking_date = data.get("date", "").strip()
        booking_time = data.get("time", "").strip() 

        if not student_name or not booking_date or not booking_time:
            return jsonify({"success": False, "message": "Please fill all scheduling parameters!"}), 400

        try:
            hour = int(booking_time.split(":")[0])
            if hour < 10 or hour >= 17:
                return jsonify({"success": False, "message": "Slots are restricted between 10:00 AM and 5:00 PM!"}), 400
        except Exception:
            return jsonify({"success": False, "message": "Invalid time format!"}), 400

        conn = get_db_connection()
        if not conn:
            return jsonify({"success": False, "message": "Database linkage failure!"}), 500
        
        cursor = conn.cursor(dictionary=True)
        parent_user_id = session.get('user_id')

        # ✅ OVERWRITE RULE: Delete old slots booked by this user first
        delete_query = "DELETE FROM mentor_bookings WHERE user_id = %s"
        cursor.execute(delete_query, (parent_user_id,))

        # Insert the fresh booking slot
        query = """
            INSERT INTO mentor_bookings (user_id, student_name, booking_date, booking_time)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (parent_user_id, student_name, booking_date, booking_time))
        conn.commit()
        
        cursor.close()
        conn.close()

        # Automated confirmation email logic
        try:
            student_email = session.get('email')
            if student_email:
                msg = Message("🚀 Mentor Session Booking Confirmed! - AscendPilot", recipients=[student_email])
                msg.body = f"Hello {student_name},\n\nYour mentorship session has been scheduled for {booking_date} at {booking_time}.\n\nBest Regards,\nTeam AscendPilot"
                mail.send(msg)
        except Exception as mail_err:
            print("Email Pipeline Mismatch: ", mail_err)
        
        return jsonify({"success": True, "message": "Mentor session booked successfully! Previous slots overwritten."})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ==================== STUDENT CENTRAL DASHBOARD CORE ====================
@app.route("/dashboard")
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    parent_user_id = session.get('user_id')
    pref_filled = 0
    student_details = {}
    active_booking = None
    
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM student_leads WHERE user_id = %s LIMIT 1", (parent_user_id,))
        result = cursor.fetchone()
        
        if result:
            pref_filled = 1
            student_details = result
            session['phone'] = result['phone']
            session['location'] = result['location']
            session['qualification'] = result['qualification']
            session['full_name'] = result['full_name']
            
        # Fetch the latest upcoming booking
        query = """
            SELECT booking_date, booking_time 
            FROM mentor_bookings 
            WHERE user_id = %s AND CONCAT(booking_date, ' ', booking_time) >= NOW()
            ORDER BY booking_date ASC, booking_time ASC LIMIT 1
        """
        cursor.execute(query, (parent_user_id,))
        booking_res = cursor.fetchone()
        
        if booking_res:
            active_booking = {
                "date": str(booking_res['booking_date']),
                "time": str(booking_res['booking_time'])
            }
            
        cursor.close()
        conn.close()

    return render_template("dashboard.html", user=session, pref_filled=pref_filled, student=student_details, booking=active_booking)

# ==================== LOGOUT MODULE ====================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True, port=5000)