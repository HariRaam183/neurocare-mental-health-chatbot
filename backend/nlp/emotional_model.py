# backend/nlp/emotional_model.py

from transformers import pipeline
import torch


class EmotionAnalyzer:
    """Emotion analyzer that explicitly loads a named HF model and uses GPU if available.

    This avoids the "No model was supplied" note from transformers and ensures
    consistent behavior across environments.
    """

    def __init__(self, model_name: str = "j-hartmann/emotion-english-distilroberta-base"):
        # Use GPU device 0 if CUDA is available, otherwise use CPU (-1)
        device = 0 if torch.cuda.is_available() else -1

        # Explicitly set task and model to avoid defaulting behavior
        self._classifier = pipeline(
            task="text-classification",
            model=model_name,
            device=device,
            return_all_scores=False,
        )

    def analyze(self, text: str) -> dict:
        """Returns a dict: {"label": str, "score": float}.

        Short-circuits on empty input and truncates very long texts.
        """
        if not text or not text.strip():
            return {"label": "NEUTRAL", "score": 0.0}

        result = self._classifier(text[:512])[0]
        label = result.get("label", "NEUTRAL").upper()
        score = float(result.get("score", 0.0))
        return {"label": label, "score": score}
