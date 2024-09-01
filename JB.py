import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import aiohttp
import asyncio
import re
from threading import Thread

class ServerCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JBG")

        # Create UI Elements
        self.create_widgets()

    def create_widgets(self):
        # Button to Show Server Creation Options
        self.show_options_button = tk.Button(self.root, text="Show JBG Options", command=self.show_options)
        self.show_options_button.pack(pady=10)

        # Button to Show Tutorial
        self.show_tutorial_button = tk.Button(self.root, text="Show Tutorial", command=self.show_tutorial)
        self.show_tutorial_button.pack(pady=10)

        # Options Frame (Initially Hidden)
        self.options_frame = tk.Frame(self.root)

        # Minecraft Version Scrollable List
        self.version_label = tk.Label(self.options_frame, text="Minecraft Version:")
        self.version_combobox = ttk.Combobox(self.options_frame, values=[])
        self.version_label.pack(side=tk.LEFT, padx=5)
        self.version_combobox.pack(side=tk.LEFT, padx=5)

        # Java Options Combobox
        self.type_label = tk.Label(self.options_frame, text="Java Options:")
        self.type_combobox = ttk.Combobox(self.options_frame, values=["Vanilla", "Spigot", "Paper"])
        self.type_label.pack(side=tk.LEFT, padx=5)
        self.type_combobox.pack(side=tk.LEFT, padx=5)

        # RAM Selector
        self.ram_label = tk.Label(self.options_frame, text="RAM Allocation (MB):")
        self.ram_entry = tk.Entry(self.options_frame)
        self.ram_label.pack(side=tk.LEFT, padx=5)
        self.ram_entry.pack(side=tk.LEFT, padx=5)
        self.ram_entry.insert(0, "2048")  # Default to 2GB

        # Server Location Entry
        self.location_label = tk.Label(self.options_frame, text="Server Location:")
        self.location_entry = tk.Entry(self.options_frame)
        self.browse_button = tk.Button(self.options_frame, text="Browse", command=self.browse_location)
        self.location_label.pack(side=tk.LEFT, padx=5)
        self.location_entry.pack(side=tk.LEFT, padx=5)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # EULA Checkbox
        self.eula_var = tk.BooleanVar()
        self.eula_checkbox = tk.Checkbutton(self.options_frame, text="I agree to the EULA", variable=self.eula_var)
        self.eula_checkbox.pack(pady=10)

        # Create Server Button
        self.create_button = tk.Button(self.options_frame, text="Create JBG files", command=self.start_server_creation)
        self.create_button.pack(pady=10)

        # Loading Indicator
        self.loading_label = tk.Label(self.root, text="", font=("Arial", 14), fg="red")
        self.loading_label.pack(pady=10)

        # Initially hide options frame and loading indicator
        self.options_frame.pack_forget()
        self.loading_label.pack_forget()

        # Load Minecraft versions asynchronously
        asyncio.run(self.load_minecraft_versions())

    async def load_minecraft_versions(self):
        versions = await self.get_minecraft_versions()
        self.version_combobox['values'] = versions

    async def get_minecraft_versions(self):
        versions_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(versions_url) as response:
                    response.raise_for_status()  # Raise an exception for HTTP errors
                    data = await response.json()
                    versions = [version['id'] for version in data['versions'] if self.is_valid_version(version['id'])]
                    return versions
        except aiohttp.ClientError as e:
            messagebox.showerror("Error", f"Failed to fetch Minecraft versions: {e}")
            return []

    def is_valid_version(self, version):
        # Regular expression to match Minecraft version formats
        return re.match(r'^\d+\.\d+(\.\d+)?$', version) is not None

    def show_options(self):
        # Display the options frame
        self.options_frame.pack(pady=10)
        # Hide the button to show options after it's clicked
        self.show_options_button.pack_forget()

    def show_tutorial(self):
        tutorial_text = (
            "Welcome to the JBG!\n\n"
            "How to Use:\n"
            "1. Select the Minecraft version you want to use from the dropdown list.\n"
            "2. Choose the type of server: Vanilla, Spigot, or Paper.\n"
            "   - Vanilla: The official Minecraft server.\n"
            "   - Spigot: A popular modified server for performance and features.\n"
            "   - Paper: A highly optimized fork of Spigot.\n"
            "3. Enter the amount of RAM (in MB) you want to allocate to the server.\n"
            "4. Choose the directory where you want to install the server files.\n"
            "5. Agree to the EULA by checking the box.\n"
            "6. Click 'Create Server' to start the setup process.\n\n"
            "The application will download the server files, create a start.bat file with the specified RAM allocation, "
            "and display a success message once the server is ready.\n\n"
            "To start the server, simply run the start.bat file in the server directory."
        )
        tutorial_window = tk.Toplevel(self.root)
        tutorial_window.title("Tutorial")
        tk.Label(tutorial_window, text=tutorial_text, padx=10, pady=10, justify=tk.LEFT).pack()

    def browse_location(self):
        directory = filedialog.askdirectory(title="Select Server Directory")
        if directory:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, directory)

    def start_server_creation(self):
        # Start the server creation in a new thread to keep the UI responsive
        Thread(target=self.create_server).start()
        self.show_loading()

    def show_loading(self):
        self.loading_label.config(text="Creating Files... Please wait.")
        self.loading_label.pack()

    def hide_loading(self):
        self.loading_label.pack_forget()

    def create_server(self):
        # Run the async server creation process
        asyncio.run(self.create_server_async())

    async def create_server_async(self):
        version = self.version_combobox.get().strip()
        java_option = self.type_combobox.get()
        location = self.location_entry.get().strip()
        ram = self.ram_entry.get().strip()
        eula_accepted = self.eula_var.get()

        if not version or not java_option or not location or not ram:
            self.hide_loading()
            messagebox.showerror("Error", "Please fill out all required fields.")
            return

        if not eula_accepted:
            self.hide_loading()
            messagebox.showerror("Error", "You must agree to the EULA before creating the server.")
            return

        # Validate RAM entry
        try:
            ram = int(ram)
            if ram <= 0:
                raise ValueError("RAM must be a positive integer.")
        except ValueError:
            self.hide_loading()
            messagebox.showerror("Error", "Invalid RAM value. Please enter a positive integer.")
            return

        # Ensure the directory exists
        if not os.path.exists(location):
            os.makedirs(location)

        # Handle server URL based on server type
        server_url = await self.get_server_url(version, java_option)
        if not server_url:
            self.hide_loading()
            messagebox.showerror("Error", "Failed to get server file URL.")
            return

        try:
            # Download the server JAR file asynchronously
            async with aiohttp.ClientSession() as session:
                async with session.get(server_url) as response:
                    response.raise_for_status()
                    server_file_path = os.path.join(location, f"{java_option.lower()}_{version}.jar")
                    with open(server_file_path, "wb") as file:
                        while True:
                            chunk = await response.content.read(8192)
                            if not chunk:
                                break
                            file.write(chunk)

            # Create the start.bat file with RAM allocation
            start_bat_path = os.path.join(location, "start.bat")
            bat_content = f"java -Xmx{ram}M -Xms{ram}M -jar {java_option.lower()}_{version}.jar nogui\n"
            with open(start_bat_path, "w") as bat_file:
                bat_file.write(bat_content)
                bat_file.write("pause\n")

            # Create the eula.txt file and accept EULA
            eula_file_path = os.path.join(location, "eula.txt")
            with open(eula_file_path, "w") as eula_file:
                eula_file.write("eula=true\n")

            # Display server creation information
            server_info = {
                "version": version,
                "java_option": java_option,
                "location": location,
                "ram": ram
            }
            self.hide_loading()
            messagebox.showinfo("Server Created", f"Server Info:\nVersion: {server_info['version']}\nJava Option: {server_info['java_option']}\nLocation: {server_info['location']}\nRAM: {server_info['ram']}MB")

        except Exception as e:
            self.hide_loading()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")
            print(f"Unexpected Error: {e}")

    async def get_server_url(self, version, server_type):
        if server_type == "Vanilla":
            manifest_url = "https://launchermeta.mojang.com/mc/game/version_manifest.json"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(manifest_url) as response:
                        response.raise_for_status()
                        manifest = await response.json()
                        version_data = next((v for v in manifest['versions'] if v['id'] == version), None)
                        if version_data:
                            version_url = version_data['url']
                            async with session.get(version_url) as response:
                                response.raise_for_status()
                                version_info = await response.json()
                                server_url = version_info['downloads']['server']['url']
                                return server_url
                        else:
                            messagebox.showerror("Error", "Version not found.")
                            return None
            except aiohttp.ClientError as e:
                messagebox.showerror("Error", f"Failed to get server URL: {e}")
                return None
        elif server_type == "Spigot":
            # Example URL for Spigot; replace with actual if available
            server_url = f"https://cdn.getbukkit.org/spigot/spigot-{version}.jar"
            return server_url
        elif server_type == "Paper":
            # Use PaperMC API to get the latest build for the specified version
            api_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds"
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(api_url) as response:
                        response.raise_for_status()
                        builds = await response.json()
                        if builds.get('builds'):
                            latest_build = builds['builds'][-1]  # Get the latest build
                            build_number = latest_build['build']
                            server_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build_number}/downloads/paper-{version}-{build_number}.jar"
                            return server_url
                        else:
                            messagebox.showerror("Error", "No builds found for the specified version.")
                            return None
            except aiohttp.ClientError as e:
                messagebox.showerror("Error", f"Failed to get Paper server URL: {e}")
                return None
        else:
            messagebox.showerror("Error", "Invalid server type.")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerCreatorApp(root)
    root.mainloop()
