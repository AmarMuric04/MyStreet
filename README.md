# Project Setup Instructions

## 1.

### If you're accessing from GitHub:

Clone this repository to your local machine using Git:

```bash
git clone ...
cd MyStreet_template
```

### If you're accessing from a Zipped file:

Unzip the file and open the "MyStreet_template" folder in VS Code, or whatever text editor you use.

## 2. Create a Virtual Environment

### Windows:

```bash
python -m venv venv
```

### macOS/Linux:

```bash
python3 -m venv venv
```

## 3. Activate the Virtual Environment

### Windows:

```bash
venv\\Scripts\\activate
```

### macOS/Linux:

```bash
source venv/bin/activate
```

Once activated, your terminal prompt should change to show the virtual environment name (e.g., `(venv)`).

## 4. Install Dependencies

With the virtual environment activated, install all the required dependencies:

```bash
pip install -r requirements.txt
```

Sit there for 2/5/10 minutes, don't worry if there's no UI, as long as it says installing ... It's installing.
When it's done, it will say "Successfully installed ..."

## 5. Run the backend

You can run the Flask - MongoDB backend by doing:

### Windows:

```bash
python backend/app.py
```

### macOS/Linux:

```bash
python3 backend/src/microblog.py
```

## 6. Open up a new terminal.

## 7. Run the venv!

```bash
source venv/bin/activate
```

## 8. Run the frontend

### Windows:

```bash
python frontend/src/app.py
```

### macOS/Linux:

```bash
python frontend/src/app.py
```

## 7. Enjoy the prototype!

---
