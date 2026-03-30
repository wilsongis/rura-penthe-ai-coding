# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "llmlingua",
#     "torch",
#     "transformers",
# ]
# ///

import sys
import argparse
from pathlib import Path
try:
    from llmlingua import PromptCompressor
except ImportError:
    print("Error: Could not import LLMLingua. Ensure 'uv' installed the dependencies correctly.")
    sys.exit(1)

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
        
    print(f"[*] Initializing LLMLingua-2 compressor on {args.device}...")
    print(f"    (Note: The first run will download model weights (~2GB) and may take significant time)")
    
    try:
        compressor = PromptCompressor(
            model_name="microsoft/llmlingua-2-xlm-roberta-large-meetingbank",
            use_llmlingua2=True,
            device_map=args.device
        )
    except Exception as e:
        print(f"Error initializing compressor: {e}")
        sys.exit(1)
        
    print(f"[*] Compressing {target_path.name} (Original size: {original_len} characters) at rate={args.rate}...")
    
    try:
        # Prevent force-removing critical syntactical whitespace or question marks
        result = compressor.compress_prompt(content, rate=args.rate, force_tokens=['\n', '?'])
        compressed_text = result["compressed_prompt"]
        compressed_len = len(compressed_text)
    except Exception as e:
        print(f"Error compressing prompt: {e}")
        sys.exit(1)
        
    savings_pct = 100 * (1.0 - (compressed_len / max(1, original_len)))
    
    # Store or output
    if args.output:
        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(compressed_text, encoding="utf-8")
        print(f"[+] Compressed successfully. Saved to {out_path}")
        print(f"    New size: {compressed_len} chars (Saved {savings_pct:.1f}%)")
    else:
        print(f"\n--- Compressed Output (Saved {savings_pct:.1f}%) ---\n")
        print(compressed_text)
        print(f"\n----------------------------------------------------\n")

if __name__ == "__main__":
    main()
