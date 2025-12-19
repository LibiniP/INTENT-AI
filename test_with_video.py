#!/usr/bin/env python3
"""
Test INTENT-AI with a video file instead of live camera
"""

import cv2
import sys

# Copy the entire IntentAI class but modify the __init__ method
from intent_ai_main import IntentAI

class IntentAI_Video(IntentAI):
    """Modified INTENT-AI to work with video files"""
    
    def __init__(self, video_path):
        print("="*60)
        print("🚀 INITIALIZING INTENT-AI SYSTEM (VIDEO MODE)")
        print("="*60)
        
        # Initialize camera with video file
        print(f"\n📹 Opening video: {video_path}")
        self.camera = cv2.VideoCapture(video_path)
        
        if not self.camera.isOpened():
            raise Exception(f"❌ Cannot open video file: {video_path}")
        
        # Get frame size
        success, frame = self.camera.read()
        if not success:
            raise Exception("❌ Cannot read from video file!")
        
        # Reset video to start
        self.camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
        
        print(f"✅ Video opened: {frame.shape[1]}x{frame.shape[0]}")
        
        # Initialize all subsystems (same as parent)
        print("\n🔧 Initializing subsystems...")
        from person_detector import PersonDetector
        from perimeter_zone import PerimeterZone
        from behavior_tracker import BehaviorTracker
        from camera_trust import CameraTrustSystem
        
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
        print("✅ INTENT-AI SYSTEM READY (VIDEO MODE)")
        print("="*60)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_with_video.py <video_file_path>")
        print("\nExample:")
        print("  python test_with_video.py videos/test_video.mp4")
        print("\nYou can download test videos from:")
        print("  - Record your own with phone/webcam")
        print("  - Use any surveillance footage")
        print("  - Get sample videos from pexels.com (free)")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    try:
        system = IntentAI_Video(video_path)
        system.run()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
