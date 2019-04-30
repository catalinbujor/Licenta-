import plotly.plotly as py
import plotly
import plotly.graph_objs as go
import numpy


class ChartGenerator:
    def __init__(self, username, api_key):
        self.username = username
        self.api_key = api_key
        self.kcf_errors = set()
        self.mil_errors = set()
        self.boosting_errors = set()
        self.csrt_errors = set()
        self.median_errors = set()
        self.kcf_csrt_errors = set()
        self.kcf_median_errors = set()
        self.kcf_mil_errors = set()
        self.kcf_time = []
        self.mil_time = []
        self.boosting_time = []
        self.csrt_time = []
        self.median_time = []
        self.kcf_median_time = []
        self.kcf_csrt_time = []
        self.kcf_mil_time =[]

    def generate_chart(self):
        print("Parsing started ... ")
        with open("./../stats/errors") as fp:
            line = fp.readline()
            while line:
                try:
                    if 'KCF' in line:
                        self.kcf_errors.add(line.rstrip())
                    if 'MIL' in line:
                        self.mil_errors.add(line.rstrip())
                    if 'BOOSTING' in line:
                        self.boosting_errors.add(line.rstrip())
                    if 'CSRT' in line:
                        self.csrt_errors.add(line.rstrip())
                    if 'MEDIANFLOW' in line:
                        self.median_errors.add(line.rstrip())
                    if 'KCF+CSRT' in line:
                        self.kcf_csrt_errors.add(line.rstrip())
                    if 'KCF+MEDIANFLOW' in line:
                        self.kcf_median_errors.add(line.rstrip())
                    if 'KCF+MIL' in line:
                        self.kcf_mil_errors.add(line.rstrip())

                except:
                    print("Ouups ! Something wrong with errors's file format !")
                line = fp.readline()

        with open("./../stats/time") as fp:
            line = fp.readline()
            while line:
                try:
                    if 'KCF' in line:
                       self.kcf_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'MIL' in line:
                       self.mil_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'BOOSTING' in line:
                       self.boosting_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'CSRT' in line:
                       self.csrt_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'MEDIANFLOW' in line:
                       self.median_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'KCF+MIL' in line :
                        self.kcf_mil_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'KCF+CSRT' in line:
                        self.kcf_csrt_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                    if 'KCF+MEDIANFLOW' in line:
                        self.kcf_median_time.append(float(line.split(':')[1].rstrip().lstrip()[:-1]))
                except:
                    print("Ouups ! Something wrong with time's file format !")
                line = fp.readline()

        print("Parsing done !")
        plotly.tools.set_credentials_file(username=self.username, api_key=self.api_key)

        print("Generating chart..")
        errors = go.Bar(
            x=['KCF', 'BOOSTING', 'MIL', 'MEDIAN', 'CSRT', "KCF+MIL",'KCF+CSRT','KCF+MEDIAN'],
            y=[len(self.kcf_errors) - 3, len(self.boosting_errors), len(self.mil_errors), len(self.median_errors), len(self.csrt_errors),
               len(self.kcf_mil_errors), len(self.kcf_csrt_errors), len(self.kcf_median_errors)],
            name='Number of errors',
            marker=dict(
                color='rgb(255, 0, 0)'
            )
        )

        time = go.Bar(
            x=['KCF', 'BOOSTING', 'MIL', 'MEDIAN', 'CSRT', 'KCF+MIL', 'KCF+CSRT' ,'KCF+MEDIAN'],
            y=[numpy.mean(self.kcf_time), numpy.mean(self.boosting_time), numpy.mean(self.mil_time), numpy.mean(self.median_time),
               numpy.mean(self.csrt_time), numpy.mean(self.kcf_mil_time), numpy.mean(self.kcf_csrt_time), numpy.mean(self.kcf_median_time)],
            name='Time to first detection',
            marker=dict(
                color='rgb(0, 255, 0)',
            )
        )

        data = [errors, time]
        layout = go.Layout(
            xaxis=dict(tickangle=-45),
            barmode='group',
        )
        fig = go.Figure(data=data, layout=layout)
        py.iplot(fig, filename='angled-text-bar')
        print("New chart generated at : " + "https://plot.ly/organize/home/")
