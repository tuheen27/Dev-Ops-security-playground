#!/bin/env python

import subprocess
import shlex
import os
from flask import Flask, request, jsonify

app = Flask(__name__)


# Static routes MUST come before dynamic catch-all routes
@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for container orchestration."""
    return 'OK'


@app.route('/exec', methods=['POST'])
def exec():
    """Execute a command (intentionally insecure for testing - use shlex to reduce risk)."""
    try:
        command = request.values.get('command')
        if not command:
            return jsonify({'error': 'Missing command parameter'}), 400
        
        # Use shlex.split() to parse command safely and avoid shell injection
        # Still runs via shell but much safer than raw string with shell=True
        try:
            args = shlex.split(command)
        except ValueError as e:
            return jsonify({'error': f'Invalid command syntax: {str(e)}'}), 400
        
        process = subprocess.run(args, capture_output=True, timeout=10, shell=False)
        
        # Return as JSON to avoid binary data issues
        return jsonify({
            'stdout': process.stdout.decode('utf-8', errors='replace'),
            'stderr': process.stderr.decode('utf-8', errors='replace'),
            'returncode': process.returncode
        }), 200
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Command timeout (>10s)'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Dynamic routes (catch-all) come AFTER static routes
@app.route('/<path:file_to_read>', methods=['GET'])
def read(file_to_read):
    """Read a file from the filesystem (intentionally insecure for testing)."""
    try:
        file_path = '/' + file_to_read
        
        # Validate file exists and is readable
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_to_read}'}), 404
        
        if not os.path.isfile(file_path):
            return jsonify({'error': f'Not a file: {file_to_read}'}), 400
        
        # Check file size to prevent huge reads
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10 MB limit
            return jsonify({'error': f'File too large: {file_size} bytes (max 10 MB)'}), 413
        
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        return jsonify({
            'file': file_to_read,
            'size': len(content),
            'content': content
        }), 200
    except PermissionError:
        return jsonify({'error': f'Permission denied: {file_to_read}'}), 403
    except IsADirectoryError:
        return jsonify({'error': f'Is a directory: {file_to_read}'}), 400
    except UnicodeDecodeError as e:
        return jsonify({'error': f'Cannot read binary file: {file_to_read}'}), 415
    except Exception as e:
        return jsonify({'error': f'Error reading file: {str(e)}'}), 500


@app.route('/<path:file_to_write>', methods=['POST'])
def write(file_to_write):
    """Write content to a file (intentionally insecure for testing)."""
    try:
        content = request.values.get('content')
        if content is None:
            return jsonify({'error': 'Missing content parameter'}), 400
        
        file_path = '/' + file_to_write
        
        # Check content size to prevent huge writes
        if len(content) > 10 * 1024 * 1024:  # 10 MB limit
            return jsonify({'error': f'Content too large: {len(content)} bytes (max 10 MB)'}), 413
        
        # Ensure parent directory exists
        parent_dir = os.path.dirname(file_path)
        if parent_dir and not os.path.exists(parent_dir):
            try:
                os.makedirs(parent_dir, exist_ok=True)
            except PermissionError:
                return jsonify({'error': f'Cannot create parent directory: {parent_dir}'}), 403
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'status': 'written',
            'file': file_to_write,
            'bytes': len(content)
        }), 201
    except PermissionError:
        return jsonify({'error': f'Permission denied: {file_to_write}'}), 403
    except IsADirectoryError:
        return jsonify({'error': f'Cannot write to directory: {file_to_write}'}), 400
    except Exception as e:
        return jsonify({'error': f'Error writing file: {str(e)}'}), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors gracefully."""
    return jsonify({'error': 'Not found'}), 404


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8080)
