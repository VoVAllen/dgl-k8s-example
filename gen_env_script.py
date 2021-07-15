import os
import json
import socket
import time
from pathlib import Path


def generate_ip_config():
    base_dir = Path("/dgl-k8s/")
    base_dir.mkdir(exist_ok=True)
    env_dict = {}
    assert "TF_CONFIG" in os.environ
    print(os.environ["TF_CONFIG"])
    config = json.loads(os.environ["TF_CONFIG"])
    my_index = config['task']['index']
    domain_port_list = config["cluster"]["ps"]
    ip_list = []
    ip_config_path = base_dir / "ip_config.txt"

    with open(ip_config_path, "w") as f:
        for domain_port in domain_port_list:
            domain, port = domain_port.split(":")
            result = None
            while result is None:
                try:
                    # connect
                    result = socket.gethostbyname(domain)
                except:
                    time.sleep(1)
            ip_list.append(result)
            f.write("{} {}\n".format(result, 30050))

    env_dict["MACHINE_ID"] = str(my_index)
    env_dict["NUM_MACHINES"] = str(len(domain_port_list))
    env_dict["MASTER_ADDRESS"] = ip_list[0]
    env_dict["DGL_IP_CONFIG"] = str(ip_config_path)

    num_trainers = int(os.environ["DGL_NUM_TRAINER"])
    num_samplers = int(os.environ["DGL_NUM_SAMPLER"])
    env_dict["DGL_NUM_CLIENT"] = num_trainers * (1 + num_samplers) * len(domain_port_list)
    print("Finished resolving domain")
    return env_dict

# def generate_dgl_related_env():
#     num_servers = os.environ["DGL_NUM_SERVERS"]
#     num_machines = len(json.loads(os.environ["TF_CONFIG"])["cluster"]["ps"])

env_dict = generate_ip_config()
script_output = Path("env.sh")

with open(script_output, "w") as f:
    for k,v in env_dict.items():
        f.write(f"export {k}={v} \n")
