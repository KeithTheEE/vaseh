from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()

setup(name='vaseh',
      version='0.0.00',
      description='A Wrapper Library for Bokeh and other visualizations with a focus on rapid data exploration',
      long_description=open('README.md').read(),
      author='Keith Murray',
      author_email='kmurrayis@gmail.com',
      license='MIT',
      packages=['vaseh'],
      install_requires=[
          'bokeh >= 1.4.0',
	  
      ],
      include_package_data=True,
      zip_safe=False)
