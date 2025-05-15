@echo off
cd /d "C:\Users\harsh\OneDrive\Desktop\Drexel\Volunteert\Detection_Pipeline"
git add .
git diff-index --quiet HEAD || git commit -m "Auto-commit on %date% %time%"
git commit -m "Auto-commit on %date% %time%"
git push origin master
