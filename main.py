import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd

# Load Champions data from Excel
champs = pd.read_excel(r"C:\Users\Matth\OneDrive\Documents\LoL\Champs.xlsx")

# Define mpen and calculated_value as global variables
mpen = 0
calculated_value = 0
selected_items = [] # list for items
def image_clicked(index):
    global mpen  # Access the global mpen variable

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
        mpen += 12
    
    return mpen

def on_select_champion(event=None):
    global calculated_value  # Access the global calculated_value variable
    global selected_champion
    selected_champion = champion_var.get()
    if selected_champion:
        print(f"Selected champion: {selected_champion}")
        # Ask for champion's level
        level = int(input(f"What level is {selected_champion}? "))
        # Perform calculations based on level and other columns in champs DataFrame
        multiplier = champs.loc[champs['Champ'] == selected_champion, 'Growth'].values[0]
        base  = champs.loc[champs['Champ'] == selected_champion, 'Base'].values[0]
        print(f"Multiplier for {selected_champion} at level {level}: {multiplier}")
        # Calculate the value globally accessible
        calculated_value = base + (level * multiplier)
        print(f"Enemies MR: {calculated_value}")

def submit_clicked():
    global mpen, calculated_value, selected_champion, selected_items
    MR = calculated_value
    formula = round((1 - (100/(100+MR)))*100,2)
    formula2 = round((1 - (100/(100+(MR-mpen))))*100,2)
    diff = formula -formula2

    print(f"you will do {diff}% more magic damage to a {selected_champion} with", selected_items)
    root.destroy()  # Destroy the Tkinter window
    return mpen, calculated_value, selected_champion

# Create the main window
root = tk.Tk()
root.title("Pick your pen items")

# Predefined images (replace with your own paths)
image_paths = [
    r"C:\Users\Matth\OneDrive\Documents\LoL\shadowflame.png",
    r"C:\Users\Matth\OneDrive\Documents\LoL\Sorcerer%27s_Shoes_item_old2.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\stormsurge.webp"
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

# Submit button
submit_button = tk.Button(root, text="Submit", command=submit_clicked)
submit_button.pack(pady=10)

# Run the main loop
root.mainloop()

final_mpen, final_calculated_value, selected_champion = submit_clicked()
print("Stored final mpen value:", final_mpen)
print("Stored final calculated value:", final_calculated_value)
