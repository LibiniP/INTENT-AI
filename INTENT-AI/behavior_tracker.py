import numpy as np
from collections import deque
import time
import cv2

class BehaviorTracker:
    """
    Remembers and analyzes movement patterns
    Detects suspicious behaviors like:
    - Pacing back and forth
    - Approaching then retreating
    - Loitering in one area
    - Sudden movements
    """
    
    def __init__(self, memory_seconds=10):
        """
        Initialize behavior tracker
        
        Args:
            memory_seconds: How many seconds to remember
        """
        self.memory_seconds = memory_seconds
        self.fps = 30  # Assume 30 frames per second
        self.max_frames = memory_seconds * self.fps
        
        # Memory storage (like a diary!)
        self.position_history = deque(maxlen=self.max_frames)
        self.zone_history = deque(maxlen=self.max_frames)
        self.timestamp_history = deque(maxlen=self.max_frames)
        
        # Behavior counters
        self.loitering_time = 0
        self.direction_changes = 0
        self.advance_retreat_count = 0
        
        print(f"🧠 Behavior Tracker initialized ({memory_seconds}s memory)")
    
    def update(self, position, zone, timestamp=None):
        """
        Record new position and zone
        
        Args:
            position: (x, y) coordinates or None
            zone: 'SAFE', 'WARNING', 'DANGER', or 'INTRUSION'
            timestamp: Time of observation (auto if None)
        """
        if timestamp is None:
            timestamp = time.time()
        
        self.position_history.append(position)
        self.zone_history.append(zone)
        self.timestamp_history.append(timestamp)
    
    def analyze_pacing(self):
        """
        Detect back-and-forth movement
        Returns: Score 0-100 (100 = definitely pacing)
        """
        if len(self.position_history) < 30:
            return 0
        
        # Look at recent positions
        recent_positions = list(self.position_history)[-30:]
        
        if None in recent_positions:
            return 0
        
        # Extract x coordinates
        x_coords = [pos[0] for pos in recent_positions if pos is not None]
        
        if len(x_coords) < 10:
            return 0
        
        # Count direction changes
        direction_changes = 0
        for i in range(1, len(x_coords) - 1):
            # Check if direction reversed
            if (x_coords[i] - x_coords[i-1]) * (x_coords[i+1] - x_coords[i]) < 0:
                direction_changes += 1
        
        # More changes = more pacing
        pacing_score = min(100, direction_changes * 15)
        return pacing_score
    
    def analyze_approach_retreat(self):
        """
        Detect approaching then backing away
        Returns: Score 0-100
        """
        if len(self.zone_history) < 50:
            return 0
        
        recent_zones = list(self.zone_history)[-50:]
        
        # Look for pattern: SAFE -> WARNING/DANGER -> back to SAFE
        score = 0
        zone_values = {
            'SAFE': 0,
            'WARNING': 1,
            'DANGER': 2,
            'INTRUSION': 3,
            'UNKNOWN': -1
        }
        
        # Convert zones to numbers
        zone_nums = [zone_values.get(z, -1) for z in recent_zones]
        
        # Find peaks (advancing) followed by valleys (retreating)
        for i in range(5, len(zone_nums) - 5):
            if zone_nums[i] == -1:
                continue
            
            # Check if this is a peak
            before = zone_nums[i-5:i]
            after = zone_nums[i:i+5]
            
            if (max(before, default=-1) < zone_nums[i] and
                max(after, default=-1) < zone_nums[i] and
                zone_nums[i] >= 1):
                score += 20
        
        return min(100, score)
    
    def analyze_loitering(self):
        """
        Detect staying in one area too long
        Returns: Score 0-100
        """
        if len(self.position_history) < 30:
            return 0
        
        recent_positions = list(self.position_history)[-60:]
        
        # Remove None values
        valid_positions = [pos for pos in recent_positions if pos is not None]
        
        if len(valid_positions) < 10:
            return 0
        
        # Calculate average position
        avg_x = np.mean([pos[0] for pos in valid_positions])
        avg_y = np.mean([pos[1] for pos in valid_positions])
        
        # Calculate how much they moved from average
        distances = []
        for pos in valid_positions:
            dist = np.sqrt((pos[0] - avg_x)**2 + (pos[1] - avg_y)**2)
            distances.append(dist)
        
        avg_distance = np.mean(distances)
        
        # Low movement = loitering
        # Normalize: 0-50 pixels movement -> 100-0 score
        loitering_score = max(0, 100 - int(avg_distance * 2))
        
        return loitering_score
    
    def analyze_sudden_movement(self):
        """
        Detect quick, jerky movements
        Returns: Score 0-100
        """
        if len(self.position_history) < 10:
            return 0
        
        recent_positions = list(self.position_history)[-10:]
        
        # Remove None values
        valid_positions = [pos for pos in recent_positions if pos is not None]
        
        if len(valid_positions) < 5:
            return 0
        
        # Calculate frame-to-frame distances
        speeds = []
        for i in range(1, len(valid_positions)):
            dist = np.sqrt(
                (valid_positions[i][0] - valid_positions[i-1][0])**2 +
                (valid_positions[i][1] - valid_positions[i-1][1])**2
            )
            speeds.append(dist)
        
        if not speeds:
            return 0
        
        # Look for sudden spikes in speed
        avg_speed = np.mean(speeds)
        max_speed = max(speeds)
        
        if avg_speed < 5:  # Almost stationary
            return 0
        
        # If max is much higher than average = sudden movement
        speed_ratio = max_speed / (avg_speed + 1)
        sudden_score = min(100, int((speed_ratio - 1) * 30))
        
        return sudden_score
    
    def get_overall_suspicion_score(self):
        """
        Combine all behaviors into one INTENT RISK SCORE
        Returns: Score 0-100
        """
        pacing = self.analyze_pacing()
        approach_retreat = self.analyze_approach_retreat()
        loitering = self.analyze_loitering()
        sudden = self.analyze_sudden_movement()
        
        # Weighted combination
        suspicion = (
            pacing * 0.3 +
            approach_retreat * 0.4 +
            loitering * 0.2 +
            sudden * 0.1
        )
        
        return int(suspicion)
    
    def get_behavior_summary(self):
        """
        Get a dictionary of all behavior scores
        """
        return {
            'pacing': self.analyze_pacing(),
            'approach_retreat': self.analyze_approach_retreat(),
            'loitering': self.analyze_loitering(),
            'sudden_movement': self.analyze_sudden_movement(),
            'overall_suspicion': self.get_overall_suspicion_score()
        }
    
    def reset(self):
        """Clear all memory"""
        self.position_history.clear()
        self.zone_history.clear()
        self.timestamp_history.clear()
        print("🧹 Behavior memory cleared")


