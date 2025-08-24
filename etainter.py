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
        
        # Construct the Throbber command
        cmd = [
            ".conda/bin/python", "./bin/analyzer.py",
            "-f", binFile,
            "-b",
        ]
        
        # Set up log file path
        log_file_path = os.path.join(outputDir, "log.txt")
        
        # Execute the command with output redirection
        with open(log_file_path, 'w') as log_file:
            process = subprocess.run(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                timeout=timeoutLimit + 3, # Add buffer to process timeout
                text=True,
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

def process_cve_directories(base_dir):
    base_path = Path(base_dir)
    cve_dirs = [d for d in base_path.iterdir() if d.is_dir() and d.name.startswith("CVE")]
    
    return cve_dirs

def run_analysis_task(task, timeout_limit, output_dir):
    bin_file, output_subdir = task
    analysis(
        timeout_limit,
        binFile=str(bin_file),
        outputDir=str(Path(output_dir) / output_subdir)
    )

if __name__ == "__main__":
    base_dir = argv[1]
    output_dir = argv[2] if len(argv) > 2 else "../etainter_output"
    timeoutLimit = int(argv[3]) if len(argv) > 3 else 24*60*60 # Default to 24 hours

    projectDirs = process_cve_directories(base_dir)
    taskQueue = []
    for dir in projectDirs:
        binFile = dir / "Instance.bin-runtime" # Attention: etainter takes runtime binaries instead of default binaries
        outputDir = dir.name
        taskQueue.append((binFile, outputDir))

    worker_func = partial(run_analysis_task, timeout_limit=timeoutLimit, output_dir=output_dir)
    
    with Pool(processes=cpu_count()) as pool:
        pool.map(worker_func, taskQueue)