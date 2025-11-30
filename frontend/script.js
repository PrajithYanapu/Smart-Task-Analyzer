
// CONNECT BACKEND

const API_BASE = 'http://127.0.0.1:8000/api/tasks/';

let tasks = [];
let lastSuggestions = []; // ⬅️ NEW: store last suggestions for feedback


// UI HELPERS

function setFeedback(msg, isError = false) {
    const f = document.getElementById('feedback');
    f.textContent = msg;
    f.style.color = isError ? 'red' : '#333';
}


// ADD TASK FROM FORM

function addTaskFromForm(e) {
    e.preventDefault();

    const title = document.getElementById('title').value.trim();
    const due_date = document.getElementById('due_date').value || null;
    const estimated_hours = parseFloat(document.getElementById('estimated_hours').value) || 1;
    const importance = parseInt(document.getElementById('importance').value) || 5;

    const deps_raw = document.getElementById('dependencies').value.trim();
    const dependencies = deps_raw ? deps_raw.split(',').map(s => s.trim()) : [];

    const id = (tasks.length + 1).toString();

    tasks.push({ id, title, due_date, estimated_hours, importance, dependencies });

    document.getElementById('task-form').reset();
    renderLocalTasks();
    setFeedback('Task added locally.');
}


// SHOW LOCAL TASKS

function renderLocalTasks() {
    const box = document.getElementById('results');
    box.innerHTML = '<h3>Local Tasks</h3>';

    tasks.forEach(t => {
        const el = document.createElement('div');
        el.className = 'task';
        el.innerHTML = `
            <strong>${t.title}</strong> (id: ${t.id})<br/>
            Due: ${t.due_date || '—'} • Est: ${t.estimated_hours}h • 
            Importance: ${t.importance} • Deps: ${t.dependencies.join(', ') || '—'}
        `;
        box.appendChild(el);
    });
}


// ANALYZE TASKS

async function analyzeTasks() {
    let bulk = document.getElementById('bulk-input').value.trim();
    let payloadTasks = tasks.slice();

    if (bulk) {
        try {
            const parsed = JSON.parse(bulk);
            if (Array.isArray(parsed)) payloadTasks = parsed;
        } catch {
            return setFeedback("Invalid JSON in bulk input", true);
        }
    }

    setFeedback("Analyzing...");
    const strategy = document.getElementById('strategy').value;

    try {
        const res = await fetch(API_BASE + "analyze/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks: payloadTasks, strategy })
        });

        const data = await res.json();
        if (!res.ok) return setFeedback("Error: " + (data.detail || "unknown"), true);

        setFeedback(data.warning ? "Circular dependencies detected." : "Analysis complete.");
        renderResults(data.result || data);

    } catch (e) {
        setFeedback("Network error: " + e.message, true);
    }
}

// DARK / LIGHT MODE TOGGLE
const darkBtn = document.getElementById("dark-mode-btn");

// Load saved mode
if (localStorage.getItem("theme") === "dark") {
    document.body.classList.add("dark");
    darkBtn.textContent = "☀️";
}

// Toggle mode
darkBtn.addEventListener("click", () => {
    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {
        darkBtn.textContent = "☀️";
        localStorage.setItem("theme", "dark");
    } else {
        darkBtn.textContent = "🌙";
        localStorage.setItem("theme", "light");
    }
});



// RENDER RESULTS

function renderResults(data) {
    const box = document.getElementById('results');
    box.innerHTML = '';

    if (data.cycles?.length) {
        const warn = document.createElement('div');
        warn.style.color = 'red';
        warn.textContent = 'Circular dependency detected: ' + JSON.stringify(data.cycles);
        box.appendChild(warn);
    }

    const header = document.createElement('h3');
    header.textContent = 'Analyzed Tasks (sorted)';
    box.appendChild(header);

    (data.tasks || []).forEach(t => {
        const el = document.createElement('div');
        el.className = 'task';

        let priorityClass = t.score >= 0.7 ? "priority-high" :
                            t.score >= 0.4 ? "priority-medium" : "priority-low";

        el.classList.add(priorityClass);

        el.innerHTML = `
            <strong>${t.title}</strong>
            <span style="float:right">Score: ${t.score}</span><br/>
            <small>${t.reason}</small><br/>
            <b>Eisenhower:</b> ${t.matrix || '—'}<br/>
            Details: Due ${t.due_date || '—'} • Est ${t.estimated_hours}h • Importance ${t.importance} • 
            Deps ${t.dependencies.join(', ') || '—'}
        `;

        box.appendChild(el);
    });
}


