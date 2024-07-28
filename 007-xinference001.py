from gradio_client import Client

client = Client("http://localhost:9997/deepseek-chat/")
result = client.predict(
		message="Hello!!",
		request=512,
		param_3=1,
		param_4="Hello!!",
		api_name="/chat"
)
print(result)

chat_history = []
prompt = "What is the largest animal?"
model= client.get_model("deepseek-chat")
# If the model has "generate" capability, then you can call the
# model.generate API.
results= model.chat(
    prompt,
    chat_history=chat_history,
    generate_config={"max_tokens": 1024}
)
print(results)