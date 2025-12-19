import cv2
import mediapipe as mp
import numpy as np

class PersonDetector:
    """
    This class finds people in video frames
    Like having magic glasses that highlight humans!
    """
    
    def __init__(self):
        print("🔧 Initializing Person Detector...")
        
        # Set up MediaPipe Pose detector
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        print("✅ Person Detector ready!")
    
    def detect(self, frame):
        """
        Find people in a single frame
        
        Args:
            frame: Image from camera
            
        Returns:
            results: Detection information
            annotated_frame: Frame with skeleton drawn
        """
        # Convert color (MediaPipe needs RGB)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect person
        results = self.pose.process(frame_rgb)
        
        # Draw skeleton if person found
        annotated_frame = frame.copy()
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(
                annotated_frame,
                results.pose_landmarks,
                self.mp_pose.POSE_CONNECTIONS
            )
        
        return results, annotated_frame
    
    def is_person_detected(self, results):
        """Check if a person was found"""
        return results.pose_landmarks is not None
    
    def get_body_center(self, results, frame_shape):
        """
        Get the center point of the person
        
        Returns:
            (x, y) coordinates or None
        """
        if not results.pose_landmarks:
            return None
        
        # Use shoulder midpoint as center
        landmarks = results.pose_landmarks.landmark
        
        left_shoulder = landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER]
        right_shoulder = landmarks[self.mp_pose.PoseLandmark.RIGHT_SHOULDER]
        
        h, w = frame_shape[:2]
        
        center_x = int((left_shoulder.x + right_shoulder.x) / 2 * w)
        center_y = int((left_shoulder.y + right_shoulder.y) / 2 * h)
        
        return (center_x, center_y)
    
    def close(self):
        """Clean up resources"""
        self.pose.close()
        print("🛑 Person Detector closed")


# Test the detector
if __name__ == "__main__":
    print("🎬 Testing Person Detector...")
    
    detector = PersonDetector()
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera")
        exit()
    
    print("📹 Camera opened. Press 'q' to quit")
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Detect person
        results, annotated = detector.detect(frame)
        
        # Show if person detected
        if detector.is_person_detected(results):
            cv2.putText(annotated, "PERSON DETECTED", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            
            # Show center point
            center = detector.get_body_center(results, frame.shape)
            if center:
                cv2.circle(annotated, center, 10, (0, 255, 0), -1)
        else:
            cv2.putText(annotated, "NO PERSON", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow('Person Detector Test - Press Q to quit', annotated)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
    detector.close()
    print("✅ Test complete!")
