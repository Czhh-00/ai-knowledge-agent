# AI Knowledge Agent

用于学习 Python 后端与 AI 应用开发的项目。学习路线见 [LEARNING_PLAN.md](LEARNING_PLAN.md)。

## Python 环境

- Python：3.12.10
- 项目虚拟环境：`.venv`
- 应用：FastAPI + Uvicorn
- 测试工具：pytest + HTTPX

以下命令在项目根目录的 PowerShell 中执行。直接使用虚拟环境中的 Python，无需先激活环境。

## 启动开发服务

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

启动后访问：

- 接口文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

健康检查应返回 `{"status":"ok"}`。按 `Ctrl+C` 停止服务。

## 可选：激活虚拟环境

```powershell
.\.venv\Scripts\Activate.ps1
python --version
python -m uvicorn app.main:app --reload
```

若 PowerShell 提示禁止执行脚本，可使用上面的完整 Python 路径启动，无需调整执行策略。激活后执行 `deactivate` 可退出环境。

## 在新电脑上重建环境

先安装 Python 3.12，再执行：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

`requirements.txt` 保存本次环境中安装的直接与间接依赖版本。`.venv` 已被 Git 忽略，不应提交到仓库。

## 检查环境与运行测试

```powershell
.\.venv\Scripts\python.exe -c "import sys; print(sys.executable); print(sys.version)"
.\.venv\Scripts\python.exe -m pip check
```

在项目根目录运行接口测试（需要本机 PostgreSQL 运行，且 `.env` 已配置）：

```powershell
.\.venv\Scripts\python.exe -m pytest
```

测试通过 `tests/conftest.py` 为每个用例创建独立的临时知识库表，并在结束后回滚，不修改项目已有的知识库记录。覆盖创建、查询、修改、删除、参数校验和记录不存在时的 404 响应。

## VS Code

已配置项目解释器为 `.venv\Scripts\python.exe`。若编辑器仍选中了全局 Python，运行 `Python: Select Interpreter`，选择本项目的 `.venv`。
