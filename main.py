import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import pandas as pd

# Load Champions data from Excel
champs = pd.read_excel(r"C:\Users\Matth\OneDrive\Documents\LoL\Champs.xlsx")

# Define mpen, ppen, and calculated_value as global variables
mpen = 0
ppen = 0
calculated_value = 0
selected_items = []  # list for offensive items
selected_defensive_items = []  # list for defensive items
selected_champion = None  # Initialize selected champion globally
additional_MR = 0  # Additional MR from items

# List to keep track of clicked indices
clicked_mp_indices = []
clicked_def_indices = []
def image_clicked(index, item_type):
    global mpen, ppen, buttons, defensive_buttons  # Access the global variables

    if index in clicked_mp_indices and item_type == "offensive":
        print("Item already selected!")
        return
    if index in clicked_def_indices and item_type == "defensive":
        print("Item already selected!")
        return
    # Disable the button
    if item_type == "offensive":
        buttons[index].config(state=tk.DISABLED)
        clicked_mp_indices.append(index)
    elif item_type == "defensive":
        defensive_buttons[index].config(state=tk.DISABLED)
        clicked_def_indices.append(index)
    

    if item_type == "offensive":
        handle_offensive_item(index)
    elif item_type == "defensive":
        handle_defensive_item(index)

    update_display()

def handle_offensive_item(index):
    global mpen, ppen
    if index == 0:
        selected_label.config(text="Shadowflame")
        selected_items.append("Shadowflame")
        mpen += 12
    elif index == 1:
        selected_label.config(text="Sorcs Shoes")
        selected_items.append("Sorcs Shoes")
        mpen += 18
    elif index == 2:
        selected_label.config(text="Stormsurge")
        selected_items.append("Stormsurge")
        mpen += 12
    elif index == 3:
        selected_label.config(text="Cryptobloom")
        selected_items.append("Cryptobloom")
        ppen += 0.35  # Adjusted to 0.35 to match your description
    elif index == 4:
        selected_label.config(text="Voidstaff")
        selected_items.append("Voidstaff")
        ppen += 0.40  # Adjusted to 0.40 to match your description

def handle_defensive_item(index):
    global additional_MR, selected_label_defensive
    if index == 0:
        selected_label_defensive.config(text="Abyssal Mask")
        selected_defensive_items.append("Abyssal Mask")
        additional_MR += 60
    elif index == 1:
        selected_label_defensive.config(text="Banshee's Veil")
        selected_defensive_items.append("Banshee's Veil")
        additional_MR += 60
    elif index == 2:
        selected_label_defensive.config(text="Force of Nature")
        selected_defensive_items.append("Force of Nature")
        additional_MR += 60
    elif index == 3:
        selected_label_defensive.config(text="Hexdrinker")
        selected_defensive_items.append("Hexdrinker")
        additional_MR += 35
    elif index == 4:
        selected_label_defensive.config(text="Maw of Malmortius")
        selected_defensive_items.append("Maw of Malmortius")
        additional_MR += 50
    elif index == 5:
        selected_label_defensive.config(text="Hallow Radiance")
        selected_defensive_items.append("Hallow Radiance")
        additional_MR += 40
    elif index == 6:
        selected_label_defensive.config(text="Wit's End")
        selected_defensive_items.append("Wit's End")
        additional_MR += 50
    elif index == 7:
        selected_label_defensive.config(text="Spirit Visage")
        selected_defensive_items.append("Spirit Visage")
        additional_MR += 450
    elif index == 8:
        selected_label_defensive.config(text="Mercury's Treads")
        selected_defensive_items.append("Mercury's Treads")
        additional_MR += 35

def update_display():
    selected_label.config(text=f"Selected offensive items: {', '.join(selected_items)}")
    selected_label_defensive.config(text=f"Selected defensive items: {', '.join(selected_defensive_items)}")

def on_select_champion(event=None):
    global selected_champion
    selected_champion = champion_var.get()
    if selected_champion:
        print(f"Selected champion: {selected_champion}")

def reset_form():
    global mpen, ppen, calculated_value, selected_items, additional_MR
    mpen = 0
    ppen = 0
    calculated_value = 0
    selected_items.clear()
    selected_defensive_items.clear()
    additional_MR = 0
    clicked_mp_indices.clear()
    clicked_def_indices.clear()

    # Reset the buttons
    for button in buttons:
        button.config(state=tk.NORMAL)
    for button in defensive_buttons:
        button.config(state=tk.NORMAL)

    selected_label.config(text="Selected offensive items: None")
    selected_label_defensive.config(text="Selected defensive items: None")
    result_label.config(text="")

    # Clear the level entry and champion selection
    level_entry.delete(0, tk.END)
    champion_var.set("Aatrox")
    
