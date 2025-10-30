# References from tutor

## Gihub repo
* https://github.com/ed-donner/llm_engineering.git


---

# Ollama API 
* Base URL =  http://localhost:11434/v1

* Sample curl
```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemma3:1b",
    "messages": [{"role": "user", "content": "Tell me a fun fact"}],
    "stream": false
  }'
```


* Sample python app
```python
from openai import OpenAI

OLLAMA_BASE_URL = "http://localhost:11434/v1"

MODEL = "gemma3:1b"
payload = [{"role": "user", "content": "Tell me a fun fact"}]

ollama = OpenAI(base_url=OLLAMA_BASE_URL)

response = ollama.chat.completions.create(model=MODEL, messages=payload, stream=False)

print(response.choices[0].message.content)
```


# We can also execute termina commands directly from .ipynb by prefixing '!' before the command
* # pull the missing ollama model
* !ollama pull smollm2:135m
