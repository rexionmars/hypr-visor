import cv2
import numpy as np
from ultralytics import YOLO
import gi
import os

# Configure for Wayland
os.environ['GDK_BACKEND'] = 'wayland'

gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, GLib, Gdk

class ObjectDetectorWindow(Gtk.Window):
    def on_model_changed(self, combo):
        """Handle model selection change"""
        if not self.load_model():
            self.status_label.set_text("Error: Could not load new model")
            
    def on_file_selected(self, button):
        """Handle video file selection"""
        dialog = Gtk.FileChooserDialog(
            title="Please choose a video file",
            parent=self,
            action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )

        # Add file filters
        filter_video = Gtk.FileFilter()
        filter_video.set_name("Video files")
        filter_video.add_mime_type("video/mp4")
        filter_video.add_mime_type("video/avi")
        filter_video.add_pattern("*.mp4")
        filter_video.add_pattern("*.avi")
        dialog.add_filter(filter_video)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            file_path = dialog.get_filename()
            dialog.destroy()
            self.setup_video(file_path)
        else:
            dialog.destroy()
            
    def __init__(self):
        Gtk.init_check()
        
        # Initialize display
        display = Gdk.Display.get_default()
        if not display:
            print("Error: Could not connect to Wayland display")
            return
        
        print(f"Connected to display: {display.get_name()}")
        
        # Initialize window with Wayland-specific settings
        super().__init__(title="Visors - Object Detection")
        self.set_default_size(800, 600)
        print("Window initialized with size 800x600")
        
        # Add frame counter for debugging
        self.frame_count = 0
        
        # Request window decoration from the compositor
        self.set_decorated(True)
        
        # Set up the rest of the window...
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)
        print("Added vertical box container")
        
        # Add controls box
        controls_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        vbox.pack_start(controls_box, False, False, 0)
        
        # Add file selection button
        self.file_button = Gtk.Button(label="Select Video File")
        self.file_button.connect("clicked", self.on_file_selected)
        controls_box.pack_start(self.file_button, False, False, 0)
        
        # Add model selection
        model_label = Gtk.Label(label="Model:")
        controls_box.pack_start(model_label, False, False, 0)
        
        self.model_combo = Gtk.ComboBoxText()
        for model in ["yolo11n-seg.pt", "yolo11s-seg.pt", "yolo11m-seg.pt", "yolo11l-seg.pt", "yolo11x-seg.pt"]:
            self.model_combo.append_text(model)
        self.model_combo.set_active(0)
        self.model_combo.connect("changed", self.on_model_changed)
        controls_box.pack_start(self.model_combo, False, False, 0)
        
        self.image = Gtk.Image()
        vbox.pack_start(self.image, True, True, 0)
        
        self.status_label = Gtk.Label(label="Please select a video file...")
        vbox.pack_end(self.status_label, False, False, 0)
        
        # Initialize model
        if not self.load_model():
            self.status_label.set_text("Error: Could not load YOLO model")
            print("Failed to load YOLO model")
            return
        
        print("Model initialized successfully")
        
        # Show test pattern immediately
        self.show_test_pattern()
        print("Test pattern displayed")
        
        # Initialize video capture as None
        self.cap = None
        self.update_id = None
            
    def setup_video(self, video_path):
        """Initialize video capture with the selected file"""
        try:
            if self.cap is not None:
                self.cap.release()
            if self.update_id is not None:
                GLib.source_remove(self.update_id)
            
            self.cap = cv2.VideoCapture(video_path)
            if not self.cap.isOpened():
                print("Error: Could not open video file.")
                self.status_label.set_text("Error: Could not open video file")
                return False
            
            # Test read a frame
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("Error: Could not read frame from video.")
                self.status_label.set_text("Error: Could not read from video file")
                return False
                
            print(f"Video initialized successfully! Frame size: {frame.shape}")
            
            # Reset video to start
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            
            # Set up timer for frame updates
            self.update_id = GLib.timeout_add(30, self.update_frame)
            self.status_label.set_text("Video loaded successfully")
            return True
            
        except Exception as e:
            print(f"Exception during video setup: {e}")
            self.status_label.set_text(f"Error: {str(e)}")
            return False
            
    def load_model(self):
        """Load YOLO model"""
        try:
            model_name = self.model_combo.get_active_text()
            print(f"Loading model: {model_name}")
            self.model = YOLO(model_name)
            return True
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
            
    def show_test_pattern(self):
        """Show a test pattern to verify display is working"""
        try:
            test_pattern = np.zeros((480, 640, 3), dtype=np.uint8)
            test_pattern[:240, :320] = [255, 0, 0]  # Red quadrant
            test_pattern[:240, 320:] = [0, 255, 0]  # Green quadrant
            test_pattern[240:, :320] = [0, 0, 255]  # Blue quadrant
            test_pattern[240:, 320:] = [255, 255, 255]  # White quadrant
            
            height, width = test_pattern.shape[:2]
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                test_pattern.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                width,
                height,
                width * 3
            )
            
            self.image.set_from_pixbuf(pixbuf)
            print("Test pattern displayed successfully")
        except Exception as e:
            print(f"Error showing test pattern: {e}")
            
    def create_pixbuf_from_frame(self, frame):
        """Convert a frame to GdkPixbuf safely"""
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create GdkPixbuf from numpy array
            height, width, channels = rgb_frame.shape
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(
                rgb_frame.tobytes(),
                GdkPixbuf.Colorspace.RGB,
                False,
                8,
                width,
                height,
                width * channels
            )
            
            return pixbuf
        except Exception as e:
            print(f"Error converting frame to pixbuf: {e}")
            return None
            
    def update_frame(self):
        """Update frame with object detection"""
        if self.cap is None:
            return True
            
        try:
            self.frame_count += 1
            print(f"\nProcessing frame {self.frame_count}")
            
            ret, frame = self.cap.read()
            if not ret or frame is None:
                print("End of video reached")
                self.status_label.set_text("End of video reached - Restarting")
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                return True
                
            print(f"Frame captured: shape={frame.shape}")
            
            # Run YOLO detection
            results = self.model(frame, verbose=False)[0]
            print("YOLO detection completed")
            
            # Get segmentation masks
            if results.masks is not None:
                annotated_frame = results.plot()
                print("Using annotated frame with masks")
            else:
                annotated_frame = frame
                print("Using original frame (no masks)")
            
            # Convert to pixbuf
            pixbuf = self.create_pixbuf_from_frame(annotated_frame)
            if pixbuf is None:
                print("Failed to create pixbuf from frame")
                return True
                
            print("Created pixbuf successfully")
            
            # Scale the image to fit the window
            win_width, win_height = self.get_size()
            scaled_pixbuf = pixbuf.scale_simple(
                max(1, win_width - 20),  # Ensure width is at least 1
                max(1, win_height - 60),  # Ensure height is at least 1
                GdkPixbuf.InterpType.BILINEAR
            )
            print(f"Scaled pixbuf to {win_width-20}x{win_height-60}")
            
            # Update the image
            self.image.set_from_pixbuf(scaled_pixbuf)
            print("Updated image widget with new pixbuf")
            
            # Force immediate redraw
            self.image.queue_draw()
            while Gtk.events_pending():
                Gtk.main_iteration_do(False)
            
            # Update status and log detections
            self.log_detections(results)
            
        except Exception as e:
            print(f"Error processing frame: {e}")
            self.status_label.set_text(f"Error: {str(e)}")
        
        # Return True to keep the timer running
        return True
        
    def log_detections(self, results):
        """Log detected objects"""
        if results.boxes is not None:
            detections = []
            for box in results.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = results.names[class_id]
                detections.append(f"{class_name} ({confidence:.2f})")
            
            if detections:
                detection_text = "Detected: " + ", ".join(detections)
                print(detection_text)
                self.status_label.set_text(detection_text)
                
    def on_destroy(self, widget):
        """Handle window close"""
        if hasattr(self, 'cap'):
            self.cap.release()
        if hasattr(self, 'update_id'):
            GLib.source_remove(self.update_id)
        Gtk.main_quit()

def main():
    print("Starting GTK application...")
    
    if not Gtk.init_check()[0]:
        print("Failed to initialize GTK")
        return
        
    win = ObjectDetectorWindow()
    win.connect("destroy", win.on_destroy)
    win.show_all()
    print("Window should be visible now")
    
    try:
        Gtk.main()
    except KeyboardInterrupt:
        print("Application terminated by user")
    except Exception as e:
        print(f"Error in main loop: {e}")

if __name__ == "__main__":
    main()