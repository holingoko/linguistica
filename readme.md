## Holingoko is a tool for language learners and translators:
https://holingoko.github.io/linguistica/
## Build From Source:
Instructions below assume git and python (version >= 3.12) are installed.
### Windows:
```
git clone https://github.com/holingoko/linguistica.git
cd linguistica
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python -m nuitka Linguistica.py --output-dir=build --enable-plugin=pyside6 --include-data-dir=resources=resources --standalone --show-scons --windows-console-mode=disable --windows-icon-from-ico=resources\images\icon.png
```
### Mac OS:
```
git clone https://github.com/holingoko/linguistica.git
cd linguistica
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
python3 -m nuitka Linguistica.py --output-dir=build --enable-plugin=pyside6 --include-data-dir=resources=resources --standalone --show-scons --macos-create-app-bundle --macos-app-icon=resources/images/icon.png
```
## Add New Application Language:
Language translation (.po) files are located under:

https://github.com/holingoko/linguistica/resources/languages

Please feel free to create pull requests to add new language translations to 
this directory.

Users can also add translations for additional languages without having to 
modify the source code of the application by moving language translation files 
to the directory set via:

Settings... > Application > User-Added Languages Directory

Note that {} in translations indicates a word or phrase will be substituted in 
at runtime, and numbers within curly braces {0}, {1}, etc. indicate order of 
substitutions. Order will likely need to be reversed for right-to-left languages.
## Add New Application Theme:
Theme (Qt style sheet, .qss) files are located under:

https://github.com/holingoko/linguistica/resources/themes

Please feel free to create pull requests to add new themes to this directory.

Users can also add new themes without having to modify the source code of the 
application by moving theme files to the directory set via:

Settings... > Application > User-Added Themes Directory

Note that these are not normal Qt style sheets as they have been set up as 
python format strings to allow the user to change the font independent of the 
style. It is recommended to leave the font substitution lines unchanged.
Otherwise, font choices made by the user in settings will be overridden by the 
theme-specified font.
## Report Issue:
Aa
