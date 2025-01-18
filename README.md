### **YAML to Zip**

#### **What?**
Converts a YAML file into a folder structure and zips it. Built it because I couldn’t find anything like this online (probably didn’t search enough). Needed it to automate some repetitive tasks.

#### **Why?**
- Automates folder/file creation from YAML.
- Saves time. That’s it.

#### **How?**
1. Upload a YAML file.
2. Get a zip with the folder structure.

#### **Run**
1. Install:
   ```bash
   pip install flask pyyaml
   ```
2. Run:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000`.

#### **YAML Example**
```yaml
project:
  src:
    - file: "project/src/main.py"
    - file: "project/src/utils.py"
  docs:
    - file: "project/docs/README.md"
```

#### **License**
Do whatever. Not my problem.