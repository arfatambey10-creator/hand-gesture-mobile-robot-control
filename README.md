# hand-gesture-mobile-robot-control
Real-time hand-gesture controlled mobile robot using Python ML, OpenCV, MediaPipe, and MATLAB/Simulink over TCP/IP.
# Real-Time Hand Gesture Controlled Mobile Robot

This project implements a real-time machine learning and computer vision pipeline to control a mobile robot using hand gestures.  
It uses **Python, OpenCV, MediaPipe, NumPy, Scikit-Learn, joblib**, and a **MATLAB/Simulink TCP server** for robot control.

---

## Project Structure

### 1. python-gesture-ml
Real-time Python ML pipeline:
Opens webcam using OpenCV  
 Extracts hand landmarks using MediaPipe  
 Computes feature vectors using NumPy  
 Loads trained gesture model (`model.pkl`)  
 Classifies Open/Closed hand  
 Sends commands to MATLAB via TCP/IP (port 55001)

### 2. matlab-tcp-server
MATLAB script that:
 Creates TCP/IP server  
 Receives gesture commands  
 Passes them to Simulink robot model

### 3. matlab-robot-model
Simulink model of a differential-drive mobile robot that:
 Receives commands from the TCP server  
 Executes robot motion in 3D environment  

---

How It Works

Python ML System → sends gesture commands → MATLAB TCP Server → controls robot in Simulink.

---
Technologies Used

 Python (OpenCV, MediaPipe, NumPy, Scikit-Learn)
 joblib for model deployment
 MATLAB/Simulink
 TCP/IP socket communication
 Real-time computer vision
 Robot kinematics and simulation

---

Author

ARFA Tambey  
MSc Electrical and Electronics Engineering  
Coventry University  
