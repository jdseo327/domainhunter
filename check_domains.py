#!/usr/bin/env python3
"""
Domain Availability Checker
----------------------------
A multi-threaded tool that checks the availability of domains from a text file
and outputs available domains to a timestamped file.

Usage:
    python domain_checker.py [options]

Options:
    -f, --file TEXT        Input file containing domains (default: domains.txt)
    -t, --threads INTEGER  Number of worker threads (default: 8)
    -o, --timeout INTEGER  Timeout in seconds for each request (default: 5, max: 25)
    -h, --help             Show this help message and exit
"""

import socket
import threading
import queue
import time
import argparse
import os
import re
import sys
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Regular expression for validating domain names
DOMAIN_REGEX = re.compile(
    r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z0-9][a-zA-Z0-9-]{0,61}[a-zA-Z0-9]$'
)

class DomainChecker:
    """Checks domain availability using a multi-threaded approach."""
    
    def __init__(self, input_file='domains.txt', num_threads=8, timeout=5):
        """Initialize the domain checker.
        
        Args:
            input_file (str): Path to the file containing domain names.
            num_threads (int): Number of worker threads.
            timeout (int): Socket timeout in seconds.
        """
        self.input_file = input_file
        self.num_threads = num_threads
        self.timeout = min(timeout, 25)  # Cap timeout at 25 seconds
        self.domain_queue = queue.Queue()
        self.available_domains = []
        self.lock = threading.Lock()
        self.output_file = f"available_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.stop_event = threading.Event()
        self.domains_checked = 0
        self.domains_available = 0
    
    def is_valid_domain(self, domain):
        """Check if the given string is a valid domain name.
        
        Args:
            domain (str): The domain name to validate.
            
        Returns:
            bool: True if domain is valid, False otherwise.
        """
        return bool(DOMAIN_REGEX.match(domain))
    
    def load_domains(self):
        """Load and validate domains from the input file."""
        try:
            if not os.path.exists(self.input_file):
                logger.error(f"Input file not found: {self.input_file}")
                return False
            
            with open(self.input_file, 'r') as file:
                for line in file:
                    # Strip whitespace and skip empty lines
                    domain = line.strip()
                    if domain and self.is_valid_domain(domain):
                        self.domain_queue.put(domain)
                    elif domain:  # Only log if the line wasn't empty
                        logger.warning(f"Skipping invalid domain: {domain}")
            
            logger.info(f"Loaded {self.domain_queue.qsize()} domains for checking")
            return self.domain_queue.qsize() > 0
            
        except Exception as e:
            logger.error(f"Error loading domains: {str(e)}")
            return False
    
    def check_domain_availability(self, domain):
        """Check if a domain is available by attempting to resolve it.
        
        Args:
            domain (str): The domain to check.
            
        Returns:
            bool: True if domain appears to be available, False otherwise.
        """
        try:
            # Attempt to resolve the domain
            socket.gethostbyname(domain)
            # If we get here, the domain resolved successfully (not available)
            return False
        except socket.gaierror:
            # Domain didn't resolve, likely available
            return True
        except socket.timeout:
            # Timed out, can't determine availability
            logger.warning(f"Connection timed out for {domain}")
            return False
        except Exception as e:
            logger.warning(f"Error checking {domain}: {str(e)}")
            return False
    
    def worker(self, worker_id):
        """Worker thread that processes domains from the queue.
        
        Args:
            worker_id (int): Identifier for the worker thread.
        """
        socket.setdefaulttimeout(self.timeout)
        logger.debug(f"Worker {worker_id} started")
        
        while not self.stop_event.is_set():
            try:
                # Get domain with a timeout to allow for graceful shutdown
                domain = self.domain_queue.get(timeout=0.5)
                
                # Check if the domain is available
                is_available = self.check_domain_availability(domain)
                
                with self.lock:
                    self.domains_checked += 1
                    
                    # If available, add to results and write to file
                    if is_available:
                        self.domains_available += 1
                        self.available_domains.append(domain)
                        with open(self.output_file, 'a') as f:
                            f.write(f"{domain}\n")
                        logger.info(f"Available: {domain}")
                
                # Mark task as done
                self.domain_queue.task_done()
                
            except queue.Empty:
                # No more domains in the queue
                break
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {str(e)}")
                if not self.stop_event.is_set():
                    self.domain_queue.task_done()
        
        logger.debug(f"Worker {worker_id} finished")
    
    def run(self):
        """Run the domain checker."""
        logger.info(f"Starting domain availability check with {self.num_threads} threads")
        logger.info(f"Results will be saved to {self.output_file}")
        
        # Create the output file
        with open(self.output_file, 'w') as f:
            f.write(f"# Available domains - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Original input file: {self.input_file}\n\n")
        
        # Load domains from input file
        if not self.load_domains():
            return False
        
        # Save the initial queue size
        initial_queue_size = self.domain_queue.qsize()
        
        # Create and start worker threads
        threads = []
        for i in range(self.num_threads):
            thread = threading.Thread(target=self.worker, args=(i,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        try:
            # Display progress until all tasks are done
            while not self.domain_queue.empty():
                remaining = self.domain_queue.qsize()
                checked = initial_queue_size - remaining
                percentage = (checked / initial_queue_size) * 100 if initial_queue_size > 0 else 0
                
                logger.info(f"Progress: {checked}/{initial_queue_size} domains ({percentage:.1f}%) - Found {self.domains_available} available")
                time.sleep(2)
            
            # Wait for all threads to complete their current tasks
            self.domain_queue.join()
            
        except KeyboardInterrupt:
            logger.info("Received interrupt, shutting down...")
            self.stop_event.set()
        
        # Signal threads to stop
        self.stop_event.set()
        
        # Wait for threads to finish
        for thread in threads:
            thread.join()
        
        # Final report
        logger.info(f"Completed! Checked {self.domains_checked} domains")
        logger.info(f"Found {self.domains_available} available domains")
        logger.info(f"Results saved to {self.output_file}")
        
        return True


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Multi-threaded domain availability checker')
    parser.add_argument('-f', '--file', type=str, default='domains.txt',
                        help='Input file containing domains (default: domains.txt)')
    parser.add_argument('-t', '--threads', type=int, default=8,
                        help='Number of worker threads (default: 8)')
    parser.add_argument('-o', '--timeout', type=int, default=5,
                        help='Timeout in seconds for each request (default: 5, max: 25)')
    args = parser.parse_args()
    
    # Create and run the domain checker
    checker = DomainChecker(
        input_file=args.file,
        num_threads=args.threads,
        timeout=args.timeout
    )
    
    success = checker.run()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
