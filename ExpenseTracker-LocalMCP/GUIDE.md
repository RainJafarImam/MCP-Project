# How to Push ExpenseTracker Changes to GitHub

## Steps

### 1. Go to your project folder
```bash
cd D:\MCP\Project
```

### 2. Clone the repo
```bash
git clone https://github.com/RainJafarImam/MCP-Project.git
```

### 3. Copy your local changes into the repo
```bash
xcopy /E /I D:\MCP\Project\ExpenseTracker-LocalMCP\* D:\MCP\Project\MCP-Project\ExpenseTracker-LocalMCP\
```

### 4. Go into the repo
```bash
cd D:\MCP\Project\MCP-Project
```

### 5. Stage the changes
```bash
git add ExpenseTracker-LocalMCP/
```

### 6. Commit
```bash
git commit -m "update ExpenseTracker"
```

### 7. Push to GitHub
```bash
git push origin main
```
