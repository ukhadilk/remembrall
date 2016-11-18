import os
PARENT_DIR = "/home/urjit/PycharmProjects/RemembrallBot/"

config_dict={}

def read_config_file():
    config_file_path = os.path.join(PARENT_DIR, "config/remembrall.properties")
    print config_file_path
    # try:
    with open(config_file_path) as f:
        for line in f:

            if line is not None and line.strip() != "":
                config_dict[line.strip().split("=")[0]] = line.strip().split("=")[1]
    # except Exception as err:
    #     print str(err)
    #     print "Error in reading config file"
    #     raise SystemExit

def read_os_environment_parameters():
    pass


def get_configs():
    read_config_file()
    read_os_environment_parameters()
    return config_dict


if __name__ == '__main__':
    print get_configs()