import os
import os.path as op
import subprocess
import argparse
import glob
import time
import pandas as pd
import numpy as np


class RunVinsFusion:
    def __init__(self):
        self.PKG_NAME = "vins"
        self.NODE_NAME = "vins_node"
        self.CONFIG_DIR = "/work/catkin_ws/src/vins-fusion/config"
        self.DATA_ROOT = "/data/dataset"
        self.OUTPUT_ROOT = "/data/output"
        self.NUM_TEST = 5
        self.TEST_IDS = None

    def run_vinsfusion(self, opt):
        self.check_base_paths()
        self.TEST_IDS = list(range(self.NUM_TEST)) if opt.test_id < 0 else [opt.test_id]

        if opt.dataset == "all":
            command_makers = [self.euroc_mav]
            commands = []
            configs = []
            for cmdmaker in command_makers:
                cmds, cfgs = cmdmaker(opt)
                commands.extend(cmds)
                configs.extend(cfgs)
        elif opt.dataset == "euroc_mav":
            commands, configs = self.euroc_mav(opt)
        else:
            raise FileNotFoundError()

        print("===== Total {} runs".format(len(commands)))

        for i in range(3):
            print("start maplab in {} sec".format(3-i))
            time.sleep(1)

        for ci, (cmd, cfg) in enumerate(zip(commands, configs)):
            bagfile = cmd[0]
            outfile = cmd[-1]
            os.makedirs(op.dirname(outfile), exist_ok=True)
            print("\n===== RUN VINS-fusion {}/{}\nconfig: {}\ncmd: {}\n"
                  .format(ci+1, len(commands), cfg, cmd))
            subprocess.Popen(cmd[1:])
            time.sleep(5)
            subprocess.run(["rosbag", "play", bagfile], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["chmod", "-R", "a+rw", self.OUTPUT_ROOT])
            assert op.isfile(outfile), "===== ERROR: output file was NOT created: {}".format(outfile)

    def check_base_paths(self):
        assert op.isfile("/work/catkin_ws/devel/lib/vins/vins_node"), "VINS executer doesn't exist"
        assert op.isdir(self.DATA_ROOT), "datset dir doesn't exist"
        assert op.isdir(self.CONFIG_DIR), "config dir doesn't exist"
        assert op.isdir(self.OUTPUT_ROOT), "output dir doesn't exist"

    # Usage:
    # rosrun vins vins_node
    #       /path/to/xxx_config.yaml
    #       /path/to/outfile
    def euroc_mav(self, opt):
        dataset = "euroc_mav"
        dataset_path = op.join(self.DATA_ROOT, dataset, "bags")
        config_path = op.join(self.CONFIG_DIR, "euroc")
        config_files = {"mvio": "euroc_mono_imu_config.yaml", "stereo": "euroc_stereo_config.yaml",
                        "svio": "euroc_stereo_imu_config.yaml"}
        output_path = op.join(self.OUTPUT_ROOT, dataset)
        if not op.isdir(output_path):
            os.makedirs(output_path)
        sequences = glob.glob(dataset_path + "/*.bag")
        if opt.seq_idx != -1:
            sequences = [sequences[opt.seq_idx]]
        outprefix = "vinsfs"

        commands = []
        configs = []
        for suffix, conf_file in config_files.items():
            for si, bagfile in enumerate(sequences):
                outname = outprefix + "_" + suffix
                config_file = op.join(config_path, conf_file)
                for test_id in self.TEST_IDS:
                    output_file = op.join(output_path, "{}_s{:02d}_{}.txt".format(outname, si, test_id))

                    cmd = [bagfile, "rosrun", self.PKG_NAME, self.NODE_NAME, config_file, output_file]
                    commands.append(cmd)
                    conf = {"executer": outname, "config": conf_file, "dataset": dataset,
                            "seq_name": op.basename(bagfile), "seq_id": si, "test id": test_id}
                    configs.append(conf)
                print("===== command:", " ".join(commands[-1]))
        return commands, configs


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--dataset", default="all", type=str, help="dataset name")
    parser.add_argument("-t", "--test_id", default=-1, type=int, help="test id")
    parser.add_argument("-s", "--seq_idx", default=-1, type=int,
                        help="int: index of sequence in sequence list, -1 means all")
    opt = parser.parse_args()

    vins = RunVinsFusion()
    vins.run_vinsfusion(opt)


if __name__ == "__main__":
    main()