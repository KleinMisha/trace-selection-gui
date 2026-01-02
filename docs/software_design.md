# Software design 
To explain the main architectural choices made to design this software, let's walk through "rebuilding this project bottom-up". 
Before starting, a little note on having both source code (in the `app/` directory) and test code (in the `tests/` directory). To keep things organized, every file in the `app/` folder has a corresponding file in the `tests/` folder.


<span style="color:coral">**_:octicons-light-bulb-16: A step-by-step guide to adding your custom feature/component is included below._**  :octicons-light-bulb-16: </span>



=== "Basic Project tree with has source code and tests"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app (:simple-python:)   
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: application_code.py  
    :material-subdirectory-arrow-right: :material-folder-open: tests (:simple-pytest:)  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: test_application_code.py  

<span style="color:coral">**_:fontawesome-solid-exclamation: To make some of the subsequent project trees easier to read, the `test/` directory will be omitted._**  :fontawesome-solid-exclamation: </span>


???- info "unit tests with `PyTest`"
    _**<span style="color:hotpink">:fontawesome-solid-question: :fontawesome-solid-question::fontawesome-solid-question: TODO: make a dedicated page for explaining tips and tricks for testing PyQt applications? :fontawesome-solid-question::fontawesome-solid-question::fontawesome-solid-question:</span> **_ 

    **What are unit tests?**  
    They programmatically define the expected/desired outcome of your source code. One way of doing this is to manually inspect every step of your code through some targeted print statements. However, what if you want to check a function for 20 different parameter sets? Or you want to test an older bit of code, just to make sure things did not break in the process? Now going the 'old-fashioned' route becomes extremely tedious. Moreover, you might even forget, or simply not know, what another part of the code is expected to do. 
    Fortunately, there is a way around this: We use a framework called `PyTest`. In a nutshell, you write a bunch of functions called `def test_...()` that end with an `assert` statement. If a test fails, normally the code will break (by design the assertion raises an exception). However, `PyTest` can handle this and will check if you pass your assertion. Using a combination of `pytest`, and the builttin `unittest` library, we can (relatively) easily

    1. supply a set of parameter combinations to test on
    2. define 'fixtures'; shared objects accross multiple tests. 
    3. test we raise exceptions when needed.
    4. `Mock` objects we must pass as dependencies (given we used the clean software design explained here to not couple things in complicated ways).



    **Why go through the hassle?**  
    They help you spot some flaws in your own code during development. Many mistakes can now be fixed before committing them. Moreover, while you might be able to track exactly what is going on in your own feature at the time of writing, having unit tests for all the code helps you make sure you are not unintentionally breaking/altering the workings of other parts to the code. 

    **Where to store tests?**  
    In addition to the source code (located in the `app/` directory), there are (unit) tests (`test/` directory). The `test/` and `app/` directories follow the exact same structure to make it easy to find which set of tests belong to what python file in the source code.  
    The `pyproject.toml` file (see below) is set up such that it 'tells PyTest to look in the `tests/` folder by default`.






# :material-file-code: A small GUI: Model-View-Controller  
While putting all your code into a single Python file might suffice for a simple script, this quickly becomes an untractable mess when creating a larger piece of software. It also will couple all parts of your code together, if you do not take caution, which makes extending and amending it later a pain. While any working piece of software needs to eventually couple different bits together for it to do anything useful, one should always aim to delay that moment to the very end (see the discussion on `main.py` below).

The Model-View-Controller (MVC) pattern is a way to separate the code with the actual calculations and operations you want to perform on your data (**the Model**) from the set of user inputs (key presses, and buttons, etc.) that act as a trigger of these operations (**the View**).  
The trick is to introduce a third layer that essentially acts as 'the brains of the application'; triggering the correct updates on the model and view side after getting the trigger (**the Controller**). 

