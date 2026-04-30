from flask import Flask, request, redirect, url_for, jsonify, render_template
import uuid
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

BIN_ID = os.getenv("BIN_ID")
API_KEY = os.getenv("API_KEY")
BASE_URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"

HEADERS = {
    "X-Master-Key": API_KEY,
    "Content-Type": "application/json"
}

def load_data():
    try:
        r = requests.get(BASE_URL + '/latest', headers=HEADERS)
        r.raise_for_status()
        data = r.json()["record"]
        return {
            "groups": data.get('groups', []),
            "joined_ids": set(data.get('joined_ids', []))
        }
    except Exception as e:
        return {
            "groups": [],
            "joined_ids": set()
        }

def save_data(data):
    try:
        payload = {
            "groups": data["groups"],
            "joined_ids": list(data["joined_ids"])
        }

        r = requests.put(BASE_URL, json=payload, headers=HEADERS)
        r.raise_for_status()
        return True
    except Exception as e:
        print("SAVE ERROR:", e)
        return False

def find_group(group_id, groups):
    for group in groups:
        if group['id'] == group_id:
            return group
    return None

@app.route("/")
def home():
    data = load_data()
    query = request.args.get('q', '').lower()
    
    groups = data['groups']
    if query:
        groups = [
            g for g in groups
            if query in g['name'].lower() or query in g['topic'].lower()
        ]
        
    return render_template(
        "index.html",
        groups=groups,
        joined_ids=data['joined_ids'],
        query=query
    )

@app.route("/create", methods=["GET", "POST"])
def create_group():
    if request.method == "GET":
        return render_template("create.html")
    
    name = request.form.get("name", "").strip()
    topic = request.form.get("topic", "").strip()
    date = request.form.get("date", "").strip()
    
    if not name or not topic or not date:
        return jsonify({"error": "Name, topic, and date are required."}), 400
    
    data = load_data()
    
    new_id = str(uuid.uuid4())
    new_group = {
        "id": new_id,
        "name": name,
        "topic": topic,
        "date": date,
        "people": 1,
        "owner": "You",
        "messages": []
    }
    
    data['groups'].append(new_group)
    if new_id not in data['joined_ids']:
        data['joined_ids'].add(new_id)
        
    ok = save_data(data)
    if not ok:
        return jsonify({"error": "Failed to save data."}), 500
    
    return redirect(url_for('home'))

@app.route("/group/<group_id>")
def group_page(group_id):
    data = load_data()
    group = find_group(group_id, data['groups'])
    
    if not group:
        return jsonify({"error": "Group not found."}), 404
    
    return render_template(
        "group.html",
        group=group,
        joined=group_id in data['joined_ids']
    )

@app.route("/group/<group_id>/join", methods=["POST"])
def join_group(group_id):
    data = load_data()
    group = find_group(group_id, data['groups'])
    
    if not group:
        return jsonify({"error": "Group not found."}), 404
    
    if group_id not in data['joined_ids']:
        data['joined_ids'].add(group_id)
        group['people'] += 1
        ok = save_data(data)
        if not ok:
            return jsonify({"error": "Failed to save data."}), 500
    
    return redirect(url_for('group_page', group_id=group_id))

@app.route("/group/<group_id>/leave", methods=["POST"])
def leave_group(group_id):
    data = load_data()
    group = find_group(group_id, data['groups'])

    if not group:
        return jsonify({"error": "Group not found."}), 404

    if group_id in data['joined_ids']:
        data['joined_ids'].remove(group_id)

        if group.get('people', 0) > 0:
            group['people'] -= 1

        ok = save_data(data)
        if not ok:
            return jsonify({"error": "Failed to save data."}), 500

    return redirect(url_for('home'))

@app.route("/group/<group_id>/message", methods=["POST"])
def send_message(group_id):
    data = load_data()
    group = find_group(group_id, data['groups'])
    
    if not group:
        return jsonify({"error": "Group not found."}), 404
    
    if group_id not in data['joined_ids']:
        return jsonify({"error": "You must join the group to send messages."}), 403
    
    message = request.form.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message cannot be empty."}), 400
    
    group.setdefault('messages', []).append("You: " + message)
    
    ok = save_data(data)
    if not ok:
        return jsonify({"error": "Failed to save data."}), 500
    
    return redirect(url_for('group_page', group_id=group_id))

@app.route("/group/<group_id>/delete", methods=["POST"])
def delete_group(group_id):
    data = load_data()
    group = find_group(group_id, data['groups'])
    
    if not group:
        return jsonify({"error": "Group not found."}), 404
    
    if group['owner'] != "You":
        return jsonify({"error": "Only the owner can delete the group."}), 403
    
    data['groups'] = [g for g in data['groups'] if g['id'] != group_id]
    if group_id in data['joined_ids']:
        data['joined_ids'].remove(group_id)
    
    ok = save_data(data)
    if not ok:
        return jsonify({"error": "Failed to save data."}), 500
    
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True, port=5001)