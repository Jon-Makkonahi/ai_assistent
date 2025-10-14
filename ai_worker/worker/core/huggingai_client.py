"""Клиент для взаимодействия с локальной моделью Hugging Face"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from ai_worker.worker.core.config import MODEL_NAME
from ai_worker.worker.utils.logger import logger


class HuggingFaceClient:
    def __init__(self):
        self.model_name = MODEL_NAME
        try:
            logger.info(f"Загрузка токенизатора для модели {self.model_name}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            logger.info(f"Загрузка модели {self.model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(self.model_name)
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
            self.model.to(self.device)
            logger.info(f"Модель {self.model_name} загружена на устройство {self.device}")
        except Exception as e:
            logger.error(f"Ошибка загрузки модели {self.model_name}: {str(e)}")
            raise RuntimeError(f"Ошибка инициализации модели: {str(e)}")

    def generate_text(self, input_data: str) -> str:
        """Генерирует текст с использованием локальной модели."""
        try:
            logger.info(f"Токенизация входных данных: {input_data}")
            inputs = self.tokenizer(input_data, return_tensors="pt").to(self.device)
            logger.info("Генерация текста моделью")
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=100,  # Увеличено для тестов
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                do_sample=True,
                top_k=50,
                top_p=0.95,
                temperature=0.7
            )
            result = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if not isinstance(result, str):
                raise RuntimeError(f"Ожидалась строка, получен {type(result)}")
            logger.info(f"Текст успешно сгенерирован: {result}")
            return result
        except Exception as e:
            logger.error(f"Ошибка генерации текста: {str(e)}")
            raise RuntimeError(f"Ошибка обработки AI: {str(e)}")

    def cleanup(self):
        """Очищает ресурсы модели."""
        if hasattr(self, "model"):
            logger.info("Очистка ресурсов модели")
            del self.model
            del self.tokenizer
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Ресурсы модели освобождены")
