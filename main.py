import gradio as gr
import google.generativeai as genai
import time
import os

# Configure the API key for Gemini model
genai.configure(api_key="put your api key here")

# Function to process the video and generate captions in the selected language
def generate_subtitles(video_file, selected_language):
    # Upload the video file
    print(f"Uploading file...")
    uploaded_file = genai.upload_file(path=video_file.name)
    print(f"Completed upload: {uploaded_file.uri}")

    # Wait for the video to be processed
    while uploaded_file.state.name == "PROCESSING":
        print('Waiting for video to be processed.')
        time.sleep(10)
        uploaded_file = genai.get_file(uploaded_file.name)

    if uploaded_file.state.name == "FAILED":
        raise ValueError(uploaded_file.state.name)
    print(f'Video processing completed: ' + uploaded_file.uri)

    # Create the prompt with the selected language
    prompt = f"""Generate only the exact SRT subtitle file content in {selected_language} with the following format:
    - Each entry must have exactly 4 lines:
    Line 1: Sequential number only
    Line 2: Timestamp in 00:hh:mm:ss,mmm --> 00:hh:mm:ss,mmm format
    Line 3: Single short phrase of speech (5-7 words)
    Line 4: Blank line
    - Do not include any additional text, introductions, explanations, comments, or formatting.
    - Begin directly with '1' as the first line and proceed sequentially."""



    # Set the model to Gemini 1.5 Flash
    model = genai.GenerativeModel(model_name="models/gemini-1.5-pro")

    # Make the LLM request to generate subtitles
    print("Making LLM inferencing request...")
    response = model.generate_content([prompt, uploaded_file], request_options={"timeout": 600})

    # Save the subtitles to a file
    subtitles = response.text
    base_name = os.path.splitext(video_file.name)[0]
    srt_file_path = f"{base_name}.srt"
    with open(srt_file_path, "w", encoding="utf-8") as file:
        file.write(subtitles)
    
    
    
    # Return the subtitles text and the file path for download
    return subtitles, srt_file_path

# Create Gradio interface with a language selection option
with gr.Blocks() as demo:
    # Input components for video file and language selection
    video_input = gr.File(label="Upload Video File")
    language_selector = gr.Radio(
        choices=["Hindi", "English", "Nepali"], 
        label="Select Subtitle Language",
        value="Hindi"  # Default language
    )
    
    # Output components for subtitles and file download
    subtitles_output = gr.Textbox(label="Generated Subtitles")
    download_output = gr.File(label="Download SRT File")
    
    # Set up the interface to pass both the video file and selected language to the function
    demo_interface = gr.Interface(
        fn=generate_subtitles,
        inputs=[video_input, language_selector],
        outputs=[subtitles_output, download_output],
    )

demo.launch(share=True)
