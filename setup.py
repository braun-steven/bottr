from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='bottr',
      version='0.1.3',
      description='Simple Reddit Bot Library',
      long_description=readme(),
      url='http://github.com/slang03/bottr',
      author='Steven Lang',
      author_email='steven.lang.mz@gmail.com',
      license='MIT',
      packages=['bottr'],
      zip_safe=False,
      keywords='reddit bot praw',
      install_requires=['praw==5.3.0'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Framework :: Robot Framework :: Library',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.2',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      )
