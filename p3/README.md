# MMORPG 2D Offline / Society Simulator

A multi-agent society simulator where you observe autonomous bots with unique personalities, memories, and evolving language.

## 🚀 How to Run (Local Setup)

Follow these steps to start the simulation on your machine.

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- A modern web browser (Chrome, Firefox, Edge).

### 2. Installation

Open your terminal (Command Prompt, PowerShell, or Terminal) and navigate to the project folder:

```bash
cd path/to/unzipped/folder
```

(Optional) Create a virtual environment to keep your system clean:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required dependencies:
```bash
pip install -r requirements.txt
```

### 3. Start the Server

Run the backend server. This handles the simulation loop and serves the game files.

```bash
python3 backend/main.py
```

You should see output indicating the server is running, like:
`INFO: Uvicorn running on http://0.0.0.0:8000`

### 4. Play

Open your web browser and go to:

👉 **http://localhost:8000**

## 🎮 Controls

- **Pan:** Click and Drag (Middle or Right Mouse Button).
- **Zoom:** Mouse Wheel.
- **Inspect:** Left Click on any agent (colored dot) to view their Mind, Inventory, and Memory.

## 🌟 Features

- **Viral Language:** Agents learn and mutate phrases from each other. Watch for gold chat bubbles!
- **Psychology:** Every agent has a unique personality (Big Five traits) and can develop mental disorders.
- **Economy:** Agents gather wood, craft weapons, and equip gear to survive.
- **Zero Control:** You are the observer. The world evolves without you.
