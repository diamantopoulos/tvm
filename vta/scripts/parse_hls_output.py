##############################################################################
#   Copyright 2019 - IBM Research GmbH. All rights reserved.
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

# @file eval_freq.py
# @author Dionysios Diamantopoulos, did@zurich.ibm.com
# @date 18 Oct 2019
# @brief Script for exploration of frequency for VTA

import os
import subprocess
import numpy as np
import os.path

def parse_hls_log(report_file):
    command = "cat " + report_file + "  | grep -A 3 Estimated | tail -n 2 | head -n 1 |  awk '{print $4}' | sed 's/.$//'"
    #print(command)
    estimated = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $3}' | sed 's/.$//'"
    brams = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $4}' | sed 's/.$//'"
    dsps = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $5}' | sed 's/.$//'"
    ffs = subprocess.getoutput(command)
    command = "cat " + report_file + "  | grep -A 3 Total | head -n 1 | awk '{print $6}' | sed 's/.$//'"
    luts = subprocess.getoutput(command)
    return [estimated, brams, dsps, ffs, luts]


tvm_root = os.environ.get("TVM_HOME")
vta_config = "pynq_1x16_i8w8a32_15_15_18_17"

filein = tvm_root + "/vta/python/vta/pkg_config.py"
fileout = tvm_root + "/vta/python/vta/pkg_config_replaced.py"
pynq_report_hls_in = tvm_root + "/vta/build/hardware/xilinx/hls/" + vta_config + "/vta_sim/soln/syn/report/compute_csynth.rpt"


[estimated, brams, dsps, ffs, luts] = parse_hls_log(pynq_report_hls_in)

line = estimated + "\t" + brams + "\t" + dsps + "\t" + ffs + "\t" + luts + "\n"

logfd = open("./run.log",'w')
logfd.write(line)
logfd.close()
