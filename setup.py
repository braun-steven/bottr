from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='bottr',
      version='0.1.0',
      description='Simple Reddit Bot Library',
      long_description=readme(),
      url='http://github.com/slang03/bottr',
      author='Steven Lang',
      author_email='steven.lang.mz@gmail.com',
      license='MIT',
      packages=['bottr'],
      zip_safe=False,
      keywords='reddit bot praw',
      install_requires=['praw'],
      include_package_data=True,
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Framework :: Robot Framework :: Library',
          'Programming Language :: Python :: 3 :: Only',
          'Topic :: Internet'
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      )
