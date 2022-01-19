from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    readme=f.read()

setup(name='nwrapy',
      version='0.1.4',
      description='Nmap wrapper',
      author='Jochem Stevense',
      author_email='',
      #long_description=readme,
      url='https://github.com/SneakyBeagle/nwrapy',
      project_urls={
          "Bug Tracker": "https://github.com/SneakyBeagle/nwrapy/issues"
      },
      classifiers=[
          "Programming Language :: Python :: 3",
      ],
      packages=find_packages(include=['nwrapy']),
      license='GPLv3',
      python_requires=">=3.6",
      entry_points={
          'console_scripts': ['nwrapy=nwrapy:main']
          }
      )
