# Gatherly

---

## Installation
### 1. Clone the repository 
```bash
git clone https://github.com/GabrielKV4/Gatherly.git
cd Gatherly
```

---

### 2. Create a virtual environment
```bash
python3 -m venv venv
```

Activate it:

Mac/Linux:
```bash
source venv/bin/activate
```

Windows:
```bash
venv\Scripts\activate
```

---

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## Environment Setup

This project uses JSONBIN.io for data storage.

### 1. Go to:
https://jsonbin.io

### 2. Create an account

### 3. Create a new bin with this content:
```json
{
  "groups": [],
  "joined_ids": []
}
```

### 4. Copy your:
- Bin ID
- API Key (X-Master-Key)

### 5. Create a `.env` file in the project root:
```env
BIN_ID=your_bin_id_here
API_KEY=your_api_key_here
```

---

## Run the App
```bash
python app.py
```

Then open:

http://127.0.0.1:5000/

---

