import os
from glob import glob
from setuptools import find_packages, setup

package_name = "mhseals_learn"

setup(
    name=package_name,
    version="0.0.0",
    packages=find_packages(exclude=["test"]),
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),

        # TODO: Add sim map reuse 
        # (os.path.join('share', package_name, 'maps'), glob(os.path.join('maps', '*'))), 
    ],
    install_requires=[
        'setuptools',
        'pyyaml',
        "numpy",
        "pygame"
    ],
    zip_safe=True,
    author="Liam Bray",
    description="Roboboat teaching/learning package",
    license="GNU GPLv3",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "basic_subscriber = mhseals_learn.lessons.ros.basic_subscriber:main",
            "basic_publisher = mhseals_learn.lessons.ros.basic_publisher:main",
            "sim = mhseals_learn.sim.sim:main"
        ],
    },
)
