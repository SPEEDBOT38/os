import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

st.set_page_config(layout="wide", page_title="OS Scheduling Visualizer", page_icon="🖥️")

# Custom CSS for dark theme and fancy styling
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
def fcfs(process_list):
    t = 0
    gantt = []
    completed = {}
    process_list.sort(key=lambda x: x[1])  # Sort by arrival time
    for process in process_list:
        burst_time, arrival_time, pid = process
        if t < arrival_time:
            gantt.extend(["Idle"] * (arrival_time - t))
            t = arrival_time
        gantt.extend([pid] * burst_time)
        t += burst_time
        ct = t
        tt = ct - arrival_time
        wt = tt - burst_time
        completed[pid] = [ct, tt, wt]
    return gantt, completed

def sjf(process_list):
    t = 0
    gantt = []
    completed = {}
    remaining_processes = sorted(process_list, key=lambda x: x[1])  # Sort by arrival time
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p[1] <= t]
        if not available_processes:
            gantt.append("Idle")
            t += 1
        else:
            process = min(available_processes, key=lambda x: x[0])  # Select process with shortest burst time
            burst_time, arrival_time, pid = process
            gantt.extend([pid] * burst_time)
            t += burst_time
            ct = t
            tt = ct - arrival_time
            wt = tt - burst_time
            completed[pid] = [ct, tt, wt]
            remaining_processes.remove(process)
    return gantt, completed

def srtf(process_list):
    t = 0
    gantt = []
    completed = {}
    remaining_processes = sorted(process_list, key=lambda x: x[1])  # Sort by arrival time
    current_process = None
    while remaining_processes or current_process:
        if not current_process and remaining_processes and remaining_processes[0][1] > t:
            gantt.append("Idle")
            t += 1
            continue
        
        if not current_process:
            current_process = remaining_processes.pop(0)
        
        available_processes = [p for p in remaining_processes if p[1] <= t]
        if available_processes and available_processes[0][0] < current_process[0]:
            remaining_processes.append(current_process)
            current_process = available_processes[0]
            remaining_processes.remove(current_process)
        
        gantt.append(current_process[2])
        current_process[0] -= 1
        t += 1
        
        if current_process[0] == 0:
            ct = t
            tt = ct - current_process[1]
            wt = tt - (ct - t)
            completed[current_process[2]] = [ct, tt, wt]
            current_process = None
    
    return gantt, completed

def priority(process_list):
    t = 0
    gantt = []
    completed = {}
    remaining_processes = sorted(process_list, key=lambda x: x[3])  # Sort by arrival time
    while remaining_processes:
        available_processes = [p for p in remaining_processes if p[3] <= t]
        if not available_processes:
            gantt.append("Idle")
            t += 1
        else:
            process = min(available_processes, key=lambda x: x[0])  # Select process with highest priority (lowest number)
            priority, pid, burst_time, arrival_time = process
            gantt.extend([pid] * burst_time)
            t += burst_time
            ct = t
            tt = ct - arrival_time
            wt = tt - burst_time
            completed[pid] = [ct, tt, wt]
            remaining_processes.remove(process)
    return gantt, completed

def round_robin(process_list, time_quantum):
    t = 0
    gantt = []
    completed = {}
    remaining_processes = sorted(process_list, key=lambda x: x[1])  # Sort by arrival time
    queue = []
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
            wt = tt - process_list[process_list.index([process_list[i][0], process_list[i][1], pid for i in range(len(process_list)) if process_list[i][2] == pid][0])][0]
            completed[pid] = [ct, tt, wt]
        
        while remaining_processes and remaining_processes[0][1] <= t:
            queue.append(remaining_processes.pop(0))
    
    return gantt, completed

