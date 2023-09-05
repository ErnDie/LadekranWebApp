import json
from datetime import datetime, timedelta
import string
import numpy as np

import ntplib


class Latency:

    def __init__(self):
        self.rtt_list = []
        self.rtt_no_upload_list = []

    def start(self):
        self.start_time_rtt = datetime.now()

    def calculateLatency(self, response: string):
        self.end_time_rtt = datetime.now()
        self.rtt = self._calculateRTT(self.end_time_rtt - self.start_time_rtt)
        self.rtt_no_upload = self._calculateRTT_No_upload(self.end_time_rtt - self.start_time_rtt - self._string_to_timedelta(response))
        self.rtt_list.append(self.rtt)
        self.rtt_no_upload_list.append( self.rtt_no_upload)
        print(len(self.rtt_list))

    def printLatency(self):
        print("RTT: " + str(self.rtt) + "s")
        print("RTT No Upload: " + str(self.rtt_no_upload) + "s")

    def _string_to_timedelta(self, time_str):
        parts = time_str.split(':')
        seconds_part = parts[-1].split('.')

        hours = int(parts[0])
        minutes = int(parts[1])
        seconds = int(seconds_part[0])
        microseconds = int(seconds_part[1])

        time_delta = timedelta(hours=hours, minutes=minutes, seconds=seconds, microseconds=microseconds)
        return time_delta

    def _calculateRTT(self, timeDelta: timedelta):
        # If you use timedelta.microseconds the 0 at the beginning will be cut
        microSecondsString = str(timeDelta).split('.')[1]
        rtt = float(str(timeDelta.seconds) + "." + microSecondsString)
        return rtt

    def _calculateRTT_No_upload(self, timeDelta: timedelta):
        # If you use timedelta.microseconds the 0 at the beginning will be cut
        microSecondsString = str(timeDelta).split('.')[1]
        rtt = float(str(timeDelta.seconds) + "." + microSecondsString)
        return rtt

    def calculateRTTMetrics(self):
        rtt_sorted = self.rtt_list.copy()
        rtt_sorted.sort()
        self.rtt_max = rtt_sorted[-1]
        self.rtt_min = rtt_sorted[0]
        self.rtt_mean_interval = round(float(np.mean(self.rtt_list)), 6)
        self.rtt_std_deviation = round(float(np.std(self.rtt_list)), 6)
        self.rtt_25_quantil = np.quantile(self.rtt_list, .25)
        self.rtt_75_quantil = np.quantile(self.rtt_list, .75)
        self.rtt_average = round(float(np.average(self.rtt_list)), 6)


    def calculateRTTJitter(self):
        self.jitter_intervals = [round(abs(self.rtt_list[i] - self.rtt_list[i - 1]), 6) for i in
                                 range(1, len(self.rtt_list))]
        self.jitter_mean_interval = round(float(np.mean(self.jitter_intervals)), 6)
        self.jitter_std_deviation = round(float(np.std(self.jitter_intervals)), 6)
        time_intervals_sorted = self.jitter_intervals.copy()
        time_intervals_sorted.sort()
        self.jitter_max = time_intervals_sorted[-1]
        self.jitter_min = time_intervals_sorted[0]
        self.jitter_25_quantil = np.quantile(self.jitter_intervals, .25)
        self.jitter_75_quantil = np.quantile(self.jitter_intervals, .75)
        self.jitter_average = round(float(np.average(self.jitter_intervals)), 6)


    def calculateRTTNoUploadMetrics(self):
        rtt_no_upload_sorted = self.rtt_no_upload_list.copy()
        rtt_no_upload_sorted.sort()
        self.rtt_no_upload_max = rtt_no_upload_sorted[-1]
        self.rtt_no_upload_min = rtt_no_upload_sorted[0]
        self.rtt_no_upload_mean_interval = round(float(np.mean(self.rtt_no_upload_list)), 6)
        self.rtt_no_upload_std_deviation = round(float(np.std(self.rtt_no_upload_list)), 6)
        self.rtt_no_upload_25_quantil = np.quantile(self.rtt_no_upload_list, .25)
        self.rtt_no_upload_75_quantil = np.quantile(self.rtt_no_upload_list, .75)
        self.rtt_no_upload_average = round(float(np.average(self.rtt_no_upload_list)), 6)


    def calculateRTTNoUploadJitter(self):
        self.jitter_no_upload_intervals = [round(abs(self.rtt_no_upload_list[i] - self.rtt_no_upload_list[i - 1]), 6) for i in
                                 range(1, len(self.rtt_no_upload_list))]
        self.jitter_no_upload_mean_interval = round(float(np.mean(self.jitter_no_upload_intervals)), 6)
        self.jitter_no_upload_std_deviation = round(float(np.std(self.jitter_no_upload_intervals)), 6)
        time_intervals_sorted = self.jitter_no_upload_intervals.copy()
        time_intervals_sorted.sort()
        self.jitter_no_upload_max = time_intervals_sorted[-1]
        self.jitter_no_upload_min = time_intervals_sorted[0]
        self.jitter_no_upload_25_quantil = np.quantile(self.jitter_no_upload_intervals, .25)
        self.jitter_no_upload_75_quantil = np.quantile(self.jitter_no_upload_intervals, .75)
        self.jitter_no_upload_average = round(float(np.average(self.jitter_no_upload_intervals)), 6)

    def saveAsJSON(self):
        time = 3
        json_object = []
        for rtt in self.rtt_list:
            dic = {"seconds": time, "latency": rtt, "latency_type": "rtt"}
            json_object.append(dic)
            time = time + 3

        time = 3
        for rtt in self.rtt_no_upload_list:
            dic = {"seconds": time, "latency": rtt, "latency_type": "rtt_no_upload"}
            json_object.append(dic)
            time = time + 3

        time = 6
        for jitter in self.jitter_intervals:
            dic = {"seconds": time, "latency": jitter, "latency_type": "jitter"}
            json_object.append(dic)
            time = time + 3

        time = 6
        for jitter in self.jitter_no_upload_intervals:
            dic = {"seconds": time, "latency": jitter, "latency_type": "jitter_no_upload"}
            json_object.append(dic)
            time = time + 3

        with open("sample.json", "w") as outfile:
            json.dump(json_object, outfile)

    def saveMetricsAsTxt(self):
        result = "RTT-Ergebnisse: " + ','.join(map(str, self.rtt_list)) + "\n"
        result += "RTT-Min: " + str(self.rtt_min) + "\n"
        result += "RTT-Max: " + str(self.rtt_max) + "\n"
        result += "RTT-25%-Quartil: " + str(self.rtt_25_quantil) + "\n"
        result += "Mean: " + str(self.rtt_mean_interval) + "\n"
        result += "RTT-75%-Quartil: " + str(self.rtt_75_quantil) + "\n"
        result += "RTT-Durchschnitt: " + str(self.rtt_average) + "\n"
        result += "RTT-Standardabweichung: " + str(self.rtt_std_deviation) + "\n\n"

        result = "RTTNoUpload-Ergebnisse: " + ','.join(map(str, self.rtt_no_upload_list)) + "\n"
        result += "RTTNoUpload-Min: " + str(self.rtt_no_upload_min) + "\n"
        result += "RTTNoUpload-Max: " + str(self.rtt_no_upload_max) + "\n"
        result += "RTTNoUpload-25%-Quartil: " + str(self.rtt_no_upload_25_quantil) + "\n"
        result += "RTTNoUpload-Mean: " + str(self.rtt_no_upload_mean_interval) + "\n"
        result += "RTTNoUpload-75%-Quartil: " + str(self.rtt_no_upload_75_quantil) + "\n"
        result += "RTTNoUpload-Durchschnitt: " + str(self.rtt_no_upload_average) + "\n"
        result += "RTTNoUpload-Standardabweichung: " + str(self.rtt_no_upload_std_deviation) + "\n\n"

        result += "Jitter-Ergebnisse: " + ','.join(map(str, self.jitter_intervals)) + "\n"
        result += "Jitter-Min: " + str(self.jitter_min) + "\n"
        result += "Jitter-Max: " + str(self.jitter_max) + "\n"
        result += "Jitter-25%-Quartil: " + str(self.jitter_25_quantil) + "\n"
        result += "Jitter-Mean: " + str(self.jitter_mean_interval) + "\n"
        result += "Jitter-75%-Quartil: " + str(self.jitter_75_quantil) + "\n"
        result += "Jitter-Durchschnitt: " + str(self.jitter_average) + "\n"
        result += "Jitter-Standardabweichung: " + str(self.jitter_std_deviation) + "\n\n"

        result += "JitterNoUpload-Ergebnisse: " + ','.join(map(str, self.jitter_no_upload_intervals)) + "\n"
        result += "JitterNoUpload-Min: " + str(self.jitter_no_upload_min) + "\n"
        result += "JitterNoUpload-Max: " + str(self.jitter_no_upload_max) + "\n"
        result += "JitterNoUpload-25%-Quartil: " + str(self.jitter_no_upload_25_quantil) + "\n"
        result += "JitterNoUpload-Mean: " + str(self.jitter_no_upload_mean_interval) + "\n"
        result += "JitterNoUpload-75%-Quartil: " + str(self.jitter_no_upload_75_quantil) + "\n"
        result += "JitterNoUpload-Durchschnitt: " + str(self.jitter_no_upload_average) + "\n"
        result += "JitterNoUpload-Standardabweichung: " + str(self.jitter_no_upload_std_deviation) + "\n\n"

        with open("metrics.txt", "w") as outfile:
            outfile.write(result)

    def cleanUpData(self):
        self.rtt_list = [val for val in self.rtt_list if val <= 0.5]  # Should be changed for individual cases
