# INTENT-AI: Trust-Aware Perimeter Surveillance System  
## Trust-Aware AI System for Predictive Border & Perimeter Threat Detection

---

## What is INTENT-AI?

INTENT-AI is an AI-powered surveillance system that predicts hostile intent **BEFORE intrusion occurs**, while continuously verifying that its camera feed is not compromised.

---

## Key Innovations

- **Pre-Intrusion Detection** – Predicts suspicious behavior before boundary crossing  
- **Behavioral Analysis** – Detects pacing, approach-retreat, loitering, sudden movements  
- **Trust-Aware Perception** – 4-layer defense against camera hacking and feed manipulation  
- **Risk-Based Alerts** – Provides Intent Risk Score (0–100) instead of binary alarms  

---

## Project Structure

```text
INTENT-AI/
├── intent_ai_main.py         # Main system (run this!)
├── person_detector.py        # Human detection module
├── perimeter_zone.py         # Virtual fence zones
├── behavior_tracker.py       # Behavioral pattern analysis
├── camera_trust.py           # Anti-hacking trust system
├── test_camera.py            # Camera test utility
├── test_with_video.py        # Test with video files
├── requirements.txt          # Python dependencies
├── videos/                   # Test videos folder
├── models/                   # AI models folder
└── logs/                     # System logs folder
Installation & Requirements
System Requirements
Python 3.10 or higher

Webcam or video file

Minimum 4GB RAM

Step 1: Install Python
Windows: Download from https://www.python.org

Mac:

bash
Copy code
brew install python3
Linux:

bash
Copy code
sudo apt install python3 python3-pip
Step 2: Install Dependencies
bash
Copy code
pip install -r requirements.txt
Step 3: Test Camera
bash
Copy code
python test_camera.py
Quick Start
Run with Live Camera
bash
Copy code
python intent_ai_main.py
Run with Video File
bash
Copy code
python test_with_video.py videos/test_video.mp4
Controls
Q – Quit system

R – Reset tracking memory

Testing Each Component
bash
Copy code
# Test person detection
python person_detector.py

# Test perimeter zones
python perimeter_zone.py

# Test behavior tracking
python behavior_tracker.py

# Test camera trust system
python camera_trust.py
How It Works
1. Person Detection
Uses MediaPipe Pose to detect humans

Tracks body center point

Works in real-time

2. Perimeter Zones
Creates four virtual zones:

SAFE – Far from perimeter (green)

WARNING – Getting close (yellow)

DANGER – Very close (orange)

INTRUSION – Crossed boundary (red)

3. Behavior Analysis
Detects suspicious patterns:

Pacing – Back-and-forth movement

Approach–Retreat – Coming close then backing away

Loitering – Staying in one area too long

Sudden Movement – Quick, jerky actions

4. Camera Trust System
4-Layer Defense
Layer 1: Liveness Detection

Detects frozen or looped video

Checks for frame repetition

Layer 2: Entropy Analysis

Measures frame complexity

Detects static or fake frames

Layer 3: Motion Verification

Analyzes realistic movement patterns

Detects unnatural motion

Layer 4: Trust Score Engine

Combines all layers

Outputs trust score (0–100)

Triggers alert if trust < 70

5. Intent Risk Score
text
Copy code
Intent Risk = Behavior Risk × Zone Multiplier × Trust Factor
Risk Levels
0–29: LOW (green)

30–59: MEDIUM (yellow)

60–79: HIGH (orange)

80–100: CRITICAL (red)

Demo Scenarios
Scenario 1: Normal Patrol
Person walks through SAFE zone

No suspicious behavior detected

Intent Risk: LOW (10–20)

Scenario 2: Suspicious Behavior
Person paces near perimeter

Approaches then retreats multiple times

Intent Risk: MEDIUM → HIGH (40–70)

System alerts BEFORE intrusion

Scenario 3: Camera Tampering
Camera lens covered or feed frozen

Camera trust drops immediately

System triggers "SUSPICIOUS FEED" alert

Requires human verification

