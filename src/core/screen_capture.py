"""Screen capture and recording functionality."""

import os
import time
import threading
from typing import Optional, Tuple, List
from PIL import Image
import mss
import cv2
import numpy as np
try:
    from ..utils.logger import logger
    from ..utils.config import ConfigManager
except ImportError:
    from utils.logger import logger
    from utils.config import ConfigManager


class ScreenCapture:
    """Handles screen capture and recording operations."""
    
    def __init__(self, config: ConfigManager):
        """Initialize screen capture.
        
        Args:
            config: Configuration manager instance
        """
        self.config = config
        self.sct = mss.mss()
        self.recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.recorded_frames: List[np.ndarray] = []
        self._lock = threading.Lock()
    
    def capture_screen(self, region: Optional[dict] = None) -> Image.Image:
        """Capture screenshot of entire screen or region.
        
        Args:
            region: Optional region dict with 'top', 'left', 'width', 'height'
            
        Returns:
            PIL Image of the screenshot
        """
        try:
            if region is None:
                # Capture entire screen (monitor 1)
                screenshot = self.sct.grab(self.sct.monitors[1])
            else:
                screenshot = self.sct.grab(region)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            logger.debug(f"Screenshot captured: {img.size}")
            return img
            
        except Exception as e:
            logger.error_with_context(e, "screen capture")
            raise
    
    def capture_region(self, x: int, y: int, width: int, height: int) -> Image.Image:
        """Capture a specific region of the screen.
        
        Args:
            x: Left coordinate
            y: Top coordinate
            width: Region width
            height: Region height
            
        Returns:
            PIL Image of the region
        """
        region = {
            "top": y,
            "left": x,
            "width": width,
            "height": height
        }
        return self.capture_screen(region)
    
    def save_screenshot(self, filename: Optional[str] = None, region: Optional[dict] = None) -> str:
        """Capture and save screenshot to file.
        
        Args:
            filename: Optional filename. If None, generates timestamp-based name
            region: Optional region to capture
            
        Returns:
            Path to saved screenshot
        """
        try:
            # Create screenshots directory
            screenshots_dir = "screenshots"
            os.makedirs(screenshots_dir, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"screenshot_{timestamp}.png"
            
            filepath = os.path.join(screenshots_dir, filename)
            
            # Capture and save
            img = self.capture_screen(region)
            img.save(filepath)
            
            logger.info(f"Screenshot saved: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error_with_context(e, "save screenshot")
            raise
    
    def start_recording(self, fps: int = 10) -> None:
        """Start screen recording.
        
        Args:
            fps: Frames per second for recording
        """
        if self.recording:
            logger.warning("Recording already in progress")
            return
        
        with self._lock:
            self.recording = True
            self.recorded_frames = []
        
        self.recording_thread = threading.Thread(
            target=self._recording_worker,
            args=(fps,),
            daemon=True
        )
        self.recording_thread.start()
        logger.info(f"Screen recording started at {fps} FPS")
    
    def stop_recording(self, filename: Optional[str] = None) -> str:
        """Stop screen recording and save to file.
        
        Args:
            filename: Optional filename for the recording
            
        Returns:
            Path to saved recording
        """
        if not self.recording:
            logger.warning("No recording in progress")
            return ""
        
        with self._lock:
            self.recording = False
        
        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join()
        
        # Save recording
        if self.recorded_frames:
            return self._save_recording(filename)
        else:
            logger.warning("No frames recorded")
            return ""
    
    def _recording_worker(self, fps: int) -> None:
        """Worker thread for screen recording.
        
        Args:
            fps: Frames per second
        """
        interval = 1.0 / fps
        
        try:
            while self.recording:
                # Capture frame
                screenshot = self.sct.grab(self.sct.monitors[1])
                frame = np.array(screenshot)
                
                # Convert BGRA to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
                
                with self._lock:
                    if self.recording:  # Check again after acquiring lock
                        self.recorded_frames.append(frame)
                
                time.sleep(interval)
                
        except Exception as e:
            logger.error_with_context(e, "screen recording worker")
            with self._lock:
                self.recording = False
    
    def _save_recording(self, filename: Optional[str] = None) -> str:
        """Save recorded frames as video file.
        
        Args:
            filename: Optional filename
            
        Returns:
            Path to saved video file
        """
        try:
            # Create recordings directory
            recordings_dir = "recordings"
            os.makedirs(recordings_dir, exist_ok=True)
            
            # Generate filename if not provided
            if filename is None:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"recording_{timestamp}.mp4"
            
            filepath = os.path.join(recordings_dir, filename)
            
            if not self.recorded_frames:
                logger.warning("No frames to save")
                return ""
            
            # Get frame dimensions
            height, width, _ = self.recorded_frames[0].shape
            
            # Set up video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            fps = 10  # Default FPS
            video_writer = cv2.VideoWriter(filepath, fourcc, fps, (width, height))
            
            # Write frames
            for frame in self.recorded_frames:
                # Convert RGB to BGR for OpenCV
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                video_writer.write(frame_bgr)
            
            video_writer.release()
            logger.info(f"Recording saved: {filepath} ({len(self.recorded_frames)} frames)")
            
            # Clear recorded frames
            with self._lock:
                self.recorded_frames = []
            
            return filepath
            
        except Exception as e:
            logger.error_with_context(e, "save recording")
            raise
    
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        monitor = self.sct.monitors[1]  # Primary monitor
        return monitor["width"], monitor["height"]
    
    def find_image_on_screen(self, template_path: str, threshold: float = 0.8) -> Optional[Tuple[int, int]]:
        """Find an image template on the current screen.
        
        Args:
            template_path: Path to template image
            threshold: Matching threshold (0-1)
            
        Returns:
            Tuple of (x, y) coordinates of top-left corner if found, None otherwise
        """
        try:
            # Capture current screen
            screenshot = self.capture_screen()
            screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
            
            # Load template
            template = cv2.imread(template_path, cv2.IMREAD_COLOR)
            if template is None:
                logger.error(f"Could not load template image: {template_path}")
                return None
            
            # Perform template matching
            result = cv2.matchTemplate(screenshot_cv, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                logger.debug(f"Template found at {max_loc} with confidence {max_val:.2f}")
                return max_loc
            else:
                logger.debug(f"Template not found (max confidence: {max_val:.2f})")
                return None
                
        except Exception as e:
            logger.error_with_context(e, "template matching")
            return None