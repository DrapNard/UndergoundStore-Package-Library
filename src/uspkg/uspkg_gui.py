import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, Label
from tkinter import ttk
import base64
from PIL import Image, ImageTk
import io
import uspkg
from threading import Thread

class UspkgApp:
    def __init__(self, root):
        self.root = root
        self.root.title("USPkg Tool")

        # Frame for buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(pady=10)

        # Create UI components
        self.create_button = ttk.Button(button_frame, text="Create .uspkg", command=self.create_uspkg)
        self.create_button.grid(row=0, column=0, padx=5, pady=5)

        self.extract_button = ttk.Button(button_frame, text="Extract .uspkg", command=self.extract_uspkg)
        self.extract_button.grid(row=0, column=1, padx=5, pady=5)

        self.preview_button = ttk.Button(button_frame, text="Preview & Verify .uspkg", command=self.preview_uspkg)
        self.preview_button.grid(row=0, column=2, padx=5, pady=5)

        # Progress bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.pack(pady=10)

        # Status label
        self.status_label = Label(root, text="", font=("Arial", 12))
        self.status_label.pack(pady=5)

    def ask_directory(self, title):
        return filedialog.askdirectory(title=title)

    def ask_file(self, title, filetypes):
        return filedialog.askopenfilename(title=title, filetypes=filetypes)

    def update_progress(self, percent):
        """Update the progress bar."""
        self.progress_bar['value'] = percent
        self.status_label.config(text=f"Progress: {percent:.2f}%")
        self.root.update_idletasks()

    def create_uspkg(self):
        folder = self.ask_directory("Select Folder to Package")
        if not folder:
            return

        output_file = filedialog.asksaveasfilename(defaultextension=".uspkg", filetypes=[("USPkg files", "*.uspkg")])
        if not output_file:
            return

        title = simpledialog.askstring("Input", "Enter Package Title:")
        description = simpledialog.askstring("Input", "Enter Package Description:")
        
        # Create a new window for selecting the type
        type_window = tk.Toplevel(self.root)
        type_window.title("Select Package Type")
        
        tk.Label(type_window, text="Select Package Style:").pack(pady=5)
        type_var = tk.StringVar()
        type_dropdown = ttk.Combobox(type_window, textvariable=type_var)
        type_dropdown['values'] = ("Roms Hack", "Fan Game")
        type_dropdown.current(0)  # Set default value
        type_dropdown.pack(pady=5)

        def on_select_type():
            _type = type_var.get()
            type_window.destroy()  # Close type window

            # New window to select the main executable file
            self.select_main_executable(folder, output_file, title, description, _type)

        ttk.Button(type_window, text="OK", command=on_select_type).pack(pady=5)

    def select_main_executable(self, folder, output_file, title, description, _type):
        # New window to select the main executable
        exe_window = tk.Toplevel(self.root)
        exe_window.title("Select Main Executable")

        tk.Label(exe_window, text="Select Main Executable for the package:").pack(pady=5)

        def browse_executable():
            main_exe = filedialog.askopenfilename(title="Select Main Executable", filetypes=[("Executable files", "*.exe;*.sh;*.bat;*.app"), ("Rom Files", "*.ips;*.bps;*.bsp;*.xdelta;*.ppf;*.ninja")])
            if main_exe:
                tk.Label(exe_window, text=f"Selected: {main_exe}").pack()

                # Proceed to ask for the image and create the package
                image_file = self.ask_file("Select Image", [("Image files", "*.png;*.jpg")])
                if not image_file:
                    return

                # Reset progress bar and status label
                self.progress_bar['value'] = 0
                self.status_label.config(text="")

                def create_package():
                    try:
                        uspkg.create_encrypted_uspkg_with_uid(
                            folder, output_file, title, description, image_file, _type, main_exe,
                            update_progress_callback=self.update_progress
                        )
                        messagebox.showinfo("Success", f"USPkg file created: {output_file}")
                    except ValueError as e:
                        messagebox.showerror("Error", f"Failed to create package: {e}")
                    except Exception as e:
                        messagebox.showerror("Error", f"An unexpected error occurred: {e}")

                # Start creating the package in a separate thread
                Thread(target=create_package).start()

        # Add a button to browse for the executable
        ttk.Button(exe_window, text="Browse", command=browse_executable).pack(pady=10)

    def extract_uspkg(self):
        uspkg_file = self.ask_file("Select .uspkg File", [("USPkg files", "*.uspkg")])
        if not uspkg_file:
            return

        output_dir = self.ask_directory("Select Output Directory")
        if not output_dir:
            return

        try:
            uspkg.extract_encrypted_uspkg_with_uid(uspkg_file, output_dir)
            messagebox.showinfo("Success", f"Files extracted to: {output_dir}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to extract package: {e}")

    def preview_uspkg(self):
        uspkg_file = self.ask_file("Select .uspkg File", [("USPkg files", "*.uspkg")])
        if not uspkg_file:
            return

        try:
            # Create a new window for preview
            preview_window = tk.Toplevel(self.root)
            preview_window.title("USPkg Preview")

            # Status label for verification
            status_label = Label(preview_window, text="Verifying package...", font=("Arial", 12))
            status_label.pack(pady=5)

            # First, verify the package
            is_valid = uspkg.verify_uspkg_file(uspkg_file)
            if is_valid:
                status_label.config(text="Verification Status: Package is valid", fg="green")
            else:
                status_label.config(text="Verification Status: Package is invalid", fg="red")
                return  # Stop if the package is invalid

            # If valid, proceed to read metadata
            _, _, metadata = uspkg.read_uspkg_metadata(uspkg_file)

            # Title and description in new window
            title_label = Label(preview_window, text=f"Package Title: {metadata.get('title', 'N/A')}", font=("Arial", 12))
            title_label.pack(pady=5)

            description_label = Label(preview_window, text=f"Package Description: {metadata.get('description', 'N/A')}", font=("Arial", 10))
            description_label.pack(pady=5)

            # Image in new window
            image_label = Label(preview_window)
            image_label.pack(pady=5)

            if metadata.get("image"):
                image_data = base64.b64decode(metadata["image"])
                image = Image.open(io.BytesIO(image_data))
                image.thumbnail((300, 300))  # Resize the image for display
                photo = ImageTk.PhotoImage(image)

                # Display the image in the new window
                image_label.config(image=photo)
                image_label.image = photo  # Keep a reference to prevent garbage collection
            else:
                image_label.config(text="No image available")

            # Close button
            close_button = ttk.Button(preview_window, text="Close", command=preview_window.destroy)
            close_button.pack(pady=10)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to preview package: {e}")


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = UspkgApp(root)
    root.mainloop()


def main():
    root = tk.Tk()
    app = UspkgApp(root)
    root.mainloop()