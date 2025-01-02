#
# maintain Toycycle Entries
#
set-location $PSScriptRoot
conda activate freecycle
git stash
git pull
git stash apply
python editorGUI.py tsconfig.ini
