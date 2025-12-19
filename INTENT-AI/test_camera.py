import cv2

print("🎥 Starting camera test...")
print("Press 'q' to quit")

# Open camera (0 means first camera)
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("❌ ERROR: Cannot open camera!")
    print("Make sure your webcam is connected")
    exit()

print("✅ Camera opened successfully!")

while True:
    # Read one frame from camera
    success, frame = camera.read()
    
    if not success:
        print("❌ Failed to read frame")
        break
    
    # Show the frame
    cv2.imshow('Camera Test - Press Q to quit', frame)
    
    # Wait for 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
camera.release()
cv2.destroyAllWindows()
print("👋 Camera closed. Test complete!")
