import gradio as gr
from gradio_sourceviewer import SourceViewer
from pyannote.audio import Pipeline
import os


def apply_pipeline(audio: str) -> tuple:
    pipeline = Pipeline.from_pretrained(
        "pyannote/speech-separation-ami-1.0", use_auth_token=os.environ["HF_TOKEN"]
    )
    return pipeline(audio)


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
            gr.Markdown('# Speaker diarization and speech separation pipeline')
    
            gr.Markdown(
                "This space is dedicated to showing the use of the speaker diarization and speech separation [pipeline](https://huggingface.co/pyannote/speech-separation-ami-1.0) integrated to `pyannote.audio`. To use this space:"
                "\n - Load or record an audio"
                "\n - Click on the apply pipeline button"
                "\n - After pipeline processed the audio, you can then listen for each speaker separetely. Annotations on waveforms correspond to the speaker diarization produced by the pipeline, with one color per speaker."
            )

    audio = gr.Audio(type="filepath")
    btn = gr.Button("Apply separation pipeline")
    source_viewer = SourceViewer(interactive=False)

    btn.click(fn=apply_pipeline, inputs=[audio], outputs=[source_viewer])


if __name__ == "__main__":
    demo.launch()
