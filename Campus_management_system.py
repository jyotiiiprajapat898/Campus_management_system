import sqlite3
from datetime import datetime

db = sqlite3.connect("campus_booking.db")
db.execute("""CREATE TABLE IF NOT EXISTS resources(
 id INTEGER PRIMARY KEY, name TEXT)""")
db.execute("""CREATE TABLE IF NOT EXISTS bookings(
 id INTEGER PRIMARY KEY, student TEXT, resource TEXT, date TEXT,
 start TEXT, end TEXT, purpose TEXT, status TEXT)""")
if db.execute("SELECT COUNT(*) FROM resources").fetchone()[0] == 0:
    db.executemany("INSERT INTO resources(name) VALUES(?)", [
        ("Seminar Hall A",), ("Computer Lab 1",), ("Projector",), ("GPU Server",)])
db.commit()

def show_bookings():
    rows = db.execute("SELECT * FROM bookings ORDER BY id DESC").fetchall()
    print("\n--- BOOKINGS ---")
    if not rows:
        print("No bookings yet.")
    for r in rows:
        print(f"ID:{r[0]} | {r[1]} | {r[2]} | {r[3]} | {r[4]}-{r[5]} | {r[6]} | {r[7]}")

while True:
    print("\n=== SMART CAMPUS RESOURCE BOOKING ===")
    print("1. Book resource")
    print("2. View bookings")
    print("3. Cancel booking")
    print("4. Exit")
    choice = input("Choose option: ").strip()

    if choice == "1":
        student = input("Student name: ").strip()
        print("Resources:", ", ".join(r[0] for r in db.execute("SELECT name FROM resources")))
        resource = input("Resource name: ").strip()
        date = input("Date (YYYY-MM-DD): ").strip()
        start = input("Start time (HH:MM): ").strip()
        end = input("End time (HH:MM): ").strip()
        purpose = input("Purpose: ").strip()

        if not all([student, resource, date, start, end, purpose]):
            print("Please fill in every field.")
            continue
        try:
            d = datetime.strptime(date, "%Y-%m-%d").date()
            s = datetime.strptime(start, "%H:%M")
            e = datetime.strptime(end, "%H:%M")
        except ValueError:
            print("Invalid date/time format.")
            continue
        if d < datetime.today().date() or e <= s:
            print("Invalid date or time range.")
            continue
        valid = [r[0] for r in db.execute("SELECT name FROM resources")]
        if resource not in valid:
            print("Resource not found. Enter a name from the list.")
            continue
        conflict = db.execute("""SELECT COUNT(*) FROM bookings
            WHERE resource=? AND date=? AND status='Pending'
            AND start < ? AND end > ?""", (resource, date, end, start)).fetchone()[0]
        if conflict:
            print("This resource is already booked for that time.")
            continue
        db.execute("INSERT INTO bookings(student,resource,date,start,end,purpose,status) VALUES(?,?,?,?,?,?,?)",
                   (student, resource, date, start, end, purpose, "Pending"))
        db.commit()
        print("Booking submitted! Status: Pending")

    elif choice == "2":
        show_bookings()

    elif choice == "3":
        show_bookings()
        try:
            booking_id = int(input("Enter booking ID to cancel: "))
        except ValueError:
            print("Please enter a valid ID.")
            continue
        cur = db.execute("UPDATE bookings SET status='Cancelled' WHERE id=? AND status='Pending'", (booking_id,))
        db.commit()
        print("Booking cancelled." if cur.rowcount else "Pending booking ID not found.")

    elif choice == "4":
        break
    else:
        print("Invalid option. Choose 1-4.")

db.close()
print("Goodbye!")