from setuptools import setup, find_packages

setup(name='nwrapy',
      version='0.1.0',
      description='Nmap wrapper',
      author='Jochem Stevense',
      author_email='',
      url='https://github.com/SneakyBeagle/nwrapy',
      packages=find_packages(include=['nwrapy', 'src']),
      license='GPLv3',
      install_requires=[],
      entry_points={
          'console_scripts': ['nwrapy=nwrapy:main']
          }
      )
