import gradio as gr
from gradio_sourceviewer import SourceViewer


example = SourceViewer().example_value()

with gr.Blocks() as demo:
    gr.Markdown("WORK IN PROGRESS")
    source_viewer = SourceViewer()

if __name__ == "__main__":
    demo.launch()
