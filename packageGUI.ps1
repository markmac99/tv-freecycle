#
# package the GUI 
#

compress-archive -literalpath editorGUI.py, createJsFromCSV.py, ddbTables.py, tsconfig.ini, fsconfig.ini, FSMaint.ps1, TSMaint.ps1, requirements.txt -destinationpath .\fsGUI.zip -update
