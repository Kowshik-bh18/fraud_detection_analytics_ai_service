import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        self.client = Groq(api_key=self.api_key)
        self.model = "llama-3.3-70b-versatile"

        # ✅ Track response times
        self.response_times = []

    def generate(self, prompt, temperature=0.5, max_retries=3):
        for attempt in range(max_retries):
            try:
                start_time = time.time()  # ⏱️ start

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=temperature
                )

                end_time = time.time()  # ⏱️ end
                duration = (end_time - start_time) * 1000  # ms

                # ✅ Store response time
                self.response_times.append(duration)

                # Keep only last 10 values
                if len(self.response_times) > 10:
                    self.response_times.pop(0)

                return response.choices[0].message.content

            except Exception:
                if attempt == max_retries - 1:
                    return "Error: Unable to generate response"

                time.sleep(2)  # retry delay

    # ✅ Get average response time
    def get_avg_response_time(self):
        if not self.response_times:
            return 0
        return sum(self.response_times) / len(self.response_times)