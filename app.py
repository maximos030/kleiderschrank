from flask import Flask, request, render_template, redirect, url_for, flash
import os
from PIL import Image
from backgroundremover.backgroundremover.bg import remove
import io

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
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
        image_path = request.form['image_path']
        size = request.form['size']
        brand = request.form['brand']
        description = request.form['description']
        # Save the information to a database or a file
        flash('Clothing item successfully saved', 'success')
        return redirect(url_for('index'))

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
