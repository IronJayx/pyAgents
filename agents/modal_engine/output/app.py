import base64
import io
import json
from typing import List, Optional, Dict, Any, Union
from urllib.request import urlopen

import modal
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl, validator

# Create a Modal app
app = modal.App("shoe-detector")

# Define the container image with required dependencies
image = (
    modal.Image.debian_slim()
    .pip_install(
        "ultralytics",
        "numpy",
        "pillow",
        "requests"
    )
)

# Input model for the API endpoint
class ShoeDetectionRequest(BaseModel):
    image_url: Optional[HttpUrl] = Field(
        default=None,
        description="URL of the image to analyze for shoe detection"
    )
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64-encoded image data to analyze for shoe detection"
    )
    confidence_threshold: float = Field(
        default=0.25,
        description="Minimum confidence threshold for detection (0.0 to 1.0)",
        ge=0.0,
        le=1.0
    )

    @validator("image_url", "image_base64")
    def check_image_source(cls, v, values):
        # Ensure at least one image source is provided
        if v is None and "image_url" not in values and "image_base64" not in values:
            raise ValueError("Either image_url or image_base64 must be provided")
        return v

# Response model
class Detection(BaseModel):
    class_name: str
    confidence: float
    bounding_box: Dict[str, float]

class ShoeDetectionResponse(BaseModel):
    detections: List[Detection]
    processing_time_ms: float

# Function to detect shoes in images
@app.function(image=image)
@modal.fastapi_endpoint()
async def detect_shoes(request: ShoeDetectionRequest) -> ShoeDetectionResponse:
    with image.imports():
        import numpy as np
        from ultralytics import YOLO
        from PIL import Image
        import time

    # Start timing
    start_time = time.time()
    
    # Load the pre-trained YOLOv8 model
    model = YOLO("yolov8n.pt")
    
    # Load the image from URL or base64
    if request.image_url:
        with urlopen(str(request.image_url)) as response:
            img_data = response.read()
            image = Image.open(io.BytesIO(img_data))
    elif request.image_base64:
        try:
            img_data = base64.b64decode(request.image_base64)
            image = Image.open(io.BytesIO(img_data))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid base64 image: {str(e)}")
    
    # Convert to RGB if needed
    if image.mode != "RGB":
        image = image.convert("RGB")
    
    # Run inference
    results = model(image)[0]
    
    # Filter for shoe-related classes
    # COCO dataset classes include:
    # 39: 'bottle', 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon',
    # 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 49: 'orange', 50: 'broccoli',
    # 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair',
    # 57: 'couch', 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet',
    # 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 66: 'keyboard', 67: 'cell phone',
    # 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator',
    # 73: 'book', 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear',
    # 78: 'hair dryer', 79: 'toothbrush', 27: 'backpack', 28: 'umbrella', 31: 'handbag', 
    # 32: 'tie', 33: 'suitcase', 0: 'person', 24: 'backpack', 26: 'handbag',
    # 27: 'tie', 29: 'suitcase', 30: 'frisbee', 31: 'skis', 32: 'snowboard',
    # 33: 'sports ball', 34: 'kite', 35: 'baseball bat', 36: 'baseball glove',
    # 37: 'skateboard', 38: 'surfboard', 39: 'tennis racket
    
    # Shoe-related class ID in COCO dataset is 27 (for shoes/sneakers in COCO)
    # In YOLOv8's COCO implementation, shoes can be detected under several classes
    shoe_related_classes = [24, 25, 26, 27, 28, 29, 30, 31, 32]  # various footwear + bags
    
    detections = []
    
    for pred in results.boxes.data.tolist():
        x1, y1, x2, y2, confidence, class_id = pred
        
        # Only include if confidence exceeds threshold
        if confidence >= request.confidence_threshold:
            class_id = int(class_id)
            class_name = results.names[class_id]
            
            # Check if the detected object is in our list of shoe-related classes
            # or if the class name contains shoe-related terms
            is_shoe_related = class_id in shoe_related_classes or any(
                term in class_name.lower() for term in ["shoe", "boot", "sneaker", "sandal", "slipper"]
            )
            
            if is_shoe_related:
                # Calculate normalized bounding box
                img_width, img_height = image.size
                bbox = {
                    "x1": float(x1) / img_width,
                    "y1": float(y1) / img_height,
                    "x2": float(x2) / img_width,
                    "y2": float(y2) / img_height,
                    "width": float(x2 - x1) / img_width,
                    "height": float(y2 - y1) / img_height
                }
                
                detections.append(
                    Detection(
                        class_name=class_name,
                        confidence=float(confidence),
                        bounding_box=bbox
                    )
                )
    
    # Calculate processing time
    processing_time_ms = (time.time() - start_time) * 1000
    
    return ShoeDetectionResponse(
        detections=detections,
        processing_time_ms=processing_time_ms
    )

@app.local_entrypoint()
def main():
    print("Shoe detection API is running. Deploy this Modal app to use it as an API endpoint.")
    print("Example usage: curl -X POST 'https://<your-modal-endpoint>/detect_shoes' -H 'Content-Type: application/json' -d '{\"image_url\": \"https://example.com/image.jpg\"}'")