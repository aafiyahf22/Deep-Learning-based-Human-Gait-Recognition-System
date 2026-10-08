from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
from werkzeug.utils import secure_filename
from pathlib import Path
from typing import List
import shutil
import re
import time


app = Flask(__name__)
CORS(app)

# ------------------- CONFIG -------------------
UPLOAD_FOLDER = 'temp_uploads'
DATASET_ROOT = Path(__file__).parent / "dataset"
MODEL_WEIGHTS_PATH = Path(__file__).parent / "gait_model.pth"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class BiLSTMClassifier(nn.Module):
    def __init__(self, num_classes, external_cnn_features, hidden_size=512, num_layers=2, dropout=0.5):
        super(BiLSTMClassifier, self).__init__()
        self.cnn_features = external_cnn_features
        self.cnn_output_dim = 1280 
        self.hidden_size = hidden_size
        self.num_layers = num_layers

        self.lstm = nn.LSTM(
            input_size=self.cnn_output_dim,
            hidden_size=hidden_size,
            num_layers=num_layers,
            batch_first=True,
            bidirectional=True,
            dropout=dropout if num_layers > 1 else 0
        )

        self.classifier = nn.Linear(2 * hidden_size, num_classes)

    def forward(self, x):
        batch_size, T, C, H, W = x.size()
        x_reshaped = x.view(batch_size * T, C, H, W)
        
        if C == 1:
            x_reshaped = x_reshaped.repeat(1, 3, 1, 1)

        cnn_features = self.cnn_features(x_reshaped)
        cnn_features = cnn_features.view(batch_size, T, self.cnn_output_dim)

        lstm_output, _ = self.lstm(cnn_features)
        pooled_output = torch.mean(lstm_output, dim=1)
        logits = self.classifier(pooled_output)

        return logits
# ------------------- UTILITY FUNCTIONS -------------------
def numeric_sort_key(path: Path):
    nums = re.findall(r"\d+", path.name)
    if nums:
        return (0, tuple(int(n) for n in nums), path.name.lower())
    return (1, tuple(), path.name.lower())

def list_subject_ids(dataset_root: Path, num_classes: int) -> List[str]:
    if dataset_root.exists():
        subject_ids = sorted([p.name for p in dataset_root.iterdir() if p.is_dir()])
        if len(subject_ids) >= num_classes:
            return subject_ids[:num_classes]
    return [f"Person {i + 1:02d}" for i in range(num_classes)]

def select_frames(frame_paths: List[Path], num_frames: int) -> List[Path]:
    if len(frame_paths) == 0:
        raise ValueError("No frames found.")

    frame_paths = sorted(frame_paths, key=numeric_sort_key)

    if len(frame_paths) > num_frames:
        start_idx = (len(frame_paths) - num_frames) // 2
        return frame_paths[start_idx : start_idx + num_frames]

    return frame_paths + [frame_paths[-1]] * (num_frames - len(frame_paths))

def build_transform():
    return transforms.Compose([
        transforms.ToTensor(),
    ])

def load_sequence_tensor(frame_paths: List[Path], image_size=(240, 240)) -> torch.Tensor:
    tfm = build_transform()
    tensors = []

    for p in frame_paths:
        img = cv2.imread(str(p), cv2.IMREAD_COLOR)

        if img is None:
            img = torch.zeros((image_size[1], image_size[0], 3), dtype=torch.uint8).numpy()
        else:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, image_size)

        pil_img = Image.fromarray(img)
        tensors.append(tfm(pil_img))

    seq = torch.stack(tensors, dim=0)
    return seq.unsqueeze(0)

@torch.no_grad()
def predict_subject(model, sequence_tensor, subject_ids, device):
    x = sequence_tensor.to(device=device, dtype=torch.float32)

    logits = model(x)
    probs = torch.softmax(logits, dim=1)[0]

    top_probs, top_indices = torch.topk(probs, 3)
    pred_idx = int(top_indices[0].item())

    top_predictions = [
        {
            "subject": subject_ids[idx],
            "confidence": round(float(prob) * 100, 2)
        }
        for idx, prob in zip(top_indices, top_probs)
    ]

    return subject_ids[pred_idx], float(probs[pred_idx]), top_predictions

# ------------------- MODEL LOADING -------------------
def load_model(weights_path: Path, num_classes: int, device: torch.device):

    print(f"🔧 Loading model on {device}...")

    efficientnet = models.efficientnet_b1(
        weights=models.EfficientNet_B1_Weights.IMAGENET1K_V1
    )
    efficientnet.classifier = nn.Identity()

    model = BiLSTMClassifier(
        num_classes=num_classes,
        external_cnn_features=efficientnet,
        hidden_size=512,
        num_layers=2,
        dropout=0.5,
    ).to(device)

    state_dict = torch.load(str(weights_path), map_location=device)
    model.load_state_dict(state_dict, strict=True)

    model.eval()
    print("✅ Model loaded successfully!")

    return model

# ------------------- INIT -------------------
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

NUM_CLASSES = 30

try:
    model = load_model(MODEL_WEIGHTS_PATH, NUM_CLASSES, device)
except Exception as e:
    print("❌ Model failed to load:", e)
    model = None

SUBJECT_IDS = list_subject_ids(DATASET_ROOT, NUM_CLASSES)

# ------------------- API -------------------
@app.route('/predict_gait', methods=['POST'])
def predict():
    if model is None:
        return jsonify({'error': 'Model not loaded'}), 500

    if 'frames' not in request.files:
        return jsonify({'error': 'No frames uploaded'}), 400

    frames_files = request.files.getlist('frames')

    if not frames_files:
        return jsonify({'error': 'Empty upload'}), 400

    request_id = str(int(time.time()))
    extract_path = os.path.join(UPLOAD_FOLDER, request_id)
    os.makedirs(extract_path, exist_ok=True)

    try:
        saved_paths = []

        for file in frames_files:
            if file and '.' in file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'bmp']:
                    filename = secure_filename(file.filename)
                    path = os.path.join(extract_path, filename)
                    file.save(path)
                    saved_paths.append(Path(path))

        if len(saved_paths) == 0:
            return jsonify({'error': 'No valid images'}), 400

        print(f"📁 Received {len(saved_paths)} frames")

        selected_paths = select_frames(saved_paths, 25)

        sequence_tensor = load_sequence_tensor(selected_paths)

        subject, confidence, top_predictions = predict_subject(
            model, sequence_tensor, SUBJECT_IDS, device
        )

        shutil.rmtree(extract_path)

        return jsonify({
            "status": "success",
            "detected_gait": subject,
            "confidence": round(confidence * 100, 2),
            "top_predictions": top_predictions,
            "frames_received": len(saved_paths)
        })

    except Exception as e:
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)

        return jsonify({"error": str(e)}), 500

# ------------------- RUN -------------------
if __name__ == '__main__':
    app.run(debug=True, port=5000)