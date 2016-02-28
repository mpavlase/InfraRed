import ConfigParser

import clg
import os
import yaml

import cli.exceptions
import cli.utils

ENV_VAR_NAME = "IR_CONFIG"
IR_CONF_FILE = 'infrared.cfg'
CWD_PATH = os.path.join(os.getcwd(), IR_CONF_FILE)
USER_PATH = os.path.expanduser('~/.' + IR_CONF_FILE)
SYSTEM_PATH = os.path.join('/etc/infrared', IR_CONF_FILE)
INFRARED_DIR_ENV_VAR = 'IR_SETTINGS'


def load_config_file():
    """Load config file order(ENV, CWD, USER HOME, SYSTEM).

    :return ConfigParser: config object
    """

    # create a parser with default path to InfraRed's main dir
    _config = ConfigParser.ConfigParser()

    env_path = os.getenv(ENV_VAR_NAME, None)
    if env_path is not None:
        env_path = os.path.expanduser(env_path)
        if os.path.isdir(env_path):
            env_path = os.path.join(env_path, IR_CONF_FILE)

    for path in (env_path, CWD_PATH, USER_PATH, SYSTEM_PATH):
        if path is not None and os.path.exists(path):
            _config.read(path)
            return _config

    conf_file_paths = "\n".join([CWD_PATH, USER_PATH, SYSTEM_PATH])
    raise cli.exceptions.IRFileNotFoundException(
        conf_file_paths,
        "IR configuration not found. "
        "Please set it in one of the following paths:\n")


class SpecManager(object):
    """
    Holds everything related to specs.
    """

    SPEC_EXTENSION = '.spec'

    def __init__(self, config):
        self.config = config

    def get_specs(self, module_name):
        """
        Gets specs files as a dict from settings/<module_name> folder.
        :param module_name: the module name: installer|provisioner|tester
        """
        res = {}
        for spec_file in self.__get_all_specs(subfolder=module_name):
            spec = yaml.load(open(spec_file))
            cli.utils.dict_merge(res, spec)
        return res

    def parse_args(self, module_name):
        """
        Looks for all the specs for specified module
        and parses the commandline input arguments accordingly.
        """
        cmd = clg.CommandLine(self.get_specs(module_name))
        return cmd.parse()

    def __get_all_specs(self, subfolder=None):
        root_dir = cli.utils.validate_settings_dir(
            self.config.get('defaults', 'settings'))
        if subfolder:
            root_dir = os.path.join(root_dir, subfolder)

        res = []
        for dirpath, _, filenames in os.walk(root_dir):
            for filename in [f for f in filenames
                             if f.endswith(self.SPEC_EXTENSION)]:
                res.append(os.path.join(dirpath, filename))

        return res

config = load_config_file()
