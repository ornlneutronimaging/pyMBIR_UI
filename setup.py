"""Information and settings for setuptools.setup(). Now the package can be installed with 'pip install .'."""
from setuptools import setup, find_packages
import versioneer

setup(name='pyMBIR_UI',
      version=versioneer.get_version(),
      description='User interface to pyMBIR.',
      url='',
      author='Jean Bilheux, Venkatrishnan (Venkat) Singanallur',
      author_email='bilheuxjm@ornl.gov, venkatakrisv@ornl.gov ',
      license='',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      scripts=["scripts/pyMBIR_UI"],
      # Requirements are handled by conda
      install_requires=['qtpy', 'pyqtgraph'],
      extras_require=dict(tests=['pytest']),
      zip_safe=False)
