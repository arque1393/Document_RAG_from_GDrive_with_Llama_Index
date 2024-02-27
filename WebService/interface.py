import gradio as gr
import pandas as pd

# Function to generate answer
def generate_answer(question):
    # Example data, replace with your own logic to generate answer
    answer_text = f"The answer to your question '{question}' is..."
    answer_table = np.array([['sss','sdghh'],['sdgfsdgh','asfgASG']])
    return answer_text, answer_table

# Interface setup
question_input = gr.Textbox(label="Enter your question here")
output_text = gr.Textbox(label="Answer (Text)")
# output_table = gr.Table(label="Answer (Table)")
output_table = gr.Table(label="Answer (Table)", type="numpy")

# Interface creation
interface = gr.Interface(
    fn=generate_answer,
    inputs=question_input,
    outputs=[output_text,output_table],
    title="Question-Answer Interface",
    description="Enter your question and get answers in both text and table format."
)

# Launch the interface
interface.launch()




























