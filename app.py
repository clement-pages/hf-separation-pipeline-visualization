import gradio as gr
from pyannote_viewer import PyannoteViewer
from pyannote.audio import Pipeline
import os
from huggingface_hub import HfApi

def apply_pipeline(audio: str, pipeline_name: str) -> tuple:
    pipeline = Pipeline.from_pretrained(
        pipeline_name, use_auth_token=os.environ["HF_TOKEN"]
    )

    outputs = pipeline(audio)
    if isinstance(outputs, tuple):
        return outputs
    else:
        return (outputs, audio)


with gr.Blocks() as demo:

    # header
    with gr.Row():
        # pyannote logo
        with gr.Column(scale=1):
            gr.Markdown(
                '<a href="https://github.com/pyannote/pyannote-audio"><img src="https://avatars.githubusercontent.com/u/7559051?s=200&v=4" alt="pyannote logo" width="170"/></a>'
            )
        # space title and description
        with gr.Column(scale=10):
            gr.Markdown('# pyannote pretrained pipelines')
    
            gr.Markdown(
                "You like [pyannote.audio](https://github.com/pyannote/pyannote-audio)? Consider using [pyannoteAI](https://pyannote.ai/) for better and faster options.\n"
                "\nGo [here](https://huggingface.co/pyannote) for more detail on each pipeline available in this space."
            )
            
            gr.Markdown()


    gr.Markdown("#### Select a pretrained pipeline:")
    available_pipelines = [p.modelId for p in HfApi().list_models(filter="pyannote-audio-pipeline")]
    available_pipelines = list(filter(lambda p: p.startswith("pyannote/"), available_pipelines))
    dropdown = gr.Dropdown(choices=available_pipelines, value=available_pipelines[0], interactive=True, label="Pretrained pipeline")

    gr.Markdown("#### Upload or record an audio:")
    audio = gr.Audio(type="filepath")

    btn = gr.Button("Apply pipeline")

    source_viewer = PyannoteViewer(interactive=False)

    btn.click(fn=apply_pipeline, inputs=[audio, dropdown], outputs=[source_viewer])


if __name__ == "__main__":
    demo.launch()
