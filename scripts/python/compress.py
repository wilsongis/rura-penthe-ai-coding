# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "llmlingua",
#     "torch",
#     "transformers",
#     "tiktoken",
# ]
# ///

import sys
import argparse
import sqlite3
import datetime
from pathlib import Path
import tiktoken
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

def main():
    parser = argparse.ArgumentParser(description="Warden Context Compressor (LLMLingua-2)")
    parser.add_argument("target", type=str, help="Target file to compress")
    parser.add_argument("--rate", type=float, default=0.3, help="Compression target rate (e.g. 0.3 for 30% retention)")
    parser.add_argument("--device", type=str, default="cpu", help="Device to run on (cpu, cuda, mps)")
    parser.add_argument("--output", "-o", type=str, default=None, help="Output file path for compressed content")
    
    args = parser.parse_args()
    
    target_path = Path(args.target)
    
    if not target_path.exists():
        print(f"Error: Target path {args.target} does not exist.")
        sys.exit(1)
        
    try:
        content = target_path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
        
    original_len = len(content)
    if original_len == 0:
        print("File is empty. Nothing to compress.")
        sys.exit(0)
        
    try:
        enc = tiktoken.get_encoding("cl100k_base")
        original_tokens = len(enc.encode(content, disallowed_special=()))
    except Exception as e:
        print(f"Warning: Failed to count original tokens: {e}")
        original_tokens = len(content) // 4  # rough fallback
        enc = None
        
    print(f"[*] Initializing LLMLingua-2 compressor on {args.device}...")
    print("    (Note: The first run will download model weights (~2GB) and may take significant time)")
    
    try:
        compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
            use_llmlingua2=True,
            device_map=args.device
        )
    except Exception as e:
        print(f"Error initializing compressor: {e}")
        sys.exit(1)
        
    print(f"[*] Compressing {target_path.name} (Original size: {original_tokens} tokens) at rate={args.rate}...")
    
    try:
        # Prevent force-removing critical syntactical whitespace or question marks
        result = compressor.compress_prompt(content, rate=args.rate, force_tokens=['\n', '?'])
        compressed_text = result["compressed_prompt"]
        compressed_len = len(compressed_text)
    except Exception as e:
        print(f"Error compressing prompt: {e}")
        sys.exit(1)
        
    if enc is not None:
        compressed_tokens = len(enc.encode(compressed_text, disallowed_special=()))
    else:
        compressed_tokens = compressed_len // 4
        
    tokens_saved = original_tokens - compressed_tokens
    savings_pct = 100 * (tokens_saved / max(1, original_tokens))
    
    # Store telemetry
    log_telemetry(target_path.name, original_tokens, compressed_tokens)
    
    # Store or output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(compressed_text, encoding="utf-8")
        print(f"[+] Compressed successfully. Saved to {out_path}")
        print(f"    New size: {compressed_tokens} tokens (Saved {tokens_saved} tokens, {savings_pct:.1f}%)")
    else:
        print(f"\n--- Compressed Output (Saved {tokens_saved} tokens, {savings_pct:.1f}%) ---\n")
        print(compressed_text)
        print("\n----------------------------------------------------\n")

if __name__ == "__main__":
    main()
