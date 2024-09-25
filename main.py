import tkinter as tk
from tkinter import ttk, messagebox
import threading
import video_processing  # Assuming this is your module with the video processing function

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("OpenCV Video Processor")
        self.root.geometry("500x450")
        self.root.config(bg="#1c1e22")  # Simplified dark background

        self.is_running = False
        self.mode = tk.StringVar(value="Auto")  # Default mode
        self.target_priority = tk.StringVar(value="Green")  # Default color priority
        self.create_widgets()

    def create_widgets(self):
        # Title Label with subtle font and padding
        title = tk.Label(self.root, text="Video Contour Detection", font=("Helvetica", 18, "bold"), fg="white", bg="#1c1e22")
        title.pack(pady=20)

        # Mode Selection Label
        mode_label = tk.Label(self.root, text="Select Mode", font=("Arial", 14), fg="lightgray", bg="#1c1e22")
        mode_label.pack(pady=5)

        # Frame for Mode Selection Radio Buttons
        mode_frame = tk.Frame(self.root, bg="#1c1e22")
        mode_frame.pack(pady=5)

        # Radio buttons for mode selection
        modes = [("Auto", "Auto"), ("Hybrid", "Hybrid"), ("Manual", "Manual")]
        for text, mode in modes:
            rb = ttk.Radiobutton(mode_frame, text=text, variable=self.mode, value=mode, style="TRadiobutton")
            rb.pack(side=tk.LEFT, padx=10)

        # Target Color Priority Label
        priority_label = tk.Label(self.root, text="Select Target Color Priority", font=("Arial", 14), fg="lightgray", bg="#1c1e22")
        priority_label.pack(pady=10)

        # Drop-down menu (combobox) for color priority selection
        color_options = ["Green", "Red", "Blue", "Yellow"]
        self.color_combobox = ttk.Combobox(self.root, values=color_options, textvariable=self.target_priority, state="readonly", font=("Arial", 12))
        self.color_combobox.pack(pady=10)

        # Frame for buttons
        button_frame = tk.Frame(self.root, bg="#1c1e22")
        button_frame.pack(pady=20)

        # Start Button (dark mode)
        self.start_button = ttk.Button(button_frame, text="Start Video", command=self.start_video, style="TButton")
        self.start_button.grid(row=0, column=0, padx=20, pady=10)

        # Stop Button (dark mode)
        self.stop_button = ttk.Button(button_frame, text="Stop Video", command=self.stop_video, state=tk.DISABLED, style="TButton")
        self.stop_button.grid(row=0, column=1, padx=20, pady=10)

        # Exit Button (dark mode)
        exit_button = ttk.Button(self.root, text="Exit", command=self.root.quit, style="TButton")
        exit_button.pack(pady=20)

        # Status Label to show feedback with improved contrast
        self.status_label = tk.Label(self.root, text="Status: Idle", font=("Arial", 12), fg="lightgray", bg="#1c1e22")
        self.status_label.pack(pady=10)

        # Styling the buttons and radio buttons for dark theme
        style = ttk.Style()
        style.configure("TButton", font=("Helvetica", 12), padding=6, relief="flat", background="#1c1e22", foreground="black")
        style.map("TButton", background=[("active", "#2e343a")], foreground=[("active", "white")])
        style.configure("TRadiobutton", background="#1c1e22", foreground="white", font=("Arial", 12))
        style.map("TRadiobutton", background=[("active", "#2e343a")])

    def start_video(self):
        if not self.is_running:
            selected_mode = self.mode.get()
            target_priority = self.target_priority.get()

            # Show a messagebox for the selected mode and priority
            messagebox.showinfo("Mode & Priority", f"Mode: {selected_mode}\nTarget Priority: {target_priority}")
            
            self.is_running = True
            self.stop_event = threading.Event()
            self.video_thread = threading.Thread(target=self.run_video)
            self.video_thread.start()
            self.update_ui_running(True)
        else:
            messagebox.showinfo("Already Running", "Video is already running.")

    def stop_video(self):
        if self.is_running:
            self.is_running = False
            self.stop_event.set()
            self.update_ui_running(False)

    def run_video(self):
        try:
            # Pass selected mode and target color to the video processing function
            video_processing.process_video(self.stop_event.is_set, self.mode.get(), self.target_priority.get())
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            self.update_ui_running(False)

    def update_ui_running(self, is_running):
        """Update UI elements depending on whether the video is running or not."""
        if is_running:
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Running", fg="lightgreen")
        else:
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Stopped", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)
    root.mainloop()
