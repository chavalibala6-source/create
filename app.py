import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

NOTES_FILE = 'notes.json'

# Load notes from JSON file
def load_notes():
    try:
        with open(NOTES_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save notes to JSON file
def save_notes(notes):
    with open(NOTES_FILE, 'w') as f:
        json.dump(notes, f, indent=4)

# Home - All Notes
@app.route('/')
def all_notes():
    notes = load_notes()
    return render_template('all_notes.html', notes=notes)

# Create or Edit a Note
@app.route('/paper')
def paper():
    page_number = request.args.get('page', type=int)
    notes = load_notes()
    note = None
    if page_number is not None:
        note = next((n for n in notes if n['page_number'] == page_number), None)
    return render_template('paper.html', note=note)

# Save Note
@app.route('/save_page', methods=['POST'])
def save_page():
    notes = load_notes()
    page_number = request.form.get('page_number', type=int)
    title = request.form['title']
    text = request.form['text']

    if page_number == 0 or page_number is None:  # New note
        page_number = max([n['page_number'] for n in notes], default=0) + 1
        notes.append({'page_number': page_number, 'title': title, 'text': text, 'images': []})
    else:  # Update existing note
        for n in notes:
            if n['page_number'] == page_number:
                n['title'] = title
                n['text'] = text
                break

    save_notes(notes)
    return redirect(url_for('all_notes'))

# Delete Note
@app.route('/delete')
def delete_page():
    page_number = request.args.get('page', type=int)
    if page_number is None:
        return "Page number missing!", 400

    notes = load_notes()
    notes = [note for note in notes if note['page_number'] != page_number]
    save_notes(notes)
    return redirect(url_for('all_notes'))

# Upload Image
@app.route('/upload_image', methods=['POST'])
def upload_image():
    page_number = request.args.get('page', type=int)
    file = request.files['image']
    if file:
        filename = f"{page_number}_{file.filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        notes = load_notes()
        for n in notes:
            if n['page_number'] == page_number:
                n.setdefault('images', []).append(filename)
                break
        save_notes(notes)

    return redirect(url_for('paper', page=page_number))

# Serve uploaded images
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
