import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent

PROTOC_PATH = "protoc"
PROTO_DIR = PROJECT_ROOT.joinpath("proto")
PYTHON_OUTPUT_DIR = PROJECT_ROOT.joinpath("src", "xiaomi_ndef", "proto")

if __name__ == "__main__":
    if os.system(f"{PROTOC_PATH} --version") != 0:
        print("protoc not found")
        exit(1)

    old_files = [i for i in os.listdir(PYTHON_OUTPUT_DIR) if i.endswith(("_pb2.py", "_pb2.pyi"))]
    if len(old_files) > 0:
        print("Removing old protobuf files")
        for file in old_files:
            os.remove(PYTHON_OUTPUT_DIR.joinpath(file))

    print("Creating protobuf files")
    os.system(" ".join([
        str(PROTOC_PATH),
        f"--proto_path=\"{PROTO_DIR}\"",
        f"--pyi_out=\"{PYTHON_OUTPUT_DIR}\"",
        f"--python_out=\"{PYTHON_OUTPUT_DIR}\"",
        f"\"{PROTO_DIR}/*\""
    ]))
