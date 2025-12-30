!!! work-in-progress "Under construction"
    :construction: :construction: :construction:

    <span style='color:rgba(221, 189, 9, 1)'> **@Dulin lab members:** </span>
    Text is still a bit bare-bones, but should be enough to get point across. I will leave it to you to extend this page :smile: :wink:

    :construction: :construction: :construction:
    
# How to started labelling your dataset 

## :fontawesome-solid-terminal:  Start the app 

To start the application: 
=== "uv"

    ```shell
    uv run python main.py
    ```
=== "other .venv/ MacOS" 

    ```shell
    source ./.venv/bin/activate 
    python main.py
    ```

## :material-import: Load your traces 
- Menubar: **File > Open**
or use the keyboard shortcut  
 MacOS: **:material-apple-keyboard-command: + O**   
 Windows: **CTRL+O**

<img src="/screenshots/trace_shown.png" width="1000" height="1000">
<img src="/screenshots/dark_mode.png" width="1000" height="1000">


## :material-cog: Adjust list of available labels
Labels and section labels are independent from each other. This means you should construct your custom list of labels for both. 

<img src="/screenshots/list_of_labels.png" width="600">

<img src="/screenshots/list_of_section_labels.png" width="600">

## :material-mouse: Create a new section 
* Click in the plot twice to indicate the start / end of the section to be labelled 

<img src="/screenshots/section_created.png" width="1000" height="1000">


## :material-tag: Assigning labels to (sections of) the trace 
* Use the controls in the label assignment panel (top right) and section label assignment panel (bottom right)
<img src="/screenshots/assigned_section_and_label.png" width="1000" height="1000">

## :bulb: Commit changes 

* Changes are committed once you move to another trace in the dataset.