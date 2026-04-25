import customtkinter as ctk
import pyodbc
from PIL import Image, ImageTk
import random
import time
import threading

# SQL Server connection details
DRIVER_NAME = 'SQL SERVER'
SERVER_NAME = 'Amr\SQLEXPRESS'
DATABASE_NAME = "cyber_user"

# Connection string
connection_string = f"""
    DRIVER={DRIVER_NAME};
    SERVER={SERVER_NAME};
    DATABASE={DATABASE_NAME};
    Trusted_Connection=yes;
"""

plaintext = [
    "xqtrve",
    "bknzup",
    "mztoar",
    "vycsam",
    "qblure",
    "zrdkup",
    "kvsqom"
]

key = [
    "1432",
    "jdyf", 
    "2413",
    "axcz",
    "4123",
    "abzt",
    "acdx"
]

cipherText = [
    "XVRTQE",
    "KPZBUN",
    "TMAOZR",
    "VACYMS", 
    "BELUQR",
    "ZURPKD",
    "KOVMSQ"
]



plaintextt = [
    "acv",
    "fgt",
    "nhd",
    "joiytr",
    "hjdus",
    "kpsf"
]

cipherTextt = [
    "97198x1354x2",
    "102206x1348x2128x3",
    "110208x1300x2",
    "106222x1315x2484x3580x4684x5",
    "104212x1300x2468x3575x4",
    "107224x1345x2408x3"
]


plaintext_Rsa = [
    "15",
    "12",
    "7",
    "12",
    "17",
    "18"
]

cipherText_Rsa = [
    "71",
    "12",
    "58",
    "177",
    "140",
    "18"
]

key_Rsa = [
    "p:7,Q:11,e:17",
    "p:3,Q:11,e:7",
    "p:5,Q:13,e:7",
    "p:11,Q:17,e:7",
    "p:13,Q:11,e:257",
    "p:13,Q:3,e:769"
]

# Setup CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

