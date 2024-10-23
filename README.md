# 🚀 Load Balancer Project


Welcome to the **Load Balancer** project! This project is a multi-process TCP load balancer implemented in Python, supporting various algorithms such as **Round Robin**, **Random**, and **Weighted Round Robin**. It's designed to efficiently balance requests between multiple workers and can be configured through a simple configuration file.

### 🎨 Key Features

- ⚡ **Multi-process**: Optimized using Python’s `multiprocessing` for handling multiple requests.
- 🎯 **Algorithm Support**: Choose from **Round Robin**, **Random**, or **Weighted Round Robin**.
- 📂 **Configurable**: Modify the behavior easily through an external configuration file.
- 🛠️ **Worker Management**: Dynamically manage workers based on their performance.
- 💾 **Efficient**: Uses buffered I/O for optimized socket communication.

---

## 📜 Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Load Balancing Algorithms](#load-balancing-algorithms)

---

## 🔧 Installation

First, clone this repository:

```bash
git clone https://github.com/yourusername/load-balancer.git
cd load-balancer
```

## 🔧 Usage

1) Setup example.cfg file as per your needs
select sutaible algorithm and ports

```bash
python main.py example.cfg
```
2) now open new terminals and initiate servers

```bash
python -m http.server 8080
python -m http.server 8081
python -m http.server 8082
python -m http.server 8083
python -m http.server 8084
```

add each command in new terminal

3) Open postman and send GET request to routes to test the code
e.g http://localhost:24003/main.py


## 📊 Load Balancing Algorithms

- The load balancer supports three algorithms:
   1) Round Robin: Distributes requests evenly among workers in sequence.
   2) Random: Assigns each incoming request to a random worker.
   3) Weighted Round Robin: Distributes requests based on worker weights, favoring more capable servers.


