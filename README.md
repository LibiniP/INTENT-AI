# INTENT-AI: Trust-Aware Perimeter Surveillance System

## Trust-Aware AI System for Predictive Border & Perimeter Threat Detection

---

## Overview

**INTENT-AI** is an AI-powered surveillance system designed to predict hostile or suspicious intent **before physical intrusion occurs**, while simultaneously verifying the integrity and trustworthiness of the camera feed itself.

Unlike traditional perimeter systems that rely on simple motion detection or boundary crossing, INTENT-AI evaluates **behavioral intent**, **proximity risk**, and **sensor trust** to produce a continuous, explainable **Intent Risk Score (0–100)**.

---

## Key Innovations

* **Pre-Intrusion Detection**
  Detects suspicious intent before a subject crosses a perimeter.

* **Behavioral Analysis**
  Identifies pacing, approach–retreat behavior, loitering, and sudden movements.

* **Trust-Aware Perception**
  Four-layer defense system to detect camera tampering, feed freezing, or replay attacks.

* **Risk-Based Alerts**
  Generates graded alerts using an Intent Risk Score instead of binary alarms.

---

## Project Structure

```text
INTENT-AI/
├── intent_ai_main.py         # Main system entry point
├── person_detector.py        # Human detection module
├── perimeter_zone.py         # Virtual perimeter & zone logic
├── behavior_tracker.py       # Behavioral pattern analysis
├── camera_trust.py           # Camera trust & anti-tampering system
├── test_camera.py            # Camera test utility
├── test_with_video.py        # Run system on video files
├── requirements.txt          # Python dependencies
├── videos/                   # Test video samples
├── models/                   # AI models
└── logs/                     # System logs
```

---

## Installation & Requirements

### System Requirements

* Python **3.10+**
* Webcam **or** video file input
* Minimum **4 GB RAM**

### Step 1: Install Python

* **Windows**: [https://www.python.org](https://www.python.org)
* **macOS**: `brew install python3`
* **Linux**: `sudo apt install python3 python3-pip`

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Test Camera

```bash
python test_camera.py
```

---

## Running the System

### Live Camera Mode

```bash
python intent_ai_main.py
```

### Video File Mode

```bash
python test_with_video.py videos/test_video.mp4
```

### Controls

* **Q** — Quit system
* **R** — Reset tracking memory

---

## Component Testing

Test individual modules independently:

```bash
# Person detection
python person_detector.py

# Perimeter zones
python perimeter_zone.py

# Behavior tracking
python behavior_tracker.py

# Camera trust system
python camera_trust.py
```

---

## System Architecture

### 1. Person Detection

* Uses **MediaPipe Pose** for human detection
* Tracks the body center point
* Operates in real time

---

### 2. Perimeter Zones

Four virtual zones define proximity risk:

* **SAFE** – Far from perimeter (Green)
* **WARNING** – Approaching perimeter (Yellow)
* **DANGER** – Very close to boundary (Orange)
* **INTRUSION** – Boundary crossed (Red)

---

### 3. Behavior Analysis

Detects suspicious motion patterns including:

* **Pacing** — Repeated back-and-forth movement
* **Approach–Retreat** — Closing distance then backing away
* **Loitering** — Remaining in one area for extended time
* **Sudden Movement** — Abrupt or jerky motion patterns

---

### 4. Camera Trust System

A four-layer defense ensures feed integrity:

**Layer 1: Liveness Detection**
Detects frozen or looped video via frame repetition checks.

**Layer 2: Entropy Analysis**
Measures visual complexity to detect static or fake frames.

**Layer 3: Motion Verification**
Analyzes motion realism to identify unnatural movement.

**Layer 4: Trust Score Engine**
Combines all layers into a **Trust Score (0–100)**.

* Trust < **70** triggers a **SUSPICIOUS FEED** alert

---

## Intent Risk Scoring

```
Intent Risk = Behavior Risk × Zone Multiplier × Trust Factor
```

### Risk Levels

| Score Range | Level    | Color  |
| ----------- | -------- | ------ |
| 0–29        | LOW      | Green  |
| 30–59       | MEDIUM   | Yellow |
| 60–79       | HIGH     | Orange |
| 80–100      | CRITICAL | Red    |

---

## Demo Scenarios

### Scenario 1: Normal Patrol

* Subject walks through SAFE zone
* No suspicious behavior detected
* **Intent Risk:** LOW (10–20)

---

### Scenario 2: Suspicious Behavior

* Subject paces near perimeter
* Repeated approach–retreat patterns
* **Intent Risk:** MEDIUM → HIGH (40–70)
* Alert triggered **before intrusion**

---

### Scenario 3: Camera Tampering

* Camera feed freezes or lens is obstructed
* Trust score drops rapidly
* **SUSPICIOUS FEED** alert triggered
* Human verification required

---

## Disclaimer

INTENT-AI is a **research and prototype system** intended for defensive security, experimentation, and educational purposes. It should be validated and adapted before deployment in real-world safety-critical environments.
