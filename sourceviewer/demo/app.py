
import gradio as gr
from gradio_sourceviewer import SourceViewer


example = SourceViewer().example_value()

demo = gr.Interface(
    lambda x:x,
    SourceViewer(),  # interactive version of your component
    SourceViewer(),  # static version of your component
    # examples=[[example]],  # uncomment this line to view the "example version" of your component
)


if __name__ == "__main__":
    demo.launch()
