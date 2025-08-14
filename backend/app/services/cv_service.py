import os
import cv2
import logging
import numpy as np
from typing import Dict, Any, List, Optional
from pathlib import Path

from app.config.settings import settings

logger = logging.getLogger(__name__)

class ComputerVisionService:
    """Service for computer vision analysis of resume images."""
    
    def __init__(self):
        self.detector = None
        self.classes = [
            "background", "aeroplane", "bicycle", "bird", "boat",
            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
            "sofa", "train", "tvmonitor"
        ]
        self._load_model()
    
    def _load_model(self):
        """Load the MobileNetSSD model."""
        try:
            proto_path = settings.CV_MODEL_PROTO
            model_path = settings.CV_MODEL_CAFFE
            
            if not os.path.exists(proto_path) or not os.path.exists(model_path):
                logger.warning("Computer vision model files not found")
                return
            
            self.detector = cv2.dnn.readNetFromCaffe(
                prototxt=proto_path, 
                caffeModel=model_path
            )
            logger.info("Computer vision model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load computer vision model: {str(e)}")
            self.detector = None
    
    async def process_images(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process images and extract computer vision insights.
        
        Args:
            image_paths: List of image file paths
            
        Returns:
            List of processed image data
        """
        if not self.detector:
            logger.warning("Computer vision model not available")
            return []
        
        processed_images = []
        
        for image_path in image_paths:
            try:
                if os.path.exists(image_path):
                    image_data = await self._analyze_image(image_path)
                    processed_images.append(image_data)
                else:
                    logger.warning(f"Image file not found: {image_path}")
                    
            except Exception as e:
                logger.error(f"Failed to process image {image_path}: {str(e)}")
                continue
        
        return processed_images
    
    async def _analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze a single image using computer vision."""
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError("Failed to load image")
            
            height, width = image.shape[:2]
            
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)), 
                0.007843, 
                (300, 300), 
                127.5
            )
            
            self.detector.setInput(blob)
            detections = self.detector.forward()
            
            objects_detected = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                if confidence > 0.5:  
                    class_id = int(detections[0, 0, i, 1])
                    class_name = self.classes[class_id]
                    
                    box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
                    x1, y1, x2, y2 = box.astype("int")
                    
                    objects_detected.append({
                        "class": class_name,
                        "confidence": float(confidence),
                        "bbox": [x1, y1, x2, y2]
                    })
            
            image_features = self._extract_image_features(image)
            
            return {
                "file_path": image_path,
                "file_name": os.path.basename(image_path),
                "dimensions": {"width": width, "height": height},
                "objects_detected": objects_detected,
                "features": image_features,
                "analysis_summary": self._create_analysis_summary(objects_detected, image_features)
            }
            
        except Exception as e:
            logger.error(f"Image analysis failed for {image_path}: {str(e)}")
            return {
                "file_path": image_path,
                "error": str(e),
                "analysis_summary": "Analysis failed"
            }
    
    def _extract_image_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract basic image features."""
        try:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])
            
            texture_score = self._calculate_texture_score(gray)
            
            return {
                "mean_intensity": float(mean_intensity),
                "std_intensity": float(std_intensity),
                "edge_density": float(edge_density),
                "texture_score": float(texture_score),
                "color_channels": image.shape[2] if len(image.shape) > 2 else 1
            }
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {str(e)}")
            return {}
    
    def _calculate_texture_score(self, gray_image: np.ndarray) -> float:
        """Calculate a simple texture score."""
        try:
            grad_x = cv2.Sobel(gray_image, cv2.CV_64F, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray_image, cv2.CV_64F, 0, 1, ksize=3)
            gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
            
            return float(np.mean(gradient_magnitude))
            
        except Exception:
            return 0.0
    
    def _create_analysis_summary(self, objects: List[Dict], features: Dict) -> str:
        """Create a human-readable analysis summary."""
        if not objects and not features:
            return "No significant features detected"
        
        summary_parts = []
        
        if objects:
            object_counts = {}
            for obj in objects:
                class_name = obj["class"]
                object_counts[class_name] = object_counts.get(class_name, 0) + 1
            
            object_summary = ", ".join([
                f"{count} {class_name}" for class_name, count in object_counts.items()
            ])
            summary_parts.append(f"Detected objects: {object_summary}")
        
        if features:
            if "mean_intensity" in features:
                intensity = "bright" if features["mean_intensity"] > 127 else "dark"
                summary_parts.append(f"Image appears {intensity}")
            
            if "edge_density" in features:
                if features["edge_density"] > 0.1:
                    summary_parts.append("High detail/edge content")
                else:
                    summary_parts.append("Low detail/edge content")
        
        return "; ".join(summary_parts) if summary_parts else "Basic image analysis completed"
    
    async def health_check(self) -> Dict[str, Any]:
        """Check computer vision service health."""
        if self.detector is None:
            return {
                "healthy": False,
                "message": "Computer vision model not loaded",
                "model_status": "unavailable"
            }
        
        try:      
            test_image = np.zeros((100, 100, 3), dtype=np.uint8)
            test_blob = cv2.dnn.blobFromImage(test_image, 0.007843, (300, 300), 127.5)
            
            return {
                "healthy": True,
                "message": "Computer vision service is operational",
                "model_status": "loaded",
                "classes_available": len(self.classes)
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Computer vision service error: {str(e)}",
                "model_status": "error"
            }
