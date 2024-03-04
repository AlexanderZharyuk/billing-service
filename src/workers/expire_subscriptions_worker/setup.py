from setuptools import setup


def get_requirements() -> list[str]:
    with open("requirements.txt") as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


setup(
    name="expire-subscriptions-worker",
    version="1.0.0",
    long_description="Expired subscriptions worker",
    long_description_content_type="text/markdown",
    package_dir={"src/workers/expire_subscriptions_worker": ""},
    python_requires=">=3.10",
    install_requires=get_requirements(),
    include_package_data=True,
    entry_points={
        "console_scripts": ["start-worker=src.workers.expire_subscriptions_worker.main:main"]
    },
)
