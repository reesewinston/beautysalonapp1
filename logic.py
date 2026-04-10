from datetime import date, datetime, timedelta
from db import connect_db


def load_categories_from_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select distinct specialty
        from stylists
        where specialty is not null
        order by specialty
    """)

    categories = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return categories


def load_services_by_category(category):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select distinct s.service_name
        from services s
        join stylists st on s.stylist_id = st.stylist_id
        where st.specialty = %s
        order by s.service_name
    """, (category,))

    services = [row[0] for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return services


def load_stylists_for_service(service_name):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select
            st.stylist_id,
            concat(st.first_name, ' ', st.last_name) as stylist_name,
            st.specialty,
            s.service_id,
            s.service_name,
            s.price,
            s.duration,
            round(avg(r.rating), 1) as avg_rating
        from services s
        join stylists st on s.stylist_id = st.stylist_id
        left join reviews r on st.stylist_id = r.stylist_id
        where s.service_name = %s
        group by st.stylist_id, stylist_name, st.specialty, s.service_id, s.service_name, s.price, s.duration
        order by avg_rating desc, s.price asc
    """, (service_name,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()
    return rows


def _timedelta_to_db_str(td):
    """Convert MySQL timedelta (e.g. datetime.timedelta(seconds=36000)) to 'HH:MM:SS'."""
    total_seconds = int(td.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"


def generate_time_slots():
    """Return display slots from 10:00 AM ET to 5:00 PM ET in 30-min increments."""
    start = datetime.strptime("10:00", "%H:%M")
    end   = datetime.strptime("17:00", "%H:%M")

    slots = []
    current = start
    while current <= end:
        # strftime gives e.g. "10:00 AM" — strip leading zero on hour
        display = current.strftime("%I:%M %p").lstrip("0") + " ET"
        slots.append(display)
        current += timedelta(minutes=30)

    return slots


def _display_to_db_time(display_time):
    """Convert '10:00 AM ET' → '10:00:00' for DB storage/comparison."""
    clean = display_time.replace(" ET", "").strip()
    return datetime.strptime(clean, "%I:%M %p").strftime("%H:%M:%S")


def get_available_times(stylist_id, appointment_date):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select appointment_time
        from appointments
        where stylist_id = %s
          and appointment_date = %s
          and appointment_status in ('scheduled', 'completed')
    """, (stylist_id, appointment_date))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # MySQL returns TIME columns as timedelta — convert safely
    booked_times = set()
    for row in rows:
        val = row[0]
        if isinstance(val, timedelta):
            booked_times.add(_timedelta_to_db_str(val))
        else:
            # fallback: already a string or datetime.time
            booked_times.add(str(val))

    all_slots = generate_time_slots()
    available_times = [
        slot for slot in all_slots
        if _display_to_db_time(slot) not in booked_times
    ]

    return available_times


def get_or_create_client(first_name, last_name, phone, email):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select client_id
        from clients
        where phone = %s
        limit 1
    """, (phone,))
    existing = cursor.fetchone()

    if existing:
        client_id = existing[0]
    else:
        cursor.execute("""
            insert into clients (first_name, last_name, phone, email)
            values (%s, %s, %s, %s)
        """, (first_name, last_name, phone, email))
        conn.commit()
        client_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return client_id


def create_appointment(client_id, stylist_id, service_id, appointment_date, appointment_time):
    conn = connect_db()
    cursor = conn.cursor()

    # convert display time (e.g. "10:00 AM ET") to DB format "10:00:00"
    db_time = _display_to_db_time(appointment_time) if " ET" in appointment_time else appointment_time

    cursor.execute("""
        select appointment_id
        from appointments
        where stylist_id = %s
          and appointment_date = %s
          and appointment_time = %s
          and appointment_status in ('scheduled', 'completed')
    """, (stylist_id, appointment_date, db_time))

    taken = cursor.fetchone()
    if taken:
        cursor.close()
        conn.close()
        return None

    cursor.execute("""
        insert into appointments (
            client_id, stylist_id, service_id, appointment_date, appointment_time, appointment_status
        )
        values (%s, %s, %s, %s, %s, 'scheduled')
    """, (client_id, stylist_id, service_id, appointment_date, db_time))

    conn.commit()
    appointment_id = cursor.lastrowid

    cursor.close()
    conn.close()
    return appointment_id


def get_bookings_by_phone(phone):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select
            a.appointment_id,
            concat(c.first_name, ' ', c.last_name),
            concat(st.first_name, ' ', st.last_name),
            s.service_name,
            a.appointment_date,
            a.appointment_time,
            a.appointment_status
        from appointments a
        join clients c on a.client_id = c.client_id
        join stylists st on a.stylist_id = st.stylist_id
        join services s on a.service_id = s.service_id
        where c.phone = %s
        order by a.appointment_date desc, a.appointment_time desc
    """, (phone,))

    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    # format appointment_time (timedelta) into readable 12-hour ET time
    formatted = []
    for row in rows:
        row = list(row)
        val = row[5]
        if isinstance(val, timedelta):
            db_str = _timedelta_to_db_str(val)
            dt = datetime.strptime(db_str, "%H:%M:%S")
            row[5] = dt.strftime("%I:%M %p").lstrip("0") + " ET"
        formatted.append(row)

    return formatted


def submit_review_by_phone(phone, stylist_id, rating, review_text):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        select client_id
        from clients
        where phone = %s
        limit 1
    """, (phone,))
    client = cursor.fetchone()

    if not client:
        cursor.close()
        conn.close()
        return "no_client"

    client_id = client[0]

    cursor.execute("""
        select appointment_id
        from appointments
        where client_id = %s
          and stylist_id = %s
          and appointment_status = 'completed'
        limit 1
    """, (client_id, stylist_id))
    completed = cursor.fetchone()

    if not completed:
        cursor.close()
        conn.close()
        return "not_completed"

    cursor.execute("""
        insert into reviews (client_id, stylist_id, rating, client_review, review_date)
        values (%s, %s, %s, %s, %s)
    """, (
        client_id,
        stylist_id,
        rating,
        review_text,
        date.today()
    ))

    conn.commit()

    cursor.close()
    conn.close()
    return "success"