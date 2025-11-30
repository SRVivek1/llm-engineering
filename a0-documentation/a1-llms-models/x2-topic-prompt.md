# Build data science UIs

# Overview of data science UIs

# Frameworks (UI for Non-frontend skills people)
* Gradio (favourite)
* Streamlit

# Introduction to gradio ui framework
# What is gradio ui ?
* Gradio from Hugging faces is a python framework


## How it works ?
- What tech stack it uses internally ?

## Dependency and Imports.

## First gradio UI program.
* Quick start: 
  * https://www.gradio.app/guides/quickstart#building-your-first-demo


# Hello world app for gradio
* Reference: https://www.gradio.app/guides/quickstart#building-your-first-demo

```python
    import gradio as gr

    def greet(name, intensity):
        return "Hello, " + name + "!" * int(intensity)

    demo = gr.Interface(
        fn=greet,
        inputs=["text", "slider"],
        outputs=["text"],
    )

    demo.launch()
```


# Share the app publicly using hugging face playground
* Intenally uses HTTP Tunneling to connect local computer with hugging face server.
* Still all calls are routed to user machine and server fetches response and present it to user.
  * This approach can run the app for free for a week.
  * use `gradio deploy` for free permanent hosting

```python

demo.launch(shared=True)
```


## Authentication in gradio

## how to enable authentication

### in place authentication
.launch(inBrowser=True, auth=("any", "rose"))


### Authentication with credentials from .env file / database

## Change UI theme from dark / light mode theme.
- Gradio recommends not to overwrite the theme and let the user choose.


# Define this variable and then pass js=force_dark_mode when creating the Interface

force_dark_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'dark') {
        url.searchParams.set('__theme', 'dark');
        window.location.href = url.href;
    }
}
"""
gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never", js=force_dark_mode).launch()


# Define this variable and then pass js=force_light_mode when creating the Interface

force_light_mode = """
function refresh() {
    const url = new URL(window.location);
    if (url.searchParams.get('__theme') !== 'light') {
        url.searchParams.set('__theme', 'light');
        window.location.href = url.href;
    }
}
"""
gr.Interface(fn=shout, inputs="textbox", outputs="textbox", flagging_mode="never", js=force_light_mode).launch()



# more refined UI design

# Adding a little more:

message_input = gr.Textbox(label="Your message:", info="Enter a message to be shouted", lines=7)
message_output = gr.Textbox(label="Response:", lines=8)

view = gr.Interface(
    fn=shout,
    title="Shout", 
    inputs=[message_input], 
    outputs=[message_output], 
    examples=["hello", "howdy"], 
    flagging_mode="never"
    )
view.launch()



# Integrate LLM
- Chnge the `fn` from shout function to a functing which connects to LLM model.