from flask import Flask, request, send_file, render_template
import os
import yaml
import zipfile
from io import BytesIO

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def create_structure_from_yaml(yaml_content, base_path):
    """
    Create folder and file structure from YAML content.
    """
    structure = yaml.safe_load(yaml_content)
    if not isinstance(structure, dict):
        raise ValueError("Invalid YAML structure. Expected a dictionary.")

    for path, items in structure.items():
        if isinstance(items, dict):
            for subfolder, subitems in items.items():
                if isinstance(subitems, list):
                    for item in subitems:
                        if isinstance(item, dict) and "file" in item:
                            file_path = item["file"]
                            full_file_path = os.path.join(base_path, file_path)
                            os.makedirs(os.path.dirname(full_file_path), exist_ok=True)
                            with open(full_file_path, "w") as f:
                                f.write(f"# {os.path.basename(file_path)}\nThis is a placeholder for {os.path.basename(file_path)}.")
                        else:
                            raise ValueError(f"Invalid item in {path}/{subfolder}. Expected a dictionary with a 'file' key.")
                else:
                    raise ValueError(f"Invalid structure in {path}/{subfolder}. Expected a list of files.")
        else:
            raise ValueError(f"Invalid structure in {path}. Expected a dictionary of folders.")


def zip_folder(folder_path, yaml_file_path):
    """
    Zip the folder and return the zip file as bytes.
    """
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zipf:
        zipf.write(yaml_file_path, os.path.basename(yaml_file_path))

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arcname)
    memory_file.seek(0)
    return memory_file


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "yaml_file" not in request.files:
            return "No file uploaded", 400

        file = request.files["yaml_file"]

        if file.filename == "":
            return "No file selected", 400

        yaml_file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(yaml_file_path)

        with open(yaml_file_path, "r") as f:
            yaml_content = f.read()

        temp_folder = os.path.join(app.config["UPLOAD_FOLDER"], "temp_structure")
        if os.path.exists(temp_folder):
            for root, dirs, files in os.walk(temp_folder, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        else:
            os.makedirs(temp_folder)

        try:
            create_structure_from_yaml(yaml_content, temp_folder)
        except ValueError as e:
            return str(e), 400
        zip_bytes = zip_folder(temp_folder, yaml_file_path)

        for root, dirs, files in os.walk(temp_folder, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_folder)
        os.remove(yaml_file_path)

        return send_file(
            zip_bytes,
            mimetype="application/zip",
            as_attachment=True,
            download_name="structure.zip",
        )

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)