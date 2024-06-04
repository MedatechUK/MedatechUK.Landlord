# MedatechUK.Landlord

## label.py

The `label.py` file contains three main classes: `BlankLabel`, `labelDef` and `mkBarcode`.

### BlankLabel

The `BlankLabel` class is used to create a simple module with specified attributes. It has a single method, `create_module`, which takes a `spec` parameter.

The `create_module` method creates a new module of type `spec.name` with the attributes `specs`, `border`, `debug`, and `testdata`.

- `specs`: This attribute is initially set to `None`.
- `border`: This attribute is a boolean that is initially set to `False`.
- `debug`: This attribute is a boolean that is initially set to `False`.
- `testdata`: This attribute is a dictionary that contains test data for the module. It includes QR code data, a count, and six parameters (`PAR1` to `PAR6`) each containing a string "Test Data X" where X is the parameter number.

### labelDef

The `labelDef` class is responsible for managing label definitions. It has a constructor that sets up the working directory and loads a label template.

The constructor takes an optional `file` parameter. If no file is provided, it creates a new file with a unique name and loads the BlankLabel template. 

The working directory is set to a subdirectory named "pyLabels" relative to the location of the script that called this class. The `labelDef` class uses the `inspect` module to determine the calling script's location, ensuring that the working directory is always correctly set relative to the calling script, regardless of where the script is run from.

### mkBarcode

The `mkBarcode` class is responsible for creating barcodes. The mkBarcode class is used to generate barcodes and QR codes. It is utilized by both Landlord.py and mkLabel.py. The class takes in three arguments during initialization: a Label object, a dictionary obj containing data for the label, and a unique identifier uuid.

The class has two attributes: ParentDir and WorkingDir. ParentDir is the parent directory path (pyLabels), and WorkingDir is the working directory path (/tmp).

The __init__ method initializes the mkBarcode class. It first gets the caller's frame and sets the parent directory. It then sets the working directory and creates it if it doesn't exist.

The method then iterates through the shapes in the label. For each shape, it checks if the shape has a name and a format string. If it does, it replaces placeholders in the format string with data from the obj dictionary.

If the shape is a barcode, it checks the encoding. If the encoding is "QRCODE", it replaces the placeholder with the QR code data, creates the QR code, and saves the image. If the encoding is not "QRCODE", it gets the barcode class, creates the barcode, and saves the image. In both cases, it adds the image path to the list of files to be cleaned up.

If an error occurs during the barcode creation, it sets the path to an empty string. If the shape is not a barcode, it sets the text of the shape to the format string.

If the shape does not have a format string, it sets the path to the filename in the parent directory.

If an error occurs during the initialization of the mkBarcode class, it prints the error.

## UI.py
The UI.py file contains several classes that are used in the Landlord GUI application. Here's a brief description of each class:

### MyLabel
The MyLabel class is a custom QLabel widget with additional signals and functionality. It extends the QLabel widget and adds the following features:

Signals for wheel events, mouse clicks, mouse movement, mouse drops, and right clicks.
- Ability to set and get the current pixmap.
- Scaling the pixmap to fit the label size.
- Accepting drops and handling drag events.
- Converting label coordinates to pixmap coordinates.
- Handling mouse press, move, and release events.

The class emits signals for various events such as wheel rotation, mouse clicks, mouse movement, mouse drops, and right clicks. It also provides methods to set and get the current pixmap, scale the pixmap to fit the label size, accept drops and handle drag events, convert label coordinates to pixmap coordinates, and handle mouse press, move, and release events.

### MyForm
This class represents a custom form widget. It inherits from the QMainWindow class and provides additional functionality for handling key press and close events. It emits a signal when a key press event occurs and when the form is being closed. It also has a boolean flag indicating whether the form is being closed.

## icons.py
Contains icon resources.