class SimpleGame:
    def __init__(self, root):
        self.root = root
        self.root.geometry("650x500")
        self.root.title("Simple Game")

        self.connection = None
        self.image_ref = None
        self.medal_images = []
        self.background_label = None  # Initialize background_label as None

        # Colors
        self.primary_color = "#00FFBF"
        self.bg_color = "#1A2A44"

        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Load and set background image for homepage only
        try:
            self.background_image = Image.open(r"C:\Users\3mr\Desktop\image.png")
            self.background_image = self.background_image.resize((800, 600), Image.LANCZOS)
            self.background_photo = ImageTk.PhotoImage(self.background_image)

            self.background_label = ctk.CTkLabel(self.main_frame, image=self.background_photo, text="")
            self.background_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.background_label.lower()  # Ensure background is at z-index 1 (lowest layer)
        except Exception as e:
            print(f"Error loading background image: {e}")

        # Title
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="Crypto Challenge",
            font=("Roboto", 32, "bold"),
            text_color=self.primary_color
        )
        title_label.place(relx=0.5, rely=0.2, anchor="center")

        # Buttons with increased margin
        buttons = [
            ("Level One", self.level_one, 0.35),
            ("Level Two", self.level_two, 0.47),
            ("Level Three", self.level_three, 0.59),
            ("Leaderboard", self.standard_level, 0.71)
        ]

        for text, command, rely in buttons:
            btn = ctk.CTkButton(
                self.main_frame,
                text=text,
                command=command,
                fg_color=self.primary_color,
                hover_color="#00CC99",
                text_color="#1A2A44",
                font=("Roboto", 16, "bold"),
                width=200,
                height=50,
                corner_radius=25,
                border_width=0
            )
            btn.place(relx=0.5, rely=rely, anchor="center")

        self.connection = self.create_connection()

    def create_connection(self):
        try:
            connection = pyodbc.connect(connection_string)
            print("Database connection successful.")
            return connection
        except Exception as e:
            print(f"Error connecting to database: {e}")
            return None

    def close_connection(self):
        if self.connection:
            self.connection.close()
            print("Database connection closed.")

    def update_score(self, user_id, score_increment):
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE Users SET score = score + ? WHERE user_id = ?",
                    (score_increment, user_id)
                )
                self.connection.commit()
                cursor.close()
                print(f"Score updated by {score_increment} successfully.")
            except Exception as e:
                print(f"Error updating score: {e}")

    def level_one(self):
        self.main_frame.place_forget()
        self.level_one_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.level_one_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.level_one_frame,
            text="Row Transposition",
            font=("Roboto", 28, "bold"),
            text_color=self.primary_color
        )
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        index = random.randint(0, len(plaintext) - 1)
        selected_plaintext = plaintext[index]
        selected_key = key[index]
        selected_cipher = cipherText[index]

        self.timer_running = True
        self.time_left = 120
        self.timer_label = ctk.CTkLabel(
            self.level_one_frame,
            text=f"Time Left: {self.time_left}s",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.timer_label.place(relx=0.1, rely=0.2)

        def update_timer():
            while self.time_left > 0 and self.timer_running:
                self.time_left -= 1
                self.timer_label.configure(text=f"Time Left: {self.time_left}s")
                self.root.update()
                time.sleep(1)
            if self.time_left <= 0 and self.timer_running:
                self.timer_running = False
                self.return_to_main()

        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()

        cipher_label = ctk.CTkLabel(
            self.level_one_frame,
            text=f"Ciphertext: {selected_cipher}",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        cipher_label.place(relx=0.1, rely=0.3)

        key_label = ctk.CTkLabel(
            self.level_one_frame,
            text=f"Key: {selected_key}",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        key_label.place(relx=0.1, rely=0.4)

        self.answer_entry = ctk.CTkEntry(
            self.level_one_frame,
            width=300,
            font=("Roboto", 14),
            fg_color=self.bg_color,
            text_color="#FFFFFF",
            border_color=self.primary_color
        )
        self.answer_entry.place(relx=0.1, rely=0.5)

        self.result_label = ctk.CTkLabel(
            self.level_one_frame,
            text="",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.result_label.place(relx=0.1, rely=0.7)
        
        self.has_submitted_correct = False
        
        def check_answer():
            if self.has_submitted_correct or not self.timer_running:
                return
            user_answer = self.answer_entry.get().strip()
            if user_answer == selected_plaintext:
                self.result_label.configure(text="Correct!", text_color="#00FF00")
                self.has_submitted_correct = True
                self.timer_running = False
                self.update_score(7, 3)
                self.answer_entry.configure(state="disabled")
                submit_button.configure(state="disabled")
            else:
                self.result_label.configure(text="Incorrect, try again.", text_color="#FF0000")
                self.answer_entry.delete(0, ctk.END)

        submit_button = ctk.CTkButton(
            self.level_one_frame,
            text="Submit",
            command=check_answer,
            fg_color=self.primary_color,
            hover_color="#00CC99",
            text_color="#1A2A44",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        submit_button.place(relx=0.1, rely=0.6)

        back_button = ctk.CTkButton(
            self.level_one_frame,
            text="Back",
            command=self.return_to_main,
            fg_color="#FF5555",
            hover_color="#CC4444",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        back_button.place(relx=0.1, rely=0.8)

    def level_two(self):
        self.main_frame.place_forget()
        self.level_two_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.level_two_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.level_two_frame,
            text="Delta",
            font=("Roboto", 28, "bold"),
            text_color=self.primary_color
        )
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        index = random.randint(0, len(plaintextt) - 1)
        selected_plaintext = plaintextt[index]
        selected_cipher = cipherTextt[index]

        self.timer_running = True
        self.time_left = 180
        self.timer_label = ctk.CTkLabel(
            self.level_two_frame,
            text=f"Time Left: {self.time_left}s",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.timer_label.place(relx=0.1, rely=0.2)

        def update_timer():
            while self.time_left > 0 and self.timer_running:
                self.time_left -= 1
                self.timer_label.configure(text=f"Time Left: {self.time_left}s")
                self.root.update()
                time.sleep(1)
            if self.time_left <= 0 and self.timer_running:
                self.timer_running = False
                self.return_to_main()

        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()

        cipher_label = ctk.CTkLabel(
            self.level_two_frame,
            text=f"Ciphertext: {selected_cipher}",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        cipher_label.place(relx=0.1, rely=0.3)

        self.answer_entry = ctk.CTkEntry(
            self.level_two_frame,
            width=300,
            font=("Roboto", 14),
            fg_color=self.bg_color,
            text_color="#FFFFFF",
            border_color=self.primary_color
        )
        self.answer_entry.place(relx=0.1, rely=0.5)

        self.result_label = ctk.CTkLabel(
            self.level_two_frame,
            text="",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.result_label.place(relx=0.1, rely=0.7)

        self.has_submitted_correct = False

        def check_answer():
            if self.has_submitted_correct or not self.timer_running:
                return
            user_answer = self.answer_entry.get().strip()
            if user_answer == selected_plaintext:
                self.result_label.configure(text="Correct!", text_color="#00FF00")
                self.has_submitted_correct = True
                self.timer_running = False
                self.update_score(7, 5)
                self.answer_entry.configure(state="disabled")
                submit_button.configure(state="disabled")
            else:
                self.result_label.configure(text="Incorrect, try again.", text_color="#FF0000")
                self.answer_entry.delete(0, ctk.END)

        submit_button = ctk.CTkButton(
            self.level_two_frame,
            text="Submit",
            command=check_answer,
            fg_color=self.primary_color,
            hover_color="#00CC99",
            text_color="#1A2A44",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        submit_button.place(relx=0.1, rely=0.6)

        back_button = ctk.CTkButton(
            self.level_two_frame,
            text="Back",
            command=self.return_to_main,
            fg_color="#FF5555",
            hover_color="#CC4444",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        back_button.place(relx=0.1, rely=0.8)

    def level_three(self):
        self.main_frame.place_forget()
        self.level_three_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.level_three_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.level_three_frame,
            text="RSA",
            font=("Roboto", 28, "bold"),
            text_color=self.primary_color
        )
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        index = random.randint(0, len(plaintext_Rsa) - 1)
        selected_plaintext = plaintext_Rsa[index]
        selected_cipher = cipherText_Rsa[index]
        selected_key = key_Rsa[index]

        self.timer_running = True
        self.time_left = 300
        self.timer_label = ctk.CTkLabel(
            self.level_three_frame,
            text=f"Time Left: {self.time_left}s",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.timer_label.place(relx=0.1, rely=0.2)

        def update_timer():
            while self.time_left > 0 and self.timer_running:
                self.time_left -= 1
                self.timer_label.configure(text=f"Time Left: {self.time_left}s")
                self.root.update()
                time.sleep(1)
            if self.time_left <= 0 and self.timer_running:
                self.timer_running = False
                self.return_to_main()

        timer_thread = threading.Thread(target=update_timer, daemon=True)
        timer_thread.start()

        cipher_label = ctk.CTkLabel(
            self.level_three_frame,
            text=f"Ciphertext: {selected_cipher}",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        cipher_label.place(relx=0.1, rely=0.3)

        key_label = ctk.CTkLabel(
            self.level_three_frame,
            text=f"Key: {selected_key}",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        key_label.place(relx=0.1, rely=0.4)

        self.answer_entry = ctk.CTkEntry(
            self.level_three_frame,
            width=300,
            font=("Roboto", 14),
            fg_color=self.bg_color,
            text_color="#FFFFFF",
            border_color=self.primary_color
        )
        self.answer_entry.place(relx=0.1, rely=0.5)

        self.result_label = ctk.CTkLabel(
            self.level_three_frame,
            text="",
            font=("Roboto", 16),
            text_color="#FFFFFF"
        )
        self.result_label.place(relx=0.1, rely=0.7)

        self.has_submitted_correct = False

        def check_answer():
            if self.has_submitted_correct or not self.timer_running:
                return
            user_answer = self.answer_entry.get().strip()
            if user_answer == selected_plaintext:
                self.result_label.configure(text="Correct!", text_color="#00FF00")
                self.has_submitted_correct = True
                self.timer_running = False
                self.update_score(7, 9)
                self.answer_entry.configure(state="disabled")
                submit_button.configure(state="disabled")
            else:
                self.result_label.configure(text="Incorrect, try again.", text_color="#FF0000")
                self.answer_entry.delete(0, ctk.END)

        submit_button = ctk.CTkButton(
            self.level_three_frame,
            text="Submit",
            command=check_answer,
            fg_color=self.primary_color,
            hover_color="#00CC99",
            text_color="#1A2A44",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        submit_button.place(relx=0.1, rely=0.6)

        back_button = ctk.CTkButton(
            self.level_three_frame,
            text="Back",
            command=self.return_to_main,
            fg_color="#FF5555",
            hover_color="#CC4444",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        back_button.place(relx=0.1, rely=0.8)

    def standard_level(self):
        self.main_frame.place_forget()
        self.standard_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        self.standard_frame.place(x=0, y=0, relwidth=1, relheight=1)

        # Title
        title_label = ctk.CTkLabel(
            self.standard_frame,
            text="Leaderboard - Top 10 Players",
            font=("Roboto", 28, "bold"),
            text_color=self.primary_color
        )
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Load medal icons
        try:
            medal_files = ['gold.png', 'silver.png', 'bronze.png']
            for file in medal_files:
                img = Image.open(file).resize((30, 30), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.medal_images.append(photo)
        except Exception as e:
            print(f"Error loading medal images: {e}")
            self.medal_images = [None, None, None]

        # Fetch top 10 users
        users = []
        if self.connection:
            try:
                cursor = self.connection.cursor()
                cursor.execute("""
                    SELECT TOP 3 name, score
                    FROM Users
                    ORDER BY score DESC
                """)
                users = cursor.fetchall()
                cursor.close()
            except Exception as e:
                print(f"Error fetching users: {e}")

        # Display users
        for i, user in enumerate(users[:10]):
            name, score = user
            y_pos = 0.2 + i * 0.06

            # Add medal for top 3
            if i < 3 and self.medal_images[i]:
                medal_label = ctk.CTkLabel(
                    self.standard_frame,
                    image=self.medal_images[i],
                    text=""
                )
                medal_label.place(relx=0.1, rely=y_pos, anchor="w")

            # Display rank
            rank_label = ctk.CTkLabel(
                self.standard_frame,
                text=f"{i+1}.",
                font=("Roboto", 16),
                text_color="#FFFFFF"
            )
            rank_label.place(relx=0.15 if i < 3 else 0.1, rely=y_pos, anchor="w")

            # Display name
            name_label = ctk.CTkLabel(
                self.standard_frame,
                text=name,
                font=("Roboto", 16),
                text_color="#FFFFFF"
            )
            name_label.place(relx=0.2 if i < 3 else 0.15, rely=y_pos, anchor="w")

            # Display score
            score_label = ctk.CTkLabel(
                self.standard_frame,
                text=f"Score: {score}",
                font=("Roboto", 16),
                text_color="#FFFFFF"
            )
            score_label.place(relx=0.5, rely=y_pos, anchor="w")

        # Back button
        back_button = ctk.CTkButton(
            self.standard_frame,
            text="Back",
            command=self.return_to_main,
            fg_color="#FF5555",
            hover_color="#CC4444",
            text_color="#FFFFFF",
            font=("Roboto", 14, "bold"),
            width=150,
            height=40,
            corner_radius=20,
            border_width=0
        )
        back_button.place(relx=0.1, rely=0.9)

    def return_to_main(self):
        self.timer_running = False
        if hasattr(self, 'level_one_frame') and self.level_one_frame.winfo_exists():
            self.level_one_frame.destroy()
        if hasattr(self, 'level_two_frame') and self.level_two_frame.winfo_exists():
            self.level_two_frame.destroy()
        if hasattr(self, 'level_three_frame') and self.level_three_frame.winfo_exists():
            self.level_three_frame.destroy()
        if hasattr(self, 'standard_frame') and self.standard_frame.winfo_exists():
            self.standard_frame.destroy()
        self.main_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # Ensure background is visible when returning to main
        if self.background_label:
            self.background_label.lower()

    def __del__(self):
        self.close_connection()

if __name__ == "__main__":
    root = ctk.CTk()
    app = SimpleGame(root)
    root.mainloop()