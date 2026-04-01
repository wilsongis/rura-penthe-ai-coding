# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "llmlingua",
#     "torch",
#     "transformers",
#     "tiktoken",
#     "pathspec"
# ]
# ///

import sys
import argparse
import sqlite3
import datetime
from pathlib import Path
import tiktoken
import pathspec

try:
    from llmlingua import PromptCompressor
except ImportError:
    print("Error: Could not import LLMLingua. Ensure 'uv' installed the dependencies correctly.")
    sys.exit(1)

def log_telemetry(target_name: str, original_tokens: int, compressed_tokens: int):
    try:
        rura_dir = Path.home() / ".rura"
        rura_dir.mkdir(parents=True, exist_ok=True)
        db_path = rura_dir / "telemetry.db"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS compression_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                target_file TEXT,
                original_tokens INTEGER,
                compressed_tokens INTEGER,
                tokens_saved INTEGER
            )
        ''')
        
        tokens_saved = original_tokens - compressed_tokens
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        cursor.execute('''
            INSERT INTO compression_logs (timestamp, target_file, original_tokens, compressed_tokens, tokens_saved)
            VALUES (?, ?, ?, ?, ?)
        ''', (now, target_name, original_tokens, compressed_tokens, tokens_saved))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: Failed to log telemetry securely: {e}")

def get_ignore_spec(base_path: Path) -> pathspec.PathSpec:
    lines = [
        ".git/",
        ".specify/",
        ".rura/",
        "node_modules/",
        "__pycache__/",
        ".venv/",
        "venv/",
        ".env",
        # Binaries & media
        "*.png", "*.jpg", "*.jpeg", "*.gif", "*.ico", "*.svg",
        "*.pdf", "*.zip", "*.tar", "*.gz", "*.mp4", "*.webm",
        "*.pyc", "*.exe", "*.dll", "*.so", "*.dylib"
    ]
    
    # Try multiple common locations for .gitignore
    gitignores = []
    if base_path.is_dir() and (base_path / ".gitignore").exists():
        gitignores.append(base_path / ".gitignore")
    elif base_path.is_file() and (base_path.parent / ".gitignore").exists():
        gitignores.append(base_path.parent / ".gitignore")
        
    for gi in gitignores:
        try:
            ignore_text = gi.read_text(encoding="utf-8")
            lines.extend(ignore_text.splitlines())
        except Exception:
            pass
            
    return pathspec.PathSpec.from_lines("gitwildmatch", lines)

def get_tokens(content: str, enc) -> int:
    if not content:
        return 0
    if enc is None:
        return len(content) // 4
    try:
        return len(enc.encode(content, disallowed_special=()))
    except Exception:
        return len(content) // 4

def compress_single_content(compressor, content: str, rate: float, enc) -> tuple[str, int, int]:
    original_tokens = get_tokens(content, enc)
    if original_tokens == 0:
        return "", 0, 0
        
    try:
        result = compressor.compress_prompt(content, rate=rate, force_tokens=['\n', '?'])
        compressed_text = result["compressed_prompt"]
        compressed_tokens = get_tokens(compressed_text, enc)
        return compressed_text, original_tokens, compressed_tokens
    except Exception as e:
        print(f"Warning: Compression failed for a chunk: {e}")
        return content, original_tokens, original_tokens

def main():
    parser = argparse.ArgumentParser(description="Warden Context Compressor (LLMLingua-2)")
    parser.add_argument("target", type=str, nargs="?", default=None, help="Target file or directory to compress")
    parser.add_argument("--rate", type=float, default=0.3, help="Compression target rate (e.g. 0.3 for 30% retention)")
    parser.add_argument("--device", type=str, default="cpu", help="Device to run on (cpu, cuda, mps)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file path for compressed content")
    parser.add_argument("--warmup", action="store_true", help="Initialize ML models and exit (for first-time downloads)")
    parser.add_argument("--stdin", action="store_true", help="Read text from standard input instead of a file")
    
    args = parser.parse_args()
    if not args.stdin:
        print(f"[*] Initializing LLMLingua-2 compressor on {args.device}...")
        print("    (Note: The first run will download model weights (~2GB) and may take significant time)")
    
    try:
        # Hide loading print blocks from stdout if doing generic stdin piping
        compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
            use_llmlingua2=True,
            device_map=args.device,
        )
    except Exception as e:
        if not args.stdin:
            print(f"Error initializing compressor: {e}")
        sys.exit(1)
        
    if args.warmup:
        print("\n[+] Success! LLMLingua-2 models downloaded and cached.")
        sys.exit(0)
        
    try:
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        enc = None

    if args.stdin:
        content = sys.stdin.read()
        compressed_text, orig, comp = compress_single_content(compressor, content, args.rate, enc)
        # For standard input piping, ONLY print the raw outcome so CLI apps can intercept cleanly
        print(compressed_text, end="")
        sys.exit(0)
        
    if not args.target:
        print("Error: you must supply a target file/directory unless using --warmup or --stdin")
        sys.exit(1)
        
    target_path = Path(args.target)
    if not target_path.exists():
        print(f"Error: Target path {args.target} does not exist.")
        sys.exit(1)
        
    try:
        enc = tiktoken.get_encoding("cl100k_base")
    except Exception:
        enc = None

    ignore_spec = get_ignore_spec(target_path)
    
    files_to_process = []
    if target_path.is_file():
        if not ignore_spec.match_file(target_path.name):
            files_to_process.append(target_path)
    else:
        for filepath in target_path.rglob("*"):
            if filepath.is_file():
                try:
                    rel_path = filepath.relative_to(target_path)
                    if not ignore_spec.match_file(str(rel_path)):
                        files_to_process.append(filepath)
                except ValueError:
                    pass
                    
    if not files_to_process:
        print("No valid text files found to compress.")
        sys.exit(0)
        
    print(f"[*] Beginning compression sweep across {len(files_to_process)} file(s)...")

    total_original_tokens = 0
    total_compressed_tokens = 0
    final_output_blocks = []
    
    for idx, filepath in enumerate(files_to_process, 1):
        try:
            content = filepath.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            print(f"    [{idx}/{len(files_to_process)}] Skipping {filepath.name} (Binary/Non-UTF8)")
            continue
        except Exception as e:
            print(f"    [{idx}/{len(files_to_process)}] Error reading {filepath.name}: {e}")
            continue
            
        rel_disp = str(filepath) if target_path.is_file() else str(filepath.relative_to(target_path))
        print(f"    [{idx}/{len(files_to_process)}] Compressing {rel_disp}...", end=" ")
        
        compressed_text, orig_toks, comp_toks = compress_single_content(compressor, content, args.rate, enc)
        
        total_original_tokens += orig_toks
        total_compressed_tokens += comp_toks
        
        block = f"<file path=\"{rel_disp}\">\n{compressed_text}\n</file>"
        final_output_blocks.append(block)
        
        pct = 100 * (1.0 - (comp_toks / max(1, orig_toks)))
        print(f"Dropped to {comp_toks} tkns ({pct:.1f}% saved)")
        
    if not final_output_blocks:
        print("No text data successfully read/compressed.")
        sys.exit(0)
        
    unified_output = "\n\n".join(final_output_blocks)
    tokens_saved = total_original_tokens - total_compressed_tokens
    savings_pct = 100 * (tokens_saved / max(1, total_original_tokens))
    
    telemetry_target = target_path.name if target_path.is_file() else f"{target_path.name}/ ({len(files_to_process)} files)"
    log_telemetry(telemetry_target, total_original_tokens, total_compressed_tokens)
    
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(unified_output, encoding="utf-8")
        print(f"\n[+] Sweep complete. Saved to {out_path}")
        print(f"    Directory aggregate: {total_compressed_tokens} tokens (Saved {tokens_saved} tokens, {savings_pct:.1f}%)")
    else:
        print(f"\n--- Compressed Output (Aggregate Saved {tokens_saved} tokens, {savings_pct:.1f}%) ---\n")
        print(unified_output)
        print("\n----------------------------------------------------\n")

if __name__ == "__main__":
    main()
