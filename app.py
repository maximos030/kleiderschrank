from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
import os
from PIL import Image
from backgroundremover.backgroundremover.bg import remove
import io
import pandas as pd

app = Flask(__name__)
app.secret_key = b'\xf4\xec\xbd\xad\x17\x85\x8d\xaf\xf8\xb0\xef\xc5\xfb\xae\x10\x92'  # Beispiel für einen generierten Schlüssel
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
DATABASE_FILE = 'clothing_data.xlsx'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

CATEGORIES = {
    'top': 'static/images/tops',
    'bottom': 'static/images/bottoms',
    'shoe': 'static/images/shoes'
}

for category in CATEGORIES.values():
    os.makedirs(category, exist_ok=True)

# Initialize the database if it does not exist
if not os.path.exists(DATABASE_FILE):
    df = pd.DataFrame(columns=['id', 'image_path', 'category', 'size', 'brand', 'description'])
    df.to_excel(DATABASE_FILE, index=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file')
        category = request.form.get('category')
        
        if not file:
            flash('No file part', 'error')
            return redirect(request.url)
        if not category or category not in CATEGORIES:
            flash('No category selected or invalid category', 'error')
            return redirect(request.url)
        if file.filename == '':
            flash('No selected file', 'error')
            return redirect(request.url)

        file_path = save_file(file)
        processed_file_path = process_image(file_path)
        new_file_path = save_processed_image(processed_file_path, category)
        flash('File successfully uploaded and processed', 'success')
        return render_template('add_clothing.html', image_path=new_file_path, category=category)
    
    return render_template('upload.html')

@app.route('/save_clothing', methods=['POST'])
def save_clothing():
    if request.method == 'POST':
        try:
            image_path = request.form['image_path']
            category = request.form['category']
            size = request.form['size']
            brand = request.form['brand']
            description = request.form['description']
        except KeyError as e:
            flash(f'Missing data: {str(e)}', 'error')
            return redirect(url_for('index'))

        # Load existing data
        df = pd.read_excel(DATABASE_FILE)
        # Generate a new ID
        new_id = get_next_id()
        # Append new data
        new_row = {
            'id': new_id,
            'image_path': image_path,
            'category': category,
            'size': size,
            'brand': brand,
            'description': description
        }
        df = df.append(new_row, ignore_index=True)
        # Save back to Excel
        df.to_excel(DATABASE_FILE, index=False)
        
        flash('Clothing item successfully saved', 'success')
        return redirect(url_for('index'))

def get_next_id():
    df = pd.read_excel(DATABASE_FILE)
    if df.empty:
        return 1
    else:
        return df['id'].max() + 1

@app.route('/get_images/<category>', methods=['GET'])
def get_images(category):
    if category not in CATEGORIES:
        return jsonify({'error': 'Invalid category'}), 400
    image_folder = CATEGORIES[category]
    images = []
    for filename in os.listdir(image_folder):
        if filename.endswith('.png'):
            images.append({
                'id': len(images) + 1,
                'src': url_for('static', filename=f'images/{category}s/{filename}'),
                'alt': f'{category.capitalize()} {len(images) + 1}'
            })
    return jsonify(images)

def save_file(file):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)
    return file_path

def process_image(file_path):
    input_image = Image.open(file_path)
    img_byte_arr = io.BytesIO()
    input_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    output_image = remove(img_byte_arr, model_name="u2net")
    output_path = os.path.join(app.config['PROCESSED_FOLDER'], 'output.png')
    with open(output_path, 'wb') as out_file:
        out_file.write(output_image)
    return output_path

def save_processed_image(processed_file_path, category):
    category_folder = CATEGORIES[category]
    file_index = 1
    while True:
        new_file_name = f'{category}{file_index}.png'
        new_file_path = os.path.join(category_folder, new_file_name)
        if not os.path.exists(new_file_path):
            break
        file_index += 1
    os.rename(processed_file_path, new_file_path)
    
    # Convert backslashes to forward slashes
    return new_file_path.replace("\\", "/")

if __name__ == '__main__':
    app.run(debug=True)
