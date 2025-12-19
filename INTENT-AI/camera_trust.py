import cv2
import numpy as np
from collections import deque

class CameraTrustSystem:
    """
    4-Layer Defense Against Camera Hacking:
    
    Layer 1: Feed Liveness Detection (is video frozen/looped?)
    Layer 2: Frame Entropy Analysis (is video static/fake?)
    Layer 3: Motion Pattern Verification (is movement realistic?)
    Layer 4: Overall Trust Score Calculation
    """
    
    def __init__(self, history_frames=30):
        """
        Initialize trust system
        
        Args:
            history_frames: How many frames to remember
        """
        self.history_frames = history_frames
        
        # Memory for analysis
        self.frame_hashes = deque(maxlen=history_frames)
        self.entropy_history = deque(maxlen=history_frames)
        self.motion_history = deque(maxlen=history_frames)
        
        self.last_frame = None
        self.frozen_frame_count = 0
        
        print("🔐 Camera Trust System initialized")
        print("   ✓ Layer 1: Liveness Detection")
        print("   ✓ Layer 2: Entropy Analysis")
        print("   ✓ Layer 3: Motion Verification")
        print("   ✓ Layer 4: Trust Score Engine")
    
    def _calculate_frame_hash(self, frame):
        """
        Create a simple fingerprint of the frame
        """
        # Resize to small size for quick comparison
        small = cv2.resize(frame, (32, 32))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        return hash(gray.tobytes())
    
    def _calculate_entropy(self, frame):
        """
        Measure how 'random' or 'information-rich' the frame is
        Static/frozen frames have low entropy
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()
        
        # Normalize
        hist = hist / (hist.sum() + 1e-7)
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist + 1e-7))
        
        return entropy
    
    def _calculate_motion_amount(self, frame):
        """
        Measure how much the frame changed from last frame
        """
        if self.last_frame is None:
            self.last_frame = frame
            return 0
        
        # Calculate difference
        diff = cv2.absdiff(frame, self.last_frame)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Amount of change
        motion = np.mean(gray_diff)
        
        self.last_frame = frame.copy()
        return motion
    
    def layer1_liveness_detection(self, frame):
        """
        LAYER 1: Detect if video is frozen or looped
        Returns: Score 0-100 (100 = definitely live)
        """
        frame_hash = self._calculate_frame_hash(frame)
        
        # Check if this exact frame appeared recently
        if frame_hash in list(self.frame_hashes)[-10:]:
            self.frozen_frame_count += 1
        else:
            self.frozen_frame_count = max(0, self.frozen_frame_count - 1)
        
        self.frame_hashes.append(frame_hash)
        
        # Calculate liveness score
        if self.frozen_frame_count > 5:
            liveness_score = max(0, 100 - (self.frozen_frame_count * 10))
        else:
            liveness_score = 100
        
        return liveness_score
    
    def layer2_entropy_analysis(self, frame):
        """
        LAYER 2: Measure frame complexity
        Returns: Score 0-100 (100 = normal entropy)
        """
        entropy = self._calculate_entropy(frame)
        self.entropy_history.append(entropy)
        
        # Normal video has entropy around 6-8
        # Static/fake video has low entropy
        
        if entropy < 4.0:
            entropy_score = int(entropy * 25)  # Low entropy = low score
        elif entropy > 8.5:
            entropy_score = max(0, 100 - int((entropy - 8.5) * 20))  # Too high = suspicious
        else:
            entropy_score = 100  # Normal range
        
        return entropy_score
    
    def layer3_motion_verification(self, frame):
        """
        LAYER 3: Verify motion patterns are realistic
        Returns: Score 0-100 (100 = realistic motion)
        """
        motion = self._calculate_motion_amount(frame)
        self.motion_history.append(motion)
        
        if len(self.motion_history) < 10:
            return 100
        
        recent_motion = list(self.motion_history)[-10:]
        
        # Check for suspicious patterns
        motion_variance = np.var(recent_motion)
        motion_mean = np.mean(recent_motion)
        
        # Realistic video has some variance in motion
        # Fake video might have constant motion or no motion
        
        if motion_variance < 0.1 and motion_mean < 0.5:
            # Almost no motion and no variance = suspicious
            motion_score = 30
        elif motion_variance < 1.0:
            # Very uniform motion = somewhat suspicious
            motion_score = 60
        else:
            # Good variance = realistic
            motion_score = 100
        
        return motion_score
    
    def layer4_calculate_trust_score(self, frame):
        """
        LAYER 4: Combine all layers into final trust score
        Returns: Trust score 0-100
        """
        liveness = self.layer1_liveness_detection(frame)
        entropy = self.layer2_entropy_analysis(frame)
        motion = self.layer3_motion_verification(frame)
        
        # Weighted average
        trust_score = int(
            liveness * 0.5 +  # Liveness is most important
            entropy * 0.3 +   # Entropy is important
            motion * 0.2      # Motion is supportive
        )
        
        return {
            'overall_trust': trust_score,
            'liveness': liveness,
            'entropy': entropy,
            'motion': motion
        }
    
    def is_feed_trustworthy(self, trust_scores, threshold=70):
        """
        Decide if camera feed is trustworthy
        
        Args:
            trust_scores: Dictionary from layer4_calculate_trust_score
            threshold: Minimum score to trust (default 70)
            
        Returns:
            True if trustworthy, False if suspicious
        """
        return trust_scores['overall_trust'] >= threshold
    
    def reset(self):
        """Clear all memory"""
        self.frame_hashes.clear()
        self.entropy_history.clear()
        self.motion_history.clear()
        self.last_frame = None
        self.frozen_frame_count = 0
        print("🧹 Camera trust memory cleared")


# Test the trust system
if __name__ == "__main__":
    print("🎬 Testing Camera Trust System...")
    print("\n🧪 Test instructions:")
    print("1. Normal mode: Move normally - should show HIGH trust")
    print("2. Cover camera: Cover lens - trust should drop")
    print("3. Freeze test: Stay very still - liveness score may drop")
    print("\nPress 'q' to quit\n")
    
    trust_system = CameraTrustSystem()
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        print("❌ Cannot open camera")
        exit()
    
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Calculate trust scores
        scores = trust_system.layer4_calculate_trust_score(frame)
        is_trusted = trust_system.is_feed_trustworthy(scores)
        
        # Create display
        display = frame.copy()
        
        # Draw trust indicator box
        box_color = (0, 255, 0) if is_trusted else (0, 0, 255)
        cv2.rectangle(display, (10, 10), (400, 180), box_color, 3)
        
        # Display scores
        y = 35
        cv2.putText(display, "=== CAMERA TRUST SYSTEM ===", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        y += 35
        
        cv2.putText(display, f"Overall Trust: {scores['overall_trust']}/100", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, box_color, 2)
        y += 30
        
        # Individual layer scores
        cv2.putText(display, f"Layer 1 (Liveness): {scores['liveness']}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(display, f"Layer 2 (Entropy): {scores['entropy']}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 25
        
        cv2.putText(display, f"Layer 3 (Motion): {scores['motion']}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        y += 30
        
        # Status
        status = "TRUSTED" if is_trusted else "SUSPICIOUS FEED!"
        status_color = (0, 255, 0) if is_trusted else (0, 0, 255)
        cv2.putText(display, f"Status: {status}", (20, y),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
        
        # Warning if suspicious
        if not is_trusted:
            cv2.putText(display, "!!! POSSIBLE CAMERA HACK !!!", (20, 250),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        
        cv2.imshow('Camera Trust Test - Press Q to quit', display)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    camera.release()
    cv2.destroyAllWindows()
    print("✅ Test complete!")
