from flask import Flask, render_template_string
import json

app = Flask(__name__)

@app.route('/')
def dashboard():
    blocks = []
    try:
        with open('blocks.json', 'r') as f:
            for line in f:
                blocks.append(json.loads(line.strip()))
        blocks = blocks[-10:]
    except FileNotFoundError:
        blocks = [{'hash': 'N/A', 'nonce': 'N/A', 'duration': 0, 'coord': (0, 0, 0), 'block_time': 0, 'transactions': []}]
    template = '''
    <html>
    <head><title>TriadNet Mining Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        table { border-collapse: collapse; width: 100%; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
    </style>
    </head>
    <body>
    <h1>TriadNet Mining Dashboard</h1>
    <table>
        <tr><th>Block Hash</th><th>Nonce</th><th>Duration (s)</th><th>Coordinates</th><th>Transactions</th></tr>
        {% for block in blocks %}
        <tr>
            <td>{{ block.hash[:20] }}...</td>
            <td>{{ block.nonce }}</td>
            <td>{{ block.duration | round(3) }}</td>
            <td>{{ block.coord }}</td>
            <td>{{ block.transactions | length }}</td>
        </tr>
        {% endfor %}
    </table>
    </body>
    </html>
    '''
    return render_template_string(template, blocks=blocks)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
