# ⚡ Smart Task Analyzer

A modern, intelligent task‑prioritization system built with **Django (Backend)** and **Vanilla JS + Vis.js (Frontend)**.  
This tool analyzes tasks, dependencies, urgency, importance, and time estimates to generate a **data‑driven priority score**.  
It also provides a **dependency graph**, **Eisenhower Matrix**, and **AI‑Learning feedback loop**.

---

## 🚀 Features

### ✅ Core Features
- Add tasks with:
  - Title  
  - Due date  
  - Estimated hours  
  - Importance score  
  - Dependencies  
- Bulk JSON task input  
- Multiple priority strategies  
  - **Smart Balance**  
  - **Fastest First**  
  - **High Impact**  
  - **Deadline Driven**  
- Detailed score reasoning  
- Color‑coded priority levels  
- Fully responsive modern UI  
- Dark mode toggle  

---

## 📊 Advanced Features
### 🔵 Dependency Graph (Vis.js)
Visualizes tasks as nodes and dependency relationships as arrows.

### 🔵 Eisenhower Matrix (Urgency × Importance)
Auto‑assigns tasks into:
- **Do First**
- **Schedule**
- **Delegate**
- **Eliminate**

### 🔵 AI Learning (User Feedback)
Users can mark suggestions as:
- 👍 Helpful  
- 👎 Not Helpful  

The backend learns from feedback and adjusts scoring weights.

### 🔵 Date Intelligence
- Urgency considers weekends and holidays  
- Overdue tasks gain high urgency weight  

---

## 🧠 Priority Scoring Factors

| Factor | Description |
|--------|------------|
| **Deadline** | Days left / overdue impact |
| **Importance** | User‑defined priority |
| **Estimated Hours** | Time‑effort normalization |
| **Dependencies** | Chain depth + blocking tasks |
| **Strategy Modifier** | Chooses algorithm behavior |

---

## 🛠️ Tech Stack

### **Backend**
- Python  
- Django REST Framework  
- CORS Headers  
- Dateutil  

### **Frontend**
- Vanilla JavaScript  
- Vis.js dependency graph  
- HTML + CSS (glass‑morphism UI)  

## 🔥 API Endpoints

### **POST /api/tasks/analyze/**
Analyze tasks and return:
- Sorted tasks
- Scores
- Explanations
- Cycle detection

### **GET /api/tasks/suggest/**
Returns **Top 3 tasks** based on chosen strategy.

### **POST /api/tasks/graph/**
Returns nodes + edges for dependency visualization.

### **POST /api/tasks/feedback/**
Stores user feedback to improve scoring.

---

## 🖥️ Running the Project

### 1️⃣ Backend (Django)
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend will start at:
```
http://127.0.0.1:8000/
```

### 2️⃣ Frontend
Use VS Code Live Server or run:

```
cd frontend
python -m http.server 3000
```

Frontend runs at:
```
http://127.0.0.1:3000/index.html
```

---

## 🧪 Running Unit Tests
Contains scoring logic tests:

```
python manage.py test
```

---

## 📸 Screenshots (Add yours)
```
📌 Dashboard
📌 Dependency Graph
📌 Suggestions UI
📌 Dark Mode View
```
# ⚡ Smart Task Analyzer

A modern, intelligent task‑prioritization system built with **Django (Backend)** and **Vanilla JS + Vis.js (Frontend)**.  
This tool analyzes tasks, dependencies, urgency, importance, and time estimates to generate a **data‑driven priority score**.  
It also provides a **dependency graph**, **Eisenhower Matrix**, and **AI‑Learning feedback loop**.

---

## 🚀 Features

### ✅ Core Features
- Add tasks with:
  - Title  
  - Due date  
  - Estimated hours  
  - Importance score  
  - Dependencies  
- Bulk JSON task input  
- Multiple priority strategies  
  - **Smart Balance**  
  - **Fastest First**  
  - **High Impact**  
  - **Deadline Driven**  
- Detailed score reasoning  
- Color‑coded priority levels  
- Fully responsive modern UI  
- Dark mode toggle  

---

## 📊 Advanced Features
### 🔵 Dependency Graph (Vis.js)
Visualizes tasks as nodes and dependency relationships as arrows.

### 🔵 Eisenhower Matrix (Urgency × Importance)
Auto‑assigns tasks into:
- **Do First**
- **Schedule**
- **Delegate**
- **Eliminate**

### 🔵 AI Learning (User Feedback)
Users can mark suggestions as:
- 👍 Helpful  
- 👎 Not Helpful  

The backend learns from feedback and adjusts scoring weights.

### 🔵 Date Intelligence
- Urgency considers weekends and holidays  
- Overdue tasks gain high urgency weight  

---

## 🧠 Priority Scoring Factors

| Factor | Description |
|--------|------------|
| **Deadline** | Days left / overdue impact |
| **Importance** | User‑defined priority |
| **Estimated Hours** | Time‑effort normalization |
| **Dependencies** | Chain depth + blocking tasks |
| **Strategy Modifier** | Chooses algorithm behavior |

---

## 🛠️ Tech Stack

### **Backend**
- Python  
- Django REST Framework  
- CORS Headers  
- Dateutil  

### **Frontend**
- Vanilla JavaScript  
- Vis.js dependency graph  
- HTML + CSS (glass‑morphism UI)  

## 🔥 API Endpoints

### **POST /api/tasks/analyze/**
Analyze tasks and return:
- Sorted tasks
- Scores
- Explanations
- Cycle detection

### **GET /api/tasks/suggest/**
Returns **Top 3 tasks** based on chosen strategy.

### **POST /api/tasks/graph/**
Returns nodes + edges for dependency visualization.

### **POST /api/tasks/feedback/**
Stores user feedback to improve scoring.

---

## 🖥️ Running the Project

### 1️⃣ Backend (Django)
```
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Backend will start at:
```
http://127.0.0.1:8000/
```

### 2️⃣ Frontend
Use VS Code Live Server or run:

```
cd frontend
python -m http.server 3000
```

Frontend runs at:
```
http://127.0.0.1:3000/index.html
```

---

## 🧪 Running Unit Tests
Contains scoring logic tests:

```
python manage.py test
```

---

## 📸 Screenshots (Add yours)
```
📌 Dashboard
📌 Dependency Graph
📌 Suggestions UI
📌 Dark Mode View
```
<img width="444" height="897" alt="image" src="https://github.com/user-attachments/assets/d9d2e631-69e2-42fa-bd56-0ca1bfeb3281" />
