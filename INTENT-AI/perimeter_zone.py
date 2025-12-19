import cv2
import numpy as np

class PerimeterZone:
    """
    Creates an invisible fence/boundary in the video
    Tracks how close people get to it
    """
    
    def __init__(self, frame_shape):
        """
        Initialize perimeter zone
        
        Args:
            frame_shape: (height, width) of video frame
        """
        self.height, self.width = frame_shape[:2]
        
        # Create zones (you can adjust these!)
        # Safe zone: far from fence (top 40% of screen)
        # Warning zone: getting close (middle 30%)
        # Danger zone: very close (bottom 30%)
        
        self.safe_line = int(self.height * 0.4)
        self.warning_line = int(self.height * 0.7)
        self.danger_line = int(self.height * 0.9)
        
        print(f"🚧 Perimeter zones created:")
        print(f"   Safe: 0 to {self.safe_line}px")
        print(f"   Warning: {self.safe_line} to {self.warning_line}px")
        print(f"   Danger: {self.warning_line} to {self.danger_line}px")
        print(f"   Intrusion: {self.danger_line}px+")
    
    def get_zone(self, position):
        """
        Check which zone a position is in
        
        Args:
            position: (x, y) coordinates
            
        Returns:
            zone name: 'SAFE', 'WARNING', 'DANGER', or 'INTRUSION'
        """
        if position is None:
            return 'UNKNOWN'
        
        x, y = position
        
        if y < self.safe_line:
            return 'SAFE'
        elif y < self.warning_line:
            return 'WARNING'
        elif y < self.danger_line:
            return 'DANGER'
        else:
            return 'INTRUSION'
    
    def get_distance_to_perimeter(self, position):
        """
        Calculate how far from the perimeter (0 to 100)
        100 = far away, 0 = at the fence
        """
        if position is None:
            return 100
        
        x, y = position
        
        # Calculate percentage distance
        distance_percent = int((1 - (y / self.height)) * 100)
        return max(0, min(100, distance_percent))
    
    def draw_zones(self, frame):
        """
        Draw the perimeter zones on the frame
        """
        overlay = frame.copy()
        
        # Draw safe zone (green)
        cv2.rectangle(overlay, (0, 0), (self.width, self.safe_line),
                     (0, 255, 0), -1)
        
        # Draw warning zone (yellow)
        cv2.rectangle(overlay, (0, self.safe_line), (self.width, self.warning_line),
                     (0, 255, 255), -1)
        
        # Draw danger zone (orange)
        cv2.rectangle(overlay, (0, self.warning_line), (self.width, self.danger_line),
                     (0, 165, 255), -1)
        
        # Draw intrusion zone (red)
        cv2.rectangle(overlay, (0, self.danger_line), (self.width, self.height),
                     (0, 0, 255), -1)
        
        # Blend with original frame (make it transparent)
        alpha = 0.2
        frame = cv2.addWeighted(frame, 1-alpha, overlay, alpha, 0)
        
        # Draw boundary lines
        cv2.line(frame, (0, self.safe_line), (self.width, self.safe_line),
                (0, 255, 0), 2)
        cv2.line(frame, (0, self.warning_line), (self.width, self.warning_line),
                (0, 255, 255), 2)
        cv2.line(frame, (0, self.danger_line), (self.width, self.danger_line),
                (0, 0, 255), 3)
        
        # Add labels
        cv2.putText(frame, "SAFE ZONE", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, "WARNING", (10, self.safe_line + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
        cv2.putText(frame, "DANGER", (10, self.warning_line + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)
        cv2.putText(frame, "INTRUSION!", (10, self.danger_line + 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return frame


# Test the perimeter zone
if __name__ == "__main__":
    print("🎬 Testing Perimeter Zone...")
    
    from person_detector import PersonDetector
    
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
    
    # Create perimeter
    perimeter = PerimeterZone(frame.shape)
    
    print("📹 Camera opened. Move around to test zones!")
    print("Press 'q' to quit")
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Detect person
        results, annotated = detector.detect(frame)
        
        # Draw zones
        annotated = perimeter.draw_zones(annotated)
        
        # Check position
        if detector.is_person_detected(results):
            center = detector.get_body_center(results, frame.shape)
            
            if center:
                zone = perimeter.get_zone(center)
                distance = perimeter.get_distance_to_perimeter(center)
                
                # Draw circle at center
                color_map = {
                    'SAFE': (0, 255, 0),
                    'WARNING': (0, 255, 255),
                    'DANGER': (0, 165, 255),
                    'INTRUSION': (0, 0, 255)
                }
                cv2.circle(annotated, center, 15, color_map[zone], -1)
                
                # Show info
                cv2.putText(annotated, f"Zone: {zone}", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                cv2.putText(annotated, f"Distance: {distance}%", (10, 90),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        
        cv2.imshow('Perimeter Zone Test - Press Q to quit', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
    detector.close()
    print("✅ Test complete!")
