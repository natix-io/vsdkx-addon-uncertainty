from setuptools import setup, find_namespace_packages

setup(
    name='vsdkx-addon-uncertainty',
    url='https://gitlab.com/natix/cvison/vsdkx/vsdkx-addon-uncertainty',
    author='Nicole',
    author_email='nicole@natix.io',
    namespace_packages=['vsdkx', 'vsdkx.addon'],
    packages=find_namespace_packages(include=['vsdkx*']),
    dependency_links=[
        'git+https://github.com/natix-io/vsdkx-core#egg=vsdkx-core'
    ],
    install_requires=[
        'vsdkx-core',
        'scipy>=1.4.1',
        'numpy>=1.18.5',
    ],
    version='1.0',
)
