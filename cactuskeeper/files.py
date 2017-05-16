import configparser
import os


def read_config_file(directory):
    """
        Read a setup.cfg file from the given directory and parse the `cactuskeeper`
        section out of it. Process the given settings and return a dict representing
        them.

        :param directory:
            The directory the ``setup.cfg`` file can be found in.

        :return:
            A dict holding the cactuskeeper configuration.
    """
    path = os.path.join(directory, "setup.cfg")
    parser = configparser.ConfigParser()
    parser.read(path)

    try:
        config = dict(parser["cactuskeeper"])
    except KeyError:
        config = {}

    # Processing
    config["tagged-files"] = config.get("tagged-files", "").split("\n")
    # prune out empty ones
    config["tagged-files"] = [f for f in config["tagged-files"] if f]

    return config
