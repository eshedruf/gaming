import tkinter as tk


class Window:
    def __init__(self):
        # Initial Connection Window
        self.connection_window = tk.Tk()
        self.connection_window.title("WELCOME!!!")

        # Create buttons for Sign In and Log In
        self.sign_in_button = tk.Button(self.connection_window, text="Sign In", command=self.show_sign_in)
        self.sign_in_button.pack(pady=10)

        self.log_in_button = tk.Button(self.connection_window, text="Log In", command=self.show_log_in)
        self.log_in_button.pack(pady=10)

        # Placeholder for username and password entry
        self.username_label = None
        self.password_label = None
        self.age_label = None
        self.username_entry = None
        self.password_entry = None
        self.age_entry = None

        self.submitted = False

    def clear_screen(self):
        """Clears all widgets from the screen."""
        # Destroy all widgets currently packed into the window
        for widget in self.connection_window.winfo_children():
            widget.destroy()

    def show_sign_in(self):
        """Show Sign In screen (username and password)."""
        self.clear_screen()

        # Add Sign In Title
        sign_in_title = tk.Label(self.connection_window, text="Sign In", font=('Helvetica', 16))
        sign_in_title.pack(pady=20)

        # Create and pack labels and entry fields for username and password
        self.username_label = tk.Label(self.connection_window, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.connection_window)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.connection_window, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.connection_window, show="*")  # Hide password input
        self.password_entry.pack(pady=5)

        self.age_label = tk.Label(self.connection_window, text="Age:")
        self.age_label.pack()

        self.age_entry = tk.Entry(self.connection_window)
        self.age_entry.pack(pady=5)

        # Add a Submit Button for Sign In
        submit_button = tk.Button(self.connection_window, text="Submit", command=self.submit)
        submit_button.pack(pady=20)


    def show_log_in(self):
        """Show Log In screen (username and password)."""
        self.clear_screen()

        # Add Log In Title
        log_in_title = tk.Label(self.connection_window, text="Log In", font=('Helvetica', 16))
        log_in_title.pack(pady=20)

        # Create and pack labels and entry fields for username and password
        self.username_label = tk.Label(self.connection_window, text="Username:")
        self.username_label.pack()

        self.username_entry = tk.Entry(self.connection_window)
        self.username_entry.pack(pady=5)

        self.password_label = tk.Label(self.connection_window, text="Password:")
        self.password_label.pack()

        self.password_entry = tk.Entry(self.connection_window, show="*")  # Hide password input
        self.password_entry.pack(pady=5)

        self.age_entry = "-1"

        # Add a Submit Button for Log In
        submit_button = tk.Button(self.connection_window, text="Submit", command=self.submit)
        submit_button.pack(pady=20)

    def submit(self):
        self.clear_screen()
        title = tk.Label(self.connection_window, text="MD5 RUSH!!", font=('Helvetica', 16))
        title.pack(pady=20)
        self.submitted = True


    def start(self):
        """Start the mainloop of the connection window."""
        self.connection_window.mainloop()
