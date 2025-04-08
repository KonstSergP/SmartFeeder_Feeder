import signal
import sys
from feeder import SmartFeeder
from settings.config import log


# Keeping it global allows access from the signal handler
feeder = None


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
    # Register signal handler for SIGINT (Ctrl+C) and SIGTERM
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        feeder = SmartFeeder()
        feeder.work()
    except Exception as e:
        log.error(f"Exception in main loop: {e}", exc_info=True)
        if feeder:
            try:
                feeder.cleanup()
            except Exception as cleanup_e:
                log.error(f"Error during cleanup: {cleanup_e}", exc_info=True)
        sys.exit(1)
