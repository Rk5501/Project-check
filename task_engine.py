import subprocess
import sys
import traceback
from typing import List
import datetime
import os
import black
import itertools
import tempfile
import textwrap


async def run_python_code(code: str, libraries: List[str], folder: str = "uploads", python_exec = sys.executable) -> dict:

    # Create a unique work directory per run
    work_dir = os.path.join(folder, f"job_")
    os.makedirs(work_dir, exist_ok=True)

    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # File where we’ll log execution results
    log_file_path = os.path.join(folder, "execution_result.txt")

    def log_to_file(content: str):
        """Append timestamped content to the log file."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_file_path, "a", encoding="utf-8") as log_file:
            log_file.write(f"\n[{timestamp}]\n{content}\n{'-'*40}\n")

    # Step 1: Check required libraries (skip installation in serverless environment)
    for lib in libraries:
        try:
            # check if already installed
            check_cmd = [
                python_exec,
                "-c",
                f"import importlib.util, sys; "
                f"sys.exit(0) if importlib.util.find_spec('{lib}') else sys.exit(1)"
            ]
            result = subprocess.run(check_cmd)
            if result.returncode != 0:  # not installed
                # In serverless environment, we can't install packages dynamically
                # Log the missing library but continue execution
                log_to_file(f"⚠️ Library '{lib}' not available in serverless environment")
            else:
                log_to_file(f"✅ {lib} already available.")
        except Exception as install_error:
            # Don't fail completely if library check fails in serverless environment
            log_to_file(f"⚠️ Could not check library '{lib}': {install_error}")
            # Continue execution instead of returning error

    # Step 2: Run the code in the isolated venv
    try:
        try:
            code_formatted = black.format_str(code, mode=black.Mode())
        except Exception:
            code_formatted = code  # fallback if formatting fails

        log_to_file(f"📜 Executing Code:\n{code_formatted}")

        # Save code to job-specific file
        code_file_path = os.path.join(work_dir, "script.py")
        with open(code_file_path, "w") as f:
            f.write(code)

        # Run in subprocess with chosen venv
        result = subprocess.run(
            [python_exec, code_file_path],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            success_message = f"✅ Code executed successfully:\n{result.stdout}"
            log_to_file(success_message)
            return {"code": 1, "output": result.stdout}
        else:
            error_message = f"❌ Execution error:\n{result.stderr}"
            log_to_file(error_message)
            return {"code": 0, "output": error_message}

    except Exception as e:
        error_details = f"❌ Error during code execution:\n{traceback.format_exc()}"
        log_to_file(error_details)
        return {"code": 0, "output": error_details}
