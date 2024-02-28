import gradio as gr
import pandas as pd


class WebInterface():
    ''' This class simulate a Web interface based on Gradio Python library 
    '''
    def __init__(self, output_func:callable) -> None:
        self.question_input = gr.Textbox(label="Enter your query")
        self.output_text = gr.Textbox(label="Answer")
        self.output_text_metadata = gr.Textbox(label="Resource")
        
        self.interface = gr.Interface(
            fn=output_func,
            inputs=self.question_input,
            outputs=[self.output_text,self.output_text_metadata],
            title="Question-Answer Interface",
            description="Enter your question and get answers in both text and table format."
        )
    def start(self):
        self.interface.launch()




if __name__ == ' __main__':

    i = WebInterface(lambda x:(x,x))
    i.start()
















