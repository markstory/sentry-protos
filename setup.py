import glob
import os
import shutil
import subprocess
import sys
import tempfile

from distutils.command.build import build
from setuptools import find_packages, setup
from os import path

here = path.abspath(path.dirname(__file__))


def get_requirements():
    with open("requirements.txt") as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


def make_protos():
    protos = glob.glob(f"{here}/src/sentry_protos/**/*.proto", recursive=True)
    with tempfile.TemporaryDirectory() as tmpd:
        for proto in protos:
            result = subprocess.run(
                [
                    "python",
                    "-m",
                    "grpc_tools.protoc",
                    f"-I{here}/src",
                    f"--python_out={tmpd}",
                    f"--mypy_out={tmpd}",
                    f"--grpc_python_out={tmpd}",
                    f"--mypy_grpc_out={tmpd}",
                    proto,
                ]
            )

            if result.returncode != 0:
                sys.exit(1)

        for dir, _, files in os.walk(os.path.join(tmpd, "sentry_protos")):
            if "__init__.py" in files:
                continue
            with open(f"{dir}/__init__.py", "w") as f:
                f.write("")

        for p in os.listdir(tmpd):
            p = f"{tmpd}/{p}"
            if not os.path.isdir(p):
                continue
            with open(f"{p}/py.typed", "w") as f:
                f.write("")

        shutil.rmtree(f"{here}/py/sentry_protos")
        shutil.move(f"{tmpd}/sentry_protos", f"{here}/py/sentry_protos")


class proto_build(build):
    def run(self):
        make_protos()
        super().run()


setup(
    name="sentry-protos",
    version=open("VERSION").read().strip(),
    package_dir={"": f"{here}/py"},
    package_data={"": ["py.typed"]},
    packages=find_packages(where="py"),
    install_requires=[
        "grpcio",
        "grpc-stubs",
        "types-protobuf",
        "protobuf",
    ],
    setup_requires=get_requirements(),
    cmdclass={"build": proto_build},
)
