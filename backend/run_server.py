#!/usr/bin/env python
"""Run Uvicorn server with proper signal handling"""
import uvicorn
import sys

if __name__ == "__main__":
    try:
        config = uvicorn.Config(
            app="main:app",
            host="127.0.0.1",
            port=8001,
            reload=False,
            log_level="info",
            access_log=True,
        )
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"Error starting server: {e}", file=sys.stderr)
        sys.exit(1)
