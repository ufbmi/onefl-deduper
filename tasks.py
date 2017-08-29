"""
Goal: store shortcuts to common tasks

@authors:
    Andrei Sura <sura.andrei@gmail.com>

"""

# import sys
from invoke import task
from onefl.partner_name import PartnerName  # noqa
from onefl.partner_name import VALID_PARTNERS

STATUS_PASS = '✔'
STATUS_FAIL = '✗'


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


@task(aliases=['hash'])
def hasher(ctx, ask=True):
    """ Generate hashes from PHI """
    inputfolder = 'data'
    outputfolder = 'data'
    opt_ask = '--ask' if ask else ''

    ctx.run('PYTHONPATH=. python run/hasher.py -i {} -o {} {}'
            .format(inputfolder, outputfolder, opt_ask))


@task(aliases=['link'],
      help={'partner': 'The partner name: {}'.format(VALID_PARTNERS)})
def linker(ctx, partner, ask=True):
    """ Generate OneFlorida Ids from hashes """
    inputfolder = 'data'
    outputfolder = 'data'
    opt_ask = '--ask' if ask else ''

    if partner:
        ctx.run('PYTHONPATH=. python run/linker.py -i {} -o {} -p {} {}'
                .format(inputfolder, outputfolder, partner, opt_ask))
    else:
        print("""
Usage:
 inv link --inputdir=dir --outputdir=dir -p=partner --ask
              """)
        print("[{}] Please specify a valid partner name"
              " and input directories.\n"
              "Available partners: {}"
              .format(STATUS_FAIL, VALID_PARTNERS))


@task
def link_flm(ctx):
    linker(ctx, partner=PartnerName.FLM.value)


@task
def link_ufh(ctx):
    linker(ctx, partner=PartnerName.UFH.value)


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
def devel_install(ctx):
    ctx.run('python setup.py develop')


@task
def devel_uninstall(ctx):
    ctx.run('python setup.py develop -u')


@task
def sdist(ctx):
    """ Create a `source` distribution """
    ctx.run("python setup.py sdist")


@task
def pypi_check_config(ctx):
    ctx.run("echo 'Check the presence of the ~/.pypirc config file'")
    ctx.run("test -f ~/.pypirc || echo 'Please create the ~/.pypirc file. "
            "Here is a template: \n'", echo=False)
    ctx.run("(test -f ~/.pypirc && echo "")|| (cat config/pypirc && exit 1)",
            echo=False)


@task(pre=[pypi_check_config])
def pypi_register(ctx):
    """ Use the ~/.pypirc config to register the package """
    ctx.run("python setup.py register -r deduper")


@task(pre=[pypi_check_config])
def pypi_upload(ctx):
    """ Use the ~/.pypirc config to upload the package """
    ctx.run("which twine || pip install twine")
    ctx.run("python setup.py sdist --formats=zip bdist_wheel")
    ctx.run("twine upload dist/* -r deduper")
    print("Done. To test please run: "
          "python -m virtualenv venv "
          " && source ./venv/bin/activate "
          " && pip install -U deduper && hasher -v")


@task
def pypi_wheel(ctx):
    """
    Download all `wheel` packages
    If the target machine has no access to internet we can build, ship, install
        pip wheel -r requirements-to-freeze.txt -w BUILT_WHEELS
        scp -r BUILT_WHEELS production_server:WHEE
        pip install -r requirements-to-freeze.txt --no-index --find-links WHEE
    """
    ctx.run('pip wheel deduper -r requirements-to-freeze.txt -w BUILT_WHEELS')


@task
def clean(ctx):
    """ Remove all generated files """
    ctx.run('find . -type f -name "*.pyc" -print | xargs rm -f')
    ctx.run('rm -rf htmlcov/ .coverage pylint.out')
    ctx.run('rm -rf .tox/* .ropeproject/')
    ctx.run('rm -rf ./dist ./build ./.eggs ./*.egg-info ./BUILT_WHEELS')
    # ctx.run('rm -f db.sqlite')


@task
def clean_log(ctx):
    """ Remove log file """
    ctx.run('rm -f logs/deduper.log')
