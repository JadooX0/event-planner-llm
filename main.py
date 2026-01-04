
from PIL import Image
from transformers import pipeline, LlavaNextProcessor, LlavaNextForConditionalGeneration, BitsAndBytesConfig
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from transformers.utils.logging import set_verbosity_error

set_verbosity_error()


model_id = "llava-hf/llava-v1.6-34b-hf" 


quantization_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16
)


processor = LlavaNextProcessor.from_pretrained(model_id)
model = LlavaNextForConditionalGeneration.from_pretrained(
    model_id, 
    quantization_config=quantization_config, 
    device_map="auto"
)


llava_pipeline = pipeline(
    "image-to-text", 
    model=model, 
    tokenizer=processor.tokenizer, 
    image_processor=processor.image_processor,
    max_new_tokens=500
)
llm = HuggingFacePipeline(pipeline=llava_pipeline)


template = """USER: <image>\n{instruction}\n\n{text}
ASSISTANT:"""
prompt = PromptTemplate.from_template(template)


image_path = input("Enter the path to the event poster image: ")
image = Image.open(image_path).convert("RGB")

instruction = "Extract the event name, date, venue, and a brief summary from this poster."
chain = prompt | llm


result = chain.invoke({"instruction": instruction, "text": "", "images": image})

print("\n🔹 **Poster Analysis:**")
print(result)


while True:
    question = input("\nAsk a question about the event (or type 'exit' to stop):\n")
    if question.lower() == "exit":
        break
    
    
    qa_result = chain.invoke({"instruction": question, "text": result, "images": image})
    print("\n🔹 **Answer:**")
    print(qa_result)
