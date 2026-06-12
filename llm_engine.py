import random
from tenacity import retry, stop_after_attempt, wait_fixed


class LLMQuestionEngine:
    def __init__(self):
        pass  # Offline mode, no API needed

    @retry(stop=stop_after_attempt(1), wait=wait_fixed(1))
    def generate_questions(self, text_chunk):
        return {
            "MCQ": self._generate_mcqs(text_chunk),
            "Short Answer": self._generate_short_answers(text_chunk),
            "Long Answer": self._generate_long_answers(text_chunk),
        }

    def _generate_mcqs(self, text):
        keywords = self._extract_keywords(text)
        questions = []

        for k in keywords:
            questions.append({
                "type": "MCQ",
                "question": (
                    f"What is {k}?\n"
                    f"a) Option A\n"
                    f"b) Option B\n"
                    f"c) Option C\n"
                    f"d) Option D\n"
                    f"Answer: a"
                )
            })

        return questions

    def _generate_short_answers(self, text):
        keywords = self._extract_keywords(text)
        return [
            {
                "type": "Short Answer",
                "question": f"Explain {k} briefly."
            }
            for k in keywords
        ]

    def _generate_long_answers(self, text):
        keywords = self._extract_keywords(text)
        return [
            {
                "type": "Long Answer",
                "question": f"Explain {k} in detail with examples."
            }
            for k in keywords
        ]

    def _extract_keywords(self, text):
        words = [w.strip(".,()").capitalize() for w in text.split() if len(w) > 6]
        if len(words) < 3:
            words += ["The topic", "This concept", "The process"]
        return random.sample(words, 3)
