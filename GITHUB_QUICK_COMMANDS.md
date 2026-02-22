# ⚡ GitHub Quick Commands Reference

## 🚀 First Time Setup (Do Once)

```bash
# 1. Navigate to your project
cd C:\Users\polis\OneDrive\Desktop\Project149_Main

# 2. Initialize git
git init

# 3. Configure git (replace with your info)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# 4. Add all files
git add .

# 5. Create first commit
git commit -m "Initial commit: E-commerce platform with ML recommendations"

# 6. Create repository on GitHub (via website)
# Go to github.com → New Repository → project149-ecommerce

# 7. Connect to GitHub (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/project149-ecommerce.git

# 8. Push to GitHub
git branch -M main
git push -u origin main
```

---

## 🔄 Daily Workflow (After Changes)

```bash
# 1. Check what changed
git status

# 2. Add changes
git add .

# 3. Commit with message
git commit -m "feat: Add new feature"

# 4. Push to GitHub
git push
```

---

## 📝 Good Commit Messages

```bash
# Feature
git commit -m "feat: Add refresh button to products page"

# Bug fix
git commit -m "fix: Resolve login authentication issue"

# Documentation
git commit -m "docs: Update README with deployment instructions"

# Style/formatting
git commit -m "style: Format code with prettier"

# Refactor
git commit -m "refactor: Improve recommendation algorithm"

# Test
git commit -m "test: Add unit tests for cart API"
```

---

## 🆘 Common Issues

### Issue: Large files error

```bash
# Remove large files
git rm --cached project149.db
git rm --cached -r datasets/

# Commit removal
git commit -m "Remove large files"
git push
```

### Issue: Authentication failed

```bash
# Use Personal Access Token (PAT) instead of password
# Create PAT: GitHub → Settings → Developer settings → Personal access tokens
# Use PAT as password when prompted
```

### Issue: Remote already exists

```bash
# Remove old remote
git remote remove origin

# Add new remote
git remote add origin https://github.com/YOUR_USERNAME/project149-ecommerce.git
```

---

## 🎯 Essential Commands

```bash
# View status
git status

# View commit history
git log --oneline

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename

# Pull latest changes
git pull origin main

# Clone repository
git clone https://github.com/YOUR_USERNAME/project149-ecommerce.git
```

---

## ✅ Checklist Before Pushing

- [ ] `.gitignore` file created
- [ ] Large files excluded (database, datasets, models)
- [ ] `.env` file not included
- [ ] README.md created
- [ ] Code tested locally
- [ ] Commit message is clear
- [ ] Remote repository created on GitHub

---

## 🔗 Your Repository URL

```
https://github.com/YOUR_USERNAME/project149-ecommerce
```

Replace `YOUR_USERNAME` with your actual GitHub username!

---

**Need help? Check `GITHUB_PUSH_GUIDE.md` for detailed instructions!**
