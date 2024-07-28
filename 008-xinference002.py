from xinference.client import Client
import openai
client = Client("http://localhost:9997")
# print(client.list_model_registrations(model_type='LLM'))
model_name="deepseek-chat"
model_engine="transformers"
model_format="pytorch"
model_size_in_billions=7
quantization="none"

model_name="glm4-chat"
model_engine="transformers"
model_format="pytorch"
model_size_in_billions=9
quantization="none"

model_uid = client.launch_model(model_name=model_name,
                                model_engine=model_engine,
                                model_format=model_format,
                                model_size_in_billions=model_size_in_billions,
                                quantization=quantization)
print("model_uid:" , model_uid)

model = client.get_model(model_uid)

client = openai.Client(api_key="not empty", base_url="http://localhost:9997/v1")
responce = client.chat.completions.create(
    model=model_uid,
    messages=[
        {
            "content": "What is the largest animal?",
            "role": "user",
        }
    ],
    max_tokens=1024
)
print(responce.choices[0].message.content)
prompt="最大的动物是什么？"
def get_completion(prompt, model=model_uid):    #model="claude-3-5-sonnet-20240620"
     response = client.chat.completions.create(model=model_uid,
            messages=[
            {
                "content": prompt,
                "role": "user",
            }
            ],
            max_tokens=1024,
            temperature = 0.5
            )
     return response.choices[0].message.content

response = get_completion(prompt, model_uid)
print(response)