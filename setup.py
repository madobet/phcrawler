import setuptools

with open("README.md", "r") as fh:
  long_descript = fh.read()

setuptools.setup(
  name='phcrawler',
  version='0.0.1',
  description='PH Crawler',
  long_description=long_descript,
  long_description_content_type="text/markdown",
  url='https://github.com/madobet/phcrawler',
  author='Tooko Madobe',
  author_email='madobet@outlook.com',
  license='GPLv3',
  packages=setuptools.find_packages(),
  install_requires=[ 'requests', 'lxml', 'js2py', 'clint', 'fire', 'loguru', 'youtube-dl' ],
  classifiers=[
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent",
  ],
  entry_points = {
    'console_scripts': [
      'phcrawler = phcrawler.__console__:main',
    ],
  }
)
