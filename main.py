import signal
import sys
from feeder import SmartFeeder
from settings.config import log


feeder = SmartFeeder()


def signal_handler(sig, frame):
    log.info("Received signal: %s", sig)
    if feeder:
        try:
            feeder.cleanup()
        except Exception as e:
            log.error(f"Error during feeder cleanup: {e}", exc_info=True)
        
    log.info("Shutdown complete")
    sys.exit(0)


if __name__ == "__main__":
    # Register signal handler for SIGINT (Ctrl+C)
    signal.signal(signal.SIGINT, signal_handler)
    # Also handle SIGTERM for proper shutdown when killed
    signal.signal(signal.SIGTERM, signal_handler)

    feeder.work()
