import natsort


class SizeSorter:
    """
    Class to sort the sizes
    """

    def __init__(self, size_list: list):
        self.size_list = size_list

        self.sorting_type: str = self.sorting_type_finder()
        self.sorted_sizes = self.sort_list()


    def sorting_type_finder(self) -> str:
        """
        Get the kind of size which are in the given list (e.g. number: 38,40 or letter: XL,S)
        :return: Type of the sizes
        """
        letter_counter: int = 0
        number_counter: int = 0
        average_letter: float = 0
        average_number: float = 0
        character_counter: int = 0

        if len(self.size_list) == 1:
            return "one_size"
        for size in self.size_list:
            if "UK" in size:
                return "number"
            for ch in size:
                character_counter += 1
                if ch.isdigit():
                    number_counter += 1
                if ch.isalpha():
                    letter_counter += 1
            if character_counter > 0:
                average_letter = letter_counter / character_counter
                average_number = number_counter / character_counter
            if average_letter > average_number:
                return "letter"

            else:
                return "number"

    def sort_list(self) -> list:
        """
        Sort the size list based on its type
        :return: Sorted size list
        """

        ordered_sizes: list = []

        if "OneSize" or "NoSize" in self.size_list:
            ordered_sizes = self.size_list
        if self.sorting_type == "one_size":
            ordered_sizes = self.size_list

        if self.sorting_type == "number":
            ordered_sizes = natsort.natsorted(self.size_list)

        if self.sorting_type == "letter":
            order_size: dict = {"XXXXXS": 0,
                                "XXXXS": 1,
                                "XXXS": 2,
                                "XXS": 3,
                                "XS": 4,
                                "XS-S": 5,
                                "S": 6,
                                "S-M": 7,
                                "M": 8,
                                "M-L": 9,
                                "L": 10,
                                "XL": 11, "XL-XXL": 12, "XXL": 13, "XXXL": 14, "XXXXL": 15, "XXXXXL": 16,
                                "XXXXXXL": 17,
                                "XXXXXXXL": 18}
            conversion_size: dict = {"5XS": "XXXXXS",
                                     "4XS": "XXXXS",
                                     "3XS": "XXXS",
                                     "2XS": "XXS",
                                     "XS": "XS",
                                     "S": "S",
                                     "M": "M",
                                     "L": "L",
                                     "XL": "XL",
                                     "2XL": "XXL",
                                     "3XL": "XXXL",
                                     "4XL": "XXXXL",
                                     "5XL": "XXXXXL",
                                     "6XL": "XXXXXXL",
                                     "7XL": "XXXXXXL"}
            tmp_dict_size: dict = {}
            for s, size in enumerate(self.size_list):
                if size in conversion_size.keys():
                    size = conversion_size[size]
                if size in order_size.keys():
                    tmp_dict_size[size] = order_size[size]
            ordered_sizes: list = list(
                {k: v for k, v in sorted(tmp_dict_size.items(), key=lambda item: item[1])}.keys())
        else:
            ordered_sizes = natsort.natsorted(self.size_list)

        return ordered_sizes

