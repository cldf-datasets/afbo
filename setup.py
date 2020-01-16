from setuptools import setup


setup(
    name='cldfbench_afbo',
    py_modules=['cldfbench_afbo'],
    include_package_data=True,
    zip_safe=False,
    entry_points={
        'cldfbench.dataset': [
            'afbo=cldfbench_afbo:Dataset',
        ]
    },
    install_requires=[
        'cldfbench',
    ],
    extras_require={
        'test': [
            'pytest-cldf',
        ],
    },
)