???-  Note "naming convention & alternative patterns"
    Technically, the pattern used here follows what is called the "Model-View-Presenter" design pattern. However, naming is not always consistent online, and some will still call the pattern presented here as Model-View-Controller. 

    Also, the canonical way of making a `PyQt` application is to use a pattern called "Model-View-'View Model'" (MVVM). However, I personally found the MVC a simpler mental model, especially when reducing coupling. The small price to pay is that we are now manually creating and wiring/connecting signal objects. This loses some of the "builtin quality of life features of PyQt6" in favor of more explicit code that is easier to explain.

    :fontawesome-solid-magnifying-glass: **For more info**  <br>
    :arrow_right: [MVC, MVP, vs MVVM](https://medium.com/@ankit.sinhal/mvc-mvp-and-mvvm-design-pattern-6e169567bbad) <br>
    :arrow_right: [Tutorial based on youtube (includes PyQt example of MVVM)](https://www.youtube.com/watch?v=eHhXoCNCI1c)



=== "Model-View-Controller" 
    ```mermaid    
    flowchart LR
    interaction(( User )) -->|interacts with| View
    View -->|informs| Controller
    Controller -->|updates| Model
    Controller -->|updates| View 
    ```

=== "Project tree with one MVC."

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: controller.py  
    :material-subdirectory-arrow-right: :material-folder-open: tests  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: test_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: test_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: test_controller.py  

## :material-database-cog: The Model 
Key to the MVC architecture is that it separates things relating to the GUI (button presses, input fields, etc.) from the stuff that should happen after the user interacts with it. 

The `Model` class 'knows'/encapsulates:

* The way data is represented internally (*do I store labels as a list? do I store sections as dictionary or as a dataframe?*)
* How to modify and analyze the data. 
* how to export the data (*do I write it into a JSON or a TXT file?*)

The `Controller` only gets to know an abstract version of the `Model`. For example, it only knows the model has some method called "`save_data()`", and does not get to (nor does it ever need to) know if `save_data` exports the data to JSON, TXT, Python code, carves the solution into a rock, or sends a carrier pigeon to deliver the message for that matter. 

Similarly, if the GUI has a button to trigger reference bead subtraction, all the controller gets to know is that the model will have some method called `subtract_reference(bead_id: int) -> None` (just an example). 

## :eyes: The View 
This is the place where it matters what framework is used to define your GUI. This project uses `pyQt6`.

The `View` class 'knows'/ encapsulates:

* The GUI's visual elements: Does the user see a button, a radiobutton, drop down, check box, or an input field? 
* Receiving the user's input and forwarding this information to the `Controller`. 



### Designing the GUI's layout. 
Big reason for choosing to use `PyQt6` over other frameworks (e.g. `Tkinter`) is the `Qt-designer` tool that allows one to quickly create a GUI's layout by dragging and dropping elements into it (called `Widgets` in Qt's terminology). See [Installation] for instructions on installing the designer tool. 
The tool produces `.ui`-files. While these can directly be imported into your Python code, your IDE (VSCode, PyCharm, etc.) will not know of the Widgets you defined. The workaround is to compile your `.ui`-file into a `.py` file. The result is a Python class of which you should make your `View` a subclass of: 

```py linenums="1" title="Setup from the designer file."
    
    # import the class created by the compiler. 
    # NOTE: The name of this class is created automatically 
    from app.view import Ui_View
    
    # Let View inherit from this auto-generated class 
    class View(Ui_View)
        def __init__(self) -> None:
            super().__init__()
            self.build_ui()

            # Now your code editor knows of all the variables defined in the designer tool. It also knows of all the attributes and methods these Widgets should have. 
            # Say, you had a button and a lineEdit, the IDE will now help you autocomplete...
            self.bigButton.clicked.connect(...)
            self.enterNumber.editingFinished.connect(...) 

        def build_ui(self) -> None:
            """use the (compiled) UI file to build things, such that this code knows about the variable names in VSCode"""
            self.setupUi(self)
``` 


???+ tip "compiling designer files to Python code"

    Drag-and-drop your elements to quickly arrange / scale things etc. within the designer tool, and save the resulting session in a `.ui` file. 

    The following script will take care of calling the compiler on all `.ui` files stored within the `app/` directory: 
    
    ```bash 
    uv run python scripts/compile_qt_ui_files.py
    ``` 
    If your original file was called `my_view.ui` this will create `my_view_ui.py` in the same directory as the original file. 




### Listening to user's input. 
The whole point of the MVC is to avoid coupling the user's actions (clicking a button, entering a number) from the operation we want to happen after (which is encapsulated in the `Model`). To make this happen, we need a way for the `View` to  retrieve the user's input, and send this to the `Controller`. Fortunately, `PyQt` has a builtin mechanism for this. A `pyqtSignal(<ENTER DATA TYPE>)` can be told to "emit" the received data of the desired type to any function that is connected to it. To hook things up properly:

1. Create a signal 
2. We tell it to emit upon triggering
3. We allow for a function of the `Controller` to connect to this signal. 






=== "The View with one signal"
    ```python linenums="1"
    from PyQt6.QtCore import pyqtSignal
    from PyQt6.QtWidgets import QWidget

    class View(QWidget):
        # we define a class-level attribute with the signal (pyQT syntax)
        _button_is_pressed_signal = pyQtSignal()
        def __init__() -> None: 
            # In stead of directly wiring the button to the model-side function (which would couple things), 
            # we connect it to a method that sends a signal. 
            self.my_button.clicked.connect(_send_button_is_pressed_signal)

        def connect_button_is_pressed_signal(callback: Callable[[], None]) -> None:
            # Next, we tell the code where to send the signal to
            # This will be a function on of the Controller. Whatever is send as the signal will be treated as an input argument of the callback function. 
            _button_is_pressed_signal.connect(callback)
        
        def _send_button_is_pressed_signal() -> None: 
            _button_is_pressed_signal.emit() 


    ```

???- tip "sending along data with the signal" 
    By default a `pyqtSignal()` will only notify the listener upon emitting the signal. To forward a user's selection or entry, we can simply supply the type of data to be emitted (instead of the default `None` type): 

    ```python linenums="1" title="User selection data in a signal."
    from PyQt6.QtCore import pyqtSignal 

    # sending any of the primitive types (int, float, bool, str): 
    _signal_w_int = pyqtSignal(int) 
    _signal_w_float = pyqtSignal(float) 
    _signal_w_bool = pyqtSignal(bool) 
    _signal_w_str = pyqtSignal(str) 
    ```
    If if callback oin the `Controller` side has the matching function signature, meaning, 

    ```python linenums="1" title="Connect to listener" 


    class Controller:
        
        def __init__(self, model: Model, view: View) -> None: 
            self.model = model 
            self.view = view

            self.view.connect_signal_w_float(self.handle_float_selection)

        def handle_float_entry(self, value: float) -> None:
            """example for creating a new 'User' with a name and and age"""
            self.model.create_user(name, age)

    class View(QWidget):
        _signal_w_float= pyqtSignal(float)

        def connect_signal_w_float(self, callback: Callback[[float], None]) -> None:
            _signal_w_float.connect(callback)
        
        def _send_signal_w_float(self, value:float) -> None:
            _signal_w_float.emit(value)
    ```

    `PyQt` will automatically take care of passing the emitted values as arguments to the connected callback. 
    When using multiple values, they will be passed to the listener/callback in the same order you omitted them. 

    ```python linenums="1" title="Multiple input values" 

    class Controller:
        
        def __init__(self, model: Model, view: View) -> None: 
            self.model = model 
            self.view = view

            self.view.connect_user_info_entry_signal(self.handle_user_creation)

        def handle_user_creation(self, name: str, age: int) -> None:
            """example for creating a new 'User' with a name and and age"""
            self.model.create_user(name, age)

    class View(QWidget):
        _user_info_entry_signal = pyqtSignal(str, int)

        def connect_user_info_entry_signal(self, callback: Callback[[str, int], None]) -> None:
            _user_info_entry_signal.connect(callback)
        
        def _send_user_info_entry_signal(self, name: str, age:int) -> None:
            _user_info_entry_signal.emit(name, age) 
    ```


## :brain: The Controller 
How do we make the model and view communicate without ever knowing of each other's existence? This is why we have the controller layer. 

The `Controller` class 'knows'/encapsulates: 

   - Receiving signals emitted by the view. 
   - Calling functions of the Model and View to perform key operations. 
   - It gets the instances of the model and view created. 
   - it only knows *what* methods exist on the model and view side, not *how* these methods work. 


=== "Handling the signals from the View"

 ```python linenums="1" title="basic Controller." 
    from typing import Protocol 
    
    class Model(Protocol):
        """Hiding implementation details of the model from the controller"""

        def do_operation(self) -> None: ...
        
    class View(Protocol):
        """Hiding implementation details of the view from the controller"""
        
        def connect_signal(callback: Callable[[],None]) -> None: ...


    class Controller: 

        def __init__(model, view) -> None: 
            self.model = model 
            self.view = view 

            # connect the correct method of the controller to the corresponding input signal (of the view)
            self.view.connect_signal(self.handle_signal)
        
        def handle_signal() -> None: 
            #Now the controller will orchestrate the updates. This function will be triggered whenever a signal gets emitted (which we now have properly setup)
            self.model.do_operation()
            self.view.update_display_to_user()
    
 ```

# :material-application-brackets: A larger GUI: Introduce components 
The above setup works fine for smaller applications, say a simple to-do-list. However, to further break up / decouple our code into smaller units, we build the app from smaller components. Each of these components is it's own enclosed MVC. 

## :bulb: Example component: Labelling traces 
Adding and removing labels from a trace is handled by a (mostly) self-contained MVC. 

The `Model` holds a single time trace, a list of assigned labels, and methods for adding/removing string-valued labels to it. 

The `View` encodes the panel with buttons to toggle between available label options, adding, and removing the 'in focus' label to the trace in question. 

The `Controller` listens to button presses in the view's panel and triggers data updates by the model. 

:material-information-outline: Note that this MVC does not know the experimental data set contains more than a single trace or how far into the dataset the selected trace occurs. Also, this component does nothing more than assigning / removing a label. 

:material-information-outline: It does not display the trace as a matplotlib figure. This is done by another component, which, in turn, does not need to know anything about the specific labels that are assigned. 


:octicons-light-bulb-16: This decoupling allows us to easily test functionality in isolation. This is how we keep the larger software, as a whole, maintainable and extensible. 


## :brain: A special component: 'the main MVC' 
If every component is a self-contained MVC, how does the application actually orchestrate them? 

 

This is where we introduce one 'special' component: the main component (with a lack of a better name. Not to be confused with `main.py` which will be discussed below.).

> *Or put differently: If our application is a person*
> 
> - *Components are organs*
> - *The main component acts as 'the brains'*
> - *It knows things pertaining to multiple components and communicates with other components ('the nervous system').*

The main component, still acts like any of the other MVC's. It has a `MainModel` to:
- Keep track of the full experiment data 
- Exporting final results 
- Keep track of what trace is "in focus" 
- Keep track of how far into the dataset you are
- etc. 

The `MainView`: 
- Defines the menubar (with actions to load/save data)
- Defines the buttons to toggle between traces, perform reference subtraction, etc. 

The `MainController` orchestrates communication between the above. 

Thus far nothing is different from any of the other MVCs explained above. Only reason for calling it `Main` is that everything mentioned above concerns entries/values that pertain to the entire dataset at once. 

The `MainController` can also communicate with any of the `ComponentController`s.

For this purpose, inject the `ComponentController` into the `MainController`. Besides the abstractions for the `Model` and `View` (here representing the `MainModel` and `MainView`, i.e. 'its own model and view"), we use abstraction to tell `MainController` what each `ComponentController` can do. 

???+ note "module with component controller protocols" 
    To keep things tidy, component controller protocols are moved to their own file, which is still stored in the directory of the `main_app`. 

```python linenums="1" title="Example MainController with one ComponentController"

from typing import Protocol 

class Model(Protocol):
    """Hide implementation details of MainModel"""

    # Examples (not the actual implementation)
    def load_data(self, filename: Path) -> None: ...
    def save_data(self, filename: Path) -> None: ... 
    def get_current_trace(self) -> Trace: ...
    def move_to_next(self) -> None: ...
    def move_to_previous(self) -> None: ... 



class View(Protocol):
    """Hide implementation details of MainView"""
    # Examples (not the actual implementation)
    def connect_next_button(self, callback: Callable[[], None]): ... 
    def connect_prev_button(self, callback: Callable[[], None]): ... 
    def open_file_selection_window(self) -> None: ... 



class ComponentController(Protocol):
    """Hide implementation details of the ComponentController""" 
    
    # Example from the ComponentController Protocol 
    def reset_for_new_trace(self, trace: Trace) -> None: ...
    def get_assigned_labels(self) -> list[str]: ...
    def get_available_labels(self) -> list[str]: ...


class Controller: 

    def __init__(self, model: Model, view:View, component: ComponentController) -> None:
        self.model = model 
        self.view = view 
        self.component = component 


        self.view.connect_next_button(self.handle_moving_to_next_trace)
    # Example of how receiving a signal from the main app can trigger an action at the component level. 
    def handle_moving_to_next_trace(self) -> None:

        # "internal" updates
        self.model.move_to_next()

        # Tell the component to restart with a new trace 
        trace = self.model.get_current_trace() 
        self.component.reset(trace)
```


!!! info "component factories"
    Actually, this dictionary is subtly set up differently, which will be explained below. 

!!! warning "Only components talk to each other" 
    The `MainController` does not get to know anything of the `ComponentModel` and `ComponentView`. It merely tells the `ComponentController` to handle things further down the road. 

    It is important to adhere to this design choice, for else additional coupling is introduced. Making tests allot harder, and increasing the potential of introducing bugs. 



## :eyes: Displaying components as part of the main window  
There is one thing we have not yet taken care of. The application displays a single frontend to the user: the `MainView`. Hence, we need a mechanism to actually display the `ComponentView`. 

To this end, we create an empty `QWidget` in the designer file for `MainView`. Next, we tell `MainView` the name of this placeholder widget upon instantiating. 



### :factory: Component factory 
To simplify creation logic, we introduce a `factory` for every component. A simple function that creates a properly instantiated `ComponentController`. 

```python linenums="1" title="simple controller factory"
from app.core.component_factory_helpers import fill_component_to_placeholder
from app.component.component_controller import ComponentController
from app.component.component_model import ComponentModel
from app.component.component_view import ComponentView


def create_component(
    placeholder: QWidget | None
) -> ComponentController:
    """To be called by the main.py when setting up the entire app"""
    model = ComponentModel()
    view = ComponentView(parent=placeholder)
    controller = ComponentController(model, view, config)
    if placeholder:
        fill_component_to_placeholder(view, placeholder, force_layout=True)
    return controller

```
This way, every component is responsible for creating their own 'lower level objects' (i.e. the model and view) and only expose their controller. 
(Of course, this introduces a bit of coupling by using a placeholder in the main view, but there is no real way around things here using `PyQt`.)

:octicons-light-bulb-16: Helper methods in `app/core/` take care of properly replacing the empty widget by the `ComponentView`. 




## :speaking_head: Multiple components 
At this point, we already recreated most of the project's file setup (see below). 
Of course, the full application needs more than a single `ComponentController`. 
The scale-up the ideas described above, we do not inject the `ComponentController` directly into the `MainController`, but supply a mapping of component name to their controllers instead. 

```python linenums="1" title="Dictionary of component controllers"


class ComponentControllers(TypedDict):
    """
    Register the new components over here

    ---
    NOTE: The types here refer to protocol types, defined in the `component_controller_protocols.py` module. 
    """

    first_component: FirstController
    second_component: SecondController



class Controller:
    def __init__(self, model: Model, view: View, components: ComponentControllers) -> None: 
        self.model = model 
        self.view = view 
        self.components = components
```
Communication between the `MainController` and a single component happens as described above. 
There are scenario's in which a user's interaction with one component should effect another component. 
For example, when the user clicks in the plot, the component taking care of section labels needs to know the selected time point. 

Important is that these components never get to communicate directly: All communication happens via the main component. 
To achieve this, the `PlotController` in this example must emit a signal after it receives the signal from the `PlotView` with the location of the user's click. 
The `MainController` then listens to this signal, and triggers updates of the `SectionPanel` by calling the `SectionPanelController`. 


The first component will have the following setup (shown here in a single code block for convenience)
```python linenums="1" title="communicate between components." 

# in first/first_view.py:

class FirstView(QWidget):
    _user_selection_signal = pyqtSignal(float)

    def connect_user_selection_signal(self, callback: Callable[[float], None]) -> None:
        self._user_selection_signal.connect(callback)
    
    def _send_user_selction_signal(self, value: float) -> None:
        self._user_selection_signal.emit(value)
    
# in first/first_controller.py:

class FirstController(QObject): 
    _relay_user_selection = pyqtSignal(float)

    def __init__(self, model: FirstModel, view: FirstView):
        self.model = model 
        self.view = view 

        # listen to its own view (the same strategy as above)
        self.view.connect_user_selection_signal(self.handle_user_selection)

    def handle_user_selection(self, value: float) -> None:

        # Examples for internal updates: 
        self.view.display_selection(value)
        self.model.update_value(value)

        # inform the main controller (this is now part of the handling control flow): 
        self._relay_user_selection.emit(value)
    
    def connect_relay_user_selection(self, callback: Callable[[float], None]) -> None: 
        self._relay_user_selection.connect(callback)

# in second/second_controller.py: 

class SecondController:

    def __init__(self, model: SecondModel, view:SecondView) -> None: 
        self.model = model 
        self.view = view 
    
    def process_user_selection(self, value) -> None: 
        """Should be triggered by an action in the first component"""

    

# in main_app/main_controller.py 

class MainController: 
    def __init__(self, model: MainModel, view: MainView, components: ComponentControllers) -> None: 
        self.model = model 
        self.view = view 
        self.components = components 

        self.connect_components()
    
    def connect_components(self) -> None: 
        """ Listen to the relayed (!) signal """ 
           self.components["first_component"].connect_relay_user_selection(
            self.handle_user_selection
        )

    def handle_user_selection(self, value: float) -> None: 
        """ Now the main Controller received the user's selection in the first component and can pass the value on to the second component""" 

        self.components["second_component"].process_user_selection(value)
```



=== "Example using a single component"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_controller_protocols.py  

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_factory.py  


=== "Larger applications will have several components"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: component_3  
    :octicons-dot-16:  
    :octicons-dot-16:  etc. (incl. tests)  
    :octicons-dot-16:


=== "Information flow" 

    The user interacts with the GUI per usual
    ```mermaid 
    flowchart LR 
    interaction(( User )) --> MainView 
    interaction(( User )) --> FirstView 
    interaction(( User )) --> SecondView 
    ```
    (Naturally, the user does not actually know which button belongs to what component.)

    Under the hood...
    ```mermaid 
    flowchart LR 

    MainController --> |updates| MainModel
    MainController --> |updates| MainView
    MainController --> |triggers model/view updates| FirstController
    MainController --> |triggers model/view updates| SecondController

    FirstController --> |informs| MainController
    SecondController --> |informs| MainController
    MainView --> |informs| MainController

    FirstController --> |updates| FirstModel
    FirstController --> |updates| FirstView
    SecondController --> |updates|SecondModel
    SecondController --> |updates|SecondView
    ```



# :door: The `main.py` entry-point: The one 'ugly place' in the code 

To run the application, we run the main python file: 

```shell
uv run python main.py
```

This 'entrypoint' into the application is also the one place where we now must take care of creating all Models, Views, Controllers, etc. 
However, given we already used our factory functions to inject the appropriate `Model` and `View` into their corresponding `Controller` , `main.py` actually just calls all these factory methods. The only exception is the main application component, which we should manually create here, and then inject all the created components. 

Naturally, this is also the place where we actually start the application. 

=== "Creating all the instances - The necessary coupling"

    ```python linenums="1"
    
    import sys 

    from PyQt6.QtWidgets import QApplication

    from app.first_component.first_component_factory import create_first_component
    from app.second_component.second_component_factory import create_second_component
    from app.main_app.main_controller import MainController, ComponentControllers 
    from app.main_app.main_model import MainModel
    from app.main_app.main_view import MainView

    def main() -> None:
        # must start with a QApplication before creating QWidgets
        app = QApplication(sys.argv)

        # Start setting up the main controller
        model = MainModel()
        view = MainView()
        view.show()

        # create the component controllers 
        components: ComponentControllers = {
            "first": create_first_component(placeholder=view.FirstView),
            "second": create_second_component(placeholder=view.SecondView)
        }
        controller = MainController(model, view, components=components)
        _ = controller

        # start the application
        app.exec()

    if __name__ == "__main__":
        main()
    ```

Thus, a project structure for a fully functional application: 

=== "Entry point allows to actually run the application"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_controller_protocols.py  

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_factory.py  

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component  
    :material-subdirectory-arrow-right:  :simple-python: main.py  





# :gear: User configuration 
At this point, we have a fully functioning application. However, we still want some additional quality-of-life improvements. 
Most notably, making it easy for the user to configure settings. 

:octicons-light-bulb-16: We want the user to be able to adjust values from a centralized location, but want components to remain decoupled. 


## :fontawesome-solid-user-gear: External representation: User adjust a single file 

The user simply adjusts values in the `config.json` file located in the root of this project. 
A nested dictionary is used to associate values to their respective components.

```json title="Excerpt from the configuration file" 
    
    // Settings for MainApp 
    "main": {
        "colors": {
            "unsaved_changes": "coral",
            "no_unsaved_changes": "white"
        },
        "keyboard_shortcuts": {
            "menu.file.open": "Ctrl+O",
            "menu.file.save": "Ctrl+S",
            "menu.file.save_as": "Ctrl+Shift+S",
            "next_trace": "Ctrl+Right",
            "previous_trace": "Ctrl+Left"
        },
        "default_file_paths": {
            "labels": "",
            "section_labels": ""
        }
    },
    // Settings specific to the Plot component 
    "plot": {
        "min_time": 0.0,
        "max_time": 3600.0,
        "min_height": -1.0,
        "max_height": 1.0
    },
```



## :material-database-cog: Internal representation: `Config` objects per component 
If we'd be to create a single object that holds all these values, we'd immediately undo all the hard work to keep things decoupled. In this scenario, the `MainController` (that would likely get this `HugeGodConfig`) would now know things about implementation details of the individual components and things are now coupled. To test the `MainController` we now need to mock values that really only matter for particular components. 

The solution is to introduce a `ConfigManager`, created in `main.py` that takes care of creating individual `Config` objects. 

=== "main.py"

    ```python linenums="1" title="using config manager"
    import sys 

    from PyQt6.QtWidgets import QApplication

    from app.first_component.first_component_factory import create_first_component
    from app.second_component.second_component_factory import create_second_component
    from app.main_app.main_controller import MainController, ComponentControllers 
    from app.main_app.main_model import MainModel
    from app.main_app.main_view import MainView
    from app.main_app.main_config import MainConfig
    from app.first_component.config import FirstConfig
    from app.second_component.config import SecondConfig
    
    # Only global constant that is in the code: The file name of the configuration file: 
    CONFIG_FILE = Path(__file__).parent / "config.json"

    def main() -> None:
        # must start with a QApplication before creating QWidgets
        app = QApplication(sys.argv)

        # Use the config file to instantiate the individual config objects. 
        config_manger = ConfigManager()
        config_manger.register("main", MainConfig)
        config_manger.register("first", FirstConfig)
        config_manger.register("second", SecondConfig)
        config_manger.load(CONFIG_FILE)

        main_config = config_manager.get_config("main")
        first_config = config_manager.get_config("first")
        second_config = config_manager.get_config("second")

        # Start setting up the main controller
        model = MainModel()
        view = MainView()
        view.show()

        # create the component controllers 
        components: ComponentControllers = {
            "first": create_first_component(placeholder=view.FirstView, config=first_config),
            "second": create_second_component(placeholder=view.SecondView, config=second_config)
        }
        controller = MainController(model, view, components=components, config=main_config)
        _ = controller

        # start the application
        app.exec()

    ```

=== "Adjustment to Controller instantiation"

    ```python linenums="1" title="using dependency injection" 

    # in app/component/component_controller.py: 

    class ComponentController:
        def __init__(self, model: ComponentModel, view: ComponentView, config: ComponentConfig): 
            self.model = model 
            self.view = view 
            self.config = config 

    # in app/main_app/main_controller.py 

    class MainController:
        def __init__(self, model: MainModel, view: MainView, components: ComponentControllers, config: MainConfig): 
            self.model = model 
            self.view = view 
            self.components = components
            self.config = config 

    # in app/component/component_factory.py: 
    def create_controller(placeholder: QWidget | None, config: ComponentConfig) -> ComponentController: 
        """Takes care of instantiating the Model and View, and injects those together with the Config (which is passed here as argument) in the Controller."""
        

    ```
Check `app/core/config_manager.py` for implementation details.  

    



Hence, now are project includes files to define configurations. 


=== "Including user-configurable settings in our example component"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: component_controller_protocols.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: main_config.py  

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_model.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_view.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_controller.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_factory.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: first_component_config.py  

    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component  
    :material-subdirectory-arrow-right:  :simple-python: main.py  
    :material-subdirectory-arrow-right:  :material-code-json: config.json  


# :octicons-file-directory-fill-16: Cross-cutting concerns in the `core/` directory 
To complete the project's architecture, we collected cross-cutting concerns into their own modules to reduce code duplication. 


=== "The `core` directory"

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder-open: core  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: config_management.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: keyboard_shortcuts.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :simple-python: error_handling.py  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  ... 

=== "Project structure including other source code" 

    :material-package: **project-root**    
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: core  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component

    :material-subdirectory-arrow-right:  :simple-python: main.py  
    :material-subdirectory-arrow-right:  :material-code-json: config.json  



:octicons-light-bulb-16: Any file in `app/` is allowed to import from `core/`, but not from anywhere else outside the subdirectory it is located in. 
=== "Allowed imports" 


    The entrypoint (`main.py`) is designed to connect all components
    ```mermaid
    flowchart TB 
    Main(main.py) --> |imports from| Core[core/]
    Main --> |imports from| ComponentController
    Main --> |imports from| MainAppController 
    ```

    All component controllers (**including the main app**) only get to import from modules inside the same directory, or import directly from `core/`

    ```mermaid
    flowchart TB
    ComponentController -->|imports from| ComponentModel
    ComponentController -->|imports from| ComponentView
    ComponentController -->|imports from| ComponentConfig
    ComponentController -->|imports from| ComponentFactory


    MainAppController -->|imports from| Core
    MainAppController -->|imports from| ... 

    ComponentController --> Core[core/] 
    MainAppController --> Core
    ```




## :exclamation: Error handling (`core/exceptions.py`)
- Defines custom `ApplicationError` exception.
- Other possible excepted cases of exceptions, e.g. `InvalidInputError`, are made subclasses thereof. 
- The `#!python @with_error_handling()` decorator to add error handling to the existing method (of a controller) without needing to adjust that function's body. 


!!! tip "Where to catch errors?"
    The natural place for the exception to be raised is the model (which is the place it will occur). 



```python linenums="1" title="Error handling in MainController" 
from app.core.state_variables import EventSeverity
# Examples of how the MainController handles errors
class Controller: 

    # To use the decorator, we need an instance method: 
    def handle_error(severity: EventSeverity, message:str) -> None: 
        """
        Code what should happen whenever an exception is caught.
        ---
        Typical solution is to let the view display a window with the error message.
        ---
        The decorator takes care of passing the caught exception's message to this function. 
        """ 
        self.view.open_message_box(severity, message)

    @with_error_handling(severity=EventSeverity.ERROR)
    def handle_file_name_selected(self, file_name: Path):
        """ If a wrong file name is selected, a message box with the error icon will appear """
    
    @with_error_handling(severity=EventSeverity.INFO)
    def handle_jump_to_trace(self, trace_id: str) -> None:
        """When the user enters something that cannot be parsed as a. valid integer value the message box with the info icon will appear. 
        ---

        The choice of severity type is purely subjective, and of course can easily be changed by changing the decorator argument's value.  
        
        """

```



## :keyboard: Keyboard shortcuts (`core/keyboard_shortcuts.py`)
- functions to assign, handle, and validate keyboard shortcuts
- Contract for controllers/views so shortcuts can be set in the config file. 
  


This module defines helper functions for assigning keyboard shortcuts to any of the menu bar actions or widget buttons. 

???+ tip "Configuring keyboard shortcuts"
    Any of the keyboard shortcuts are completely customizable. They are supplied as a dictionary in the config file. 

When using the following pattern, keyboard shortcuts can be made completely configurable. It makes use of the `ConfigManager` to prevent coupling between components. 


=== "1. Config file"
    Shortcuts are assigned on a per-component basis 

    ```JSON linenums="1"
    "main": {
        "keyboard_shortcuts": {
            "menu.file.open": "Ctrl+O",
            "menu.file.save": "Ctrl+S",
            "menu.file.save_as": "Ctrl+Shift+S",
            "next_trace": "Ctrl+Right",
            "previous_trace": "Ctrl+Left"
        },
    "label_assignment": {
        "keyboard_shortcuts": {
            "assign_label": "Ctrl+=",
            "unassign_label": "Ctrl+-",
            "next_label": "Ctrl+Up",
            "previous_label": "Ctrl+Down"
        }
    },
    ```

=== "2. Component Controller Template"
    The config needs the following method 

    ```python linenums="1"
    class ConfigWithShortcuts(Config, Protocol):
        """If configurations include keyboard shortcuts

        * implement the following API
        * only important for wiring things within the component's controller

        """

        def get_shortcuts(self) -> dict[Enum, str]:
            """dictionary of all keyboard shortcuts for this component"""
            ...
    ```

=== "3. Shortcut Items"
    For every component, we define an enumerated file to list all elements that except a keyboard shortcut 

    ```python linenums="1"
    from enum import Enum, auto 

    class MainShortcutID(Enum):
        """
        Defines logical identifiers for elements in the MainApp component that (can) get a shortcut assigned to them

        These enum values serve as the shared contract between:
        - `MainConfig.get_shortcuts()`, which provides the actual key sequences,
        - `MainView.get_shortcut_targets()`, which exposes the corresponding UI targets,
        - and `MainController.apply_config()`, which ties both together.

        By using Enum members instead of plain strings, we ensure:
        * auto-completion and refactor-safety
        * compile-time checking in IDEs / linters
        * an easy way to validate that every config key matches a defined shortcut
        """

        MENU_FILE_OPEN = auto()
        MENU_FILE_SAVE = auto()
        MENU_FILE_SAVE_AS = auto()
        NEXT_TRACE = auto()
        PREVIOUS_TRACE = auto()
    ```

    The View now exposes a mapping of these values to the appropriate widgets. 

    ```python linenums="1" 
    from app.main_app.main_shortcut_items import MainShortcutID as ShortcutID 

    class View(QWidget):
        def get_shortcut_targets(self) -> dict[ShortcutID, AcceptsShortCut]:
        """Dictionary with all Qt Actions and Widgets to which a shortcut should get assigned."""
        return {
            ShortcutID.MENU_FILE_OPEN: self.actionOpen,
            ShortcutID.MENU_FILE_SAVE: self.actionSave,
            ShortcutID.MENU_FILE_SAVE_AS: self.actionSaveAs,
            ShortcutID.NEXT_TRACE: self.NextTraceButton,
            ShortcutID.PREVIOUS_TRACE: self.previousTraceButton,
        }
    ```

    NOTE: `AcceptsShortCut` is simply an alias signifying those `PyQt` elements that can get a shortcut assigned to them. 



=== "4. Assignment" 
    When initializing a controller,  we call the helper function from the `keyboard_shortcuts.py` module

    ```python linenums="1"
    from app.core.keyboard_shortcuts import assign_shortcut

    class Controller: 

        def __init__(self, ...) -> None: 
            # previous parts shown

            # setup app using user's settings 
            self.apply_config()


        def apply_config(self) -> None:
            """apply settings to model(s) and view(s)"""

            # setup shortcuts
            shortcuts = self.config.get_shortcuts()
            shortcut_targets = self.view.get_shortcut_targets()
            for key in ShortcutID:
                assign_shortcut(shortcut_targets[key], shortcuts[key])
    ```





## :material-palette: Theming 
To create a consistent look throughout controllers.

- A base QSS-file is used as a template string
- Colors from the config file will populate the this file  

See individual component controllers for how theme (changes) gets applied. 



## :gear: User settings etc.
- Separates creation of the `Config` objects from usage 







# :bulb: How to create a new component? 
1. Create a new feature branch from the `develop` branch. 
2. Design your UI (using Qt designer)
   1. Design in Qt designer --> saves a `.ui` file 
   2. Run `scripts/compile_qt_ui_files.py` 
3. Programme component's Model, View, and Controller (logic). 
4. Setup communication with main application in main Controller. (*if needed*)
5. Add a placeholder widget in the main window by editing the designer file of the main View. (*if needed*)
6. Write the component's factory function. 
7. Register your component in `main.py`. 
8. Merge into `develop` branch &#x2192; now ready to test integration with other features developed in parallel, if any. 
9. Merge `develop` into `main` branch &#x2192; Triggers automated unit tests on `GitLab` &#x2192; release a new version & update release notes. 

???+ tip "optional steps"

    To make your component even cooler, you can later think of adding:

    :gear: **Config**  
    :keyboard: **Keyboard shortcuts** 


# :octicons-file-directory-fill-16: Remaining contents of repository 
Why are we not done just yet? We actually are, as far as the code itself goes. However, a proper repository is not complete without some additional contents. 

### :material-script-text: `scripts/` 
   - Code not part of the application. 
   - example: compiling UI-designer files.

### :simple-uv: Dependency management
* `pyproject.toml`
* `uv.lock`
* `.venv/` directory 

### :simple-git: Git settings 
* `.gitignore` 

### :simple-readthedocs: Documentation website you are currently viewing: 
* Markdowns in `docs/` 
* Configuration in `mkdocs.yml` 

### :simple-githubactions: Deployment & Integrated testing 
* `gitlab-ci.yml` 
* Automated testing when pushing to main branch. 
* Deploy the website  
* Bump the version (both as a git tag and in the uv pyproject.toml)
  



=== "Complete project tree" 

    :material-package: **project-root**    
    :material-subdirectory-arrow-right:  :material-folder: .venv      
    :material-subdirectory-arrow-right: :material-folder-open: app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: core  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component  
    :material-subdirectory-arrow-right: :material-folder-open: tests      
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: core  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: main_app  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: first_component  
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;:material-subdirectory-arrow-right:  :material-folder: second_component  
    :material-subdirectory-arrow-right:  :material-folder: scripts  
    :material-subdirectory-arrow-right:  :material-folder: docs      
    :material-subdirectory-arrow-right:  :material-folder: ci      
    :material-subdirectory-arrow-right:  :simple-python: main.py    
    :material-subdirectory-arrow-right:  :material-code-json: config.json  
    :material-subdirectory-arrow-right:  :material-file-document: mkdocs.yml    
    :material-subdirectory-arrow-right:  :simple-toml: pyproject.toml      
    :material-subdirectory-arrow-right:  :material-file-document: .python-version      
    :material-subdirectory-arrow-right:  :lock: uv.lock  
    :material-subdirectory-arrow-right:  :material-information: README.md  
    :material-subdirectory-arrow-right:  :material-gitlab: gitlab-ci.yml  
    :material-subdirectory-arrow-right:  :material-git: .gitignore  