def submit_clicked():
    global mpen, ppen, calculated_value, selected_champion, selected_items, additional_MR
    
    # Get the level input from Entry widget
    try:
        level = int(level_entry.get())
    except ValueError:
        print("Invalid level input")
        return
    
    # Perform calculations based on level, MR, and other columns in champs DataFrame
    multiplier = champs.loc[champs['Champ'] == selected_champion, 'Growth'].values[0]
    base = champs.loc[champs['Champ'] == selected_champion, 'Base'].values[0]
    print(f"Additional MR from items: {additional_MR}")
    print(f"MR Multiplier for {selected_champion} at level {level}: {multiplier}")
    
    # Calculate the value globally accessible
    calculated_value = round(base + (level * multiplier),2)
    print(f"Enemies MR: {calculated_value}\n")

    # Calculate formulas and differences
    MR = calculated_value + additional_MR
    formula = round((1 - (100 / (100 + MR))) * 100, 2)
    formula2 = round((1 - (100 / ((100 + (MR - mpen)*(1-ppen))))) * 100, 2)
    diff = round((formula - formula2),2)
    formula3 = round((100 / (100 + MR)) * 100, 2)  # Formula 3: Percentage of magic damage dealt
    formula4 = round((100 / (100 + (MR - mpen)*(1-ppen))) * 100, 2)  # Formula 4: Percentage of magic damage received

    # Format selected items without brackets and quotes
    selected_items_str = ', '.join(selected_items)
    selected_defensive_items_str = ', '.join(selected_defensive_items)

    # Print results
    print(f"You will do {diff}% more magic damage to {selected_champion} at level {level} with {additional_MR} additional MR, if you have {selected_items_str} and {selected_defensive_items_str}\n")
    print(f"{selected_champion} with {additional_MR} additional MR will take {formula3}% of magic damage with no pen items vs {formula4}% of magic damage, if you have {selected_items_str} and {selected_defensive_items_str}\n")
    # Display results in the label
    result_text = (
       
        f"You will do {diff}% more magic damage to {selected_champion} at level {level} with {additional_MR} additional MR, "
        f"if you have {selected_items_str} and {selected_defensive_items_str}\n"
        f"{selected_champion} with {additional_MR} additional MR will take {formula3}% of magic damage with no pen items vs "
        f"{formula4}% of magic damage, if you have {selected_items_str} and {selected_defensive_items_str}\n"
    )
    
    result_label.config(text=result_text)
    
    return mpen, calculated_value, selected_champion

# Create the main window
root = tk.Tk()
root.title("Pick your pen items and defensive items")

# LabelFrame for offensive items
frame_offensive = ttk.LabelFrame(root, text="Pick your pen items")
frame_offensive.grid(row=0, column=0, padx=10, pady=10)

# LabelFrame for defensive items
frame_defensive = ttk.LabelFrame(root, text="Pick opponents defensive items")
frame_defensive.grid(row=0, column=1, padx=10, pady=10)

# Predefined images for offensive items (replace with your own paths)
image_paths = [
    r"C:\Users\Matth\OneDrive\Documents\LoL\shadowflame.png",
    r"C:\Users\Matth\OneDrive\Documents\LoL\Sorcerer%27s_Shoes_item_old2.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\stormsurge.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\cryptobloom.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\void.webp"
]

# Predefined images for defensive items (replace with your own paths)
defensive_image_paths = [
    r"C:\Users\Matth\OneDrive\Documents\LoL\abyssal.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\banshees.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\Force.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\hex.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\maw.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\hollow.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\wits.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\spirit visage.webp",
    r"C:\Users\Matth\OneDrive\Documents\LoL\mercs.jpg"  # Added Mercury's Treads
]

# List to store ImageTk objects for offensive items
images = []
buttons = []

# Load images and create buttons for offensive items
for i, path in enumerate(image_paths):
    image = Image.open(path)
    image.thumbnail((100, 100))  # Resize image if necessary
    images.append(ImageTk.PhotoImage(image))
    
    # Create a button with the image and bind it to a function
    button = tk.Button(frame_offensive, image=images[i], command=lambda idx=i: image_clicked(idx, "offensive"))
    button.grid(row=i // 2, column=i % 2, padx=5, pady=5, sticky="nsew")
    buttons.append(button)

# List to store ImageTk objects for defensive items
defensive_images = []
defensive_buttons = []

# Load defensive item images and create buttons
for i, path in enumerate(defensive_image_paths):
    image = Image.open(path)
    image.thumbnail((100, 100))  # Resize image if necessary
    defensive_images.append(ImageTk.PhotoImage(image))
    
    # Create a button with the image and bind it to a function
    button = tk.Button(frame_defensive, image=defensive_images[i], command=lambda idx=i: image_clicked(idx, "defensive"))
    button.grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")
    defensive_buttons.append(button)

# Labels to display selected items
selected_label = ttk.Label(root, text="Selected offensive items: None")
selected_label.grid(row=1, column=0, padx=10, pady=10, sticky='w')

selected_label_defensive = ttk.Label(root, text="Selected defensive item: None")
selected_label_defensive.grid(row=1, column=1, padx=10, pady=10, sticky='w')

# Dropdown menu for champion selection
champion_var = tk.StringVar()
champion_dropdown = ttk.OptionMenu(root, champion_var, *champs['Champ'].unique(), command=on_select_champion)
champion_dropdown.grid(row=2, column=0, columnspan=2, padx=20, pady=10)
# Labels for champ selection
Champ_label = ttk.Label(root, text="Select Champion")
Champ_label.grid(row=2, column=0, padx=10, pady=10, sticky='w')



# Label for level input
level_label = ttk.Label(root, text="Enter champion's level:")
level_label.grid(row=3, column=0, padx=10, pady=5, sticky='w')
level_entry = ttk.Entry(root)
level_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

# Submit button
submit_button = ttk.Button(root, text="Submit", command=submit_clicked)
submit_button.grid(row=4, column=0, columnspan=2, pady=10)

#Reset button
# Submit button
Reset_button = ttk.Button(root, text="Reset", command=reset_form)
Reset_button.grid(row=4, column=1, columnspan=2, pady=10)

# Label to display the result
result_label = ttk.Label(root, text="")
result_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky='w')
# Run the main loop
root.mainloop()







