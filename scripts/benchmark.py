import os
import random
from pathlib import Path


QUESTIONS = [
    "What is the total amount due?",
    "What is the invoice date?",
    "Who is the sender of this document?",
    "What payment method is mentioned?",
    "What is the document reference number?",
    "What services or products are listed?",
    "What is the delivery address?",
    "What are the payment terms?",
    "Is there a VAT or tax amount mentioned?",
    "What is the due date for payment?",
]


def _ollama_available():
    import urllib.request
    url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    try:
        urllib.request.urlopen(url, timeout=3)
        return True
    except Exception:
        return False


def _count_docs():
    folder = Path(os.getenv("DOCS_PATH", "./data/docs"))
    exts = {".pdf", ".txt", ".docx", ".csv"}
    return len([f for f in folder.iterdir() if f.suffix.lower() in exts])


def run_live():
    from src.ingestor import ingest_folder
    from src.pipeline import run_query

    print("Ingesting documents...")
    results = ingest_folder()
    ingested = [r for r in results if r["status"] == "ok"]
    skipped = [r for r in results if r["status"] == "skipped"]
    print(f"  Ingested: {len(ingested)}, Skipped: {len(skipped)}")

    doc_count = len(results)
    latencies = []

    print(f"\nRunning {len(QUESTIONS)} queries...\n")
    for i, question in enumerate(QUESTIONS, 1):
        result = run_query(question)
        ms = result["latency_ms"]
        latencies.append(ms)
        print(f"  [{i:2d}/{len(QUESTIONS)}] {ms:5d}ms -- {question}")

    return doc_count, latencies, False


def run_synthetic():
    print("Ollama not available -- running synthetic benchmark.\n")
    doc_count = _count_docs()
    print(f"  Documents found: {doc_count}")

    random.seed(42)
    latencies = [random.randint(800, 2400) for _ in QUESTIONS]

    print(f"\nSynthetic latencies for {len(QUESTIONS)} queries:\n")
    for i, (question, ms) in enumerate(zip(QUESTIONS, latencies), 1):
        print(f"  [{i:2d}/{len(QUESTIONS)}] {ms:5d}ms -- {question}")

    return doc_count, latencies, True


def compute_p95(latencies):
    s = sorted(latencies)
    return s[min(int(len(s) * 0.95), len(s) - 1)]


def print_summary(doc_count, latencies):
    avg = sum(latencies) // len(latencies)
    p95 = compute_p95(latencies)
    print("\n" + "=" * 55)
    print(f"{'Total docs':<15} | {'Total queries':<15} | {'Avg latency':<13} | {'P95 latency'}")
    print("-" * 55)
    print(f"{doc_count:<15} | {len(latencies):<15} | {avg:>8}ms    | {p95:>5}ms")
    print("=" * 55)


def save_results(doc_count, latencies, synthetic=False):
    avg = sum(latencies) // len(latencies)
    p95 = compute_p95(latencies)

    lines = ["# Benchmark Results\n"]
    if synthetic:
        lines.append(
            "> Results from synthetic run"
            " -- connect Ollama for live measurements.\n"
        )

    lines += [
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total documents | {doc_count} |",
        f"| Total queries | {len(latencies)} |",
        f"| Avg latency | {avg}ms |",
        f"| P95 latency | {p95}ms |",
        "",
        "## Per-query results\n",
        "| # | Question | Latency |",
        "|---|----------|---------|",
    ]

    for i, (question, ms) in enumerate(zip(QUESTIONS, latencies), 1):
        lines.append(f"| {i} | {question} | {ms}ms |")

    with open("benchmark_results.md", "w") as f:
        f.write("\n".join(lines) + "\n")

    print("\nSaved to benchmark_results.md")


def main():
    print("=" * 55)
    print("SOVEREIGN DOCUMENT AGENT -- BENCHMARK")
    print("=" * 55)

    if _ollama_available():
        try:
            doc_count, latencies, synthetic = run_live()
        except Exception as exc:
            print(f"\nLive run failed ({exc}), falling back to synthetic.\n")
            doc_count, latencies, synthetic = run_synthetic()
    else:
        doc_count, latencies, synthetic = run_synthetic()

    print_summary(doc_count, latencies)
    save_results(doc_count, latencies, synthetic)


if __name__ == "__main__":
    main()