// TOP 3 SUGGESTIONS

async function suggestTop3() {
    let bulk = document.getElementById('bulk-input').value.trim();
    let payloadTasks = tasks.slice();

    if (bulk) {
        try {
            const parsed = JSON.parse(bulk);
            if (Array.isArray(parsed)) payloadTasks = parsed;
        } catch {
            return setFeedback("Invalid JSON in bulk input", true);
        }
    }

    setFeedback("Getting suggestions...");
    const strategy = document.getElementById('strategy').value;

    try {
        const url =
            API_BASE + "suggest/?tasks=" +
            encodeURIComponent(JSON.stringify(payloadTasks)) +
            "&strategy=" + encodeURIComponent(strategy);

        const res = await fetch(url);
        const data = await res.json();

        if (!res.ok) return setFeedback("Error: " + (data.detail || "unknown"), true);

        lastSuggestions = data.suggestions || [];  // ⬅️ NEW: store last suggestions
        setFeedback("Top suggestions ready.");

        const box = document.getElementById("results");
        box.innerHTML = "<h3>Top 3 Suggestions</h3>";

        lastSuggestions.forEach(s => {
            const el = document.createElement("div");
            el.className = "task";
            el.innerHTML = `
                <strong>${s.title}</strong>
                <span style="float:right">Score: ${s.score}</span><br/>
                <small>${s.explanation}</small>
            `;
            box.appendChild(el);
        });

    } catch (e) {
        setFeedback("Network error: " + e.message, true);
    }
}


// BONUS: FULL GRAPH RENDER

async function showGraph() {
    if (!tasks.length) return setFeedback("No tasks to graph.", true);

    try {
        const res = await fetch(API_BASE + "graph/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ tasks })
        });

        const data = await res.json();
        console.log("Graph data:", data);

        const container = document.getElementById("graph-container");
        container.innerHTML = "";

        const nodes = new vis.DataSet(data.nodes);
        const edges = new vis.DataSet(data.edges);

        new vis.Network(container, { nodes, edges }, {
            physics: true,
            edges: { arrows: "to", color: "#666" },
            nodes: { shape: "dot", size: 18 }
        });

        setFeedback("Graph generated below.");

    } catch (e) {
        setFeedback("Graph error: " + e.message, true);
    }
}


// UPDATED FEEDBACK (HELPFUL / NOT HELPFUL)

async function sendFeedback(helpful) {
    if (!lastSuggestions.length)
        return setFeedback("Run Suggestions first.", true);

    const selectedIds = lastSuggestions.map(s => s.id);

    try {
        const res = await fetch(API_BASE + "feedback/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ selected: selectedIds, helpful })
        });

        await res.json();
        setFeedback(helpful ? "Thanks! System learned." : "Feedback applied.");

    } catch (e) {
        setFeedback("Feedback error: " + e.message, true);
    }
}


// EVENT LISTENERS

document.getElementById("task-form").addEventListener("submit", addTaskFromForm);
document.getElementById("analyze-btn").addEventListener("click", analyzeTasks);
document.getElementById("suggest-btn").addEventListener("click", suggestTop3);
document.getElementById("graph-btn").addEventListener("click", showGraph);

// NEW feedback buttons
document.getElementById("feedback-yes-btn")?.addEventListener("click", () => sendFeedback(true));
document.getElementById("feedback-no-btn")?.addEventListener("click", () => sendFeedback(false));

renderLocalTasks();
