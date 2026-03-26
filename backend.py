import os
import shutil
import uuid
from flask import Flask, request, jsonify, send_from_directory, abort
from dotenv import load_dotenv
from files_processor import process_files
from vector_store import VectorStore
from rag import ask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, static_folder='static', static_url_path='/static')

state = {
    'store': None,
    'loaded_files': [],
    'history': []
}

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/status')
def status():
    files = [os.path.basename(p) for p in state['loaded_files']]
    return jsonify({'ok': True, 'filenames': files})

@app.route('/upload', methods=['POST'])
def upload():
    if 'files' not in request.files:
        return jsonify({'detail': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'detail': 'No files uploaded'}), 400

    saved_paths = []
    for file in files:
        filename = file.filename
        if not filename:
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in ('.pdf', '.docx', '.txt', '.pptx'):
            return jsonify({'detail': f'Unsupported file type: {filename}'}), 400

        unique_name = f"{uuid.uuid4().hex}_{os.path.basename(filename)}"
        dest = os.path.join(UPLOAD_FOLDER, unique_name)
        file.save(dest)
        saved_paths.append(dest)

    # load and index
    chunks = process_files(saved_paths)
    store = VectorStore()
    store.add(chunks)

    state['store'] = store
    state['loaded_files'] = saved_paths
    state['history'] = []

    return jsonify({'message': f'Loaded {len(chunks)} chunks from {len(saved_paths)} files.'})

@app.route('/ask', methods=['POST'])
def ask_endpoint():
    if state['store'] is None:
        return jsonify({'detail': 'No files loaded. Upload documents first.'}), 400

    data = request.json or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'detail': 'Question is required.'}), 400

    # Use rag.ask in debug mode to expose vector hits for troubleshooting.
    answer, sources, results = ask(question, state['store'], state['history'], debug=True)
    state['history'].append({'question': question, 'answer': answer})

    result_debug = [
        {
            'source': r[0]['source'],
            'page': r[0]['page'],
            'score': r[1],
            'text_preview': r[0]['text'][:220]
        }
        for r in results
    ]

    return jsonify({
        'answer': answer,
        'sources': sources,
        'history': state['history'],
        'debug': result_debug
    })

@app.route('/reset', methods=['DELETE'])
def reset():
    state['store'] = None
    state['loaded_files'] = []
    state['history'] = []

    if os.path.isdir(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    return jsonify({'message': 'Reset complete'})

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
