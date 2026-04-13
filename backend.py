import os
import shutil
import uuid
from typing import Optional
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
from files_processor import process_files
from vector_store import VectorStore
from rag import ask

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

app = Flask(__name__, static_folder='static', static_url_path='/static')

# Typed module-level state
store: Optional[VectorStore] = None
loaded_files: list[str] = []
history: list[dict] = []


def _restore_from_disk() -> None:
    """Re-index any files already in UPLOAD_FOLDER from a previous session."""
    global store, loaded_files
    existing = [
        os.path.join(UPLOAD_FOLDER, f)
        for f in sorted(os.listdir(UPLOAD_FOLDER))
        if os.path.isfile(os.path.join(UPLOAD_FOLDER, f))
    ]
    if not existing:
        return
    try:
        chunks = process_files(existing)
        new_store = VectorStore()
        new_store.add(chunks)
        store = new_store
        loaded_files = existing
        print(f"[startup] Re-indexed {len(existing)} file(s) from uploads folder.")
    except Exception as exc:
        print(f"[startup] Warning: could not re-index existing files: {exc}")


_restore_from_disk()


@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/status')
def status():
    filenames = [os.path.basename(p) for p in loaded_files]
    return jsonify({'ok': True, 'filenames': filenames})


@app.route('/upload', methods=['POST'])
def upload():
    global store, loaded_files, history

    if 'files' not in request.files:
        return jsonify({'detail': 'No files provided'}), 400

    files = request.files.getlist('files')
    if not files:
        return jsonify({'detail': 'No files uploaded'}), 400

    saved_paths: list[str] = []
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

    # Append to existing files
    loaded_files.extend(saved_paths)
    print(f"[upload] Added {len(saved_paths)} new file(s). Current total: {len(loaded_files)}")
    
    # Re-index EVERYTHING to keep store in sync
    try:
        chunks = process_files(loaded_files)
        if chunks:
            new_store = VectorStore()
            new_store.add(chunks)
            store = new_store
        else:
            store = None
            
        history = []
        return jsonify({'message': f'Added {len(saved_paths)} new file(s). Total: {len(loaded_files)} files indexed.'})
    except Exception as e:
        print(f"[upload] Error indexing: {e}")
        # Rollback loaded_files if indexing fails (explicitly typed to satisfy Pyre2)
        loaded_files = [str(p) for p in loaded_files if p not in saved_paths]
        return jsonify({'detail': f'Error indexing files: {str(e)}'}), 500


@app.route('/ask', methods=['POST'])
def ask_endpoint():
    global history

    if store is None:
        return jsonify({'detail': 'No files loaded. Upload documents first.'}), 400

    data = request.json or {}
    question = data.get('question', '').strip()
    if not question:
        return jsonify({'detail': 'Question is required.'}), 400

    answer, sources, results = ask(question, store, history, debug=True)
    history.append({'question': question, 'answer': answer})

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
        'history': history,
        'debug': result_debug
    })


@app.route('/delete-file', methods=['DELETE'])
def delete_file():
    global store, loaded_files, history

    data = request.get_json(force=True, silent=True) or {}
    filename = data.get('filename', '').strip()
    if not filename:
        return jsonify({'detail': 'filename is required'}), 400

    print(f"[delete] Targeting file: {filename}")
    print(f"[delete] Current files in list ({len(loaded_files)}): {[os.path.basename(p) for p in loaded_files]}")

    # Find the matching path (stored paths have a uuid prefix)
    target: Optional[str] = None
    for path in loaded_files:
        if os.path.basename(path) == filename:
            target = path
            break

    if target is None:
        print(f"[delete] Error: File '{filename}' not found in loaded_files.")
        return jsonify({'detail': 'File not found'}), 404

    assert isinstance(target, str)

    # Remove from disk
    if os.path.exists(target):
        try:
            os.remove(target)
            print(f"[delete] Removed from disk: {target}")
        except Exception as e:
            print(f"[delete] Warning: could not remove file from disk: {e}")

    # Update state - be very explicit here
    new_loaded_files = [str(p) for p in loaded_files if str(p) != target]
    loaded_files = new_loaded_files
    history = []
    
    print(f"[delete] Files remaining after removal ({len(loaded_files)}): {[os.path.basename(p) for p in loaded_files]}")

    if loaded_files:
        try:
            chunks = process_files(loaded_files)
            if chunks:
                new_store = VectorStore()
                new_store.add(chunks)
                store = new_store
            else:
                store = None
        except Exception as e:
            print(f"[delete] Error re-indexing: {e}")
            # Even if indexing fails, the file list should be correct
    else:
        store = None

    filenames = [os.path.basename(p) for p in loaded_files]
    return jsonify({'message': f'Deleted {filename}', 'filenames': filenames})


@app.route('/reset', methods=['DELETE'])
def reset():
    global store, loaded_files, history

    store = None
    loaded_files = []
    history = []

    if os.path.isdir(UPLOAD_FOLDER):
        shutil.rmtree(UPLOAD_FOLDER)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    return jsonify({'message': 'Reset complete'})


@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)