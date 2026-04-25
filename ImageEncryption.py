import tkinter as tk
from tkinter import filedialog, messagebox
from itertools import cycle

def xor_encrypt_decrypt(data, key):
    """Encrypt/decrypt data using XOR cipher with the given key"""
    key_bytes = key.encode('utf-8')
    return bytes(a ^ b for a, b in zip(data, cycle(key_bytes)))

def browse_image():
    """Open file dialog to select image file"""
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp")])
    if file_path:
        lbl_file.config(text=file_path)

def process_image(mode):
    """Handle encryption/decryption process"""
    file_path = lbl_file.cget("text")
    key = entry_key.get()
    
    if not file_path or file_path == "No file selected":
        messagebox.showerror("Error", "Please select an image file!")
        return
    if not key:
        messagebox.showerror("Error", "Please enter an encryption key!")
        return
    
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        processed_data = xor_encrypt_decrypt(data, key)
        
        save_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("All files", "*.*")]
        )
        
        if save_path:
            with open(save_path, 'wb') as f:
                f.write(processed_data)
            messagebox.showinfo("Success", f"Image {mode} successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Create main window
root = tk.Tk()
root.title("Image Cryptography")
root.geometry("500x600")
root.configure(bg="#1A2A44")
root.resizable(False, False)

# Custom styles
style = {
    "bg": "#1A2A44",
    "fg": "#00FFBF",
    "btn_bg": "#00FFBF",
    "btn_fg": "#1A2A44",
    "entry_bg": "#2A3B5A",
    "font": ("Helvetica", 12, "bold"),
    "title_font": ("Helvetica", 20, "bold"),
}

# Main frame with gradient background
main_frame = tk.Frame(root, bg=style["bg"])
main_frame.pack(expand=True, fill="both", padx=20, pady=20)

# Title
lbl_title = tk.Label(
    main_frame,
    text="Image Cryptography",
    font=style["title_font"],
    fg=style["fg"],
    bg=style["bg"],
)
lbl_title.pack(pady=(20, 30))

# File selection
file_frame = tk.Frame(main_frame, bg=style["bg"])
file_frame.pack(fill="x", pady=10)

lbl_file = tk.Label(
    file_frame,
    text="No file selected",
    font=style["font"],
    fg="#FFFFFF",
    bg=style["entry_bg"],
    wraplength=400,
    relief="flat",
    pady=10,
    padx=10,
)
lbl_file.pack(fill="x", pady=5)

btn_browse = tk.Button(
    file_frame,
    text="Browse Image",
    font=style["font"],
    bg=style["btn_bg"],
    fg=style["btn_fg"],
    relief="flat",
    activebackground="#00CC99",
    activeforeground="#1A2A44",
    command=browse_image,
)
btn_browse.pack(pady=10)
btn_browse.bind("<Enter>", lambda e: btn_browse.config(bg="#00CC99"))
btn_browse.bind("<Leave>", lambda e: btn_browse.config(bg=style["btn_bg"]))

# Key entry
key_frame = tk.Frame(main_frame, bg=style["bg"])
key_frame.pack(fill="x", pady=20)

lbl_key = tk.Label(
    key_frame,
    text="Encryption Key:",
    font=style["font"],
    fg=style["fg"],
    bg=style["bg"],
)
lbl_key.pack(anchor="w", pady=5)

entry_key = tk.Entry(
    key_frame,
    font=style["font"],
    bg=style["entry_bg"],
    fg="#FFFFFF",
    insertbackground=style["fg"],
    relief="flat",
    width=30,
)
entry_key.pack(fill="x", pady=5, ipady=5)

# Buttons
button_frame = tk.Frame(main_frame, bg=style["bg"])
button_frame.pack(pady=30)

btn_encrypt = tk.Button(
    button_frame,
    text="Encrypt",
    font=style["font"],
    bg=style["btn_bg"],
    fg=style["btn_fg"],
    relief="flat",
    activebackground="#00CC99",
    activeforeground="#1A2A44",
    command=lambda: process_image("encrypted"),
    width=12,
)
btn_encrypt.pack(side="left", padx=10)
btn_encrypt.bind("<Enter>", lambda e: btn_encrypt.config(bg="#00CC99"))
btn_encrypt.bind("<Leave>", lambda e: btn_encrypt.config(bg=style["btn_bg"]))

btn_decrypt = tk.Button(
    button_frame,
    text="Decrypt",
    font=style["font"],
    bg=style["btn_bg"],
    fg=style["btn_fg"],
    relief="flat",
    activebackground="#00CC99",
    activeforeground="#1A2A44",
    command=lambda: process_image("decrypted"),
    width=12,
)
btn_decrypt.pack(side="left", padx=10)
btn_decrypt.bind("<Enter>", lambda e: btn_decrypt.config(bg="#00CC99"))
btn_decrypt.bind("<Leave>", lambda e: btn_decrypt.config(bg=style["btn_bg"]))

# Animation for window appearance
def animate_window():
    alpha = 0.0
    root.attributes("-alpha", alpha)
    def fade_in():
        nonlocal alpha
        alpha += 0.05
        if alpha < 1:
            root.attributes("-alpha", alpha)
            root.after(30, fade_in)
        else:
            root.attributes("-alpha", 1.0)
    fade_in()

# Run animation
animate_window()

root.mainloop()