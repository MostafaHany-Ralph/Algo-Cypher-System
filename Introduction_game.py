import customtkinter as ctk
from tkinter import messagebox
import random
import subprocess


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
NEON_GREEN = "#00FF00"
BLACK = "#000000"
RED = "#FF0000"
WHITE = "#FFFFFF"
FONT = ("Consolas", 18)
FONT_BUTTON = ("Consolas", 16, "bold")
FONT_LOG = ("Consolas", 14)

SECOND_PROJECT_PATH = r"D:\AAST\Term 4\Cyber Security\AlgoCypher\Cyphers.py"

# Setup CustomTkinter
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# Hieroglyph mapping
english_to_hieroglyph = {
    'a': '𓄿', 'b': '𓃀', 'c': '𓈜', 'd': '𓂧', 'e': '𓇋', 'f': '𓆑', 'g': '𓎼',
    'h': '𓉔', 'i': '𓇑', 'j': '𓆓', 'k': '𓎡', 'l': '𓃭', 'm': '𓅓', 'n': '𓈖',
    'o': '𓂝', 'p': '𓊪', 'q': '𓈎', 'r': '𓂋', 's': '𓋴', 't': '𓏏', 'u': '𓅱',
    'v': '𓆰', 'w': '𓏲', 'x': '𓐍', 'y': '𓇳', 'z': '𓊃', ' ': ' '
}
hieroglyph_to_english = {v: k for k, v in english_to_hieroglyph.items()}

def fibonacci(n):
    """Return the nth Fibonacci number (1-based: fib(1)=1, fib(2)=1, fib(3)=2, ...)."""
    if n <= 0:
        return 0
    fib = [1, 1]
    for i in range(2, n):
        fib.append(fib[i-1] + fib[i-2])
    return fib[n-1]

def caesar_fibonacci_decrypt(text):
    """Apply Caesar + Fibonacci position decryption: (E - fib(p)) % 26."""
    result = []
    for p, char in enumerate(text.lower(), 1):
        if char.isalpha():
            e = ord(char) - ord('a')
            shifted = (e - fibonacci(p)) % 26
            result.append(chr(shifted + ord('a')))
        else:
            result.append(char)
    return ''.join(result)

def decrypt_hieroglyphs(hieroglyphs):
    """Convert Hieroglyphs to English with Caesar + Fibonacci decryption."""
    result = []
    i = 0
    while i < len(hieroglyphs):
        if hieroglyphs[i] in hieroglyph_to_english:
            result.append(hieroglyph_to_english[hieroglyphs[i]])
            i += 1
        else:
            result.append('?')
            i += 1
    return caesar_fibonacci_decrypt(''.join(result))

def decrypt_round5_cipher(cipher):
    """Decrypt Round 5 cipher: [n]#[Freq-a]#[pos1]#[flag1]#[pos2]#[flag2]..."""
    parts = cipher.split('#')
    if len(parts) < 2:
        raise ValueError("Invalid cipher format")
    try:
        n = int(parts[0])  # Length of string
        # freq_a = int(parts[1])  # Frequency of 'a' (not used in decryption)
        chars = []
        for i in range(2, len(parts), 2):
            if i + 1 >= len(parts):
                break
            pos = int(parts[i])
            flag = int(parts[i + 1])
            if pos >= n:
                continue
            if flag == 0:  # Lowercase letter (category Letters [1-26])
                char = 'a'
            elif flag == 1:  # Uppercase letter (category Letters [1-26])
                char = 'A'
            elif flag == 2:  # Digit (category 28)
                char = 'b'
            else:
                continue
            chars.append((pos, char))
        # Sort by position to reconstruct string
        chars.sort(key=lambda x: x[0])
        result = [char for _, char in chars]
        return ''.join(result)
    except ValueError as e:
        raise ValueError(f"Invalid cipher data: {str(e)}")

