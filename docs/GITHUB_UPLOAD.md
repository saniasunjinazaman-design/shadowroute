# Upload This Project to GitHub

1. Create a new empty repository on GitHub. Do not add a second README if this package already includes one.
2. Extract the ZIP into a local folder and open a terminal in that folder.
3. Review the files before publishing. Keep `.env`, `users.json`, personal credentials, and private logs out of the repository. The supplied `.gitignore` excludes common local data.
4. Initialize and push the repository:

   ```bash
   git init
   git add .
   git status
   git commit -m "Add Project Shadow Route lab"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

Replace the remote URL with the address of the repository you created. Never paste a password or access token into the source files.
