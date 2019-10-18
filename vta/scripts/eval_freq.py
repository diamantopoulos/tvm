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

def parse_hls_log(report_file):
    command = "cat " + pynq_report_hls_in + "  | grep -A 3 Estimated | tail -n 2 | head -n 1 |  awk '{print $4}' | sed 's/.$//'"
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

def parse_vivado_log(util_file, timing_file):
    # parse Vivado utilization report file
    command = "cat " + util_file + "  | grep  \"Slice LUTs\" |  awk '{print $5}'"
    vluts = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice LUTs\" |  awk '{print $11}'"
    vlutsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice Registers\" | head -n 1 | awk '{print $5}'"
    vffs = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Slice Registers\" | head -n 1 | awk '{print $11}'"
    vffsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Block RAM Tile\" | head -n 1 | awk '{print $6}'"
    vbrams = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"Block RAM Tile\" | head -n 1 | awk '{print $12}'"
    vbramsp = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"DSPs\" | head -n 1 | awk '{print $4}'"
    vdsps = subprocess.getoutput(command)
    command = "cat " + util_file + "  | grep  \"DSPs\" | head -n 1 | awk '{print $10}'"
    vdspsp = subprocess.getoutput(command)

    # parse Vivado timing report file: WNS(ns), TNS(ns), TNS Failing Endpoints, TNS Total Endpoints
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $1}'"
    wns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $2}'"
    tns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $3}'"
    tns_fail_endpns = subprocess.getoutput(command)
    command = "cat " + timing_file + "  | grep -A 2 \"WNS(ns)\" | head -n 3 | tail -n 1 | awk '{print $4}'"
    tns_tot_endpns = subprocess.getoutput(command)

    return [vbrams, vdsps, vffs, vluts, vbramsp, vdspsp, vffsp, vlutsp, wns, tns, tns_fail_endpns, tns_tot_endpns]




LOAD_SESSION = 0
PLOT_ENABLE = 1

savesessionfile = 'globalsave.npy'

if (LOAD_SESSION == 1):
    #dill.load_session(filename)
    [labels, confMat, mat_acc_min, mat_acc_max, [total_bits, frac_bits], mat_brams, mat_dsps, mat_ffs, mat_luts] = np.load(savesessionfile)

