from matplotlib import pyplot

from data_processing.data_processing.utils.getHeaders import get_header_index
from data_processing.data_processing.utils.utils import get_lines_csv
import numpy as np
import matplotlib.pyplot as plt


class DataAnalyser:
    def __init__(self, data_feed_path: str):
        self.data_feed_path = data_feed_path
        self.data_feed = get_lines_csv(data_feed_path, "\t")
        self.data_feed = self.data_feed[1:]

    def create_pie_plot(self, labels, numbers, title: str):

        fig1, ax1 = plt.subplots()
        ax1.pie(numbers, labels=labels, autopct='%1.1f%%',
                shadow=True, startangle=90)
        ax1.axis('equal')  # Equa   l aspect ratio ensures that pie is drawn as a circle.
        ax1.set_title(title)
        plt.savefig("/home/graphn/repositories/you_conscious/data_processing/data_analysis/images/" + title + "_pie.png")
    def create_simple_chart(self,labels,numbers,title):

        # libraries
        import numpy as np
        import matplotlib.pyplot as plt

        # Fake dataset
        height = [3, 12, 5, 18, 45]
        bars = ('A', 'B', 'C', 'D', 'E')
        y_pos = np.arange(len(bars))

        # Create bars and choose color
        plt.bar(y_pos, height, color=(0.5, 0.1, 0.5, 0.6))

        # Add title and axis names
        plt.title('My title')
        plt.xlabel('categories')
        plt.ylabel('values')

        # Limits for the Y axis
        plt.ylim(0, 60)

        # Create names
        plt.xticks(y_pos, bars)

        # Show graphic
        plt.show()

    def get_stats(self, column_name):
        merchants_index = get_header_index(column_name,
                                           self.data_feed_path)
        stats: dict = {}
        for row in self.data_feed:
            content = row[merchants_index]
            if content not in stats:
                stats[content] = 1
            else:
                stats[content] += 1
        return stats
