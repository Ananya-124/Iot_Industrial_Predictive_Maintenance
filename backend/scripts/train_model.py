from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from backend.app.model import train_prototype_model

if __name__ == "__main__":
    model = train_prototype_model()
    print(f"Prototype Random Forest trained. Classes: {list(model.classes_)}")
    print("WARNING: trained on synthetic data, not measured motor data.")
