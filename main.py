import sys

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        from server.server import run_server
        run_server()
    else:
        from client.client import run_client
        run_client()
