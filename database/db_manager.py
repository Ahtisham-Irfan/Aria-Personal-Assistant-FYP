import sqlite3
import os
import datetime


class DatabaseManager:
    def __init__(self):
        # --- Database Path ---
        self.db_path = os.path.join(
            'database', 'aria.db'
        )

        # --- Create database folder ---
        os.makedirs('database', exist_ok=True)

        # --- Initialize database ---
        self.connection = None
        self.cursor = None
        self.connect()
        self.create_tables()

        print("Database initialized successfully!")

    # ----------------------------
    # Connect to Database
    # ----------------------------
    def connect(self):
        try:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False
            )
            self.cursor = self.connection.cursor()
            print(f"Connected to database: "
                  f"{self.db_path}")
        except Exception as e:
            print(f"Database connection error: {e}")

    # ----------------------------
    # Create All Tables
    # ----------------------------
    def create_tables(self):
        try:
            # --- Users Table ---
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY
                        AUTOINCREMENT,
                    username TEXT NOT NULL
                        DEFAULT "User",
                    role TEXT DEFAULT "user",
                    created_date TEXT NOT NULL
                )
            ''')

            # --- Command Log Table ---
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS
                command_log (
                    command_id INTEGER PRIMARY KEY
                        AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    command_text TEXT NOT NULL,
                    command_type TEXT,
                    aria_response TEXT,
                    execution_time TEXT NOT NULL,
                    status TEXT DEFAULT "success",
                    FOREIGN KEY (user_id)
                        REFERENCES users (user_id)
                )
            ''')

            # --- System Settings Table ---
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS
                system_settings (
                    setting_id INTEGER PRIMARY KEY
                        AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    setting_name TEXT NOT NULL,
                    setting_value TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    FOREIGN KEY (user_id)
                        REFERENCES users (user_id)
                )
            ''')

            # --- Session Log Table ---
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS
                session_log (
                    session_id INTEGER PRIMARY KEY
                        AUTOINCREMENT,
                    user_id INTEGER DEFAULT 1,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    total_commands INTEGER
                        DEFAULT 0,
                    FOREIGN KEY (user_id)
                        REFERENCES users (user_id)
                )
            ''')

            self.connection.commit()

            # --- Create default user ---
            self.create_default_user()

            print("All tables created successfully!")

        except Exception as e:
            print(f"Table creation error: {e}")

    # ----------------------------
    # Create Default User
    # ----------------------------
    def create_default_user(self):
        try:
            # Check if default user exists
            self.cursor.execute('''
                SELECT * FROM users
                WHERE user_id = 1
            ''')
            user = self.cursor.fetchone()

            if not user:
                now = datetime.datetime.now()\
                    .strftime("%Y-%m-%d %H:%M:%S")
                self.cursor.execute('''
                    INSERT INTO users
                    (username, role, created_date)
                    VALUES (?, ?, ?)
                ''', ("User", "user", now))
                self.connection.commit()
                print("Default user created!")

        except Exception as e:
            print(f"Default user error: {e}")

    # ----------------------------
    # Log Command
    # ----------------------------
    def log_command(
        self,
        command_text,
        command_type,
        aria_response,
        status="success"
    ):
        try:
            now = datetime.datetime.now()\
                .strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute('''
                INSERT INTO command_log (
                    user_id,
                    command_text,
                    command_type,
                    aria_response,
                    execution_time,
                    status
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                1,
                command_text,
                command_type,
                aria_response,
                now,
                status
            ))
            self.connection.commit()

        except Exception as e:
            print(f"Log command error: {e}")

    # ----------------------------
    # Start Session
    # ----------------------------
    def start_session(self):
        try:
            now = datetime.datetime.now()\
                .strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute('''
                INSERT INTO session_log (
                    user_id,
                    start_time,
                    total_commands
                ) VALUES (?, ?, ?)
            ''', (1, now, 0))
            self.connection.commit()

            # Return session id
            return self.cursor.lastrowid

        except Exception as e:
            print(f"Start session error: {e}")
            return None

    # ----------------------------
    # End Session
    # ----------------------------
    def end_session(self, session_id):
        try:
            now = datetime.datetime.now()\
                .strftime("%Y-%m-%d %H:%M:%S")

            # Get total commands in session
            self.cursor.execute('''
                SELECT COUNT(*) FROM command_log
                WHERE execution_time >= (
                    SELECT start_time
                    FROM session_log
                    WHERE session_id = ?
                )
            ''', (session_id,))

            total = self.cursor.fetchone()[0]

            self.cursor.execute('''
                UPDATE session_log
                SET end_time = ?,
                    total_commands = ?
                WHERE session_id = ?
            ''', (now, total, session_id))
            self.connection.commit()

        except Exception as e:
            print(f"End session error: {e}")

    # ----------------------------
    # Save Setting
    # ----------------------------
    def save_setting(self, name, value):
        try:
            now = datetime.datetime.now()\
                .strftime("%Y-%m-%d %H:%M:%S")

            # Check if setting exists
            self.cursor.execute('''
                SELECT * FROM system_settings
                WHERE setting_name = ?
                AND user_id = 1
            ''', (name,))
            existing = self.cursor.fetchone()

            if existing:
                # Update existing setting
                self.cursor.execute('''
                    UPDATE system_settings
                    SET setting_value = ?,
                        last_updated = ?
                    WHERE setting_name = ?
                    AND user_id = 1
                ''', (value, now, name))
            else:
                # Insert new setting
                self.cursor.execute('''
                    INSERT INTO system_settings (
                        user_id,
                        setting_name,
                        setting_value,
                        last_updated
                    ) VALUES (?, ?, ?, ?)
                ''', (1, name, value, now))

            self.connection.commit()

        except Exception as e:
            print(f"Save setting error: {e}")

    # ----------------------------
    # Get Setting
    # ----------------------------
    def get_setting(self, name, default=None):
        try:
            self.cursor.execute('''
                SELECT setting_value
                FROM system_settings
                WHERE setting_name = ?
                AND user_id = 1
            ''', (name,))
            result = self.cursor.fetchone()
            if result:
                return result[0]
            return default

        except Exception as e:
            print(f"Get setting error: {e}")
            return default

    # ----------------------------
    # Get Command History
    # ----------------------------
    def get_history(self, limit=50):
        try:
            self.cursor.execute('''
                SELECT
                    command_text,
                    aria_response,
                    execution_time,
                    status
                FROM command_log
                ORDER BY execution_time DESC
                LIMIT ?
            ''', (limit,))
            return self.cursor.fetchall()

        except Exception as e:
            print(f"Get history error: {e}")
            return []

    # ----------------------------
    # Get Session Stats
    # ----------------------------
    def get_stats(self):
        try:
            # Total commands
            self.cursor.execute('''
                SELECT COUNT(*) FROM command_log
            ''')
            total_commands = self.cursor\
                .fetchone()[0]

            # Total sessions
            self.cursor.execute('''
                SELECT COUNT(*) FROM session_log
            ''')
            total_sessions = self.cursor\
                .fetchone()[0]

            # Most used command
            self.cursor.execute('''
                SELECT command_type, COUNT(*)
                as count
                FROM command_log
                GROUP BY command_type
                ORDER BY count DESC
                LIMIT 1
            ''')
            most_used = self.cursor.fetchone()

            return {
                'total_commands': total_commands,
                'total_sessions': total_sessions,
                'most_used': most_used[0]
                if most_used else "None"
            }

        except Exception as e:
            print(f"Get stats error: {e}")
            return {}

    # ----------------------------
    # Clear History
    # ----------------------------
    def clear_history(self):
        try:
            self.cursor.execute('''
                DELETE FROM command_log
            ''')
            self.connection.commit()
            print("History cleared!")

        except Exception as e:
            print(f"Clear history error: {e}")

    # ----------------------------
    # Close Connection
    # ----------------------------
    def close(self):
        try:
            if self.connection:
                self.connection.close()
                print("Database connection closed!")
        except Exception as e:
            print(f"Close error: {e}")