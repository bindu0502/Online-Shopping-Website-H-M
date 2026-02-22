# 🚀 GitHub Push Guide - Project149

## Step-by-Step Guide to Push Your Project to GitHub

---

## 📋 Prerequisites

Before pushing to GitHub, make sure you have:
- ✅ Git installed on your computer
- ✅ GitHub account created
- ✅ Git configured with your name and email

---

## 🔧 Step 1: Configure Git (First Time Only)

Open your terminal/command prompt and run:

```bash
# Set your name
git config --global user.name "Your Name"

# Set your email (use your GitHub email)
git config --global user.email "your.email@example.com"

# Verify configuration
git config --list
```

---

## 📁 Step 2: Create .gitignore File

First, let's make sure we don't push sensitive or unnecessary files.

**Check if `.gitignore` exists:**
```bash
# Windows
dir .gitignore

# Linux/Mac
ls -la .gitignore
```

**If it doesn't exist, create it with this content:**

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Database
*.db
*.sqlite
*.sqlite3
project149.db

# Environment variables
.env
.env.local
.env.*.local

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Node modules (frontend)
frontend/node_modules/
frontend/dist/
frontend/build/

# ML Models (optional - these are large)
models/*.pkl
Project149/models/*.pkl

# Datasets (optional - these are large)
datasets/
Project149/datasets/
*.csv

# Images (optional - these are large)
Project149/datasets/images_128_128/
images/

# Jupyter Notebooks checkpoints
.ipynb_checkpoints/

# Cache
.cache/
*.cache

# Test coverage
htmlcov/
.coverage
.pytest_cache/

# Temporary files
*.tmp
*.temp
```

---

## 🎯 Step 3: Initialize Git Repository

In your project root directory:

```bash
# Navigate to your project folder
cd C:\Users\polis\OneDrive\Desktop\Project149_Main

# Initialize git repository
git init

# Check status
git status
```

---

## 📦 Step 4: Stage Your Files

```bash
# Add all files (respecting .gitignore)
git add .

# Or add specific files/folders
git add src/
git add frontend/
git add main.py
git add requirements.txt
git add README.md

# Check what will be committed
git status
```

---

## 💾 Step 5: Create First Commit

```bash
# Create your first commit
git commit -m "Initial commit: E-commerce platform with ML recommendations"

# Or more detailed commit message
git commit -m "feat: Complete e-commerce platform with ML-powered recommendations

- Full-stack application (React + FastAPI)
- 3 recommendation systems (ML, similarity, cold-start)
- AI-powered search (Google Gemini)
- 105k+ products catalog
- User authentication (JWT)
- Shopping cart, wishlist, orders
- Docker deployment ready"
```

---

## 🌐 Step 6: Create GitHub Repository

### Option A: Via GitHub Website

1. Go to https://github.com
2. Click the **"+"** icon (top right) → **"New repository"**
3. Fill in details:
   - **Repository name**: `project149-ecommerce` (or your preferred name)
   - **Description**: "Full-stack e-commerce platform with ML-powered recommendations"
   - **Visibility**: Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
4. Click **"Create repository"**

### Option B: Via GitHub CLI (if installed)

```bash
gh repo create project149-ecommerce --public --source=. --remote=origin
```

---

## 🔗 Step 7: Connect Local Repository to GitHub

After creating the repository on GitHub, you'll see commands like these:

```bash
# Add remote repository
git remote add origin https://github.com/YOUR_USERNAME/project149-ecommerce.git

# Verify remote
git remote -v

# If you need to change the remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/project149-ecommerce.git
```

**Replace `YOUR_USERNAME` with your actual GitHub username!**

---

## 🚀 Step 8: Push to GitHub

```bash
# Push to GitHub (first time)
git push -u origin main

# Or if your default branch is 'master'
git push -u origin master

# If you get an error about branch name, rename it:
git branch -M main
git push -u origin main
```

### If You Get Authentication Error:

**For HTTPS (recommended):**
1. GitHub no longer accepts passwords
2. You need a **Personal Access Token (PAT)**

**Create a PAT:**
1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name: "Project149 Push"
4. Select scopes: `repo` (full control)
5. Click "Generate token"
6. **Copy the token immediately** (you won't see it again!)

**Use the token as password:**
```bash
# When prompted for password, paste your PAT
git push -u origin main
```

**Or use SSH (alternative):**
```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your.email@example.com"

# Add to GitHub: Settings → SSH and GPG keys → New SSH key
# Then change remote to SSH
git remote set-url origin git@github.com:YOUR_USERNAME/project149-ecommerce.git
```

---

## ✅ Step 9: Verify Upload

1. Go to your GitHub repository URL
2. Refresh the page
3. You should see all your files!

---

## 📝 Step 10: Create a Good README.md

Create or update `README.md` in your project root:

```markdown
# 🛍️ Project149 - E-Commerce Platform with ML Recommendations

Full-stack e-commerce platform with AI-powered personalized recommendations.

## 🎯 Features

- **105,542 products** catalog
- **3 recommendation systems**: ML-based (LightGBM), Similarity-based, Cold-start
- **AI-powered search** using Google Gemini
- **User authentication** with JWT
- **Shopping cart & wishlist**
- **Order management**
- **Real-time recommendations**

## 🛠️ Tech Stack

**Frontend:**
- React 19
- Vite
- TailwindCSS
- Axios

**Backend:**
- FastAPI
- SQLAlchemy
- LightGBM
- Google Gemini AI

**Database:**
- SQLite (dev) / PostgreSQL (prod)

**DevOps:**
- Docker
- Docker Compose

## 🚀 Quick Start

### Using Docker (Recommended)

\`\`\`bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/project149-ecommerce.git
cd project149-ecommerce

# Start with Docker Compose
docker-compose up -d

# Access application
# Frontend: http://localhost
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
\`\`\`

### Manual Setup

**Backend:**
\`\`\`bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn main:app --reload
\`\`\`

**Frontend:**
\`\`\`bash
cd frontend
npm install
npm run dev
\`\`\`

## 📚 Documentation

- [Complete Project Guide](PROJECT_COMPLETE_GUIDE.md)
- [Tech Stack Details](TECH_STACK.md)
- [API Documentation](API_COMPLETE.md)
- [Deployment Guide](DEPLOY.md)

## 🎓 Project Highlights

- **Full-stack development** (React + FastAPI)
- **Machine learning** (LightGBM, 50+ features)
- **AI integration** (Google Gemini)
- **Production-ready** (Docker, CI/CD)
- **Comprehensive testing**

## 📄 License

MIT License

## 👤 Author

Your Name - [GitHub](https://github.com/YOUR_USERNAME)
```

---

## 🔄 Future Updates

After making changes to your code:

```bash
# Check what changed
git status

# Stage changes
git add .

# Commit with message
git commit -m "feat: Add refresh button to products page"

# Push to GitHub
git push
```

---

## 🎨 Optional: Add GitHub Actions Badge

Add to your README.md:

```markdown
![CI/CD](https://github.com/YOUR_USERNAME/project149-ecommerce/workflows/CI/badge.svg)
```

---

## 📊 Optional: Add Project Stats

Add to README.md:

```markdown
## 📊 Project Stats

- **Lines of Code**: ~15,000+
- **Files**: 150+
- **Languages**: Python, JavaScript
- **Commits**: Check GitHub
- **Contributors**: 1 (You!)
```

---

## 🚨 Common Issues & Solutions

### Issue 1: "fatal: not a git repository"
**Solution:**
```bash
git init
```

### Issue 2: "remote origin already exists"
**Solution:**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/repo.git
```

### Issue 3: "failed to push some refs"
**Solution:**
```bash
git pull origin main --rebase
git push origin main
```

### Issue 4: Large files error
**Solution:**
```bash
# Remove large files from git
git rm --cached project149.db
git rm --cached -r datasets/

# Add to .gitignore
echo "project149.db" >> .gitignore
echo "datasets/" >> .gitignore

# Commit and push
git commit -m "Remove large files"
git push
```

---

## 🎯 Best Practices

1. **Commit Often**: Make small, focused commits
2. **Write Good Messages**: Use clear commit messages
3. **Use Branches**: Create branches for new features
4. **Pull Before Push**: Always pull latest changes first
5. **Review Changes**: Use `git diff` before committing

---

## 📱 Useful Git Commands

```bash
# View commit history
git log --oneline

# View changes
git diff

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Discard local changes
git checkout -- filename

# Create new branch
git checkout -b feature-name

# Switch branches
git checkout main

# Merge branch
git merge feature-name

# Delete branch
git branch -d feature-name
```

---

## 🎉 Success!

Your project is now on GitHub! 🚀

**Next Steps:**
1. ✅ Add a good README.md
2. ✅ Add LICENSE file
3. ✅ Set up GitHub Pages (optional)
4. ✅ Enable GitHub Actions (optional)
5. ✅ Share your repository!

---

**Repository URL Format:**
`https://github.com/YOUR_USERNAME/project149-ecommerce`

**Clone Command for Others:**
```bash
git clone https://github.com/YOUR_USERNAME/project149-ecommerce.git
```

---

Good luck with your GitHub repository! 🎊
