from setuptools import setup, find_packages
from pathlib import Path


with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()     
   
HYPEN_E_DOT='-e .'

def get_requirements(file_path):
    requirements=[]
    with open(file_path) as file_obj:
        requirements=file_obj.readlines()
        requirements=[req.replace("\n","") for req in requirements]

        if HYPEN_E_DOT in requirements:
            requirements.remove(HYPEN_E_DOT)

    return requirements

__version__ = "0.0.1"
REPO_NAME = "Ineuron_internhip_proj"
PKG_NAME= "src"
AUTHOR_USER_NAME = "pranav-c01"
AUTHOR_EMAIL = "pranavc430@gmail.com"

setup(
    name=PKG_NAME,
    version=__version__,
    author=AUTHOR_USER_NAME,
    author_email=AUTHOR_EMAIL,
    description="Predict Mushroom is suitable to eat or it is  poisonous .",
    long_description=long_description,
    url=f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}",
    project_urls={
        "Bug Tracker": f"https://github.com/{AUTHOR_USER_NAME}/{REPO_NAME}/issues",
    },
    packages=find_packages(),
    install_requires = get_requirements(Path("./requirements.txt"))
    )



