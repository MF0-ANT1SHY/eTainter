import subprocess
import os
import sys
from sys import argv
from pathlib import Path

from multiprocessing import Pool, cpu_count
from functools import partial

def analysis(timeoutLimit, binFile, outputDir):
    try:
        # Validate input files exist
        if not os.path.exists(binFile):
            raise FileNotFoundError(f"Binary file not found: {binFile}")
        
        # Create output directory if it doesn't exist
        Path(outputDir).mkdir(parents=True, exist_ok=True)
        
        cmd = [
            ".conda/bin/python", "./bin/findbug.py",
            "-f", binFile,
        ]
        print(f"Executing command: {' '.join(cmd)}")
        
        # Set up log file path
        log_file_path = os.path.join(outputDir, "log.txt")
        
        # Execute the command with output redirection
        with open(log_file_path, 'w') as log_file:
            process = subprocess.run(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=timeoutLimit + 3,  # Add buffer to process timeout
                text=True
            )
        
        # Read the log file content
        with open(log_file_path, 'r') as log_file:
            log_content = log_file.read()
        
        # Return results
        return {
            "success": process.returncode == 0,
            "return_code": process.returncode,
            "log_file": log_file_path,
            "log_content": log_content,
            "output_dir": outputDir
        }
        
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Process timed out",
            "timeout": True,
            "output_dir": outputDir
        }
    
    except FileNotFoundError as e:
        return {
            "success": False,
            "error": str(e),
            "output_dir": outputDir
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "output_dir": outputDir
        }

def process_project_json_files(base_dir):
    base_path = Path(base_dir)
    # 仅扫描给定目录中的 *.project.json 文件（不递归）
    project_json_files = [p for p in base_path.iterdir() if p.is_file() and p.suffix.lower() == ".json"]
    return project_json_files

def run_analysis_task(task, timeout_limit, output_dir):
    bin_file, output_subdir = task
    analysis(
        timeout_limit,
        binFile=str(bin_file),
        outputDir=str(Path(output_dir) / output_subdir)
    )

if __name__ == "__main__":
    base_dir = argv[1]
    output_dir = argv[2] if len(argv) > 2 else "./eTainter_findbug_output"
    timeoutLimit = int(argv[3]) if len(argv) > 3 else 120  # Default to 120 seconds

    project_json_files = process_project_json_files(base_dir)

    taskQueue = []
    for f in project_json_files:
        outputSubdir = f.stem  # 文件名去掉扩展名
        taskQueue.append((f, outputSubdir))

    if not taskQueue:
        print(f"No .project.json files found in directory: {base_dir}", file=sys.stderr)
        sys.exit(1)

    worker_func = partial(run_analysis_task, timeout_limit=timeoutLimit, output_dir=output_dir)
    
    with Pool(processes=cpu_count()) as pool:
        pool.map(worker_func, taskQueue)