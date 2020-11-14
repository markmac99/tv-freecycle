#
# package the GUI 
#

compress-archive -literalpath editorGUI.py, createJsFromCSV.py, tsconfig.ini, fsconfig.ini, inuse.txt, FSMaint.ps1, TSMaint.ps1, requirements.txt -destinationpath .\fsGUI.zip -update
