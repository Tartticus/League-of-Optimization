import tkinter as tk
from tkinter import ttk, simpledialog
from PIL import Image, ImageTk
import pandas as pd

# Load Champions data from Excel
champs = pd.read_excel(r"C:\Users\Matth\OneDrive\Documents\LoL\Champs.xlsx")

# Define mpen, ppen, and calculated_value as global variables
mpen = 0
ppen = 0
calculated_value = 0
selected_items = [] # list for items
selected_champion = None  # Initialize selected champion globally
additional_MR = 0  # Additional MR from items

def image_clicked(index):
    global mpen, ppen, additional_MR  # Access the global variables

    if index == 0:
        selected_label.config(text="Shadowflame")
        selected_items.append("Shadowflame")
        mpen += 12
    elif index == 1:
        selected_label.config(text="Sorcs shoes")
        selected_items.append("Sorcs shoes")
        mpen += 18
    elif index == 2:
        selected_label.config(text="Stormsurge")
        selected_items.append("Stormsurge")
        mpen += 10
    elif index == 3:
        selected_label.config(text="Cryptobloom")
        selected_items.append("Cryptobloom")
        ppen += 0.35  # Adjusted to 0.35 to match your description
    elif index == 4:
        selected_label.config(text="Voidstaff")
        selected_items.append("Voidstaff")
        ppen += 0.40  # Adjusted to 0.40 to match your description
    
    return mpen, ppen

def on_select_champion(event=None):
    global selected_champion
    selected_champion = champion_var.get()
    if selected_champion:
        print(f"Selected champion: {selected_champion}")

def submit_clicked():
    global mpen, ppen, calculated_value, selected_champion, selected_items, additional_MR
    
    # Get the level input from Entry widget
    try:
        level = int(level_entry.get())
    except ValueError:
        print("Invalid level input")
        return
    
    # Get additional MR input from user
    try:
        additional_MR = float(simpledialog.askstring("Additional MR", "Enter additional MR from items:"))
    except ValueError:
        print("Invalid additional MR input")
        return

    # Perform calculations based on level, MR, and other columns in champs DataFrame
    multiplier = champs.loc[champs['Champ'] == selected_champion, 'Growth'].values[0]
    base = champs.loc[champs['Champ'] == selected_champion, 'Base'].values[0]
    print(f"Multiplier for {selected_champion} at level {level}: {multiplier}")
    
    # Calculate the value globally accessible
    calculated_value = base + (level * multiplier)
    print(f"Enemies MR: {calculated_value}")

    # Calculate formulas and differences
    MR = calculated_value + additional_MR
    formula = round((1 - (100 / (100 + MR))) * 100, 2)
    formula2 = round((1 - (100 / ((100 + (MR - mpen)*(1-ppen))))) * 100, 2)
    diff = round((formula - formula2),2)

    print(f"You will do {diff}% more magic damage to {selected_champion} at level {level} with {selected_items}")
    root.destroy()  # Destroy the Tkinter window
    return mpen, calculated_value, selected_champion

# Create the main window
root = tk.Tk()
root.title("Pick your pen items")

# Predefined images (replace with your own paths)
image_paths = [
    r"C:\Users\Matth\OneDrive\Documents\LoL\shadowflame.png",
    r"C:\Users\Matth\OneDrive\Documents\LoL\Sorcerer%27s_Shoes_item_old2.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\stormsurge.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\cryptobloom.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\void.webp"
]

# List to store ImageTk objects
images = []

# Load images and create buttons
for i, path in enumerate(image_paths):
    image = Image.open(path)
    image.thumbnail((100, 100))  # Resize image if necessary
    images.append(ImageTk.PhotoImage(image))
    
    # Create a button with the image and bind it to a function
    button = tk.Button(root, image=images[i], command=lambda idx=i: image_clicked(idx))
    button.pack(pady=5)

# Label to display selected image
selected_label = tk.Label(root, text="Pick your items")
selected_label.pack(pady=10)

# Dropdown menu for champion selection
champion_var = tk.StringVar()
champion_dropdown = ttk.OptionMenu(root, champion_var, *champs['Champ'].unique(), command=on_select_champion)
champion_dropdown.pack(padx=20, pady=10)

# Label for instruction
instruction_label = tk.Label(root, text="Select a champion:")
instruction_label.pack()

# Entry widget for level input
level_label = tk.Label(root, text="Enter champion's level:")
level_label.pack()
level_entry = tk.Entry(root)
level_entry.pack()

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_clicked)
submit_button.pack(pady=10)

# Run the main loop
root.mainloop()



