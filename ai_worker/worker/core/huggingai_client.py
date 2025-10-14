"""Клиент для взаимодействия с локальной моделью Hugging Face"""
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from fastapi import HTTPException, status
from ai_worker.utils.logger import logger
from ai_worker.core.config import MODEL_NAME

class HuggingFaceClient:
    def __init__(self):
        self.model_name = MODEL_NAME
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Модель {self.model_name} загружена на устройство {self.device}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {self.model_name}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка инициализации модели"
            )

    async def generate_text(self, input_data: str) -> str:
        """Генерирует текст с использованием локальной модели."""
        try:
            inputs = self.tokenizer(input_data, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=50,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            logger.info(f"Текст успешно сгенерирован для входа: {input_data}")
            return result
        except Exception as e:
            logger.error(f"Ошибка генерации текста: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка обработки AI"
            )
