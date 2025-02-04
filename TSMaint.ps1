#
# maintain Toycycle Entries
#
set-location $PSScriptRoot
conda activate freecycle
git stash
git pull
git stash apply
$env:AWS_PROFILE=$null
python editorGUI.py tsconfig.ini
