"""
Example of how the main LogGenerator class could be refactored
to use the individual log generator classes.
"""

import os
import sys
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from log_generators import LOG_GENERATORS


class LogGenerator:
    def __init__(self, output_file: str = None, lines_per_format: int = 5000, pause_seconds: float = 0.0):
        self.lines_per_format = lines_per_format
        self.output_file = output_file or self._choose_output_file()
        self.pause_seconds = pause_seconds
        self.lock = threading.Lock()
        self._ensure_output_directory()
        self._setup_logging()
        
    def _choose_output_file(self) -> str:
        """Choose output file location, trying /var/log first, falling back to home directory"""
        default_path = "/var/log/loadgen/loadgen.log"
        fallback_path = os.path.expanduser("~/loadgen.log")
        
        try:
            os.makedirs(os.path.dirname(default_path), exist_ok=True)
            with open(default_path, 'a') as f:
                f.write("probe\n")
            return default_path
        except (PermissionError, OSError):
            with open(fallback_path, 'a') as f:
                f.write("probe\n")
            return fallback_path
    
    def _ensure_output_directory(self):
        """Ensure the output directory exists for the output file and status file"""
        # Ensure directory for main output file
        output_dir = os.path.dirname(self.output_file)
        if output_dir:  # Only create directory if there's a directory path
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"[*] Ensured output directory exists: {output_dir}")
            except (PermissionError, OSError) as e:
                print(f"[!] Could not create output directory {output_dir}: {e}")
                # Try to use a fallback location
                fallback_path = os.path.expanduser("~/loadgen.log")
                self.output_file = fallback_path
                print(f"[*] Using fallback output file: {fallback_path}")
        
        # Ensure directory for status file
        status_file = f"{self.output_file}.status"
        status_dir = os.path.dirname(status_file)
        if status_dir and status_dir != output_dir:  # Only if different from main output dir
            try:
                os.makedirs(status_dir, exist_ok=True)
                print(f"[*] Ensured status file directory exists: {status_dir}")
            except (PermissionError, OSError) as e:
                print(f"[!] Could not create status file directory {status_dir}: {e}")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler(f"{self.output_file}.status", mode='a')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _generate_single_format(self, format_name: str):
        """Generate logs for a single format using the appropriate generator class"""
        if format_name not in LOG_GENERATORS:
            self.logger.error(f"[!] Unknown format: {format_name}")
            return
        
        generator_class = LOG_GENERATORS[format_name]
        generator = generator_class(
            lines=self.lines_per_format,
            output_file=self.output_file,
            lock=self.lock,
            logger=self.logger
        )
        
        generator.generate()
    
    def run_concurrent(self):
        """Run all log formats concurrently"""
        self.logger.info(f"[*] Writing logs to: {self.output_file}")
        self.logger.info(f"[*] Concurrent generation: {self.lines_per_format * 6} total lines across 6 formats")
        
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = []
            for format_name in LOG_GENERATORS.keys():
                future = executor.submit(self._generate_single_format, format_name)
                futures.append(future)
            
            # Wait for all to complete
            for future in futures:
                future.result()
        
        self.logger.info(f"[OK] All formats finished. Total lines: {self.lines_per_format * 6}. Output file: {self.output_file}")
    
    def run_with_duration(self, duration_seconds: int) -> None:
        """Run log generation for a specified duration, restarting if it finishes early"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        self.logger.info(f"[*] Starting time-based execution for {duration_seconds} seconds")
        self.logger.info(f"[*] Will run until: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        iteration = 1
        
        while time.time() < end_time:
            remaining_time = end_time - time.time()
            self.logger.info(f"[*] Starting iteration {iteration} (remaining: {remaining_time:.1f}s)")
            
            # Run the concurrent generation
            self.run_concurrent()
            
            # Check if we still have time left
            if time.time() < end_time:
                self.logger.info(f"[*] Iteration {iteration} completed, restarting for remaining time...")
                iteration += 1
                
                # Add pause between iterations if specified
                if self.pause_seconds > 0:
                    self.logger.info(f"[*] Pausing for {self.pause_seconds:.1f} seconds...")
                    time.sleep(self.pause_seconds)
            else:
                self.logger.info(f"[*] Time limit reached after {iteration} iteration(s)")
                break
        
        total_runtime = time.time() - start_time
        self.logger.info(f"[OK] Time-based execution completed. Total runtime: {total_runtime:.1f}s, Iterations: {iteration}")


# Example usage:
if __name__ == "__main__":
    generator = LogGenerator(lines_per_format=100, pause_seconds=0.1)
    generator.run_concurrent()
