from flask import Flask, render_template_string, request, jsonify
from datetime import datetime, timedelta

app = Flask(__name__)

# --- MOCK DATABASE ---
# In a real app, you would use a database like SQLite.
# 'interval_hours' represents the limit before the machine is at risk of crashing.
machines = [
    {"id": 1, "name": "CNC Lathe", "last_service": "2026-04-14 10:00:00", "interval_hours": 50},
    {"id": 2, "name": "Hydraulic Press", "last_service": "2026-04-10 08:00:00", "interval_hours": 100},
    {"id": 3, "name": "3D Printer", "last_service": "2026-04-15 12:00:00", "interval_hours": 24},
]

# --- LOGIC: TIME UNTIL CRASH ---
def get_uptime_stats(last_service_str, interval_hours):
    last_service = datetime.strptime(last_service_str, '%Y-%m-%d %H:%M:%S')
    crash_point = last_service + timedelta(hours=interval_hours)
    now = datetime.now()
    
    remaining = crash_point - now
    
    if remaining.total_seconds() <= 0:
        return "CRASH RISK: Overdue", 0, "Red"
    
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds // 60) % 60
    
    status_text = f"{days}d {hours}h {minutes}m remaining"
    return status_text, days, "Green"

# --- API ROUTES (CRUD) ---
@app.route('/api/machines', methods=['GET'])
def api_get_machines():
    return jsonify(machines)

@app.route('/api/machines/<int:id>/service', methods=['POST'])
def api_service_machine(id):
    machine = next((m for m in machines if m['id'] == id), None)
    if machine:
        # Reset last service to current time
        machine['last_service'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return jsonify({"message": "Machine serviced successfully", "new_date": machine['last_service']})
    return jsonify({"error": "Machine not found"}), 404

# --- FRONTEND (HTML Template) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Machine Maintenance Logger</title>
    <style>
        body { font-family: sans-serif; background: #f4f7f6; padding: 20px; color: #333; }
        .container { max-width: 900px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { text-align: center; color: #2c3e50; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
        th { background-color: #f8f9fa; }
        .status-pill { padding: 5px 12px; border-radius: 20px; font-size: 0.85em; font-weight: bold; color: white; }
        .Green { background-color: #27ae60; }
        .Red { background-color: #e74c3c; }
        .btn-service { background: #3498db; color: white; border: none; padding: 8px 15px; border-radius: 4px; cursor: pointer; }
        .btn-service:hover { background: #2980b9; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Machine Maintenance Logger</h1>
        <table>
            <thead>
                <tr>
                    <th>Machine Name</th>
                    <th>Last Serviced</th>
                    <th>Operating Limit</th>
                    <th>Time Until Crash</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for m in machines %}
                {% set time_text, days_left, color = get_stats(m.last_service, m.interval_hours) %}
                <tr>
                    <td><strong>{{ m.name }}</strong></td>
                    <td>{{ m.last_service }}</td>
                    <td>{{ m.interval_hours }} Hours</td>
                    <td><span class="status-pill {{ color }}">{{ time_text }}</span></td>
                    <td>
                        <button class="btn-service" onclick="serviceMachine({{ m.id }})">Mark Serviced</button>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>

    <script>
        function serviceMachine(id) {
            fetch(`/api/machines/${id}/service`, { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE, machines=machines, get_stats=get_uptime_stats)

if __name__ == '__main__':
    # Set debug=True for development
    app.run(debug=True)
