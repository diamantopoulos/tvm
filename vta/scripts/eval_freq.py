##############################################################################
#   Copyright 2018 - The OPRECOMP Project Consortium,
#                    IBM Research GmbH. All rights reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
##############################################################################

# @file evaluate_solution_bitacc.py
# @author Dionysios Diamantopoulos, did@zurich.ibm.com
# @date 15 Oct 2017
# @brief Script for fixed-point exploration for the BLSTM mb Uses the fixed-point
# library of Xilinx Vivado HLS. For a combination of fixed-point format,
# collects accuracy and synthesis results and plots them

import os
import subprocess
import numpy as np
import os.path
import fileinput
from shutil import copyfile
import pathlib


def check(file_to_search, string_to_find):
    if (not os.path.exists(file_to_search)):
        print("ERROR: file " + file_to_search + " does not exist, skipping...")
        return False
    else:
        with open(file_to_search) as f:
            datafile = f.readlines()
            found = False  # This isn't really necessary
            for line in datafile:
                if string_to_find in line:
                    # found = True # Not necessary
                    return True
            return False  # Because you finished the search without finding

def parse_hls_syn(report_file):
    command = "cat " + syn_log + "  | grep -A 3 Estimated | tail -n 2 | head -n 1 |  awk '{print $4}' | sed 's/.$//'"
    #print(command)
    estimated = subprocess.getoutput(command)
    command = "cat " + syn_log + "  | grep -A 3 Total | head -n 1 | awk '{print $3}' | sed 's/.$//'"
    brams = subprocess.getoutput(command)
    command = "cat " + syn_log + "  | grep -A 3 Total | head -n 1 | awk '{print $4}' | sed 's/.$//'"
    dsps = subprocess.getoutput(command)
    command = "cat " + syn_log + "  | grep -A 3 Total | head -n 1 | awk '{print $5}' | sed 's/.$//'"
    ffs = subprocess.getoutput(command)
    command = "cat " + syn_log + "  | grep -A 3 Total | head -n 1 | awk '{print $6}' | sed 's/.$//'"
    luts = subprocess.getoutput(command)
    return [estimated, brams, dsps, ffs, luts]


LOAD_SESSION = 0
PLOT_ENABLE = 1

savesessionfile = 'globalsave.npy'

if (LOAD_SESSION == 1):
    #dill.load_session(filename)
    [labels, confMat, mat_acc_min, mat_acc_max, [total_bits, frac_bits], mat_brams, mat_dsps, mat_ffs, mat_luts] = np.load(savesessionfile)

else:
    RUN_SIM = 1
    RUN_SYN  = True
    RUN_EVAL = True

    tvm_root = os.environ.get("TVM_HOME")
    vta_config = "pynq_1x16_i8w8a32_15_15_18_17"

    filein = tvm_root + "/vta/python/vta/pkg_config.py"
    fileout = tvm_root + "/vta/python/vta/pkg_config_replaced.py"
    log_file_path = "/tmp/run.log"
    syn_log = tvm_root + "/vta/build/hardware/xilinx/hls/" + vta_config + "/vta_sim/soln/syn/report/vta_csynth.rpt"
    pynq_images_dir = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/Images/"
    pathlib.Path(pynq_images_dir).mkdir(parents=True, exist_ok=True)
    pynq_image_path = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/export/"
    pathlib.Path(pynq_image_path).mkdir(parents=True, exist_ok=True)
    pynq_image_in = pynq_image_path + "vta.bit"

    f = open(filein,'r')
    filedata = f.read()
    f.close()
    print("1\n")
    if (RUN_SIM == 1):
        logfd = open("./run.log",'w')
        line = "hls_clk\tstatus\test\tbrams\tdsps\tffs\tluts"
        logfd.write(line+"\n")

        HLS_CLK_list = [7]

        sstring_HLSCLK = "self.fpga_per = "
        rstring_HLSCLK = "self.fpga_per = "
        print("2\n")

        for tr in HLS_CLK_list:
            search_string = sstring_HLSCLK
            replace_string = rstring_HLSCLK + str(tr) + " #"
            newdata = filedata.replace(search_string, replace_string)
            infostr = "Injecting " + filein + " with " + replace_string
            print(infostr)
            f = open(fileout,'w')
            f.write(newdata)
            f.close()
            copyfile(fileout, filein)
            print("3\n")


            evaluation = vta_config + "_FREQ-200_TARGET-" + str(tr)
            pynq_image_out = pynq_images_dir + evaluation + "_vta.bit"

            if (RUN_SYN):
                print("INFO: Synthesis of " + evaluation + " with Vivado...\n")
                if (not os.path.exists(pynq_image_out)):
                    print("WARNING: file " + pynq_image_out + " does not exist. Generating it...")

                    command = "cd " + tvm_root + "/vta/hardware/xilinx && make clean && make cleanall && make ip && time make > " + log_file_path
                    print(command)
                    subprocess.getoutput(command)
                    #process = subprocess.Popen(command, stderr=subprocess.STDOUT)
                    #if process.wait() != 0:
                    #    print("Severe Error executing command: " + command + ". Aborting this evaluation...\n")
                    #    continue
                    print("4\n")
                    if check(log_file_path, "BITSTREAM ERROR"):
                        status = 'FAIL'; estimated='0'; brams='0'; dsps='0'; ffs='0'; luts='0';
                    else:
                        status = ' OK '
                        [estimated, brams, dsps, ffs, luts] = parse_hls_syn(syn_log)
                        copyfile(pynq_image_out, pynq_image_in) #copyfile is oppsite to cp
                    print("5\n")
                else:
                    print("WARNING: file " + pynq_image_out + " was found already. Skipping generation.")
                    copyfile(pynq_image_in, pynq_image_out) # opposite copy
                    status = 'FOUND'; estimated='0'; brams='0'; dsps='0'; ffs='0'; luts='0';
            else:
                print("INFO: Skipping synthesis of " + evaluation + " with Vivado\n")
                status = 'SKIP'; estimated='0'; brams='0'; dsps='0'; ffs='0'; luts='0';


            if (RUN_EVAL):
                print("INFO: Evaluation of " + evaluation + " on PYNQs...\n")
                command = "python3 " + tvm_root + "/vta/tests/python/integration/test_did_benchmark_topi_conv2d.py > "  + log_file_path
                print(command)
                subprocess.getoutput(command)
                #process = subprocess.Popen(command, stderr=subprocess.STDOUT)
                #if process.wait() != 0:
                #    print("Severe Error executing command: " + command + ". Aborting this evaluation...\n")
                #    continue
                line = str(tr) + "\t" + status + "\t" + estimated + "\t" +  brams + "\t" + dsps + "\t" + ffs + "\t" + luts
                logfd.write(line+"\n")
            else:
                print("INFO: Skipping evaluation " + evaluation + " on PYNQs\n")
    print("6\n")

    if (RUN_SYN == 1):
        logfd.close()
