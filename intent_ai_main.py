#!/usr/bin/env python3
"""
INTENT-AI: Trust-Aware AI System for Predictive Border & Perimeter Threat Detection

Main System Integration
"""

import cv2
import time
import numpy as np
from datetime import datetime

from person_detector import PersonDetector
from perimeter_zone import PerimeterZone
from behavior_tracker import BehaviorTracker
from camera_trust import CameraTrustSystem

import pygame
pygame.mixer.init()

class IntentAI:
    """
    Main INTENT-AI System
    
    Combines:
    - Person detection
    - Perimeter monitoring
    - Behavior analysis
    - Camera trust verification
    """
    
    def __init__(self):
        print("="*60)
        print("🚀 INITIALIZING INTENT-AI SYSTEM")
        print("="*60)
        
        # Initialize alert sound
        try:
            self.alert_sound = pygame.mixer.Sound('alert.wav')
        except:
            print("⚠️ Warning: alert.wav not found, alerts will be silent")
            self.alert_sound = None
        
        # Initialize recording
        self.recording = False
        self.video_writer = None
        
        # Initialize camera
        print("\n📹 Opening camera...")
        self.camera = cv2.VideoCapture(0)
        
        if not self.camera.isOpened():
            raise Exception("❌ Cannot open camera!")
        
        # Get frame size
        success, frame = self.camera.read()
        if not success:
            raise Exception("❌ Cannot read from camera!")
        
        print(f"✅ Camera opened: {frame.shape[1]}x{frame.shape[0]}")
        
        # Initialize all subsystems
        print("\n🔧 Initializing subsystems...")
        self.detector = PersonDetector()
        self.perimeter = PerimeterZone(frame.shape)
        self.tracker = BehaviorTracker(memory_seconds=10)
        self.trust_system = CameraTrustSystem()
        
        # System state
        self.running = False
        self.alert_active = False
        self.alert_start_time = None
        
        # Statistics
        self.frame_count = 0
        self.detection_count = 0
        self.alert_count = 0
        
        print("\n" + "="*60)
        print("✅ INTENT-AI SYSTEM READY")
        print("="*60)
    
    def calculate_intent_risk_score(self, behavior_scores, zone, camera_trust):
        """
        Calculate final INTENT RISK SCORE (0-100)
        
        This is the core innovation: combining behavioral analysis
        with camera trust verification
        """
        # Base risk from behavior
        behavior_risk = behavior_scores['overall_suspicion']
        
        # Zone multiplier (closer to perimeter = higher risk)
        zone_multipliers = {
            'SAFE': 0.5,
            'WARNING': 1.0,
            'DANGER': 1.5,
            'INTRUSION': 2.0,
            'UNKNOWN': 0.0
        }
        zone_mult = zone_multipliers.get(zone, 0)
        
        # Calculate base intent risk
        intent_risk = behavior_risk * zone_mult
        
        # CRITICAL: Adjust by camera trust
        # Low trust = we can't be confident in the risk assessment
        trust_factor = camera_trust['overall_trust'] / 100.0
        
        # If camera trust is low, we should be suspicious even if behavior seems normal
        if trust_factor < 0.7:
            # Low trust = increase baseline risk
            intent_risk = max(intent_risk, 50)
        
        # Cap at 100
        intent_risk = min(100, intent_risk)
        
        return int(intent_risk)
    
    def get_risk_level(self, intent_risk):
        """
        Convert intent risk score to risk level
        """
        if intent_risk < 30:
            return 'LOW', (0, 255, 0)
        elif intent_risk < 60:
            return 'MEDIUM', (0, 255, 255)
        elif intent_risk < 80:
            return 'HIGH', (0, 165, 255)
        else:
            return 'CRITICAL', (0, 0, 255)
    
    def draw_dashboard(self, frame, person_detected, center, zone, 
                      behavior_scores, camera_trust, intent_risk):
        """
        Draw the complete INTENT-AI dashboard overlay
        """
        display = frame.copy()
        
        # Draw perimeter zones
        display = self.perimeter.draw_zones(display)
        
        # Draw person skeleton if detected
        if person_detected:
            results, annotated = self.detector.detect(frame)
            display = annotated
            
            # Draw center point
            if center:
                cv2.circle(display, center, 12, (255, 0, 255), -1)
                cv2.circle(display, center, 15, (255, 255, 255), 2)
        
        # === HEADER ===
        cv2.rectangle(display, (0, 0), (display.shape[1], 60), (0, 0, 0), -1)
        cv2.putText(display, "INTENT-AI: PERIMETER SURVEILLANCE", (10, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255), 2)
        cv2.putText(display, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                   (display.shape[1] - 250, 35),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        
        # === MAIN INTENT RISK SCORE ===
        risk_level, risk_color = self.get_risk_level(intent_risk)
        
        # Big box for intent risk
        box_y = 80
        box_h = 120
        cv2.rectangle(display, (10, box_y), (400, box_y + box_h), risk_color, 3)
        cv2.rectangle(display, (10, box_y), (400, box_y + box_h), (0, 0, 0), -1)
        cv2.rectangle(display, (10, box_y), (400, box_y + box_h), risk_color, 3)
        
        cv2.putText(display, "INTENT RISK SCORE", (20, box_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        cv2.putText(display, f"{intent_risk}", (120, box_y + 80),
                   cv2.FONT_HERSHEY_SIMPLEX, 2.0, risk_color, 4)
        
        cv2.putText(display, f"Risk Level: {risk_level}", (20, box_y + 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, risk_color, 2)
        
        # === BEHAVIOR ANALYSIS ===
        behavior_y = box_y + box_h + 20
        cv2.putText(display, "BEHAVIOR ANALYSIS", (10, behavior_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        behaviors = [
            ('Pacing', behavior_scores['pacing']),
            ('Approach/Retreat', behavior_scores['approach_retreat']),
            ('Loitering', behavior_scores['loitering']),
            ('Sudden Movement', behavior_scores['sudden_movement'])
        ]
        
        for i, (name, score) in enumerate(behaviors):
            y = behavior_y + 30 + (i * 25)
            color = (0, 255, 0) if score < 40 else (0, 255, 255) if score < 70 else (0, 0, 255)
            cv2.putText(display, f"{name}: {score}", (10, y),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # === CAMERA TRUST ===
        trust_y = behavior_y + 150
        cv2.putText(display, "CAMERA TRUST", (10, trust_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        trust_color = (0, 255, 0) if camera_trust['overall_trust'] >= 70 else (0, 0, 255)
        cv2.putText(display, f"Overall: {camera_trust['overall_trust']}/100", (10, trust_y + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, trust_color, 2)
        
        cv2.putText(display, f"Liveness: {camera_trust['liveness']} | "
                            f"Entropy: {camera_trust['entropy']} | "
                            f"Motion: {camera_trust['motion']}", 
                   (10, trust_y + 55),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        # === STATUS INFO ===
        status_y = trust_y + 85
        cv2.putText(display, f"Zone: {zone}", (10, status_y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(display, f"Person: {'DETECTED' if person_detected else 'NONE'}", 
                   (10, status_y + 25),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # === CRITICAL ALERT ===
        if intent_risk >= 75 or camera_trust['overall_trust'] < 60:
            # Flashing alert
            if int(time.time() * 2) % 2 == 0:
                cv2.rectangle(display, (0, 0), (display.shape[1], display.shape[0]), 
                             (0, 0, 255), 10)
                
                alert_text = "!!! ALERT: HIGH THREAT DETECTED !!!"
                if camera_trust['overall_trust'] < 60:
                    alert_text = "!!! ALERT: CAMERA FEED SUSPICIOUS !!!"
                
                cv2.putText(display, alert_text, 
                           (int(display.shape[1]/2) - 300, display.shape[0] - 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3)
        
        return display
    
    def run(self):
        """
        Main system loop
        """
        self.running = True
        print("\n🎬 INTENT-AI SYSTEM ACTIVE")
        print("Press 'q' to quit, 'r' to reset tracking\n")
        
        try:
            while self.running:
                success, frame = self.camera.read()
                if not success:
                    print("❌ Failed to read frame")
                    break
                
                self.frame_count += 1
                
                # === STEP 1: Verify Camera Trust ===
                camera_trust = self.trust_system.layer4_calculate_trust_score(frame)
                
                # === STEP 2: Detect Person ===
                results, _ = self.detector.detect(frame)
                person_detected = self.detector.is_person_detected(results)
                
                # === STEP 3: Track Position & Behavior ===
                center = None
                zone = 'UNKNOWN'
                behavior_scores = {
                    'pacing': 0,
                    'approach_retreat': 0,
                    'loitering': 0,
                    'sudden_movement': 0,
                    'overall_suspicion': 0
                }
                
                if person_detected:
                    self.detection_count += 1
                    center = self.detector.get_body_center(results, frame.shape)
                    
                    if center:
                        zone = self.perimeter.get_zone(center)
                        self.tracker.update(center, zone)
                        behavior_scores = self.tracker.get_behavior_summary()
                
                # === STEP 4: Calculate Intent Risk ===
                intent_risk = self.calculate_intent_risk_score(
                    behavior_scores, zone, camera_trust
                )
                
                # === STEP 5: Handle Alerts and Recording ===
                if intent_risk >= 75:
                    # Play alert sound
                    if self.alert_sound:
                        self.alert_sound.play()
                    
                    # Write to log
                    with open('logs/alerts.log', 'a') as f:
                        f.write(f"{datetime.now()}: Alert #{self.alert_count}, Risk: {intent_risk}\n")
                    
                    # Start recording if not already recording
                    if not self.recording:
                        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
                        self.video_writer = cv2.VideoWriter('logs/alert_video.mp4', fourcc, 20.0, (640, 480))
                        self.recording = True
                
                # Write frame if recording
                if self.recording and self.video_writer:
                    self.video_writer.write(frame)
                
                # === STEP 6: Draw Dashboard ===
                display = self.draw_dashboard(
                    frame, person_detected, center, zone,
                    behavior_scores, camera_trust, intent_risk
                )
                
                # === STEP 7: Show Display ===
                cv2.imshow('INTENT-AI System - Press Q to quit, R to reset', display)
                
                # === STEP 8: Handle Input ===
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('r'):
                    print("🔄 Resetting tracking...")
                    self.tracker.reset()
                    self.trust_system.reset()
                
                # Log alerts
                if intent_risk >= 75 and not self.alert_active:
                    self.alert_active = True
                    self.alert_count += 1
                    self.alert_start_time = time.time()
                    print(f"🚨 ALERT #{self.alert_count}: High intent risk detected!")
                elif intent_risk < 60 and self.alert_active:
                    self.alert_active = False
                    duration = time.time() - self.alert_start_time
                    print(f"✅ Alert cleared (duration: {duration:.1f}s)")
                    # Stop recording
                    if self.recording and self.video_writer:
                        self.video_writer.release()
                        self.recording = False
        
        except KeyboardInterrupt:
            print("\n⚠️ Interrupted by user")
        
        finally:
            self.shutdown()
    
    def shutdown(self):
        """
        Clean shutdown
        """
        print("\n" + "="*60)
        print("🛑 SHUTTING DOWN INTENT-AI SYSTEM")
        print("="*60)
        
        print(f"\n📊 Session Statistics:")
        print(f"   Total Frames: {self.frame_count}")
        print(f"   Detections: {self.detection_count}")
        print(f"   Alerts: {self.alert_count}")
        
        # Release video writer if still recording
        if self.recording and self.video_writer:
            self.video_writer.release()
        
        self.camera.release()
        cv2.destroyAllWindows()
        self.detector.close()
        
        print("\n✅ Shutdown complete")
        print("="*60 + "\n")


# === MAIN ENTRY POINT ===
if __name__ == "__main__":
    print("\n" + "="*60)
    print("  _____ _   _ _____ _____ _   _ _____       _    ___ ")
    print(" |_   _| \\ | |_   _| ____| \\ | |_   _|     / \\  |_ _|")
    print("   | | |  \\| | | | |  _| |  \\| | | | _____ / _ \\  | | ")
    print("   | | | |\\  | | | | |___| |\\  | | ||_____/ ___ \\ | | ")
    print("   |_| |_| \\_| |_| |_____|_| \\_| |_|     /_/   \\_\\___|")
    print("")
    print("  Trust-Aware AI System for Predictive Border Detection")
    print("="*60 + "\n")
    
    try:
        system = IntentAI()
        system.run()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("Make sure all required modules are present:")
        print("  - person_detector.py")
        print("  - perimeter_zone.py")
        print("  - behavior_tracker.py")
        print("  - camera_trust.py")
