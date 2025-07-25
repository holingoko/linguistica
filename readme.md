... Holingoko is an application for language learners and translators.
## <a href="http://www.holingoko.github.io/linguistica.com/pages/download">Download Application</a>
### or
## Build From Source (Windows):
```
git clone https://github.com/holingoko/linguistica.git
cd linguistica
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m nuitka Linguistica.py --enable-plugin=pyside6 --include-data-dir=resources=resources --standalone --show-scons --windows-console-mode=disable --windows-icon-from-ico=resources\images\icon.png
```
## Build From Source (Mac OS):
```
git clone https://github.com/holingoko/linguistica.git
cd linguistica
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 -m nuitka Linguistica.py --enable-plugin=pyside6 --include-data-dir=resources=resources --standalone --show-scons --macos-create-app-bundle --macos-app-icon=resources/images/icon.png
```
