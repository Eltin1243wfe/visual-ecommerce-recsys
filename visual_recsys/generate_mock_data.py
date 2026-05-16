import os
import csv
import random
from PIL import Image, ImageDraw

# Create standard nested folders
os.makedirs('visual_recsys/data/raw', exist_ok=True)

categories = ['Shirts', 'Pants', 'Shoes', 'Hoodies']
colors = ['red', 'blue', 'green', 'yellow', 'purple', 'black']
shapes = ['circle', 'square', 'triangle']

csv_path = 'visual_recsys/data/raw/products.csv'

with open(csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['product_id', 'name', 'category', 'price', 'image_path'])
    
    for i in range(1, 21):
        cat = random.choice(categories)
        col = random.choice(colors)
        sha = random.choice(shapes)
        price = round(random.uniform(19.99, 89.99), 2)
        
        img = Image.new('RGB', (300, 300), color='white')
        draw = ImageDraw.Draw(img)
        
        if sha == 'circle':
            draw.ellipse([50, 50, 250, 250], fill=col)
        elif sha == 'square':
            draw.rectangle([50, 50, 250, 250], fill=col)
        elif sha == 'triangle':
            draw.polygon([(150, 50), (50, 250), (250, 250)], fill=col)
            
        img_name = f"prod_{i}.jpg"
        # Store clean path relative to the project root folder
        img_path = f"visual_recsys/data/raw/{img_name}"
        img.save(img_path)
        
        writer.writerow([i, f"{col.capitalize()} {sha.capitalize()}", cat, price, img_path])

print(f"Generated 20 mock images and products.csv successfully!")