else:
    RUN_SIM = 1
    RUN_SYN  = True
    RUN_EVAL = False

    tvm_root = os.environ.get("TVM_HOME")
    vta_config = "pynq_1x16_i8w8a32_15_15_18_17"

    filein = tvm_root + "/vta/python/vta/pkg_config.py"
    fileout = tvm_root + "/vta/python/vta/pkg_config_replaced.py"
    log_file_path = "/tmp/run.log"
    pynq_report_hls_in = tvm_root + "/vta/build/hardware/xilinx/hls/" + vta_config + "/vta_sim/soln/syn/report/vta_csynth.rpt"
    pynq_images_dir = tvm_root + "/vta/Images/"
    pathlib.Path(pynq_images_dir).mkdir(parents=True, exist_ok=True)
    pynq_image_path  = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/export/"
    pynq_report_path = tvm_root + "/vta/build/hardware/xilinx/vivado/" + vta_config + "/vta.runs/impl_1/"

    pathlib.Path(pynq_image_path).mkdir(parents=True, exist_ok=True)
    pynq_image_in = pynq_image_path + "vta.bit"
    pynq_report_timing_in = pynq_report_path + "vta_wrapper_timing_summary_routed.rpt"
    pynq_report_utilization_in = pynq_report_path + "vta_wrapper_utilization_placed.rpt"

    f = open(filein,'r')
    filedata = newdata = f.read()
    f.close()
    print("1\n")
    if (RUN_SIM == 1):
        logfd = open("./run.log",'w')
        line = "hls_clk\tstatus\test\tbrams\tdsps\tffs\tluts\tvbrams\tvdsps\tvffs\tvluts\twns\ttns\ttns_fail_endpns\ttns_tot_endpns\n"
        logfd.write(line)
        logfd.close()

        HLS_CLK_list = [1, 2, 3, 3.5, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10]

        sstring_HLSCLK = "self.fpga_per = "
        rstring_HLSCLK = "self.fpga_per = "

        for tr in HLS_CLK_list:
            search_string = sstring_HLSCLK
            replace_string = rstring_HLSCLK + str(tr) + " #"
            newdata = newdata.replace(search_string, replace_string)
            infostr = "Injecting " + filein + " with " + replace_string
            f = open(fileout,'w')
            f.write(newdata)
            f.close()
            copyfile(fileout, filein)

            evaluation = vta_config + "_FREQ-100_TARGET-" + str(tr)
            pynq_image_out = pynq_images_dir + evaluation + "_vta.bit"
            pynq_report_hls_out = pynq_images_dir + evaluation + "_vta_csynth.rpt"
            pynq_report_timing_out = pynq_images_dir + evaluation + "_vta_wrapper_timing_summary_routed.rpt"
            pynq_report_utilization_out = pynq_images_dir + evaluation + "_vta_wrapper_utilization_placed.rpt"

            if (RUN_SYN):
                print("INFO: Synthesis of " + evaluation + " with Vivado...")
                if (not os.path.exists(pynq_image_out)):
                    print("WARNING: file " + pynq_image_out + " does not exist. Generating it...")
                    command = "cd " + tvm_root + "/vta/hardware/xilinx && make clean && make cleanall && make ip && time make > " + log_file_path
                    subprocess.getoutput(command)
                    #process = subprocess.Popen(command, stderr=subprocess.STDOUT)
                    #if process.wait() != 0:
                    #    print("Severe Error executing command: " + command + ". Aborting this evaluation...\n")
                    #    continue
                    status = ' OK '
                    copyfile(pynq_image_in, pynq_image_out)
                    copyfile(pynq_report_hls_in, pynq_report_hls_out)
                    copyfile(pynq_report_timing_in, pynq_report_timing_out)
                    copyfile(pynq_report_utilization_in, pynq_report_utilization_out)
                    [estimated, brams, dsps, ffs, luts] = parse_hls_log(pynq_report_hls_in)
                    [vbrams, vdsps, vffs, vluts, vbramsp, vdspsp, vffsp, vlutsp, wns, tns, tns_fail_endpns, tns_tot_endpns] = parse_vivado_log(pynq_report_utilization_in, pynq_report_timing_in)
                else:
                    print("WARNING: file " + pynq_image_out + " was found already. Skipping generation.")
                    copyfile(pynq_image_out, pynq_image_in) # opposite copy
                    status = 'FOUND';
                    [estimated, brams, dsps, ffs, luts] = parse_hls_log(pynq_report_hls_out)
                    [vbrams, vdsps, vffs, vluts, vbramsp, vdspsp, vffsp, vlutsp, wns, tns, tns_fail_endpns, tns_tot_endpns] = parse_vivado_log(pynq_report_utilization_out, pynq_report_timing_out)
            else:
                print("INFO: Skipping synthesis of " + evaluation + " with Vivado\n")
                status = 'SKIP'; estimated='0'; brams='0'; dsps='0'; ffs='0'; luts='0'; bramsp='0'; dspsp='0'; ffsp='0'; lutsp='0'; wns='0'; tns='0'; tns_fail_endpns='0'; tns_tot_endpns='0';


            if (RUN_EVAL):
                print("INFO: Evaluation of " + evaluation + " on PYNQs...\n")
                command = "python3 " + tvm_root + "/vta/tests/python/integration/test_did_benchmark_topi_conv2d.py > "  + log_file_path
                subprocess.getoutput(command)
                #process = subprocess.Popen(command, stderr=subprocess.STDOUT)
                #if process.wait() != 0:
                #    print("Severe Error executing command: " + command + ". Aborting this evaluation...\n")
                #    continue
            else:
                print("INFO: Skipping evaluation " + evaluation + " on PYNQs\n")

            line = line + str(tr) + "\t" + status + "\t" + estimated + "\t" +  brams + "\t" + dsps + "\t" + ffs + "\t" + luts + "\t" +  vbrams + "\t" + vdsps + "\t" + vffs + "\t" + vluts + "\t" + wns + "\t" + tns + "\t" + tns_fail_endpns + "\t" + tns_tot_endpns + "\n"
            logfd = open("./run.log",'w')
            logfd.write(line)
            logfd.close()


    #restore config
    f = open(filein,'w')
    f.write(filedata)
    f.close()
