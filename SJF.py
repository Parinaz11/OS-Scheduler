import threading
# from queue import PriorityQueue
from queue import Queue
import time

class Task:
    def __init__(self, name, task_type, duration):
        self.name = name
        self.task_type = task_type
        self.duration = duration
        self.resources = []
        self.state = 'Ready'
        self.exec_time = 0
        self.priority = 0

        if task_type == 'X':
            self.resources = ['R1', 'R2']
            self.priority = 3
        elif task_type == 'Y':
            self.resources = ['R2', 'R3']
            self.priority = 2
        elif task_type == 'Z':
            self.resources = ['R1', 'R3']
            self.priority = 1

mutex = threading.Lock()
waiting_q = Queue()
ready_q = Queue()
timeUnit = 1
core = 1
tasks = []
kernel_threads = []
cores_in_use = 0
print_mutex = threading.Lock()

kernel_threads_lock = threading.Lock()  # Add a lock for kernel_threads

def SJF(ready_q):
    global core
    global cores_in_use
    global timeUnit
    global tasks
    global kernel_threads_lock
    global waiting_q

    # Use a lock for thread safety
    mutex = threading.Lock()

    # Sort ready queue based on duration
    # duration_list = sorted([(task.duration, task) for task in ready_q.queue])
    duration_list = []
    while not ready_q.empty():
        task = ready_q.get()
        duration_list.append((task.duration, task))  # Use priority for sorting

    duration_list.sort() 

    while len(duration_list) > 0:
        mutex.acquire()
        if cores_in_use < 4 and duration_list:  # Check available cores and tasks
            cores_in_use += 1
            current_task = duration_list.pop(0)[1]  # Pop the task with the shortest duration
            mutex.release()

            kernel_thread = threading.Thread(target=execute_task, args=(core, current_task))
            kernel_thread.start()  # Start the new thread
            core += 1

            if core == 5:
                timeUnit += 1
                core = 1
        else:
            mutex.release()
            # If resources are not available, add the task to the waiting queue
            waiting_q.put(duration_list.pop(0)[1])
            #  SJF(waiting_q)
            break

# def SJF(ready_q):
#     global core
#     global cores_in_use
#     global timeUnit
#     global tasks
#     global kernel_threads_lock

#     # Use a lock for thread safety
#     mutex = threading.Lock()

#     # Sort ready queue based on duration
#     duration_list = sorted([(task.duration, task) for task in ready_q.queue])

#     while len(duration_list) > 0:
#         mutex.acquire()
#         if cores_in_use < 4 and duration_list:  # Check available cores and tasks
#             cores_in_use += 1
#             current_task = duration_list.pop(0)[1]  # Pop the task with the shortest duration
#             mutex.release()

#             kernel_thread = threading.Thread(target=execute_task, args=(core, current_task))
#             kernel_thread.start()  # Start the new thread
#             core += 1

#             if core == 5:
#                 timeUnit += 1
#                 core = 1
#         else:
#             mutex.release()
#             break


def execute_task(core, task):
    global timeUnit
    global mutex
    global print_mutex

    print(f"Core {core}: Executing {task.name} with Duration: {task.duration} in time: {timeUnit}")

    time.sleep(task.duration)

    task.state = 'Completed'
    task.exec_time = task.duration
    print(f"Core {core}: {task.name} completed in time: {timeUnit+task.exec_time}")

    with mutex:
        print(f"Core {core}: Releasing resources {task.resources}")

        global cores_in_use
        cores_in_use -= 1

        with print_mutex:
            print_execution_result(core, task)

def print_execution_result(core, task):
    print(f"Core {core}: {task.name} completed in time: {timeUnit+task.exec_time}")

def print_results():
    global kernel_threads
    for thread in kernel_threads:
        thread.join()

    print("\nExecution Results:")
    for task in tasks:
        print(f"{task.name}: State: {task.state}, Execution Time: {task.exec_time}")

def main():
    global core
    global tasks
    num_resources = list(map(int, input("Enter the data for resources and tasks:\n").split()))
    num_tasks = int(input())
    # tasks = []

    for _ in range(num_tasks):
        task_data = input().split()
        task_name, task_type, duration = task_data[0], task_data[1], int(task_data[2])
        t = Task(task_name, task_type, duration)
        tasks.append(t)

    print(f"Resources: {num_resources}")
    print(f"Number of tasks: {num_tasks}")
    print("Task details:")
    count = 1

    for task in tasks: 
        ready_q.put(task)

    for task in tasks:
        print(f"{count}) Duration: {task.duration}, Type: {task.task_type}, Name: {task.name}, State: {task.state}, Time On CPU: {task.exec_time}")
        count += 1

    # Start the printing thread
    print_thread = threading.Thread(target=print_results)
    print_thread.start()

    # Start the SJF scheduling
    SJF(ready_q)

    # Wait for the printing thread to finish
    print_thread.join()

if __name__ == "__main__":
    print("---- SJF ---")
    main()
