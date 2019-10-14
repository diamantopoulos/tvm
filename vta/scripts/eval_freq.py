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

LOAD_SESSION = 0

PLOT_ENABLE = 1

savesessionfile = 'globalsave.npy'

if (LOAD_SESSION == 1):
    #dill.load_session(filename)
    [labels, confMat, mat_acc_min, mat_acc_max, [total_bits, frac_bits], mat_brams, mat_dsps, mat_ffs, mat_luts] = np.load(savesessionfile)

else:
    RUN_SIM = 1
    RUN_VHLS = 0

    filein = "/home/did/tvm_did/vta/python/vta/pkg_config.py"
    fileout = "/home/did/tvm_did/vta/python/vta/pkg_config_replaced.py"
    log_file_path = "/tmp/run.log"
    syn_log = "./hw/hlsBLSTM_xcku060-ffva1156-2-e/blstm/syn/report/Single_Kernel_BLSTM_csynth.rpt"
    f = open(filein,'r')
    filedata = f.read()
    f.close()

    if (RUN_SIM == 1):
        logfd = open("./run.log",'w')

        HLS_CLK_list = [2, 3]

        sstring_HLSCLK = "self.fpga_per = "
        rstring_HLSCLK = "self.fpga_per = "


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

            if (RUN_SIM == 1):
                command = "cd /home/did/tvm_did/vta/hardware/xilinx/hw/ && make clean && make cleanall && time make && python3 /home/did/tvm_did/vta/tests/python/integration/test_benchmark_topi_conv2d.py > " + log_file_path
                print(command)
                #subprocess.getoutput(command)

    if (RUN_VHLS == 1):
        logfd.close()
