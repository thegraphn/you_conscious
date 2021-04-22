import logging
from pathlib import Path
from farm.data_handler.data_silo import DataSilo
from farm.data_handler.processor import TextClassificationProcessor
from farm.modeling.optimization import initialize_optimizer
from farm.infer import Inferencer
from farm.modeling.adaptive_model import AdaptiveModel
from farm.modeling.language_model import LanguageModel
from farm.modeling.prediction_head import TextClassificationHead
from farm.modeling.tokenization import Tokenizer
from farm.train import Trainer, EarlyStopping
from farm.utils import set_all_seeds, MLFlowLogger, initialize_device_settings
import csv


def doc_classification_multilabel():
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s",
        datefmt="%m/%d/%Y %H:%M:%S",
        level=logging.INFO)
    # https://public-mlflow.deepset.ai/#/experiments/162
    #https://public-mlflow.deepset.ai/#/experiments/162
    ml_logger = MLFlowLogger(tracking_uri="https://public-mlflow.deepset.ai/")
    ml_logger.init_experiment(experiment_name="category", run_name="distill_v3")

    ##########################
    # Settings
    ##########################
    data_path = "/home/graphn/repositories/you_conscious/dl_xp/data/category"
    set_all_seeds(seed=42)
    device, n_gpu = initialize_device_settings(use_cuda=True)
    n_epochs = 40
    batch_size =50

    evaluate_every = 1074
    lang_model = "distilbert-base-german-cased"
    do_lower_case = False

    # 1.Create a tokenizer
    tokenizer = Tokenizer.load(
        pretrained_model_name_or_path=lang_model,
        do_lower_case=do_lower_case)

    # 2. Create a DataProcessor that handles all the conversion from raw text into a pytorch Dataset
    # Here we load Toxic Comments Data automatically if it is not available.

    # get label lists

    import pandas as pd
    t = pd.read_csv("/home/graphn/repositories/you_conscious/dl_xp/data/category/train_category.tsv",sep="\t")
    tt = pd.read_csv("/home/graphn/repositories/you_conscious/dl_xp/data/category/test_category.tsv", sep="\t")
    tl = t["label"].tolist()
    ttl = tt["label"].tolist()
    label_list = list(set(tl+ttl))
    metric = "f1_macro"

    processor = TextClassificationProcessor(tokenizer=tokenizer,
                                            max_seq_len=200,
                                            data_dir=Path(data_path),
                                            label_list=label_list,
                                            metric=metric,
                                            quote_char='"',
                                            multilabel=False,
                                            train_filename="train_category.tsv",
                                            # dev_filename="val_category.tsv",
                                            test_filename="test_category.tsv",
                                            dev_split=0.2,
                                            )

    # 3. Create a DataSilo that loads several datasets (train/dev/test), provides DataLoaders for them and calculates a few descriptive statistics of our datasets
    data_silo = DataSilo(
        processor=processor,
        batch_size=batch_size)

    # 4. Create an AdaptiveModel
    language_model = LanguageModel.load(lang_model)
    prediction_head = TextClassificationHead(num_labels=len(label_list))

    model = AdaptiveModel(
        language_model=language_model,
        prediction_heads=[prediction_head],
        embeds_dropout_prob=0.1,
        lm_output_types=["per_sequence"],
        device=device)

    # 5. Create an optimizer
    model, optimizer, lr_schedule = initialize_optimizer(
        model=model,
        learning_rate=3e-5,
        device=device,
        n_batches=len(data_silo.loaders["train"]),
        n_epochs=n_epochs,
    )
    save_dir = Path("../trained_models/category_distil_v3")

    earlystopping = EarlyStopping(
        metric="f1_macro", mode="max",  # use the metric from our own metrics function instead of loss

        save_dir=save_dir,  # where to save the best model
        patience=round(n_epochs * 0.10)  # number of evaluations to wait for improvement before terminating the training
    )
    # 6. Feed everything to the Trainer, which keeps care of growing our model into powerful plant and evaluates it
    # from time to time
    trainer = Trainer(
        model=model,
        optimizer=optimizer,
        data_silo=data_silo,
        epochs=n_epochs,
        n_gpu=n_gpu,
        lr_schedule=lr_schedule,
        evaluate_every=evaluate_every,
        device=device,
        early_stopping=earlystopping)

    # 7. Let it grow
    trainer.train()

    # 8. Hooray! You have a model. Store it:

    # 9. Load it & harvest your fruits (Inference)
    basic_texts = [
        {
            "text": "Avocadostore [SEP] Herren [SEP] Gumbies Brown Retro – Nachhaltige Sommerschuhe Für Damen Und Herren [SEP] GUMBIES Brown Retro – 100% vegan. Nachhaltigkeit ist unser Gedanke. Deswegen verwenden wir für deine Sommerschuhe recyceltes Material: Die Sohle besteht aus recyceltem Kautschuk und der Fußriemen ist aus recycelter Baumwolle hergestellt. Sohle besteht aus recyceltem Kautschuk Besonders robuste Sohle für einen idealen Halt auf beinahe allen Untergründen Fußriemen aus recycelter Baumwolle Baumwoll-Zehensteg ist besonders weich und tragefreundlich Ideales Tragegefühl durch das ergonomisch geformte Fußbett Keine Verwendung von Polyester und Plastik Farbe: Braun / türkiser Fußriemen Größen: 36-46 Deine GUMBIES kannst du den ganzen Tag tragen. Die nachhaltigen Sandalen sind super weich und extrem bequem. Und das Beste: Endlich kein Scheuern mehr zwischen deinen Zehen. Deine Füße werden dich dafür lieben. Als die Idee der GUMBIES entstanden ist, war der Grundgedanke, einen nachhaltigen Sommer-Schuh zu entwickeln. Die Grundlage hinter den GUMBIES bildet dabei die markante Sohle, die aus recyceltem Kautschuk sowie Jute besteht und perfekten Halt auf allen Untergründen bietet. Die einzige Spur, die unsere GUMBIES in der Natur hinterlassen, ist ein nachhaltiger Fußabdruck beim Laufen durch den Sand. <SEP>"},

    ]
    model = Inferencer.load(save_dir)
    result = model.inference_from_dicts(dicts=basic_texts)
    print(result[0])


if __name__ == "__main__":
    doc_classification_multilabel()