# Test the behavior tracker
if __name__ == "__main__":
    print("🎬 Testing Behavior Tracker...")
    
    from person_detector import PersonDetector
    from perimeter_zone import PerimeterZone
    
    detector = PersonDetector()
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera")
        exit()
    
    # Get frame size
    success, frame = camera.read()
    if not success:
        print("❌ Cannot read frame")
        exit()
    
    perimeter = PerimeterZone(frame.shape)
    tracker = BehaviorTracker(memory_seconds=10)
    
    print("📹 Move around to generate behavior scores!")
    print("Try: pacing, approaching and backing away, staying still")
    print("Press 'q' to quit")
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Detect person
        results, annotated = detector.detect(frame)
        annotated = perimeter.draw_zones(annotated)
        
        # Track behavior
        if detector.is_person_detected(results):
            center = detector.get_body_center(results, frame.shape)
            zone = perimeter.get_zone(center)
            
            # Update tracker
            tracker.update(center, zone)
            
            # Get behavior scores
            behaviors = tracker.get_behavior_summary()
            
            # Display scores
            y_offset = 120
            cv2.putText(annotated, f"=== BEHAVIOR ANALYSIS ===", (10, y_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            y_offset += 30
            
            for behavior, score in behaviors.items():
                color = (0, 255, 0) if score < 30 else (0, 255, 255) if score < 60 else (0, 0, 255)
                cv2.putText(annotated, f"{behavior}: {score}", (10, y_offset),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
                y_offset += 25
            
            # Big warning if suspicious
            if behaviors['overall_suspicion'] > 60:
                cv2.putText(annotated, "!!! SUSPICIOUS BEHAVIOR !!!", (10, 350),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
        
        cv2.imshow('Behavior Tracker Test - Press Q to quit', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
    detector.close()
    print("✅ Test complete!")
