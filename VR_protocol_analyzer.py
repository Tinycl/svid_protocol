
signal_list = []
csv_file_handle = open("vrm_1.csv") 

clk_column = 2
dio_column = 0
alert_column = 1
time_column = 3

csv_index = 0
count = 0;


clk = 0
dio = 0
alert = 0
time = 0

last_clk = 2
last_dio = 2
last_last_dio = 2
last_time = 0
last_last_time = 0


svid_start_time = 0
svid_str_start = "" #3b
svid_str_add = "" #4b
svid_str_cmd = "" #5b
svid_str_data = "" #8b
svid_str_p1 = "" #1b
svid_str_end = "" #3b
svid_str_ta1 = "" #2b

svid_str_ack = "" #2b
svid_str_vrdata = "" #8b
svid_str_p2 = "" #1b
svid_str_ta2 = "" #2b

svid_start_flag = 0
svid_finish_flag = 0

svid_len = -1

vrm_sample = 1

while True:
    strline = csv_file_handle.readline()
    csv_index = csv_index + 1;
    if not strline:
        break
    #print(strline);
    strlist = strline.split(" ")
    if strlist[0] == "COLUMN":
        signal_list.append(strlist[1][1:-1])
    if strline == "HEADER_END\n":
        break
csv_file_handle.close()

csv_file_handle = open("vrm_1.csv") 
while True:
    strline = csv_file_handle.readline()
    count = count + 1;
    if not strline:
        break
    if count > csv_index:
        #print(strline)
        #break
        strlist = strline.strip('\n').split(',')
        clk = int(strlist[clk_column])
        dio = int(strlist[dio_column])
        alert = int(strlist[alert_column])
        time = int(strlist[time_column].strip(' '))
        #print(clk, dio, alert, time)

        if vrm_sample == 1:  # when cpu drive, vrm sample at falling edge
            if last_clk == 1 and clk == 0:
                if svid_start_flag == 0:
                    if last_last_dio == 0 and last_dio == 1 and dio == 0:
                        svid_start_flag = 1
                        svid_start_time = last_last_time
                     
                        
                    last_last_dio = last_dio
                    last_dio = dio  
                    

                if svid_start_flag == 1:
                    svid_len = svid_len + 1
                    if svid_len >= 1 and svid_len <= 4:
                        svid_str_add = svid_str_add + str(dio)
                    elif svid_len >= 5 and svid_len <= 9:
                        svid_str_cmd = svid_str_cmd + str(dio)
                    elif svid_len >= 10 and svid_len <= 17:
                        svid_str_data = svid_str_data + str(dio)
                    elif svid_len == 18 :
                        svid_str_p1 = svid_str_p1 + str(dio)
                    elif svid_len >= 19 and svid_len <= 21:
                        svid_str_end = svid_str_end + str(dio)
                    elif svid_len >= 22 and svid_len <= 23:
                        svid_str_ta1 = svid_str_ta1 + str(dio)
                        if svid_len == 23:
                            vrm_sample = 0
              
        
        if vrm_sample == 0:  #when vrm drive, cpu sample at rise edge
            if last_clk == 0 and clk == 1:
                svid_len = svid_len + 1
                if svid_len >= 24 and svid_len <= 25:
                    svid_str_ack = svid_str_ack + str(dio)
                elif svid_len >= 26 and svid_len <= 33:
                    svid_str_vrdata = svid_str_vrdata + str(dio)
                elif svid_len == 34:
                    svid_str_p2 = svid_str_p2 + str(dio)
                elif svid_len >= 35 and svid_len <= 36:
                    svid_str_ta2 = svid_str_ta2 + str(dio)
                    if svid_len == 36:
                        svid_finish_flag = 1
                        
        if svid_finish_flag == 1:
            svid_finish_flag = 0
            svid_len = -1
            vrm_sample = 1
            svid_start_flag = 0
            
            svid_iaddr = int(svid_str_add,2)

            svid_icmd = int(svid_str_cmd,2)
            str_tmp_cmd = ""
            if svid_icmd == 0x00:
                str_tmp_cmd = "Extended"
            elif svid_icmd == 0x01:
                str_tmp_cmd = "SetVID-fast"
            elif svid_icmd == 0x02:
                str_tmp_cmd = "SetVID-slow"
            elif svid_icmd == 0x03:
                str_tmp_cmd = "SetVID-Decay"
            elif svid_icmd == 0x04:
                str_tmp_cmd = "SetPS"
            elif svid_icmd == 0x05:
                str_tmp_cmd = "SetRegADR"
            elif svid_icmd == 0x06:
                str_tmp_cmd = "SetRegDAT"
            elif svid_icmd == 0x07:
                str_tmp_cmd = "GetReg"
            elif svid_icmd == 0x08:
                str_tmp_cmd = "Test Mode"
            else:
                str_tmp_cmd = "Reserved"

            svid_idata = int(svid_str_data,2)
            svid_iack = int(svid_str_ack,2)
            svid_ivrdata = int(svid_str_vrdata,2)
            svid_iend = int(svid_str_end,2)
            if svid_iend == 3:
                print(svid_start_time,",","VRM", svid_iaddr,",", str_tmp_cmd,",", "cmddata", hex(svid_idata),",", "ack", bin(svid_iack),",", "vrdata", hex(svid_ivrdata))
            else:
                print(svid_start_time, "," "svid bus error")

            svid_str_start = ""
            svid_str_add = ""
            svid_str_cmd = ""
            svid_str_data = ""
            svid_str_p1 = ""
            svid_str_end = ""
            svid_str_ta1 = ""

            svid_str_ack = ""
            svid_str_vrdata = ""
            svid_str_p2 = ""
            svid_str_ta2 = ""

        
        last_clk = clk
        last_last_time = last_time
        last_time = time


csv_file_handle.close()