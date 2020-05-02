import os
import sys

PROJECT_FOLDER = os.path.dirname(os.path.abspath(os.getcwd()))
PROJECT_FOLDER = PROJECT_FOLDER.replace("text_classification/main_category_de", "")
sys.path.append(PROJECT_FOLDER)

PROJECT_FOLDER = os.path.dirname(os.path.abspath(os.getcwd()))
PROJECT_FOLDER = PROJECT_FOLDER.replace("text_classification/main_category_de", "")
sys.path.append(PROJECT_FOLDER)
from text_classification.main_category_de.evaluation.evaluator import Evaluator

from absl import flags
from absl import app

FLAGS = flags.FLAGS
flags.DEFINE_string("input_data_set", "", "path to the training data set")
flags.DEFINE_string("model_path", "",
                    "The model and dictionaries files you will use for the predictions")
flags.DEFINE_bool("model_dependencies", False,
                  "Set on true if the model requires dependencies. They must be in the same"
                  "model's folder")
flags.DEFINE_integer("batch_size", 32, "batch size")
flags.DEFINE_string("csv_delimiter", "", "delimiter used in the training data set. If it is \t please write tab")
flags.DEFINE_integer("position_class", None, "position's index of the classes")
flags.DEFINE_integer("position_text", None, "position's index of the texts")
flags.DEFINE_string("optimizer", "", "sgd rmsprop adagrad adadelta adam adamax nadam")
flags.DEFINE_string("label_delimiter", "", "Delimiter used to split the different possible labels")


def main(argv):
    evaluator: Evaluator = Evaluator(model_path=FLAGS.model_path, model_path_dependencies=FLAGS.model_dependencies,
                                     data_set_path=FLAGS.input_data_set, batch_size=FLAGS.batch_size,
                                     csv_delimiter=FLAGS.csv_delimiter, label_delimiter=FLAGS.label_delimiter,
                                     label_row_index=FLAGS.position_class, text_row_index=FLAGS.position_text)
    x_test = evaluator.x_test
    y_test = evaluator.y_test
    print("x", x_test[10])
    print("y", y_test[10])
    evaluator.evaluate(x_test, y_test)


if __name__ == "__main__":
    app.run(main)
