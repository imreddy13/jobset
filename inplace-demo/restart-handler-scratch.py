#!/usr/bin/env python3
import os
import psutil
import signal
import subprocess
import sys
import time
import asyncio
import time
import logging
from datetime import datetime, timezone, timedelta

from kubernetes import client, config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

# Create a logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Set the overall logging level

# Create file handler (for writing to a file)
file_handler = logging.FileHandler('restart_handler.log')  # Choose your log file name
file_handler.setLevel(logging.DEBUG)  # Set the level for this handler

# Create console handler (for writing to stdout)
console_handler = logging.StreamHandler(sys.stdout)  # Defaults to sys.stderr
console_handler.setLevel(logging.DEBUG)   # Set the level for this handler (e.g., only INFO and above)

# Create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# constants
WRAPPER_CONTAINER_NAME = "wrapper"
POD_NAME_ENV = "POD_NAME"
JOBSET_NAME_ENV = "JOBSET_NAME"
USER_COMMAND_ENV = "USER_COMMAND"

class RestartHandler:
    def __init__(self, namespace: str = "default"):
        self.user_process = None
        self.pod_name = os.getenv(POD_NAME_ENV)
        self.namespace = namespace

        # setup signal handler for SIGUSR1, which the main process will use to restart the user process.
        signal.signal(signal.SIGUSR1, self.handle_restart_signal)

    def get_pod_names(self, namespace: str = "default") -> list[str]:
        """Get all pods owned by the given JobSet, except self."""
        self_pod_name = os.getenv(POD_NAME_ENV)
        pods = client.CoreV1Api().list_namespaced_pod(namespace)
        # filter out self pod name
        return [pod.metadata.name for pod in pods.items if pod.metadata.name != self_pod_name]

    def handle_restart_signal(self, signum, frame):
        """Signal handler for SIGUSR1 (restart)."""
        logger.debug("Restart signal received. Killing user process...")
        # kill existing user process
        self.user_process.kill() # kill local user process

    async def run(self) -> None:
            '''Run the monitoring loop, broadcast restart signal & restart the user process if needed.'''

            # run monitoring loop
            while True:
                for proc in psutil.process_iter(['pid', 'name', 'username']):
                    logger.debug("process name: ")
                    logger.debug(proc.name())
                    print(proc.info)
                    if proc.name() == "sh":
                        self.user_process = proc

                await asyncio.sleep(120)
                logger.debug("Restart signal received. Killing user process...")
                logger.debug(proc.name())
                logger.debug(self.user_process.name())
                self.user_process.kill()
                await asyncio.sleep(600)  # sleep to avoid excessive polling

async def main(namespace: str):
    try: 
        # for in cluster testing
        config.load_incluster_config()
    except:
        # for local testing
        config.load_kube_config()

    # start the restart handler
    restart_handler = RestartHandler(namespace=namespace)
    await restart_handler.run()


if __name__ == "__main__":
    asyncio.run(main("default"))