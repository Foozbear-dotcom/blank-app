## Start of a session##

pkill -f streamlit
streamlit run streamlit_app.py

## when adding a new feature and it doesnt break##

git add .
git commit -m ["Version 4.0.0f - Move fixture validation into module"]
git push

## CHecking Status of The Codespace##

git status
git branch

## Create a new module

1. Create the file in /modules
2. Import the function into streamlit_app.py
3. Replace existing code with the function call
4. Test
5. Commit

