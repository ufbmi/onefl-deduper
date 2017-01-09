"""
Goal: store shortcuts to common tasks

@authors:
    Andrei Sura <sura.andrei@gmail.com>

"""

# import sys
from invoke import task


@task
def list(ctx):
    """ Show available tasks """
    ctx.run('inv -l')


@task
def prep_develop(ctx):
    """ Install the requirements """
    ctx.run('pip install -U -r requirements.txt')
    print("==> Pip packages installed:")
    ctx.run('pip freeze')


@task(aliases=['go'])
def gen_hashes(ctx):
    """ Generate hashes from PHI """
    ctx.run('PYTHONPATH=. python gen_hashes.py -i data -o data')


@task
def lint(ctx):
    """ Show the lint score """
    ctx.run("which pylint || pip install pylint")
    ctx.run("pylint -f parseable onefl")


@task
def test(ctx):
    """ Run tests
    -s: shows details
    """
    ctx.run('PYTHONPATH="." py.test -v -s --tb=short tests/ --color=yes')


@task(aliases=['cov'])
def coverage(ctx):
    """ Create coverage report """
    ctx.run('PYTHONPATH="." py.test -v -s --tb=short tests/ --color=yes'
            ' --cov onefl ')  # --cov-config tests/.coveragerc')


@task(aliases=['cov_html'])
def coverage_html(ctx):
    """ Create coverage report and open it in the browser"""
    ctx.run('PYTHONPATH="." py.test --tb=short -s --cov onefl '
            ' --cov-report term-missing --cov-report html tests/')
    ctx.run('open htmlcov/index.html')


@task
def clean(ctx):
    """
    Remove all generated files
    """
    ctx.run('find . -type f -name "*.pyc" -print | xargs rm -f')
    ctx.run('rm -rf htmlcov/ .coverage pylint.out')
    ctx.run('rm -rf .tox/* .ropeproject/')
    ctx.run('rm -rf ./dist ./build ./.eggs ./*.egg-info ./BUILT_WHEELS')
    # ctx.run('rm -f db.sqlite')
