import sys

from src.ingestor import ingest_file, ingest_folder


def main():
    if len(sys.argv) > 1:
        result = ingest_file(sys.argv[1], force="--force" in sys.argv)
        print(f"{result['doc_name']}: {result['status']} ({result['chunks_created']} chunks)")
    else:
        results = ingest_folder()
        for r in results:
            print(f"{r['doc_name']}: {r['status']} ({r['chunks_created']} chunks)")
        print(f"\nTotal: {len(results)} files processed")


if __name__ == "__main__":
    main()
