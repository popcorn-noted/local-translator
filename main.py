import sys
from qvac import QVAC

def main():
    sdk = QVAC()
    model = sdk.loadModel("translate")

    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        print("Enter Spanish text to translate (empty line to exit):")
        text = sys.stdin.readline().strip()

    if not text:
        return

    result = sdk.translate(text, target_language="en")
    print(result)

if __name__ == "__main__":
    main()
