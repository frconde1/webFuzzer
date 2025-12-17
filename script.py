import argparse
import requests
import sys
import concurrent.futures
import time 
import random
from tqdm import tqdm

DEFAULT_WORDLIST = ["account", "login", "admin", "blog", "about"]

def get_wordlist(pathWordlist):
    if pathWordlist:
        try:
            with open(pathWordlist, 'r') as file:
                return file.read().splitlines()
        except FileNotFoundError:
            prinf(f"No file found")
            sys.exit(1)
    else:
        print("Default Wordlist")
        return DEFAULT_WORDLIST

def fuzz_url(target, delay):
    if delay > 0:
        time.sleep(delay)
    try:
        response = requests.get(target, timeout=3)

        if response.status_code == 200:
            return f"Found: {target} (200 OK)"
        elif response.status_code == 403:
            return f"Forbidden: {target} (403 Forbidden)"
    except requests.RequestException:
        pass 
    return None

def main():

    parser = argparse.ArgumentParser(description="Fuzzing tool")
    parser.add_argument("url", help="base URL")
    parser.add_argument("-w", "--wordlist", help="/path/to/wordlist.txt")
    parser.add_argument("-t", "--threads", help="Threads (Default: 10)", type=int, default=10)
    parser.add_argument("--delay", help="Delay between requests", type=int, default=0)
    args = parser.parse_args()

    wordlist = get_wordlist(args.wordlist)
    baseUrl = args.url if args.url.endswith("/") else f"{args.url}/"

    urls = [f"{baseUrl}{path}" for path in wordlist]

    print(f"[*] Starting Fuzzing on: {baseUrl}")
    print(f"[*] Active Threads: {args.threads}")
    print(f"[*] Wordlist Length: {len(wordlist)}")
    print("-" * 40)
 
    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as executor:
            delayTime = args.delay if hasattr(args, 'delay') else 0
            futures = {executor.submit(fuzz_url, url, delayTime): url for url in urls}
            for future in tqdm(concurrent.futures.as_completed(futures), total=len(urls), unit="req", dynamic_ncols=True):
                result = future.result()
                if result:
                    tqdm.write(result)



    except KeyboardInterrupt:
        print("\n [!] Keyboard Interrupt (CTRL + C)")
        executor.shutdown(wait=False)
        sys.exit(0)

if __name__ == "__main__":
    main()