# Visualization function
def visualize_schedule(gantt, algorithm):
    fig, ax = plt.subplots(figsize=(12, 5), facecolor='#1E1E1E')
    ax.set_facecolor('#1E1E1E')
    ax.set_xlabel("Time", color='#E0E0E0')
    ax.set_ylabel("Process", color='#E0E0E0')
    ax.set_title(f"{algorithm} Scheduling", color='#4CAF50', fontweight='bold')

    unique_processes = sorted(set(gantt) - {"Idle"})
    colors = plt.cm.get_cmap('Set3')(np.linspace(0, 1, len(unique_processes)))
    color_map = dict(zip(unique_processes, colors))
    color_map["Idle"] = '#808080'

    current_process = gantt[0]
    start_time = 0
    y_positions = {process: i for i, process in enumerate(unique_processes + ["Idle"])}

    for i, process in enumerate(gantt[1:], 1):
        if process != current_process:
            ax.barh(y_positions[current_process], i - start_time, left=start_time, 
                    color=color_map[current_process], edgecolor='white', alpha=0.8)
            ax.text((start_time + i) / 2, y_positions[current_process], current_process, 
                    ha='center', va='center', fontweight='bold', color='black')
            current_process = process
            start_time = i

    ax.barh(y_positions[current_process], len(gantt) - start_time, left=start_time, 
            color=color_map[current_process], edgecolor='white', alpha=0.8)
    ax.text((start_time + len(gantt)) / 2, y_positions[current_process], current_process, 
            ha='center', va='center', fontweight='bold', color='black')

    ax.set_ylim(-0.5, len(y_positions) - 0.5)
    ax.set_xlim(0, len(gantt))
    ax.set_yticks(range(len(y_positions)))
    ax.set_yticklabels(list(y_positions.keys()))
    ax.invert_yaxis()  # Invert y-axis to show processes from top to bottom
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
    algorithm = st.selectbox("Select Algorithm", ["FCFS", "SJF", "SRTF", "Priority", "Round Robin"])
    
    if algorithm == "Round Robin":
        time_quantum = st.number_input("Time Quantum", min_value=1, value=2)
    
    num_processes = st.number_input("Number of Processes", min_value=1, max_value=10, value=3)
    
    processes = []
    for i in range(num_processes):
        with st.expander(f"Process {i+1}"):
            name = st.text_input("Name", f"P{i+1}", key=f"name_{i}")
            arrival_time = st.number_input("Arrival Time", min_value=0, value=0, key=f"arrival_{i}")
            burst_time = st.number_input("Burst Time", min_value=1, value=5, key=f"burst_{i}")
            if algorithm == "Priority":
                priority = st.number_input("Priority", min_value=1, value=1, key=f"priority_{i}")
                processes.append([priority, name, burst_time, arrival_time])
            else:
                processes.append([burst_time, arrival_time, name])

    if st.button("Visualize"):
        with col2:
            st.subheader("📊 Visualization")
            if algorithm == "FCFS":
                gantt, completed = fcfs(processes)
            elif algorithm == "SJF":
                gantt, completed = sjf(processes)
            elif algorithm == "SRTF":
                gantt, completed = srtf(processes)
            elif algorithm == "Priority":
                gantt, completed = priority(processes)
            elif algorithm == "Round Robin":
                gantt, completed = round_robin(processes, time_quantum)
            
            fig = visualize_schedule(gantt, algorithm)
            st.pyplot(fig)
            
            st.subheader("📋 Process Data")
            df = pd.DataFrame(columns=['AT', 'BT', 'CT', 'TT', 'WT'])
            for process in processes:
                pid = process[2] if algorithm != "Priority" else process[1]
                at = process[1] if algorithm != "Priority" else process[3]
                bt = process[0] if algorithm != "Priority" else process[2]
                ct, tt, wt = completed[pid]
                df.loc[pid] = [at, bt, ct, tt, wt]
            
            st.dataframe(df.style.background_gradient(cmap='viridis', axis=0))
            
            avg_turnaround = df['TT'].mean()
            avg_waiting = df['WT'].mean()
            st.markdown(f"**Average Turnaround Time:** `{avg_turnaround:.2f}`")
            st.markdown(f"**Average Waiting Time:** `{avg_waiting:.2f}`")

st.sidebar.title("ℹ️ About")
st.sidebar.info(
    "This app visualizes common OS scheduling algorithms. "
    "Select an algorithm, input process details, and click 'Visualize' to see the results."
)