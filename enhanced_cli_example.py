"""
Enhanced command-line interface for the class-based log generator
"""

import argparse
import os
import sys
import time
import threading
import logging
from concurrent.futures import ThreadPoolExecutor
from log_generators import LOG_GENERATORS


def load_env_config():
    """Load configuration from .env file if it exists"""
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        return {
            'lines': os.getenv('LOG_LINES'),
            'output': os.getenv('LOG_OUTPUT'),
            'format': os.getenv('LOG_FORMAT'),
            'duration': os.getenv('LOG_DURATION'),
            'pause': os.getenv('LOG_PAUSE')
        }
    return {}


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
        output_dir = os.path.dirname(self.output_file)
        if output_dir:
            try:
                os.makedirs(output_dir, exist_ok=True)
                print(f"[*] Ensured output directory exists: {output_dir}")
            except (PermissionError, OSError) as e:
                print(f"[!] Could not create output directory {output_dir}: {e}")
                fallback_path = os.path.expanduser("~/loadgen.log")
                self.output_file = fallback_path
                print(f"[*] Using fallback output file: {fallback_path}")
    
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
            
            for future in futures:
                future.result()
        
        self.logger.info(f"[OK] All formats finished. Total lines: {self.lines_per_format * 6}. Output file: {self.output_file}")
    
    def run_single_format(self, format_name: str):
        """Run a single log format"""
        self.logger.info(f"[*] Writing logs to: {self.output_file}")
        self.logger.info(f"[*] Single format generation: {self.lines_per_format} lines for {format_name}")
        
        self._generate_single_format(format_name)
        
        self.logger.info(f"[OK] {format_name} format finished. Total lines: {self.lines_per_format}. Output file: {self.output_file}")
    
    def run_with_duration(self, duration_seconds: int, format_name: str = None) -> None:
        """Run log generation for a specified duration, restarting if it finishes early"""
        from datetime import datetime
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        self.logger.info(f"[*] Starting time-based execution for {duration_seconds} seconds")
        self.logger.info(f"[*] Will run until: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
        
        iteration = 1
        
        while time.time() < end_time:
            remaining_time = end_time - time.time()
            self.logger.info(f"[*] Starting iteration {iteration} (remaining: {remaining_time:.1f}s)")
            
            if format_name and format_name != "all":
                self.run_single_format(format_name)
            else:
                self.run_concurrent()
            
            if time.time() < end_time:
                self.logger.info(f"[*] Iteration {iteration} completed, restarting for remaining time...")
                iteration += 1
                
                if self.pause_seconds > 0:
                    self.logger.info(f"[*] Pausing for {self.pause_seconds:.1f} seconds...")
                    time.sleep(self.pause_seconds)
            else:
                self.logger.info(f"[*] Time limit reached after {iteration} iteration(s)")
                break
        
        total_runtime = time.time() - start_time
        self.logger.info(f"[OK] Time-based execution completed. Total runtime: {total_runtime:.1f}s, Iterations: {iteration}")


def main():
    # Load environment configuration first
    env_config = load_env_config()
    
    parser = argparse.ArgumentParser(description="Generate synthetic log data in multiple formats")
    parser.add_argument("--lines", "-l", type=int, 
                       default=int(env_config.get('lines', 5000)),
                       help="Number of lines to generate per format (default: 5000)")
    parser.add_argument("--output", "-o", type=str, 
                       default=env_config.get('output'),
                       help="Output file path (default: auto-detect)")
    parser.add_argument("--format", "-f", choices=list(LOG_GENERATORS.keys()) + ['all'],
                       default=env_config.get('format', 'all'), 
                       help="Log format to generate (default: all)")
    parser.add_argument("--duration", "-d", type=int, 
                       default=int(env_config.get('duration')) if env_config.get('duration') else None,
                       help="Run for specified duration in seconds (restarts if finishes early)")
    parser.add_argument("--pause", "-p", type=float, 
                       default=float(env_config.get('pause')) if env_config.get('pause') else 0.0,
                       help="Pause duration in seconds between iterations (default: 0.0)")
    
    # New enhanced options
    parser.add_argument("--list-formats", action="store_true",
                       help="List available log formats and exit")
    parser.add_argument("--format-info", type=str, metavar="FORMAT",
                       help="Show information about a specific format")
    
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_formats:
        print("Available log formats:")
        for format_name, generator_class in LOG_GENERATORS.items():
            doc = generator_class.__doc__ or "No description available"
            print(f"  {format_name:10} - {doc}")
        return
    
    if args.format_info:
        if args.format_info in LOG_GENERATORS:
            generator_class = LOG_GENERATORS[args.format_info]
            print(f"Format: {args.format_info}")
            print(f"Description: {generator_class.__doc__ or 'No description available'}")
            print(f"Class: {generator_class.__name__}")
        else:
            print(f"Unknown format: {args.format_info}")
            print("Available formats:", ", ".join(LOG_GENERATORS.keys()))
        return
    
    generator = LogGenerator(
        output_file=args.output,
        lines_per_format=args.lines,
        pause_seconds=args.pause
    )
    
    # Execute based on arguments
    if args.duration:
        if args.format != "all":
            generator.logger.warning("[!] Duration mode with specific format may not work as expected.")
        generator.run_with_duration(args.duration, args.format)
    else:
        if args.format == "all":
            generator.run_concurrent()
        else:
            generator.run_single_format(args.format)


if __name__ == "__main__":
    main()
