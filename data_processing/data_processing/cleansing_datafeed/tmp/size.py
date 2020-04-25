import re


class SizeFinder:
    def __init__(self, str_used: str):
        self.str_used: str = str_used
        self.list_regex: list = self.getRegexes()

    def getRegexes(self):
        list_regex: list = ["(Gr.?)\s{0,3}\d\d?",
                            "(Grosse.?)\s{0,3}\d\d?",
                            "(Grösse.?)\s{0,3}\d\d?",
                            "(Größe.?)\s{0,3}\d\d?",
                            "\w?\d?\d?\/\w?\d\d"

                            ]
        return list_regex

    def find_size(self)->list:
        """
        search for the begin and the end of size
        :return:
        """
        for size_regex in self.list_regex:
            matches = re.finditer(size_regex, self.str_used, re.MULTILINE)

            for matchNum, match in enumerate(matches, start=1):

                if type(match.start()) == int and type(match.end()) == int:
                    return [match.start(), match.end()]

    def delete_size(self)->str:
        """
        delete the size
        :return: cleansed string
        """

        for size_regex in self.list_regex:
            self.str_used = re.sub(size_regex,"",self.str_used)
        return self.str_used