class CalculusCipherGame:
    def __init__(self, root):
        self.root = root
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.title("Cipher of Shadows: Calculus Vault")
        self.root.configure(bg=BLACK, fg_color=BLACK)
        self.scene = "intro"
        self.input_text = ""
        self.feedback = ""
        self.round = 1
        self.ciphertexts = {
            1: "97218x1342x2",
            2: "104202x1324x2432x3555x4",
            3: "𓎼𓃀𓏏𓂧𓏏𓆰",  # Hieroglyphs for "klyya" (decrypts to "world")
            4: "abcdefg",  # Plaintext, user must input shuffled "acbgfed"
            5: "3#2#0#0#1#1#1#2#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0#0"
        }
        self.correct_answers = {
            1: "hi",
            2: "hello",
            3: "world",
            4: "acbgfed",
            5: "aAb"
        }
        self.door_locked = True
        self.clue_lines = {
            1: [
                "The cypher speaks in calculus.....",
                f"Cipher: {self.ciphertexts[1]}",
                "Look at the screen carefully to start, the answer is somewhere inside.",
                "First letter: 1 means three digits, else two.",
                "Others: coefficients before 'x', powers after.",
                "Decrypt the message to unlock Round 1."
            ],
            2: [
                "Welcome to Round 2!",
                f"Cipher: {self.ciphertexts[2]}",
                "Now the challenge is harder.",
                "First letter: 1 means three digits, else two.",
                "Others: coefficients before 'x', powers after.",
                "Decrypt the message to unlock the vault."
            ],
            3: [
                "Final Round: The Hieroglyphic Vault!",
                f"Cipher: {self.ciphertexts[3]}",
                "The sequence grows: 1, 1, 2, 3, 5, 8... each number sums the two before.",
                "Letters shift back by this sequence, position by position, wrapping around the alphabet.",
                "Hieroglyphs hide the code. Map them:",
                "a=𓄿, b=𓃀, c=𓈜, d=𓂧, e=𓇋, f=𓆑, g=𓎼, h=𓉔, i=𓇑, j=𓆓,",
                "k=𓎡, l=𓃭, m=𓅓, n=𓈖, o=𓂝, p=𓊪, q=𓈎, r=𓂋, s=𓋴, t=𓏏,",
                "u=𓅱, v=𓆰, w=𓏲, x=𓐍, y=𓇳, z=𓊃, space= ",
                "Decrypt the ancient message to open the final vault."
            ],
            4: [
                "Round 4: Last Dance!",
                f"Plaintext: {self.ciphertexts[4]}",
                "Tip 1: Letters are placed in a binary tree.",
                "Tip 2: Left and right child nodes are swapped.",
                "Tip 3: The final string is read using pre-order traversal (root, left, right).",
                "Before shuffling:    A",
                "                    / \\",
                "                   B   C",
                "                  / \\ / \\",
                "                 D  E F  G",
                "After shuffling:     A",
                "                    / \\",
                "                   C   B",
                "                  / \\ / \\",
                "                 G  F E  D",
                "Enter the shuffled string to unlock the vault."
            ],
            5: [
                "Round 5: The Cryptic Sequence!",
                f"Cipher: {self.ciphertexts[5]}",
                "The cipher encodes a string as: [n]#[Freq-a]#[pos1]#[flag1]#[pos2]#[flag2]...",
                "n: length of the string.",
                "Freq-a: frequency of 'a' (may be ignored).",
                "pos: position in the string (0-based).",
                "flag: category of character:",
                "  0 = lowercase letter, 1 = uppercase letter, 2 = digit, 38 = special character.",
                "Example: Input 'aA1@' stores:",
                "  'a' at pos 0, lowercase → flag 0",
                "  'A' at pos 1, uppercase → flag 1",
                "  '1' at pos 2, digit → flag 2",
                "  '@' at pos 3, special → flag 38",
                "Decrypt the sequence to reveal the key."
            ]
        }
        self.intermediate_message_1 = ["Great job! Ready for Round 2?"]
        self.intermediate_message_2 = ["Excellent! The final challenge awaits in Round 3!"]
        self.intermediate_message_3 = ["Superb! Prepare for the Last Dance in Round 4!"]
        self.intermediate_message_4 = ["Incredible! Face the Cryptic Sequence in Round 5!"]
        self.success_message = ["You're a master of ciphers and calculus!", "Your username: amr", "Your password: 123"]
        self.current_line = 0
        self.current_char = 0
        self.display_text = ""
        self.typing = True
        self.clue_labels = []
        self.symbol_alpha = 1.0
        self.symbol_fade = -0.02
        self.button_pulse_alpha = 1.0
        self.button_pulse_fade = -0.02
        self.door_position = 0
        self.log_messages = []
        self.show_intro_scene()

    def decrypt_obfuscated(self, obf_text):
        decrypted = ''
        pos = 0
        if len(obf_text) == 0:
            return ''
        try:
            if obf_text[0] == '1' and len(obf_text) >= 3:
                num = obf_text[:3]
                if not num.isdigit():
                    raise ValueError("Expected 3-digit number for first character")
                ascii_val = int(num)
                pos = 3
            else:
                if len(obf_text) >= 2:
                    num = obf_text[:2]
                    if not num.isdigit():
                        raise ValueError("Expected 2-digit number for first character")
                    ascii_val = int(num)
                    pos = 2
                else:
                    raise ValueError("Insufficient characters for first character")
            if not (0 <= ascii_val <= 255):
                raise ValueError(f"ASCII value {ascii_val} out of valid range")
            decrypted += chr(ascii_val)
        except Exception as e:
            raise ValueError(f"Failed to parse first character: {str(e)}")
        parts = []
        current_part = ''
        power_index = 1
        while pos < len(obf_text):
            if obf_text[pos] == 'x':
                if current_part:
                    parts.append(current_part)
                parts.append('x')
                current_part = ''
                pos += 1
                if pos < len(obf_text) and obf_text[pos].isdigit():
                    if power_index == 1:
                        if obf_text[pos] != '1':
                            raise ValueError(f"Expected exponent '1' at position {pos}")
                        parts.append('1')
                        pos += 1
                    else:   #aAb
                        expected_power = str(power_index)
                        if pos + len(expected_power) > len(obf_text) or obf_text[pos:pos+len(expected_power)] != expected_power:
                            raise ValueError(f"Expected exponent '{expected_power}' at position {pos}")
                        parts.append(expected_power)
                        pos += len(expected_power)
                    power_index += 1
            else:
                current_part += obf_text[pos]
                pos += 1
        if current_part:
            parts.append(current_part)
        i = 0
        part_position = 1
        while i < len(parts):
            if parts[i] == 'x' and i+1 < len(parts) and parts[i+1].isdigit():
                if i-1 < 0 or not parts[i-1].isdigit():
                    raise ValueError(f"Missing coefficient at part position {part_position}")
                coefficient = int(parts[i-1])
                power = int(parts[i+1])
                integrated_coeff = coefficient // (power + 1)
                if not (0 <= integrated_coeff <= 255):
                    raise ValueError(f"Computed ASCII value {integrated_coeff} out of valid range")
                decrypted += chr(integrated_coeff)
                i += 2
                part_position += 1
            else:
                i += 1
        return decrypted

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.log_messages = []

    def add_log_message(self, message):
        self.log_messages.append(f"[SYS] {message}")
        if len(self.log_messages) > 5:
            self.log_messages.pop(0)
        self.update_log_area()

    def update_log_area(self):
        if hasattr(self, 'log_area'):
            log_text = "\n".join(self.log_messages)
            self.log_area.configure(text=log_text)

    def create_log_area(self):
        self.log_area = ctk.CTkLabel(
            self.root,
            text="",
            font=FONT_LOG,
            text_color=NEON_GREEN,
            fg_color=BLACK,
            anchor="nw",
            justify="left",
            height=100
        )
        self.log_area.place(x=10, y=WINDOW_HEIGHT - 110)
        self.add_log_message("SYSTEM BOOT...")

    def animate_text(self, label, text, index=0):
        if index < len(text):
            if random.random() < 0.1:
                label.place_configure(x=100 + random.randint(-2, 2))
            else:
                label.place_configure(x=100)
            label.configure(text=text[:index+1])
            self.root.after(50, lambda: self.animate_text(label, text, index+1))
        elif self.current_line < len(self.current_lines) - 1:
            self.current_line += 1
            self.current_char = 0
            self.display_text = ""
            self.root.after(500, lambda: self.show_next_clue_line())
        else:
            self.typing = False
            if self.scene == "intro":
                self.add_log_message("AWAITING INPUT...")
                self.show_start_button()
            elif self.scene == "intermediate_1":
                self.add_log_message("ROUND 1 COMPLETE.")
                self.show_continue_button("CONTINUE TO ROUND 2", self.start_round_2)
            elif self.scene == "intermediate_2":
                self.add_log_message("ROUND 2 COMPLETE.")
                self.show_continue_button("CONTINUE TO ROUND 3", self.start_round_3)
            elif self.scene == "intermediate_3":
                self.add_log_message("ROUND 3 COMPLETE.")
                self.show_continue_button("CONTINUE TO ROUND 4", self.start_round_4)
            elif self.scene == "intermediate_4":
                self.add_log_message("ROUND 4 COMPLETE.")
                self.show_continue_button("CONTINUE TO ROUND 5", self.start_round_5)
            elif self.scene == "success":
                self.add_log_message("SYSTEM SHUTDOWN...")
                self.root.after(1000, lambda: self.fade_out_scene())

    def show_next_clue_line(self):
        if self.clue_labels and self.current_line < len(self.current_lines):
            label = self.clue_labels[self.current_line]
            label.configure(text="")
            self.animate_text(label, self.current_lines[self.current_line])

    def show_start_button(self):
        self.start_btn = ctk.CTkButton(
            self.root,
            text="START",
            command=self.show_input_scene,
            corner_radius=5,
            fg_color=BLACK,
            text_color=NEON_GREEN,
            border_color=NEON_GREEN,
            border_width=2,
            font=FONT_BUTTON
        )
        self.start_btn.place(relx=0.5, rely=0.7, anchor="center")
        self.pulse_button(self.start_btn)

    def show_continue_button(self, text, command):
        self.continue_btn = ctk.CTkButton(
            self.root,
            text=text,
            command=command,
            corner_radius=5,
            fg_color=BLACK,
            text_color=NEON_GREEN,
            border_color=NEON_GREEN,
            border_width=2,
            font=FONT_BUTTON
        )
        self.continue_btn.place(relx=0.5, rely=0.7, anchor="center")
        self.pulse_button(self.continue_btn)

    def pulse_button(self, button):
        self.button_pulse_alpha += self.button_pulse_fade
        if self.button_pulse_alpha <= 0.7 or self.button_pulse_alpha >= 1.0:
            self.button_pulse_fade = -self.button_pulse_fade
        transparent_color = self.get_transparent_color(NEON_GREEN, self.button_pulse_alpha)
        button.configure(border_color=transparent_color)
        self.root.after(50, lambda: self.pulse_button(button))

    def get_transparent_color(self, base_color, alpha):
        base_color = base_color.lstrip('#')
        r = int(base_color[0:2], 16)
        g = int(base_color[2:4], 16)
        b = int(base_color[4:6], 16)
        r = int(r * alpha)
        g = int(g * alpha)
        b = int(b * alpha)
        return f'#{r:02x}{g:02x}{b:02x}'

    def show_intro_scene(self):
        self.scene = "intro"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.clue_lines[self.round]
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def update_symbol_opacity(self):
        self.symbol_alpha += self.symbol_fade
        if self.symbol_alpha <= 0.3 or self.symbol_alpha >= 1.0:
            self.symbol_fade = -self.symbol_fade
        transparent_color = self.get_transparent_color(NEON_GREEN, self.symbol_alpha)
        self.integral_label.configure(text_color=transparent_color)
        self.deriv_label.configure(text_color=transparent_color)
        self.root.after(50, self.update_symbol_opacity)

    def show_input_scene(self):
        self.scene = "input"
        self.clear_window()
        self.create_log_area()
        self.add_log_message(f"ROUND {self.round} INITIATED.")
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        cipher_label = ctk.CTkLabel(
            self.root,
            text=f"{'Plaintext' if self.round == 4 else 'Cipher'}: {self.ciphertexts[self.round]}",
            font=FONT,
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        cipher_label.place(x=100, y=100)
        prompt_label = ctk.CTkLabel(
            self.root,
            text="Enter Decrypted Text:",
            font=FONT,
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        prompt_label.place(x=100, y=150)
        self.input_field = ctk.CTkEntry(
            self.root,
            placeholder_text="Type here",
            width=300,
            font=FONT,
            text_color=NEON_GREEN,
            fg_color=BLACK,
            border_color=NEON_GREEN,
            border_width=2
        )
        self.input_field.place(x=100, y=190)
        self.input_field.bind("<Return>", lambda event: self.validate_input())
        self.submit_btn = ctk.CTkButton(
            self.root,
            text="SUBMIT",
            command=self.validate_input,
            corner_radius=5,
            fg_color=BLACK,
            text_color=NEON_GREEN,
            border_color=NEON_GREEN,
            border_width=2,
            font=FONT_BUTTON
        )
        self.submit_btn.place(x=450, y=190)
        self.pulse_button(self.submit_btn)
        self.feedback_label = ctk.CTkLabel(
            self.root,
            text="",
            font=FONT,
            text_color=WHITE,
            fg_color=BLACK
        )
        self.feedback_label.place(x=100, y=260)
        door_text = "🔒" if self.door_locked else "🔓"
        self.door_label = ctk.CTkLabel(
            self.root,
            text=door_text,
            font=("Consolas", 40),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.door_label.place(relx=0.5, rely=0.6, anchor="center")
        self.door_position = 0

    def animate_door(self):
        if self.door_position < 50:
            self.door_position += 5
            self.door_label.place_configure(relx=0.5 + self.door_position / WINDOW_WIDTH)
            self.root.after(50, self.animate_door)

    def validate_input(self):
        self.input_text = self.input_field.get().strip()
        try:
            if self.round in [1, 2]:
                decrypted = self.decrypt_obfuscated(self.ciphertexts[self.round])
            elif self.round == 3:
                decrypted = decrypt_hieroglyphs(self.ciphertexts[self.round])
            elif self.round == 5:
                decrypted = self.correct_answers[self.round]
            else:  # Round 4
                decrypted = self.correct_answers[self.round]  # Direct comparison to "acbgfed"
            if self.input_text == decrypted:
                self.feedback = "✔️ Correct!"
                self.feedback_label.configure(text=self.feedback, text_color=NEON_GREEN)
                self.input_field.configure(border_color=NEON_GREEN)
                self.door_locked = False
                self.door_label.configure(text="🔓")
                self.animate_door()
                self.add_log_message("ACCESS GRANTED.")
                if self.round == 1:
                    self.root.after(1000, self.show_intermediate_scene_1)
                elif self.round == 2:
                    self.root.after(1000, self.show_intermediate_scene_2)
                elif self.round == 3:
                    self.root.after(1000, self.show_intermediate_scene_3)
                elif self.round == 4:
                    self.root.after(1000, self.show_intermediate_scene_4)
                else:
                    self.root.after(1000, self.show_success_scene)
            else:
                self.feedback = "❌ Incorrect!"
                self.feedback_label.configure(text=self.feedback, text_color=RED)
                self.input_field.configure(border_color=RED)
                self.input_field.delete(0, "end")
                self.add_log_message("ACCESS DENIED.")
        except Exception as e:
            self.feedback = f"⚠️ Error: {str(e)}"
            self.feedback_label.configure(text=self.feedback, text_color=RED)
            self.input_field.configure(border_color=RED)
            self.input_field.delete(0, "end")
            self.add_log_message(f"ERROR: {str(e)}")

    def start_round_2(self):
        self.round = 2
        self.door_locked = True
        self.show_intro_scene()

    def start_round_3(self):
        self.round = 3
        self.door_locked = True
        self.show_intro_scene()

    def start_round_4(self):
        self.round = 4
        self.door_locked = True
        self.show_intro_scene()

    def start_round_5(self):
        self.round = 5
        self.door_locked = True
        self.show_intro_scene()

    def show_intermediate_scene_1(self):
        self.scene = "intermediate_1"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.intermediate_message_1
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def show_intermediate_scene_2(self):
        self.scene = "intermediate_2"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.intermediate_message_2
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def show_intermediate_scene_3(self):
        self.scene = "intermediate_3"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.intermediate_message_3
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def show_intermediate_scene_4(self):
        self.scene = "intermediate_4"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.intermediate_message_4
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def show_success_scene(self):
        self.scene = "success"
        self.clear_window()
        self.clue_labels = []
        self.current_line = 0
        self.current_char = 0
        self.typing = True
        self.current_lines = self.success_message
        self.create_log_area()
        self.integral_label = ctk.CTkLabel(
            self.root,
            text="∫",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.integral_label.place(x=50, y=50)
        self.deriv_label = ctk.CTkLabel(
            self.root,
            text="d/dx",
            font=("Consolas", 30),
            text_color=NEON_GREEN,
            fg_color=BLACK
        )
        self.deriv_label.place(x=WINDOW_WIDTH - 100, y=50)
        self.update_symbol_opacity()
        y = 100
        for _ in range(len(self.current_lines)):
            label = ctk.CTkLabel(
                self.root,
                text="",
                font=FONT,
                text_color=NEON_GREEN,
                fg_color=BLACK
            )
            label.place(x=100, y=y)
            self.clue_labels.append(label)
            y += 40
        if self.clue_labels:
            self.animate_text(self.clue_labels[0], self.current_lines[0])

    def fade_out_scene(self):
        alpha = 1.0
        def fade(alpha=alpha):
            if alpha > 0:
                transparent_color = self.get_transparent_color(NEON_GREEN, alpha)
                for label in self.clue_labels:
                    label.configure(text_color=transparent_color)
                self.integral_label.configure(text_color=transparent_color)
                self.deriv_label.configure(text_color=transparent_color)
                self.log_area.configure(text_color=transparent_color)
                self.root.after(50, lambda: fade(alpha - 0.05))
            else:
                try:
                    subprocess.run(["python", SECOND_PROJECT_PATH], check=True)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to open second project: {e}")
                self.root.quit()
        fade()

if __name__ == "__main__":
    root = ctk.CTk()
    app = CalculusCipherGame(root)
    root.mainloop()