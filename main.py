import json
import shutil
from typer import Typer, Option, Argument, Exit
import subprocess
from pathlib import Path
from rich import print
from typing_extensions import Annotated


app = Typer()
source = Path(__file__).parent


def cmd(command: str | list[str], **kwargs) -> subprocess.CompletedProcess:
    try:
        command = command.split() if isinstance(command, str) else command
        return subprocess.run(command, check=True, **kwargs)
    except subprocess.CalledProcessError as e:
        print(e.stderr)
        raise Exit()


@app.command()
def init(
    project_path: Annotated[Path, Argument(help="Project path")] = Path.cwd(),
    intall_deps: Annotated[bool, Option('-i', '--install', help="Install dependencies")] = False
):
    # copy config files
    for f in ['prettier.config.js', 'tailwind.config.ts', '.env.local', '.gitignore']:
        shutil.copy(source / f, project_path / f)

    # update package.json
    data = json.loads((source / 'package.json').read_text())
    pkgs = json.loads((project_path / 'package.json').read_text())

    for k in ['scripts', 'dependencies', 'devDependencies']:
        if k not in pkgs:
            pkgs[k] = {}
        for sub_k, v in data[k].items():
            pkgs[k][sub_k] = v

    (project_path / 'package.json').write_text(json.dumps(pkgs, indent=2))

    # merge src folder
    if (project_path / 'src').exists():
        shutil.rmtree(project_path / 'src')
    shutil.copytree(source / 'src', project_path / 'src')

    # install dependencies
    if intall_deps:
        cmd('npm install', cwd=project_path)


if __name__ == '__main__':
    app()
