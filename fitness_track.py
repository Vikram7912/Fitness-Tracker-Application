import sqlite3

# Database Setup
def init_db():
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    # Users Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            weight REAL,
            height REAL,
            fitness_goal TEXT
        )
    """)
    
    # Activities Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_type TEXT,
            duration INTEGER,
            distance REAL,
            calories_burned REAL,
            heart_rate INTEGER,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Goals Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            target_weight REAL,
            target_distance REAL,
            target_calories REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Workout Plans Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workout_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            plan_name TEXT,
            exercises TEXT,
            schedule TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Posts Table (Activity Sharing)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            activity_id INTEGER,
            caption TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (activity_id) REFERENCES activities(id)
        )
    """)

    conn.commit()
    conn.close()

# Activity Tracking
def calculate_calories(activity_type, duration):
    activity_met = {
        "running": 10,
        "walking": 4,
        "cycling": 8,
        "swimming": 11
    }
    met = activity_met.get(activity_type.lower(), 5)
    weight = 70  # Assuming an average weight of 70 kg
    calories_burned = (met * weight * duration) / 60
    return calories_burned

def track_activity(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    activity_type = input("Enter activity type (running, walking, cycling, etc.): ")
    duration = int(input("Enter duration (minutes): "))
    distance = float(input("Enter distance covered (km): "))
    calories = calculate_calories(activity_type, duration)
    heart_rate = input("Enter heart rate (optional, press Enter to skip): ")
    heart_rate = int(heart_rate) if heart_rate else None
    cursor.execute("""
        INSERT INTO activities (user_id, activity_type, duration, distance, calories_burned, heart_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, activity_type, duration, distance, calories, heart_rate))
    conn.commit()
    conn.close()
    print("Activity recorded successfully!\n Calories Burned: {:.2f}".format(calories))

def view_activities(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    cursor.execute("SELECT activity_type, duration, distance, calories_burned, heart_rate FROM activities WHERE user_id = ?", (user_id,))
    activities = cursor.fetchall()
    conn.close()
    if activities:
        print("\nYour Activities:")
        for activity in activities:
            print(f"Type: {activity[0]}, Duration: {activity[1]} min, Distance: {activity[2]} km, Calories: {activity[3]}, Heart Rate: {activity[4]}")
    else:
        print("No activities recorded yet.")

# Goal Setting
def set_goals(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    target_weight = float(input("Enter target weight (kg): "))
    target_distance = float(input("Enter target distance to run (km): "))
    target_calories = float(input("Enter target calories to burn: "))
    cursor.execute("""
        INSERT INTO goals (user_id, target_weight, target_distance, target_calories)
        VALUES (?, ?, ?, ?)
    """, (user_id, target_weight, target_distance, target_calories))
    conn.commit()
    conn.close()
    print("Goals set successfully!")

# Workout Plans
def create_workout_plan(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    plan_name = input("Enter workout plan name: ")
    exercises = input("Enter exercises (comma-separated): ")
    schedule = input("Enter workout schedule (e.g., Monday, Wednesday, Friday): ")
    
    cursor.execute("""
        INSERT INTO workout_plans (user_id, plan_name, exercises, schedule)
        VALUES (?, ?, ?, ?)
    """, (user_id, plan_name, exercises, schedule))
    
    conn.commit()
    conn.close()
    print("Workout plan added successfully!")

def view_workout_plans(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT plan_name, exercises, schedule FROM workout_plans WHERE user_id = ?", (user_id,))
    plans = cursor.fetchall()
    
    conn.close()
    
    if plans:
        print("\nYour Workout Plans:")
        for plan in plans:
            print(f"Plan Name: {plan[0]}")
            print(f"Exercises: {plan[1]}")
            print(f"Schedule: {plan[2]}")
            print("-" * 30)
    else:
        print("No workout plans found. Create one to get started!")

def get_predefined_workout_plan(level):
    predefined_plans = {
        "beginner": "Walking, Bodyweight Squats, Push-ups, Yoga",
        "intermediate": "Running, Dumbbell Exercises, Planks, Jump Rope",
        "advanced": "HIIT, Weightlifting, Sprinting, Deadlifts"
    }
    
    return predefined_plans.get(level.lower(), "Invalid fitness level.")

def workout_plans_menu(user_id):
    print("\n1) Create Custom Workout Plan")
    print("2) View My Workout Plans")
    print("3) Get Predefined Workout Plan")
    choice = input("Select an option: ")

    if choice == "1":
        create_workout_plan(user_id)
    elif choice == "2":
        view_workout_plans(user_id)
    elif choice == "3":
        level = input("Enter fitness level (Beginner, Intermediate, Advanced): ")
        print("\nPredefined Workout Plan:")
        print(get_predefined_workout_plan(level))
    else:
        print("Invalid choice. Try again.")

# Share Activity
def social_features(user_id):
    print("\n1) Share activity")
    print("2) View shared activities")
    choice = input("\nSelect an option: ")

    if choice == "1":
        share_activity(user_id)
    elif choice == "2":
        view_shared_activities(user_id)
    else:
        print("Invalid choice. Try again.")

def share_activity(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, activity_type, duration, distance FROM activities WHERE user_id = ?", (user_id,))
    activities = cursor.fetchall()
    
    if not activities:
        print("No activities to share.")
        return
    
    print("\nSelect an activity to share:\n")
    for idx, activity in enumerate(activities, 1):
        print(f"{idx}) {activity[1]} - {activity[2]} min, {activity[3]} km")
    
    choice = int(input("Enter activity number: ")) - 1
    
    if choice < 0 or choice >= len(activities):
        print("Invalid choice.")
        return
    
    activity_id = activities[choice][0]
    caption = input("Enter a caption for your post: ")
    
    cursor.execute("INSERT INTO posts (user_id, activity_id, caption) VALUES (?, ?, ?)", (user_id, activity_id, caption))
    conn.commit()
    conn.close()
    
    print("Activity shared successfully!")

# View Shared Activities
def view_shared_activities(user_id):
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT users.username, activities.activity_type, activities.duration, activities.distance, posts.caption, posts.timestamp 
        FROM posts 
        JOIN users ON posts.user_id = users.id 
        JOIN activities ON posts.activity_id = activities.id
        ORDER BY posts.timestamp DESC
    """)
    
    posts = cursor.fetchall()
    conn.close()
    
    if posts:
        print("\nShared Activities:")
        for post in posts:
            print(f"{post[0]}: {post[4]} ({post[1]}, {post[2]} min, {post[3]} km) - {post[5]}")
    else:
        print("No shared activities yet.")


# User Authentication
def sign_up():
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    username = input("Enter username: ")
    password = input("Enter password: ")
    age = int(input("Enter your age: "))
    weight = float(input("Enter your weight (kg): "))
    height = float(input("Enter your height (cm): "))
    fitness_goal = input("Enter your fitness goal (e.g., weight loss, muscle gain, endurance): ")

    try:
        cursor.execute("""
            INSERT INTO users (username, password, age, weight, height, fitness_goal) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (username, password, age, weight, height, fitness_goal))
        
        conn.commit()
        print("Account created successfully!")
    except sqlite3.IntegrityError:
        print("Username already exists! Try again.")
    
    conn.close()


def log_in():
    conn = sqlite3.connect("fitness_tracker.db")
    cursor = conn.cursor()
    
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute("""
        SELECT id, age, weight, height, fitness_goal 
        FROM users WHERE username = ? AND password = ?
    """, (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    if user:
        user_id, age, weight, height, fitness_goal = user
        print("\nLogin successful!\n")
        print(f"Welcome, {username}!")
        print(f"Age: {age} | Weight: {weight} kg | Height: {height} cm")
        print(f"Fitness Goal: {fitness_goal}\n")
        main_menu(user_id)
    else:
        print("Invalid credentials. Try again.")


# Main Menu
def main_menu(user_id):
    while True:
        print("\n1) Activity Tracking")
        print("2) View Activities")
        print("3) Workout Plans")
        print("4) Goal Setting")
        print("5) Social Features")
        print("6) Log out or Exit")
        
        choice = input("Select an option: ")
        if choice == "1":
            track_activity(user_id)
        elif choice == "2":
            view_activities(user_id)
        elif choice == "3":
            workout_plans_menu(user_id)
        elif choice == "4":
            set_goals(user_id)
        elif choice == "5":
            social_features(user_id)
        elif choice == "6":
            break
        else:
            print("Invalid option. Try again.")


# Main Function
def main():
    init_db()
    while True:
        print("\n1) Sign Up")
        print("2) Log In")
        print("3) Exit")
        choice = input("Select an option: ")
        if choice == "1":
            sign_up()
        elif choice == "2":
            log_in()
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")

main()
