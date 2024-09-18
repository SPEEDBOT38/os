import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="OS Scheduling Visualizer", page_icon="🖥️")

# Custom CSS for dark theme and fancier styling
st.markdown("""
<style>
    .stApp {
        background-color: #1E1E1E;
        color: #E0E0E0;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px;
        font-weight: bold;
        border-radius: 5px;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .stExpander {
        background-color: #2D2D2D;
        border-radius: 5px;
        border: 1px solid #3D3D3D;
    }
    .stSelectbox [data-baseweb="select"] {
        background-color: #2D2D2D;
    }
    .stDataFrame {
        background-color: #2D2D2D;
    }
    h1, h2, h3 {
        color: #4CAF50;
    }
    .stSidebar {
        background-color: #252525;
    }
    .stSidebar [data-testid="stMarkdownContainer"] {
        color: #B0B0B0;
    }
</style>
""", unsafe_allow_html=True)

# Scheduling algorithms
def fcfs(processes):
    current_time = 0
    for p in processes:
        p["start_time"] = max(current_time, p["arrival_time"])
        p["end_time"] = p["start_time"] + p["burst_time"]
        current_time = p["end_time"]
    return processes

def sjf(processes):
    processes.sort(key=lambda x: (x["burst_time"], x["arrival_time"]))
    return fcfs(processes)

def priority_scheduling(processes):
    processes.sort(key=lambda x: (-x["priority"], x["arrival_time"]))
    return fcfs(processes)

def round_robin(processes, time_quantum):
    t = 0
    gantt = []
    completed = {}
    remaining_processes = sorted(processes.copy(), key=lambda x: x[1])  # Sort by arrival time
    queue = []
    original_burst_times = {p[2]: p[0] for p in processes}  # Store original burst times
    
    while remaining_processes or queue:
        while remaining_processes and remaining_processes[0][1] <= t:
            queue.append(remaining_processes.pop(0))
        
        if not queue:
            gantt.append("Idle")
            t += 1
            continue
        
        current_process = queue.pop(0)
        burst_time, arrival_time, pid = current_process
        execution_time = min(time_quantum, burst_time)
        gantt.extend([pid] * execution_time)
        t += execution_time
        burst_time -= execution_time
        
        if burst_time > 0:
            queue.append([burst_time, arrival_time, pid])
        else:
            ct = t
            tt = ct - arrival_time
            wt = tt - original_burst_times[pid]
            completed[pid] = [ct, tt, wt]
        
        while remaining_processes and remaining_processes[0][1] <= t:
            queue.append(remaining_processes.pop(0))
    
    return gantt, completed

# Visualization function
def visualize_schedule(processes, algorithm, time_quantum=None):
    fig, ax = plt.subplots(figsize=(12, 5), facecolor='#1E1E1E')
    ax.set_facecolor('#1E1E1E')
    ax.set_xlabel("Time", color='#E0E0E0')
    ax.set_ylabel("Process", color='#E0E0E0')
    ax.set_title(f"{algorithm} Scheduling", color='#4CAF50', fontweight='bold')

    colors = plt.cm.get_cmap('Set3')(np.linspace(0, 1, len(processes)))
    
    for i, p in enumerate(processes):
        ax.barh(p["name"], p["burst_time"], left=p["start_time"], color=colors[i], edgecolor='white', alpha=0.8)
        ax.text(p["start_time"], p["name"], f"{p['start_time']}", va='center', ha='right', fontweight='bold', color='white')
        ax.text(p["end_time"], p["name"], f"{p['end_time']}", va='center', ha='left', fontweight='bold', color='white')

    ax.set_ylim(-0.5, len(processes) - 0.5)
    ax.invert_yaxis()
    ax.set_axisbelow(True)
    ax.grid(axis='x', linestyle='--', alpha=0.3, color='#808080')
    ax.tick_params(colors='#E0E0E0')

    for spine in ax.spines.values():
        spine.set_edgecolor('#808080')

    plt.tight_layout()
    return fig

# Streamlit app
st.title("🖥️ OS Scheduling Algorithm Visualizer")

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("⚙️ Configuration")
    algorithm = st.selectbox("Select Algorithm", ["FCFS", "SJF", "Priority", "Round Robin"])
    
    if algorithm == "Round Robin":
        time_quantum = st.number_input("Time Quantum", min_value=1, value=2)
    
    num_processes = st.number_input("Number of Processes", min_value=1, max_value=10, value=3)
    
    processes = []
    for i in range(num_processes):
        with st.expander(f"Process {i+1}"):
            name = st.text_input("Name", f"P{i+1}", key=f"name_{i}")
            arrival_time = st.number_input("Arrival Time", min_value=0, value=0, key=f"arrival_{i}")
            burst_time = st.number_input("Burst Time", min_value=1, value=5, key=f"burst_{i}")
            priority = st.number_input("Priority", min_value=1, value=1, key=f"priority_{i}")
            processes.append({
                "name": name,
                "arrival_time": arrival_time,
                "burst_time": burst_time,
                "priority": priority,
                "remaining_time": burst_time
            })

    if st.button("Visualize"):
        with col2:
            st.subheader("📊 Visualization")
            if algorithm == "FCFS":
                scheduled_processes = fcfs(processes)
            elif algorithm == "SJF":
                scheduled_processes = sjf(processes)
            elif algorithm == "Priority":
                scheduled_processes = priority_scheduling(processes)
            elif algorithm == "Round Robin":
                scheduled_processes = round_robin(processes, time_quantum)
            
            fig = visualize_schedule(scheduled_processes, algorithm, time_quantum if algorithm == "Round Robin" else None)
            st.pyplot(fig)
            
            st.subheader("📋 Process Data")
            df = pd.DataFrame(scheduled_processes)
            if algorithm != "Round Robin":
                df["Turnaround Time"] = df["end_time"] - df["arrival_time"]
                df["Waiting Time"] = df["Turnaround Time"] - df["burst_time"]
            st.dataframe(df.style.background_gradient(cmap='viridis', axis=0))
            
            if algorithm != "Round Robin":
                avg_turnaround = df["Turnaround Time"].mean()
                avg_waiting = df["Waiting Time"].mean()
                st.markdown(f"**Average Turnaround Time:** `{avg_turnaround:.2f}`")
                st.markdown(f"**Average Waiting Time:** `{avg_waiting:.2f}`")

st.sidebar.title("ℹ️ About")
st.sidebar.info(
    "This app visualizes common OS scheduling algorithms. "
    "Select an algorithm, input process details, and click 'Visualize' to see the results."
)