from generate_zh import main
import sys

if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--check"]
    raise SystemExit(main())
