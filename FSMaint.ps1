#
# maintain Freecycle Entries
#
set-location $PSScriptRoot
git stash
git pull
git stash apply
python editorGUI.py fsconfig.ini
