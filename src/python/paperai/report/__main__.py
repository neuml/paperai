"""
Defines main entry point for Report process.
"""

import sys

from .execute import Execute

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run report with params: input file, topn, render format, embeddings model path, qa model path
        Execute.run(sys.argv[1],
                    int(sys.argv[2]) if len(sys.argv) > 2 else None,
                    sys.argv[3] if len(sys.argv) > 3 else None,
                    sys.argv[4] if len(sys.argv) > 4 else None,
                    sys.argv[5] if len(sys.argv) > 5 else None,
                    sys.argv[6] if len(sys.argv) > 6 else None)
