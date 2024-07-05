from flask import Flask, render_template
import os

app = Flask(__name__, 
            template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), 'app', 'templates')))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    print(f"Current working directory: {os.getcwd()}")
    print(f"Template folder: {app.template_folder}")
    print(f"Templates exist: {os.path.exists(app.template_folder)}")
    print(f"Contents of template folder: {os.listdir(app.template_folder)}")
    app.run(debug=True)